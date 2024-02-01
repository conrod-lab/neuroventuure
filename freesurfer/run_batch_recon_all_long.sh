#!/bin/bash

BIDSROOT="/home/spinney/project/data/neuroventure/bids"
OUTPUT="/scratch/spinney/neuroventure/derivatives/freesurfer"
FREESURFER_DATA="${OUTPUT}/sourcedata"
LOGDIR="${SCRATCH}/freesurfer-logs"

mkdir -p "${FREESURFER_DATA}"
mkdir -p "${LOGDIR}"

# Copy data from root to FreeSurfer directory
rsync -rv "${BIDSROOT}"/* "${FREESURFER_DATA}/"

# Find all DICOM directories that start with "sub"
subject_numbers=($(find "${FREESURFER_DATA}" -maxdepth 2 -type d -name "sub-*" | cut -d'-' -f2))
subject_numbers=(155)

# More resources
sbatch --array=0-`expr ${#subject_numbers[@]} - 1`%100 \
       --cpus-per-task=8 \
       --mem=10GB \
       --time=12:00:00 \
       --output="${LOGDIR}/recon-all-long_%A_%a.out" \
       --error="${LOGDIR}/recon-all-long_%A_%a.err" \
       run_recon_all_long.sh "${FREESURFER_DATA}" "${OUTPUT}" "${subject_numbers[@]}"
