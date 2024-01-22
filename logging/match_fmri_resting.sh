#!/bin/bash

bids_dir="${PROJECT}/data/neuroventure/bids"
log_file="${SCRATCH}/verify_fmri_rest_runs_log.csv"  # Replace with the actual path for the log file
error_log_file="${SCRATCH}/verify_fmri_rest_runs_error_log.txt"  # Replace with the actual path for the error log file

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
                printf "Session ID: %s, Session Number: %s\n" "$session_id" "$session_number"
                # Iterate through resting-state fMRI files
                fmri_task_files=("$session_dir"/func/*rest*_bold.nii.gz)

                if [ ${#fmri_task_files[@]} -eq 0 ]; then
                    printf "Error: No resting-state fMRI files found for Subject %s, Session %s.\n" "$subject_id" "$session_id"
                    log_error "$subject_id" "$session_id" "No resting-state fMRI files found."
                else
                    for fmri_task_file in "${fmri_task_files[@]}"; do
                        if [ -f "$fmri_task_file" ]; then
                            # Extract session number from the fMRI task file name
                            run_number=$(basename "$fmri_task_file" | awk -F '_' '{print $NF}' | cut -d '.' -f1)

                            printf "Subject %s, Session %s, Run %s - Correct session and subject.\n" "$subject_id" "$session_id" "$run_number"
                            log_to_csv "$subject_id" "$session_id" "$run_number" "1"
                        else
                            log_error "$subject_id" "$session_id" "Not a file - $fmri_task_file"
                        fi
                    done
                fi
            fi
        done
    fi
done
