import os
import re
import subprocess
import argparse

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Traverse subject directories and run the script on MIDT fMRI files.")
parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without executing the script.")
args = parser.parse_args()

# Base directory containing the subject folders
base_dir = '/home/spinney/project/data/neuroventure/sourcedata/eprime'
bids_dir = '/home/spinney/project/data/neuroventure/bids'
# Regular expression pattern to identify STOP fMRI files
midt_fMRI_pattern = re.compile(r'NeuroVen_MIDT_fMRI_*_(.*?)-(\d+)-(\d+)\.txt')

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
                midt_fMRI_files = [f for f in os.listdir(subject_path) if midt_fMRI_pattern.match(f)]

                if midt_fMRI_files:                    

                    subject_match = midt_fMRI_pattern.match(midt_fMRI_files[0])
                    subject_label = subject_match.group(2).zfill(3)
                    run_number = subject_match.group(3).zfill(2)

                    subject_number = os.path.basename(subject_path)[-3:]

                    if subject_label == subject_number:
                        print(subject_number)
                    else:
                        subject_label = subject_number

                    session_match = session_pattern.search(v_dir_path)
                    if session_match:
                        session = session_match.group(1).zfill(2)  # Padding with zero
                    else:
                        session = ''  # Handle cases where there's no match

                    if len(midt_fMRI_files) > 1:
                        print(f"Found {len(midt_fMRI_files)} midt event files. Mapping them to runs.")
                        for run, log_file in enumerate(midt_fMRI_files):
                            subject_match = midt_fMRI_pattern.match(log_file)
                            subject_label = subject_match.group(2).zfill(3)
                            run_number = subject_match.group(3).zfill(2)
                            if run != run_number:
                                print(f"Run {run} and run number from current eprime file: {run_number} not the same.")
                                raise ValueError
                            m=midt_fMRI_pattern.match(log_file)
                            #subject_label = m.group(2)
                            #session = m.group(3).zfill(2)  
                            
                            # Extract the session from the directory name
                            #session_match = session_pattern.search(v_dir_path)
                            #if session_match:
                            #    session = session_match.group(1).zfill(2)  # Padding with zero
                            #else:
                            #    session = ''  # Handle cases where there's no match
            
                            print(f"Subject: {subject_label}, Session: {session}, V Directory: {v_dir}")
            
                            # Construct the command to call the previous script with the subject label, session, BIDS directory, and log file
                            #log_file = os.path.join(subject_path, midt_fMRI_files[0])
                            cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_midt_eventfiles.py', '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{str(run+1).zfill(2)}', '--bids-dir', f'{bids_dir}']
            
                            if args.dry_run:
                                print("Dry run: Would execute the following command:")
                                print(' '.join(cmd))
                            else:
                                # Execute the script
                                subprocess.run(cmd)


                    else:
                        # Extract the subject label from the first matching file
                        #m=midt_fMRI_pattern.match(midt_fMRI_files[0])
                        #subject_label = m.group(2)
                        #session = m.group(3).zfill(2)  
                        
                        # Extract the session from the directory name
                        #session_match = session_pattern.search(v_dir_path)
                        #if session_match:
                        #    session = session_match.group(1).zfill(2)  # Padding with zero
                        #else:
                        #    session = ''  # Handle cases where there's no match
        
                        print(f"Subject: {subject_label}, Session: {session}, Run: {run_number}(01), V Directory: {v_dir}")
                        if "01" != run_number:
                            print(f"Run 01 and run number from current eprime file: {run_number} not the same.")
                            raise ValueError
                        # Construct the command to call the previous script with the subject label, session, BIDS directory, and log file
                        log_file = os.path.join(subject_path, midt_fMRI_files[0])
                        cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_midt_eventfiles.py', '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', "01", '--bids-dir', f'{bids_dir}']
        
                        if args.dry_run:
                            print("Dry run: Would execute the following command:")
                            print(' '.join(cmd))
                        else:
                            # Execute the script
                            subprocess.run(cmd)
