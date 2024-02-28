import os
import re
import subprocess
import argparse

def process_stop_subjects(subject_sessions, dry_run):
    # Base directory containing the subject folders
    base_dir = '/home/spinney/project/data/neuroventure/sourcedata/eprime'
    bids_dir = '/home/spinney/project/data/neuroventure/bids'

    stop_fMRI_pattern = re.compile(r'NeuroVen_STOP_fMRI_FRENCH_2JB-(\d+)-\d+.txt')
    session_pattern = re.compile(r'V(\d+)')

    v_directories = ['V1', 'V2', 'V3']

    if not subject_sessions:
        subject_sessions = [f"{v}:{subject}" for v in v_directories for subject in os.listdir(os.path.join(base_dir, v)) if os.path.isdir(os.path.join(base_dir, v, subject))]

    for subject_session in subject_sessions:
        v_dir, subject_folder = subject_session.split(':')

        v_dir_path = os.path.join(base_dir, v_dir, subject_folder)

        if os.path.exists(v_dir_path):
            stop_fMRI_files = [f for f in os.listdir(v_dir_path) if stop_fMRI_pattern.match(f)]

            if stop_fMRI_files:
                subject_match = stop_fMRI_pattern.match(stop_fMRI_files[0])
                subject_label = subject_match.group(1).zfill(3)
                subject_number = os.path.basename(subject_folder)[-3:]
                run_number = "01"

                if subject_label == subject_number:
                    print(subject_number)
                else:
                    subject_label = subject_number

                session_match = session_pattern.search(v_dir_path)
                session = session_match.group(1).zfill(2) if session_match else ''

                print(f"Subject: {subject_label}, Session: {session}, V Directory: {v_dir}")
                print(stop_fMRI_files)
                if len(stop_fMRI_files) > 1:
                    print(f"Found {len(stop_fMRI_files)} stop event files. Mapping them to runs.")
                    for run, log_file in enumerate(stop_fMRI_files):
                        log_file = os.path.join(v_dir_path, log_file)
                        run_number = str(run+1).zfill(2)
                        print(f"Run {run+1}; Logfile: {log_file}")

                        cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_stop_eventfiles.py',
                               '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{str(run+1).zfill(2)}', '--bids-dir', f'{bids_dir}']

                        if dry_run:
                            print("Dry run: Would execute the following command:")
                            print(' '.join(cmd))
                        else:
                            subprocess.run(cmd)
                else:
                    run = "01"
                    log_file = os.path.join(v_dir_path, stop_fMRI_files[0])
                    cmd = ['python', '/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data/create_fmri_stop_eventfiles.py',
                           '--log_file', log_file, '--subject-label', f'{subject_label}', '--session', f'{session}', '--run', f'{run.zfill(2)}', '--bids-dir', f'{bids_dir}']

                    if dry_run:
                        print("Dry run: Would execute the following command:")
                        print(' '.join(cmd))
                    else:
                        subprocess.run(cmd)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traverse subject directories and run the script on STOP fMRI files.")
    parser.add_argument('--dry-run', action='store_true', help="Perform a dry run without executing the script.")
    parser.add_argument('subject_sessions', nargs='*', help="List of subject-sessions in the format Vx:subject_folder.")
    args = parser.parse_args()

    process_stop_subjects(args.subject_sessions, args.dry_run)
