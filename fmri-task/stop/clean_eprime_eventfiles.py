import os
import json
import glob
import re
import chardet
import shutil

# Define the directory paths
subjects_directory = '/home/spinney/project/data/neuroventure/sourcedata/eprime/V1'
output_directory = '/path/to/output_directory'  # Specify the desired output directory

# Function to extract information from the eprime event file
def extract_info(file_path, subject, session):
    encodings = ['utf-8', 'latin-1']  # Add more encodings as needed

    # Try to detect the encoding of the file
    with open(file_path, 'rb') as file:
        raw_content = file.read()
        detected_encoding = chardet.detect(raw_content)['encoding']

    if detected_encoding:
        encodings.insert(0, detected_encoding)

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()

                # Check if the required patterns are present in the content
                subject_match = re.findall(r'Subject:\s+(\d+)', content)
                session_match = re.findall(r'Session:\s+(\d+)', content)

                if (int(subject_match[0]) != int(subject)) or (int(session_match[0]) != int(session)):
                    return [{'subject': (int(subject_match[0]), int(subject)), 
                            'session': (int(session_match[0]), int(session)), 
                            'file':file_path,
                            'reason': "mismatch"}]

                if (len(subject_match) != 2 or len(session_match) != 2) and content.strip().endswith('*** LogFrame End ***'):
                    return [{'subject': (int(subject_match[0]), int(subject)), 
                            'session': (int(session_match[0]), int(session)), 
                            'file':file_path,
                            'reason': "incomplete run"}]

                else:
                    # Extract session date and time
                    session_date = re.search(r'SessionDate: (\d{2}-\d{2}-\d{4})', content).group(1)
                    session_time = re.search(r'SessionTime: (\d{2}:\d{2}:\d{2})', content).group(1)
                    
                    return {
                        "Subject": int(subject_match[0]),
                        "Session": int(session_match[0]),
                        "Experiment": "NeuroVen_STOP_fMRI_FRENCH_2JB",
                        "SessionDate": session_date,
                        "SessionTime": session_time
                    }

        except UnicodeDecodeError:
            continue  # Try next encoding if decoding fails

    return None

dryrun = True
session_id = 1
failed_attempts = []

# Iterate through each subject directory
for subject_dir in glob.glob(os.path.join(subjects_directory, 'NV_*')):
    subject_id = re.search(r'NV_(\d+)', subject_dir).group(1)
    # Create the BIDS subject directory in the output directory
    output_subject_dir = os.path.join(output_directory, f'sub-{int(subject_id):03d}', f'ses-{int(session_id):02d}')
    os.makedirs(output_subject_dir, exist_ok=True)
    
    # Find all eprime event files for the STOP task
    stop_files = [f for f in glob.glob(os.path.join(subject_dir, '*STOP*.txt')) if 'Instructions' not in f]
    print(f"Found {len(stop_files)} stop files in subject dir {subject_dir}")
    print(stop_files)
    complete_runs = []
    for file in stop_files:
        # Extract information from each file
        info = extract_info(file, subject_id, session_id)
        if isinstance(info, list):
            failed_attempts.append(info)
        else:
            if info:
                complete_runs.append((file, info))

    # Rename and create JSON sidecar files for complete runs
    print(f"Number of complete runs: {len(complete_runs)}")
    for idx, (file, info) in enumerate(complete_runs, start=1):
        # Rename the file
        new_filename = f'sub-{info["Subject"]:03d}_ses-{info["Session"]:02d}_task-stop_run-{idx:02d}_eprime.txt'
        new_filepath = os.path.join(output_subject_dir, new_filename)
        if not dryrun:
            shutil.copy(file, new_filepath)  # Copy instead of rename to preserve original files
            
        # Create JSON sidecar file
        json_filename = f'sub-{info["Subject"]:03d}_ses-{info["Session"]:02d}_task-stop_run-{idx:02d}_eprime.json'
        json_filepath = os.path.join(output_subject_dir, json_filename)
        if not dryrun:
            with open(json_filepath, 'w') as json_file:
                json.dump(info, json_file, indent=4)

        print(f'Renamed: {os.path.basename(file)} -> {new_filename}')
        print(f'Created JSON sidecar: {json_filename}')

print(f"Failed attempts by mismatch between subject/session in filename, and the content of eprime:")
for sublist in failed_attempts:
    for item in sublist:
        subject = item['subject']
        session = item['session']
        if isinstance(subject, tuple):
            subject_found, subject_expected = subject
        else:
            subject_found, subject_expected = subject, None
        if isinstance(session, tuple):
            session_found, session_expected = session
        else:
            session_found, session_expected = session, None
        print(f"Subject Found: {subject_found}, Subject Expected: {subject_expected}, Session Found: {session_found}, Session Expected: {session_expected}, File: {item['file']}, Reason: {item['reason']}")
