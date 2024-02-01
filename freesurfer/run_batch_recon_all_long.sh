#!/bin/bash

#set -eu

BIDSROOT=/home/spinney/project/data/neuroventure/bids
OUTPUT=/scratch/spinney/neuroventure/derivatives/freesurfer
FREESURFER_DATA=/scratch/spinney/neuroventure/derivatives/freesurfer/sourcedata

# copy data from root to freesurfer directory
rsync -rv $BIDSROOT/* $FREESURFER_DATA/

# find all DICOM directories that start with "voice"
subject_numbers=($(find "$FREESURFER_DATA" -maxdepth 2 -type d -name "sub-*" | cut -d'-' -f2))
subject_numbers=(155)


#More ressources
sbatch --array=0-`expr ${#subject_numbers[@]} - 1`%100 \
       --cpus-per-task=8 \
       --mem=10GB \
       --time=12:00:00 \
       --output=/home/spinney/scratch/neuroventure/raw/tmp/output/freesurfer/recon-all-long_%A_%a.out \
       --error=/home/spinney/scratch/neuroventure/raw/tmp/error/freesurfer/recon-all-long_%A_%a.err \
       run_recon_all_long.sh ${FREESURFER_DATA} ${OUTPUT} ${subject_numbers[@]}
