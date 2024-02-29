import re
import argparse
import pandas as pd
import chardet
import os

def parse_log_file(log_file_path, subject_label, session, run, bids_dir):

    skipped_frames = ["BlockProc", "RunProc"]

    # Detect the file's encoding
    rawdata = open(log_file_path, "rb").read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    # Read the log file
    with open(log_file_path, 'r', encoding=encoding) as log_file:
        log_content = log_file.read()

    # Initialize lists to store the extracted data
    onset_list = []
    duration_list = []
    trial_type_list = []
    event_type_list = []
    response_time_list = []
    stim_file_list = []
    accuracy_list = []

    # Define regular expressions to match the desired information
    #event_pattern = r"(\w+)\.OnsetTime: (\d+)\n(\w+)\.Duration: (\d+)\n\w+\.RT: (\d+)\n\w+\.RESP: (\d*)"
    onset_pattern = r"(\w+)\.OnsetTime: (\d+)"
    duration_pattern = r"(\w+)\.Duration: (\d+)"
    trialtype_pattern = r"trialType: (\w+)"
    rewardturn_pattern = r"rewardturn: (\w+)"
    accuracy_pattern = r"(\w+)\.ACC: (\d+)"
    rt_pattern = r"(\w+)\.RT: (\d+)"
    resp_pattern = r"(\w+)\.RESP: (\d*)"
    # Split the log data into individual log frames
    log_frames = re.findall(r'\*\*\* LogFrame Start \*\*\*(.*?)\*\*\* LogFrame End \*\*\*', log_content, re.DOTALL)
    combined_data = []

    # List of event types
    event_types = ['ImageDisplay1', 
                   'StartDisplay',
                   'ImageDisplay2', 
                   'ChoiceDisplay', 
                   'ChosenDisplay', 
                   'TurnDisplay', 
                   'OutcomeDisplay']
    
    last_frame = log_frames[-1]
    if re.findall(r"Experiment: (\w+)", last_frame):
        log_frames = log_frames[:-1]

    for i, frame in enumerate(log_frames):
        
        is_skip = re.findall(r"Procedure: (\w*)", frame)
        if is_skip:
            if is_skip[0] in skipped_frames:
                continue

        # Extract and convert relevant fields using the event_pattern
        #event_matches = re.findall(event_pattern, frame)
        onset_match = re.findall(onset_pattern, frame)
        duration_match = re.findall(duration_pattern, frame)
        trialtype_match = re.findall(trialtype_pattern, frame)
        rewardturn_match = re.findall(rewardturn_pattern, frame)
        rt_match = re.findall(rt_pattern, frame)
        resp_match = re.findall(resp_pattern, frame)
        
        trialtype_value = f'{trialtype_match[0]}-{rewardturn_match[0]}'
         
        for event_type in event_types:
            onset_value = next((match[1] for match in onset_match if match[0] == event_type), None)
            duration_value = next((match[1] for match in duration_match if match[0] == event_type), None)
            stim_file_value = next((match[1] for match in resp_match if match[0] == event_type), None)
            accuracy_value = next((match[1] for match in resp_match if match[0] == event_type), None)
            rt_value = next((match[1] for match in rt_match if match[0] == event_type), None)
            resp_value = next((match[1] for match in resp_match if match[0] == event_type), None)
            try:
                # Create a dictionary with the header you want
                row = {
                    'frame': i,
                    'onset': int(onset_value)/ 1000.0 if onset_value else None,
                    'duration': int(duration_value) / 1000.0 if duration_value else None,
                    'trial_type': trialtype_value,
                    'event_type': event_type,
                    'response_type': resp_value,
                    'response_time': float(rt_value) / 1000.0 if rt_value else None,
                    'stim_file': stim_file_value,
                    'accuracy': accuracy_value
                }
            except Exception as e:
                raise(f"Could not match. Check file for {subject_label}, ses-{session}, run-{run}.\n{e}")
            combined_data.append(row)

    # Create a DataFrame with the specified header
    df = pd.DataFrame(combined_data)
    df.replace('', None, inplace=True)
    df = df.dropna()
    # Define the output directory and file path
    output_dir = os.path.join(bids_dir, f'sub-{subject_label}/ses-{session}/func/')
    # create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = f'sub-{subject_label}_ses-{session}_task-midt_run-{run}_events.tsv'

    # Save the DataFrame to the output file
    df.to_csv(os.path.join(output_dir, output_file), sep='\t', index=False)
    print(f"Saved {output_file}")
    
if __name__ == '__main__':
    # Argument parsing
    parser = argparse.ArgumentParser(description="Parse log file and extract event data.")
    parser.add_argument('--log_file', type=str, help="Path to the log file", default="/Users/sean/Projects/cpip/NeuroVen_MIDT_fMRI_fr_avril2014-001-03.txt")
    parser.add_argument('--subject-label', type=str, help="Subject label", default="001")
    parser.add_argument('--session', type=str, help="Scanning session (timepoint)", default="03")
    parser.add_argument('--run', type=str, help="Run for repeated acquisition (same scan parameters)", default="01")
    parser.add_argument('--bids-dir', type=str, help="BIDS directory", default=os.curdir)
    args = parser.parse_args()

    # Call the function to parse the log file
    parse_log_file(args.log_file, args.subject_label, args.session, args.run, args.bids_dir)
