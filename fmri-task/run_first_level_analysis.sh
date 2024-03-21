#!/bin/bash
set -eu

module load StdEnv/2020 apptainer/1.1.8

source $SCRATCH/venv_datalad/bin/activate

log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# write function that takes in subject name, session name, task name, and a detailed error message
# into columns of a csv log file called extract_task_contrasts_detailed.log
log_detailed() {
    echo "$1,$2,$3,$4" >> $LOG_OUTPUT/first-level_task-${TASK}.log
}

PROJECT_HOME=${1}
OUTDIR=${2}
LOG_OUTPUT=${3}
FMRIPREPDIR=${4}
TASK=${5}
ANATSPACE=${6}
# receive all directories, and index them per job array

BIDSDIRS=("${@:7}")
BIDSDIR=${BIDSDIRS[${SLURM_ARRAY_TASK_ID}]}
BIDSROOT=$(dirname "$(dirname "$BIDSDIR")")

SUBJECT_NUMBER=${BIDSDIR##*/sub-}
SUBJECT_NUMBER=${SUBJECT_NUMBER%%/*}
echo "Subject Number: $SUBJECT_NUMBER"

# Extract the session number from the DCMDIR variable
SESSION_NUMBER=${BIDSDIR##*/ses-}
SESSION_NUMBER=${SESSION_NUMBER%%/*}
echo "Session Number: $SESSION_NUMBER"
echo "Task: $TASK"

# Find the task nii.gz file in the subject's session directory
# sub-001_ses-01_task-stop_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.json
FMRI_FILE=$(find ${FMRIPREPDIR} -name "*sub-${SUBJECT_NUMBER}*ses-${SESSION_NUMBER}*${TASK}*${ANATSPACE}*preproc_bold.nii.gz")

# Check that the task file exists or log 
if [ -z "$FMRI_FILE" ]; then
    echo "No fmri file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${FMRIPREPDIR}"
    # log to $LOG_OUTPUT/extract_task_contrasts.log
    log "No fmri file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${FMRIPREPDIR}" >> $LOG_OUTPUT/extract_task_contrasts.log
    # log detailed
    log_detailed $SUBJECT_NUMBER $SESSION_NUMBER $TASK "No fmri file found for ${TASK} in ${FMRIPREPDIR}"
    exit 1
fi

# Find the event file, check that it contains more than a header
EVENT_FILE=$(find ${BIDSDIR} -name "*${TASK}*.tsv")

if [ -z "$EVENT_FILE" ]; then
    echo "No event file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${BIDSDIR}"
    # log to $LOG_OUTPUT/extract_task_contrasts.log
    log "No event file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${BIDSDIR}" >> $LOG_OUTPUT/extract_task_contrasts.log
    # log detailed
    log_detailed $SUBJECT_NUMBER $SESSION_NUMBER $TASK "No event file found for ${TASK} in ${BIDSDIR}"
    exit 1
fi

# Find the fmriprep motions file (confounds), check that it exists
MOTIONS_FILE=$(find ${FMRIPREPDIR} -name "*${SUBJECT_NUMBER}*${SESSION_NUMBER}*${TASK}*_desc-confounds_timeseries.tsv")

if [ -z "$MOTIONS_FILE" ]; then
    echo "No motions file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${FMRIPREPDIR}"
    # log to $LOG_OUTPUT/extract_task_contrasts.log
    log "No motions file found for subject ${SUBJECT_NUMBER} session ${SESSION_NUMBER} task ${TASK} in ${FMRIPREPDIR}" >> $LOG_OUTPUT/extract_task_contrasts.log
    # log detailed
    log_detailed $SUBJECT_NUMBER $SESSION_NUMBER $TASK "No motions file found for ${TASK} in ${FMRIPREPDIR}"
    exit 1
fi

# Get the participants.tsv file at the bids root
PARTICIPANTS_FILE=$(find ${BIDSROOT} -name "participants.tsv")

# Get the subject sub-XXX_sessions.tsv file and read it
# look for it in the subjects sub-XXX folder 
SESSIONS_FILE=$(find ${BIDSROOT} -name "sub-${SUBJECT_NUMBER}_sessions.tsv")

# If the sessions file does not exist, log it and exit
if [ -z "$SESSIONS_FILE" ]; then
    echo "No sessions file found for subject ${SUBJECT_NUMBER} in ${BIDSROOT}"
    # log to $LOG_OUTPUT/extract_task_contrasts.log
    log "No sessions file found for subject ${SUBJECT_NUMBER} in ${BIDSROOT}" >> $LOG_OUTPUT/extract_task_contrasts.log
    # log detailed
    log_detailed $SUBJECT_NUMBER $SESSION_NUMBER $TASK "No sessions file found for ${TASK} in ${BIDSROOT}"
    exit 1
fi

# Get the row in the participants file corresponding to this subject number
participant_row=$(grep "sub-${SUBJECT_NUMBER}" "$PARTICIPANTS_FILE")

# Get the row in the sessions file corresponding to this session number
session_row=$(grep "ses-${SESSION_NUMBER}" "$SESSIONS_FILE")

# Combine the two rows into a single row
combined_row="$participant_row $session_row"

# Write the combined row to the second level confounds CSV file
echo "$combined_row" >> "$OUTDIR/second_level_confounds.csv"

# Following BIDS derivatives naming: <source_entities>[_keyword-<value>]_<suffix>.<extension
SUBJECT_OUTPUT_DIR=${OUTDIR}/sub-${SUBJECT_NUMBER}/ses-${SESSION_NUMBER}
# create derivatives output folder
mkdir -p $SUBJECT_OUTPUT_DIR

# Run the python script to extract the task contrasts
#python $PROJECT_HOME/neuroventure/fmri-task/estimate_first_level.py $FMRI_FILE $EVENT_FILE $TASK $EVENT_FILE $MOTIONS_FILE $SUBJECT_OUTPUT_DIR
python $PROJECT_HOME/neuroventure/fmri-task/estimate_first_level.py "$FMRI_FILE" "$EVENT_FILE" "$TASK"  "motion"  "$SUBJECT_OUTPUT_DIR"

# rename logs using subject number
original_out="firstlevelstop_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out"
original_err="firstlevelstop_${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.err"

# Rename logs with subject number
new_out="firstlevelstop_sub-${SUBJECT_NUM}.out"
new_err="firstlevelstop_sub-${SUBJECT_NUM}.err"

# Copy and rename logs
mv "${LOG_DIR}/slurm/${original_out}" "${LOG_DIR}/slurm/${new_out}"
mv "${LOG_DIR}/slurm/${original_err}" "${LOG_DIR}/slurm/${new_err}"

echo "Logs renamed:"
echo "Original OUT log: $original_out --> New OUT log: $new_out"
echo "Original ERR log: $original_err --> New ERR log: $new_err"
