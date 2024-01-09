import os
import re
import subprocess
import argparse

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Traverse subject directories and run the script on STOP fMRI files.")
parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without executing the script.")
args = parser.parse_args()

# Base directory containing the subject folders
base_dir = '/home/spinney/project/data/neuroventure/sourcedata/eprime'
bids_dir = '/home/spinney/project/data/neuroventure/bids'
# Regular expression pattern to identify STOP fMRI files
stop_fMRI_pattern = re.compile(r'NeuroVen_STOP_fMRI_FRENCH_2JB-(\d+)-\d+.txt')

# Regular expression pattern to extract the session from the directory name
session_pattern = re.compile(r'V(\d+)')

# List of directories (V1, V2, V3)
v_directories = ['V1', 'V2', 'V3']

# Iterate through V directories
for v_dir in v_directories:
    v_dir_path = os.path.join(base_dir, v_dir)
    
    if os.path.exists(v_dir_path):
        # Iterate through subject folders within the V directory
        for subject_folder in os.listdir(v_dir_path):
            subject_path = os.path.join(v_dir_path, subject_folder)
            
            if os.path.isdir(subject_path):
                # Look for STOP fMRI files in the subject's directory
                stop_fMRI_files = [f for f in os.listdir(subject_path) if stop_fMRI_pattern.match(f)]
    
                if stop_fMRI_files:
                    # Extract the subject label from the first matching file
                    subject_match = stop_fMRI_pattern.match(stop_fMRI_files[0])
                    subject_label = subject_match.group(1).zfill(3)
                    subject_number = os.path.basename(subject_path)[-3:]
                    if subject_label == subject_number:
                        print(subject_number)
                    else:
                        subject_label = subject_number
                    
                    # Extract the session from the directory name
                    session_match = session_pattern.search(v_dir_path)
                    if session_match:
                        session = session_match.group(1).zfill(2)  # Padding with zero
                    else:
                        session = ''  # Handle cases where there's no match
    
                    print(f"Subject: {subject_label}, Session: {session}, V Directory: {v_dir}")
    
                    # Construct the command to call the previous script with the subject label, session, BIDS directory, and log file
                    if len(stop_fMRI_files) > 1:
                        print(f"Found {len(stop_fMRI_files)} stop event files. Mapping them to runs.")
                        for run, log_file in enumerate(stop_fMRI_files):
                            log_file = os.path.join(subject_path, log_file)
                            print(f"Run {run}; Logfile: {log_file}")
                            cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_stop_eventfiles.py', '--log_file', f'{log_file}','--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{str(run+1).zfill(2)}', '--bids-dir', f'{bids_dir}']
        
                        if args.dry_run:
                            print("Dry run: Would execute the following command:")
                            print(' '.join(cmd))
                        else:
                            # Execute the script
                            subprocess.run(cmd)

                    else:            
                        run="01"                
                        log_file = os.path.join(subject_path, stop_fMRI_files[0])
                        cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_stop_eventfiles.py', '--log_file', f'{log_file}','--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{run.zfill(2)}', '--bids-dir', f'{bids_dir}']
        
                        if args.dry_run:
                            print("Dry run: Would execute the following command:")
                            print(' '.join(cmd))
                        else:
                            # Execute the script
                            subprocess.run(cmd)
