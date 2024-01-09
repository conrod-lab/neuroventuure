#!/bin/bash

set -eu

# where the DICOMs are located
DCMROOT=/scratch/spinney/neuroventure/raw/dicoms
# where we want to output the data
OUTPUT=/scratch/spinney/neuroventure/raw/bids

# find all DICOM directories that start with "voice"
DCMDIRS=( $(find ${DCMROOT} -maxdepth 2 -type d -name "ses-*" ) )

# submit to another script as a job array on SLURM
sbatch --array=0-`expr ${#DCMDIRS[@]} - 1` /home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/models/run_heudiconv.sh ${OUTPUT} ${DCMDIRS[@]}

# More ressources
# sbatch --array=0-`expr ${#DCMDIRS[@]} - 1` \
#        --cpus-per-task=1 \
#        --mem=2GB \
#        /home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/models/run_heudiconv.sh ${OUTPUT} ${DCMDIRS[@]}
