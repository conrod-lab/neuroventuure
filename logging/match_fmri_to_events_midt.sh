#!/bin/bash

bids_dir="${PROJECT}/data/neuroventure/bids"
eprime_dir="${PROJECT}/data/neuroventure/sourcedata/eprime"
log_file="${SCRATCH}/verify_fmri_midt_runs_log.csv"  # Replace with the actual path for the log file
error_log_file="${SCRATCH}/verify_fmri_midt_runs_error_log.txt"  # Replace with the actual path for the error log file

# Function to log data into CSV file
log_to_csv() {
    local subject="$1"
    local session="$2"
    local run="$3"
    local completed="$4"
    echo "$subject, $session, $run, $completed" >> "$log_file"
}

# Function to log errors into a separate file
log_error() {
    local subject="$1"
    local session="$2"
    local error_message="$3"
    echo "Subject ID: $subject, Session ID: $session, Error: $error_message" >> "$error_log_file"
}

# New log files
echo "subject, session, run, completed" > "$log_file"
echo "" > "$error_log_file"

# ...

# Iterate through BIDS dataset
for subject_dir in "$bids_dir"/sub-*; do
    if [ -d "$subject_dir" ]; then
        subject_id=$(basename "$subject_dir")
        subject_number=$(echo "$subject_id" | sed 's/[^0-9]*//g')
        printf "Subject ID: %s, Subject Number: %s\n" "$subject_id" "$subject_number"
        for session_dir in "$subject_dir"/ses-*; do
            if [ -d "$session_dir" ]; then
                session_id=$(basename "$session_dir")
                session_number=$(echo "$session_id" | sed 's/[^0-9]*//g; s/^0*//')
                #printf "Session ID: %s, Session Number: %s\n" "$session_id" "$session_number"
                # Iterate through fMRI task files
                for fmri_task_file in "$session_dir"/func/*midt*_bold.nii.gz; do
                    if [ -f "$fmri_task_file" ]; then
                        # Extract session number from the fMRI task file name
                        run_number=$(basename "$fmri_task_file" | awk -F '_' '{print $NF}' | cut -d '.' -f1)
                        
                        # Extract session number and subject from raw event file using midt pattern
                        eprime_raw_file=$(find "$eprime_dir/V$session_number/NV_$subject_number" -type f -iname "*MIDT_fMRI*.txt"  | head -n 1)
                        
                        if [ -f "$eprime_raw_file" ]; then
                            raw_session=$(iconv -f UTF-16LE -t UTF-8 "$eprime_raw_file" | grep "Session:" | awk -F: '{print $2}' | head -n 1 | sed 's/[^0-9]*//g; s/^0*//; s/^[[:space:]]*//; s/[[:space:]]*$//')
                            raw_subject=$(iconv -f UTF-16LE -t UTF-8 "$eprime_raw_file" | grep "Subject:" | awk -F: '{print $2}' | head -n 1 | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
                            #printf "Raw Subject: %s, Raw Session: %s\n" "$raw_subject" "$raw_session"
                            
                            # Check if the session numbers match
                            if [ "$session_number" == "$raw_session" ] && [ "$subject_number" == "$raw_subject" ]; then
                                printf "Subject %s, Session %s, Run %s has the correct session and subject.\n" "$subject_id" "$session_id" "$run_number"
                                log_to_csv "$subject_id" "$session_id" "$run_number" "1"
                            else
                                printf "Error: Subject %s, Session %s, Run %s has incorrect session or subject.\n" "$subject_id" "$session_id" "$run_number"
                                log_to_csv "$subject_id" "$session_id" "$run_number" "0"
                                log_error "$subject_id" "$session_id" "Matching failed - $eprime_raw_file"
                            fi
                        else
                            log_error "$subject_id" "$session_id" "File not found - $eprime_raw_file"
                        fi
                    fi
                done
            fi
        done
    fi
done
