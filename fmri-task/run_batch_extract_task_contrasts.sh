#!/bin/bash

set -eu

# Change this to where you git cloned the project neuroventure:
PROJECT_HOME=/home/spinney/project/spinney
# Change this to where you want your slurm outputs to go
LOG_OUTPUT=$SCRATCH/batch_extract_constrasts/

# Output of conversion
OUTPUT=$SCRATCH/neuroventure/raw/bids
# where the DICOMs are located
BIDSROOT=$HOME/projects/def-patricia/data/neuroventure/bids
FMRIPREPDIR=$HOME/projects/def-patricia/data/neuroventure/derivatives/fmriprep
TASK="stop"

# This is what you change to grab a subject you want for a specific session
subject_session_to_filter=("sub-020/ses-01" "sub-028/ses-01" "sub-029/ses-01" "sub-030/ses-01" "sub-033/ses-02" "sub-052/ses-03" "sub-069/ses-01" "sub-072/ses-01" "sub-073/ses-03" "sub-074/ses-02" "sub-079/ses-02" "sub-086/ses-01" "sub-090/ses-01" "sub-153/ses-01")

# Set use_filter_paths to true or false depending on your needs
use_filter_paths=true

# if log output directory does not exist, create it
if [ ! -d $LOG_OUTPUT ]; then
    mkdir -p $LOG_OUTPUT

fi

# check if participants.tsv file exists
PARTICIPANTS_FILE=$(find ${BIDSROOT} -name "participants.tsv")
if [ -z "$PARTICIPANTS_FILE" ]; then
    echo "No participants.tsv file found in ${BIDSROOT}"
    exit 1
fi

touch $LOG_OUTPUT/extract_task_contrasts.log
# create another csv log file with columns for subject, session, task, and error message
echo "subject,session,task,error" > $LOG_OUTPUT/extract_task_contrasts_detailed.log

# Create a second level confounds csv file
#TODO: add any other columns
echo "subject,age,sex" > $OUTPUT/second_level_confounds.csv

# Add an if statement here to check if use_filter_paths is set to true
if [ "$use_filter_paths" = true ]; then
    # find all DICOM directories
    BIDSDIRS=( $(find ${BIDSROOT} -maxdepth 2 -type d -name "ses-*" ) )

    # Array to store filtered paths
    filtered_paths=()

    # Loop through the array of paths
    for path in "${BIDSDIRS[@]}"; do
        # Extract the subject_session from the path
        subject_session=$(echo "$path" | grep -oP 'sub-\d+/ses-\d+')

        # Check if the subject_session is in the list to be filtered
        if [[ " ${subject_session_to_filter[@]} " =~ " ${subject_session} " ]]; then
            filtered_paths+=("$path")
        fi
    done
else
    
    filtered_paths=( $(find ${BIDSROOT} -maxdepth 2 -type d -name "ses-*" ) )

    # Print the filtered paths
    for path in "${filtered_paths[@]}"; do
        echo "$path"
    done
fi

# We pass the found bids session paths to the slurm job array
# If it fails to find the tsv file, or its empty, or fmriprep failed to produce
# the necessary motion and confound regression, it will not run the python
# script and simply log the subject/session that failed
sbatch --array=0-`expr ${#filtered_paths[@]} - 1`%100 \
        --cpus-per-task=1 \
        --mem=2GB \
        --output=${LOG_OUTPUT}/slurm/extract_task_contrast_%A_%a.out \
        --error=${LOG_OUTPUT}/slurm/extract_task_contrast_%A_%a.err \
        $PROJECT_HOME/neuroventure/fmri-contrasts/run_extract_task_contrasts.sh ${OUTPUT} ${LOG_OUTPUT} ${FMRIPREPDIR} ${TASK} ${filtered_paths[@]}

