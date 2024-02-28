import os
import re
import subprocess
import argparse

def process_subjects(subject_sessions, dry_run):
    # Base directory containing the subject folders
    base_dir = '/home/spinney/project/data/neuroventure/sourcedata/eprime'
    bids_dir = '/home/spinney/project/data/neuroventure/bids'

    midt_fMRI_pattern = re.compile(r'NeuroVen_MIDT_fMRI_*_(.*?)-(\d+)-(\d+)\.txt')
    session_pattern = re.compile(r'V(\d+)')

    # If subject_sessions is empty, process all subjects
    if not subject_sessions:
        v_directories = ['V1', 'V2', 'V3']
        subject_sessions = [f"{v}:{subject}" for v in v_directories for subject in os.listdir(os.path.join(base_dir, v)) if os.path.isdir(os.path.join(base_dir, v, subject))]

    for subject_session in subject_sessions:
        v_dir, subject_folder = subject_session.split(':')

        v_dir_path = os.path.join(base_dir, v_dir, subject_folder)
        
        if os.path.exists(v_dir_path):
            midt_fMRI_files = [f for f in os.listdir(v_dir_path) if midt_fMRI_pattern.match(f)]

            if midt_fMRI_files:
                subject_match = midt_fMRI_pattern.match(midt_fMRI_files[0])
                subject_label = subject_match.group(2).zfill(3)
                run_number = subject_match.group(3).zfill(2)

                subject_number = os.path.basename(subject_folder)[-3:]

                if subject_label == subject_number:
                    print(subject_number)
                else:
                    subject_label = subject_number

                session_match = session_pattern.search(v_dir_path)
                session = session_match.group(1).zfill(2) if session_match else ''
                print(midt_fMRI_files)
                if len(midt_fMRI_files) > 1:
                    print(f"Found {len(midt_fMRI_files)} midt event files. Mapping them to runs.")
                    for run, log_file in enumerate(midt_fMRI_files):
                        subject_match = midt_fMRI_pattern.match(log_file)
                        subject_label = subject_match.group(2).zfill(3)
                        run_number = str(run+1).zfill(2)#subject_match.group(3).zfill(2)

                        print(f"Subject: {subject_label}, Session: {session}, V Directory: {v_dir}")

                        cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_midt_eventfiles.py',
                               '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{str(run+1).zfill(2)}', '--bids-dir', f'{bids_dir}']

                        if dry_run:
                            print("Dry run: Would execute the following command:")
                            print(' '.join(cmd))
                        else:
                            subprocess.run(cmd)
                else:
                    print(f"Subject: {subject_label}, Session: {session}, Run: {run_number}, V Directory: {v_dir}")
                    # if "01" != run_number:
                    #     print(f"Run 01 and run number from current eprime file: {run_number} not the same.")
                    #     raise ValueError

                    log_file = os.path.join(v_dir_path, midt_fMRI_files[0])
                    cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_midt_eventfiles.py',
                           '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', "01", '--bids-dir', f'{bids_dir}']

                    if dry_run:
                        print("Dry run: Would execute the following command:")
                        print(' '.join(cmd))
                    else:
                        subprocess.run(cmd)

if __name__ == "__main__":
    # Define the command-line arguments
    parser = argparse.ArgumentParser(description="Run the script on MIDT fMRI files for specified subject-sessions.")
    parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without executing the script.")
    parser.add_argument('subject_sessions', nargs='*', help="List of subject-sessions in the format Vx:subject_folder.")
    args = parser.parse_args()

    # Call the function with the provided arguments
    process_subjects(args.subject_sessions, args.dry_run)
