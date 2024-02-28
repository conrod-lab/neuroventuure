#!/bin/bash
set -eu

module load StdEnv/2020 apptainer/1.1.8

OUTDIR=${1}

# Get a list of all sub-XXX folders found in OUTDIR
sub_folders=$(find "$OUTDIR" -mindepth 1 -maxdepth 1 -type d -name "sub-*")

# Create participants.tsv with top header row: participant_id
echo "participant_id" > "$OUTDIR/participants.tsv"

# Loop through each sub-XXX folder
for sub_folder in $sub_folders; do
    sub_name=$(basename "$sub_folder")
    participant_id=$(echo "$sub_name" | cut -d '-' -f 2)
    echo "$participant_id" >> "$OUTDIR/participants.tsv"

    # Create sub-XXX_sessions.tsv file in sub-XXX folder
    sessions_file="$sub_folder/${sub_name}_sessions.tsv"
    echo "session_id" > "$sessions_file"

    # Find ses-XX folders and add session_id rows
    ses_folders=$(find "$sub_folder" -mindepth 1 -maxdepth 1 -type d -name "ses-*")
    for ses_folder in $ses_folders; do
        session_id=$(basename "$ses_folder")
        echo "$session_id" >> "$sessions_file"
    done
done

echo "Successful process"
