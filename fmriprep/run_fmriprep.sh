#!/bin/bash

set -eu

module load StdEnv/2020 apptainer/1.1.8

CONTAINER_DIR=$PROJECT/containers

# # Check if the correct number of arguments is provided
# if [ "$#" -ne 2 ]; then
#     log "Usage: $0 <DATASET_DIR> <SUBJECT_NUM>"
#     exit 1
# fi

BIDSROOT=${1}
OUTPUT=${2}
#SUBJECT_NUM="$2"
SUBJECT_NUMS=("${@:3}")
SUBJECT_NUM=${SUBJECT_NUMS[${SLURM_ARRAY_TASK_ID}]}

# Logging Function
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}


# singularity run --cleanenv ${CONTAINER_DIR}/fmriprep-latest.simg \
#   $BIDSROOT $OUTPUT \
#   participant \
#   --participant-label $SUBJECT_NUM -t "rest" --n_cpus 8 -w $SLURM_TMPDIR


#SUBJECT_NUM=${subject_numbers[0]}
# singularity run --cleanenv ${CONTAINER_DIR}/fmriprep-latest.simg \
# $FMRIPREP_DATA $OUTPUT \
# participant \
# --participant-label $SUBJECT_NUM -t "rest" --n_cpus 8 -w $SCRATCH

log "Run singularity image"

export APPTAINERENV_FS_LICENSE=$HOME/.licenses/freesurfer/license.txt
export FS_LICENSE=$HOME/.licenses/freesurfer/license.txt
singularity run --cleanenv \
  -B $SLURM_TMPDIR:/work \
  -B $OUTPUT:/out \
  -B $BIDSROOT:/data \
  ${CONTAINER_DIR}/fmriprep_23.1.4.sif \
  /data /out/derivatives/fmriprep \
  participant \
  --participant-label $SUBJECT_NUM --nthreads 8 \
  --omp-nthreads 8 \
  -w /work \
  -vvv \
  --fs-license-file $FS_LICENSE
  --debug all

log "Run complete."

# singularity run --cleanenv -B $OUTPUT:/work ${CONTAINER_DIR}/fmriprep_23.1.4.sif \
#   /work/sourcedata /work/derivatives/fmriprep \
#   participant \
#   --participant-label 153 \
#   --nprocs 8 \
#   --omp-nthreads 8 \
#   --ignore "fieldmaps slicetiming sbref t2w flair" \
#   --output-spaces MNI152Lin T1w \
#   --longitudinal \
#   --bold2t1w-init register \
#   --bold2t1w-dof 6 \
#   --me-t2s-fit-method curvefit loglin \
#   --force-bbr \
#   --force-no-bbr \
#   --output-layout bids \
#   --me-output-echos \
#   --medial-surface-nan \
#   --project-goodvoxels \
#   --md-only-boilerplate \
#   --cifti-output 91k 170k \
#   --return-all-components \
#   --fd-spike-threshold REGRESSORS_FD_TH \
#   --dvars-spike-threshold REGRESSORS_DVARS_TH \
#   --skull-strip-template SKULL_STRIP_TEMPLATE \
#   --skull-strip-fixed-seed \
#   --skull-strip-t1w force \
#   --fmap-no-demean \
#   --force-syn \
#   -vvv \
#   --clean-workdir \
#   --resource-monitor \
#   --write-graph \
#   --stop-on-first-crash \
#   --notrack \
#   --debug all


