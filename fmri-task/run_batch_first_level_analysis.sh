#!/bin/bash

module load git-annex

set -eu

source $SCRATCH/venv_datalad/bin/activate
# Change this to where you git cloned the project neuroventure:
PROJECT_HOME=/home/spinney/project/spinney

# Output of conversion
OUTPUT=$SCRATCH/neuroventure/derivatives/fmri-task
# where the DICOMs are located
BIDSROOT=$HOME/projects/def-patricia/data/neuroventure/bids
FMRIPREPDIR=$HOME/projects/def-patricia/data/neuroventure/derivatives/fmriprep/derivatives/fmriprep
TASK="stop"
ANATSPACE="MNI152NLin2009cAsym"

# Change this to where you want your slurm outputs to go
LOG_OUTPUT=$OUTPUT/logs/$TASK

# This is what you change to grab a subject you want for a specific session
subject_session_to_filter=("sub-011/ses-01")

# Set use_filter_paths to true or false depending on your needs
use_filter_paths=true

# if output derivatives folder does not exist create it 
if [ ! -d $OUTPUT ]; then
    mkdir -p $OUTPUT
fi

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

touch $LOG_OUTPUT/first-level_space-${ANATSPACE}_task-${TASK}.log
# create another csv log file with columns for subject, session, task, and error message
echo "subject,session,task,error" > $LOG_OUTPUT/first-level_space-${ANATSPACE}_task-${TASK}.log

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


fi

# Print the filtered paths
for path in "${filtered_paths[@]}"; do
    echo "Unlocking $path"
    cd $path
    datalad unlock $path
done
# We pass the found bids session paths to the slurm job array
# If it fails to find the tsv file, or its empty, or fmriprep failed to produce
# the necessary motion and confound regression, it will not run the python
# script and simply log the subject/session that failed
echo "Starting array jobs..."
sbatch --array=0-`expr ${#filtered_paths[@]} - 1`%100 \
        --cpus-per-task=2 \
        --mem=10GB \
        --output=${LOG_OUTPUT}/slurm/firstlevelstop_%A_%a.out \
        --error=${LOG_OUTPUT}/slurm/firstlevelstop_%A_%a.err \
        $PROJECT_HOME/neuroventure/fmri-task/run_first_level_analysis.sh ${PROJECT_HOME} ${OUTPUT} ${LOG_OUTPUT} ${FMRIPREPDIR} ${TASK} ${ANATSPACE} ${filtered_paths[@]}
