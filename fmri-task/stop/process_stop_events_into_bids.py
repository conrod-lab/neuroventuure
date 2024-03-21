import os
import re
import subprocess
import argparse
import glob

def extract_subject_session_run_id(bids_file):
    # Extract subject ID, session ID, and run ID from the bids file name
    filename = os.path.basename(bids_file)
    match = re.match(r'sub-(\d+)_ses-(\d+)_task-stop_run-(\d+)_eprime\.txt', filename)
    if match:
        subject_id = match.group(1)
        session_id = match.group(2)
        run_id = match.group(3)
        return subject_id, session_id, run_id
    else:
        return None, None, None

def process_stop_subjects(subject_sessions, dry_run):
    # Base directory containing the subject folders
    base_dir = '/Users/seanspinney/data/neuroventure-derivatives/eprime'#'/home/spinney/project/data/neuroventure/derivatives/eprime'
    bids_dir = '/Users/seanspinney/data/neuroventure' #/home/spinney/project/data/neuroventure/bids'

    if not subject_sessions:
        subject_sessions = glob.glob(os.path.join(base_dir, "**", "sub-*stop*eprime.txt"), recursive=True)

    for subject_logfile in subject_sessions:
        subject_id, session_id, run_id = extract_subject_session_run_id(subject_logfile)
        if subject_id is None or session_id is None or run_id is None:
            print(f"Could not extract subject ID, session ID, and run ID from {subject_logfile}. Skipping.")
            continue

        cmd = ['python', '/Users/seanspinney/projects/neuroventure/fmri-task/stop/create_fmri_stop_eventfiles.py',
                '--log_file', subject_logfile, '--subject-label', f'{subject_id}', '--session', f'{session_id}', '--run', f'{run_id}', '--bids-dir', f'{bids_dir}']

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
