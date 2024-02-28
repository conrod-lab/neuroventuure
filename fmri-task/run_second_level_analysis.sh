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
FIRSTLEVELDIR=
TASK="stop"

# if log output directory does not exist, create it
if [ ! -d $LOG_OUTPUT ]; then
    mkdir -p $LOG_OUTPUT
    touch $LOG_OUTPUT/second_level_analysis.log
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
        $PROJECT_HOME/neuroventure/fmri-contrasts/run_extract_task_contrasts.sh ${PROJECT_HOME} ${OUTPUT} ${LOG_OUTPUT} ${FMRIPREPDIR} ${TASK} ${filtered_paths[@]}

python $PROJECT_HOME/neuroventure/fmri-contrasts/estimate_second_level.py $FMRI_FILE $EVENT_FILE $TASK $EVENT_FILE $MOTIONS_FILE $SUBJECT_OUTPUT_DIR