import re
import argparse
import pandas as pd
import os 
import chardet

# Define mappings for trial types
trial_type_mapping = {
    "gotrial": "go",
    "stoptrial": "stop",
}

def parse_log_file(log_file_path, subject_label, session, run, bids_dir):
    # Read the log file
    # Detect the file's encoding
    rawdata = open(log_file_path, "rb").read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    # Read the log file
    with open(log_file_path, 'r', encoding=encoding) as log_file:
        log_content = log_file.read()

    # Initialize variables to store the extracted data
    onset_list = []
    duration_list = []
    trial_type_list = []
    response_time_list = []
    stim_file_list = []
    accuracy_list = []

    # Define regular expressions to match the desired information
    onset_pattern = r"goscreen.OnsetTime: (\d+)"
    duration_pattern = r"goscreen.Duration: (\d+)"
    procedure_pattern = r"Procedure: (\w+)"
    response_time_pattern = r"goscreen.RT: (\d+)"
    stimulus_pattern = r"go_stimulus: (.+)"
    accuracy_pattern = r"goscreen.ACC: (\d+)"

    # Split the log data into individual log frames
    log_frames = re.findall(r'\*\*\* LogFrame Start \*\*\*(.*?)\*\*\* LogFrame End \*\*\*', log_content, re.DOTALL)
    

    for frame in log_frames:
        # Extract relevant fields
        onset_match = re.search(onset_pattern, frame)
        if onset_match:
            onset_time = float(onset_match.group(1)) / 1000.0  # Convert to seconds
        else:
            onset_time = None  # Handle cases where there's no match
        duration_match = re.search(duration_pattern, frame)
        if duration_match:
            duration = float(duration_match.group(1)) / 1000.0  # Convert to seconds
        else:
            duration = None
        procedure_match = re.search(procedure_pattern, frame)
        if procedure_match:
            procedure = procedure_match.group(1)
        else:
            procedure = None
        response_time_match = re.search(response_time_pattern, frame)
        if response_time_match:
            response_time = float(response_time_match.group(1)) / 1000.0  # Convert to seconds
        else:
            response_time = None
        go_stimulus_match = re.search(stimulus_pattern, frame)
        if go_stimulus_match:
            go_stimulus = go_stimulus_match.group(1)
        else:
            go_stimulus = None
        accuracy_match = re.search(accuracy_pattern, frame)
        if accuracy_match:
            accuracy = int(accuracy_match.group(1))
        else:
            accuracy = None

        # Map trial type
        trial_type = trial_type_mapping.get(procedure, "unknown")

        # Append the extracted data to the lists
        onset_list.append(onset_time)
        duration_list.append(duration)
        trial_type_list.append(trial_type)
        response_time_list.append(response_time)
        stim_file_list.append(go_stimulus)
        accuracy_list.append(accuracy)

    # Combine the extracted data into a list of tuples
    event_data = list(zip(onset_list, duration_list, trial_type_list, response_time_list, stim_file_list, accuracy_list))

    # Save the data to a TSV file
    df = pd.DataFrame(event_data, columns=['onset', 'duration', 'trial_type', 'response_time','stim_file', 'accuracy'])
    # Remove rows with None values
    df = df.dropna()

    # Define the output directory
    output_dir = os.path.join(bids_dir, f'sub-{subject_label}/ses-{session}/func/')

    # Check if the output directory exists
    if not os.path.exists(output_dir):
        print(f"Bids output directory does not exist: {output_dir}")
        raise ValueError(f"Error: Participant {subject_label} has event data for session {session} and run {run}, but no BIDS folder found.")

    # Define the output file path using BIDS naming conventions
    output_file = f'sub-{subject_label}_ses-{session}_task-stop_run-{run}_events.tsv'

    # Save the DataFrame to the output file
    df.to_csv(os.path.join(output_dir, output_file), sep='\t', index=False)
    print(f"Successfully saved stop event file to {output_file}")

if __name__ == '__main__':
    # Argument parsing
    parser = argparse.ArgumentParser(description="Parse log file and extract event data.")
    parser.add_argument('--log_file', type=str, help="Path to the log file", default="/Users/sean/Projects/cpip/NeuroVen_STOP_fMRI_FRENCH_2JB-001-03.txt")
    parser.add_argument('--subject-label', type=str, help="Subject label", default="NV_001")
    parser.add_argument('--session', type=str, help="Scanning session (timepoint)", default="V3")
    parser.add_argument('--run', type=str, help="Run for repeated acquisition (same scan parameters)", default="01")
    parser.add_argument('--bids-dir', type=str, help="BIDS directory", default="")
    args = parser.parse_args()

    # Call the function to parse the log file
    parse_log_file(args.log_file, args.subject_label, args.session, args.run, args.bids_dir)


# log_file_path="/home/spinney/project/data/neuroventure/raw/sourcedata/eprime/V3/NV_014/NeuroVen_STOP_fMRI_FRENCH_2JB-014-03.txt" 
# subject_label="014" 
# session="03" 
# run="01" 
# bids_dir="/home/spinney/project/data/neuroventure/raw/bids"
