#!/bin/bash

set -eu

module load StdEnv/2020 apptainer/1.1.8

CONTAINER_DIR=$PROJECT/containers

BIDSROOT=${1}
OUTPUT=${2}
#SUBJECT_NUM="$2"
SUBJECT_NUMS=("${@:3}")
SUBJECT_NUM=${SUBJECT_NUMS[${SLURM_ARRAY_TASK_ID}]}

# Logging Function
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log "Run singularity image"

export APPTAINERENV_FS_LICENSE=$HOME/.licenses/freesurfer/license.txt
export FS_LICENSE=$HOME/.licenses/freesurfer/license.txt
singularity run --cleanenv \
  -B $SLURM_TMPDIR:/work \
  -B $OUTPUT:/out \
  -B $BIDSROOT:/data \
  ${CONTAINER_DIR}/freesurfer.sif \
  recon-all \
  -i /data/sub-${SUBJECT_NUM}/ses-01/anat/sub-${SUBJECT_NUM}_ses-01_run-01_T1w.nii.gz \
  -subjid $SUBJECT_NUM \
  -all -sd /out

log "Run complete."
