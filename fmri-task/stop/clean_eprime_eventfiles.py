import os
import json
import glob
import re
import chardet

# Define the task
task = 'STOP'  # Change this to the desired task

# Define the directory paths
base_subjects_directory = '/home/spinney/project/data/neuroventure/sourcedata/eprime'
output_directory = os.path.join(os.environ['SCRATCH'], 'test_clean_eprime')  # Specify the desired output directory

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
                #subject_match = re.findall(r'Subject(?:ID)?:\s+(\d+)', content)
                subject_match = re.findall(r'Subject(?:ID)?:\s+(\d+)', content)
                session_match = re.findall(r'Session:\s+(\d+)', content)

                if not subject_match or not session_match:
                    return [{'subject': (None, int(subject)), 
                            'session': (None, int(session)), 
                            'file':file_path,
                            'reason': "missing basic info"}], None

                subject_is_match = False
                found_subject = None
                for matched_subject in subject_match:
                    if int(matched_subject) == int(subject):
                        subject_is_match = True
                        found_subject = matched_subject
                        if (int(session_match[0]) != int(session)):
                            return [{'subject': (int(found_subject), int(subject)), 
                                     'session': (int(session_match[0]), int(session)), 
                                     'file':file_path,
                                     'reason': "session-mismatch"}], None

                if not subject_is_match:
                    return [{'subject': (subject_match[:], int(subject)),
                            'session': (int(session_match[0]), int(session)),
                            'file': file_path,
                            'reason': "subject-mismatch"}], None


                if not content.strip().endswith('*** LogFrame End ***'):
                    return [{'subject': (int(found_subject), int(subject)), 
                            'session': (int(session_match[0]), int(session)), 
                            'file':file_path,
                            'reason': "incomplete run"}], None

                else:
                    # Extract session date and time
                    session_date = re.search(r'SessionDate: (\d{2}-\d{2}-\d{4})', content).group(1)
                    session_time = re.search(r'SessionTime: (\d{2}:\d{2}:\d{2})', content).group(1)
                    
                    return {
                        "Subject": int(found_subject),
                        "Session": int(session_match[0]),
                        "Experiment": f"NeuroVen_{task}_fMRI_FRENCH_2JB",
                        "SessionDate": session_date,
                        "SessionTime": session_time
                    }, content

        except UnicodeDecodeError:
            continue  # Try next encoding if decoding fails

    return None

dryrun = False
failed_attempts = []

# Iterate through each timepoint directory
for timepoint_dir in glob.glob(os.path.join(base_subjects_directory, 'V*')):
    session_id = re.search(r'V(\d+)', timepoint_dir).group(1)

    # Define the subjects directory for the current timepoint
    subjects_directory = os.path.join(timepoint_dir, 'NV*')
    
    # Iterate through each subject directory
    for subject_dir in glob.glob(subjects_directory):
        subject_id = re.search(r'NV_(\d+)', subject_dir).group(1)
        # Create the BIDS subject directory in the output directory
        output_subject_dir = os.path.join(output_directory, f'sub-{int(subject_id):03d}', f'ses-{int(session_id):02d}')
        os.makedirs(output_subject_dir, exist_ok=True)
        
        # Find all eprime event files for the task
        task_files = [f for f in glob.glob(os.path.join(subject_dir, f'*{task}*.txt')) if 'Instructions' not in f]
        print(f"Found {len(task_files)} {task} files in subject dir {subject_dir}")
        print(task_files)
        complete_runs = []
        for file in task_files:
            # Extract information from each file
            info, content = extract_info(file, subject_id, session_id)
            if isinstance(info, list):
                failed_attempts.append(info)
            else:
                if info:
                    complete_runs.append((file, info, content))

        # Rename and create JSON sidecar files for complete runs
        print(f"Number of complete runs: {len(complete_runs)}")
        for idx, (file, info, content) in enumerate(complete_runs, start=1):
            # Rename the file
            new_filename = f'sub-{info["Subject"]:03d}_ses-{info["Session"]:02d}_task-{task.lower()}_run-{idx:02d}_eprime.txt'
            new_filepath = os.path.join(output_subject_dir, new_filename)
            if not dryrun:
                #shutil.copy(file, new_filepath)  # Copy instead of rename to preserve original files
                with open(new_filepath, 'w', encoding='utf-8') as dest_file:
                    dest_file.write(content) 

            # Create JSON sidecar file
            json_filename = f'sub-{info["Subject"]:03d}_ses-{info["Session"]:02d}_task-{task.lower()}_run-{idx:02d}_eprime.json'
            json_filepath = os.path.join(output_subject_dir, json_filename)
            if not dryrun:
                with open(json_filepath, 'w') as json_file:
                    json.dump(info, json_file, indent=4)

            print(f'Renamed: {os.path.basename(file)} -> {new_filename}')
            print(f'Created JSON sidecar: {json_filename}')

# Save failed attempts to a file
output_file_path = os.path.join(output_directory, f'failed_attempts_{task.lower()}.txt')
with open(output_file_path, 'w') as output_file:
    output_file.write(f"Failed attempts by mismatch between subject/session in filename, and the content of {task}:\n")
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
            output_file.write(f"Subject Found: {subject_found}, Subject Expected: {subject_expected}, Session Found: {session_found}, Session Expected: {session_expected}, File: {item['file']}, Reason: {item['reason']}\n")

print(f"Failed attempts saved to: {output_file_path}")
