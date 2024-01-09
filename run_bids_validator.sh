#!/bin/bash
set -eu

module load StdEnv/2020 apptainer/1.1.8

#OUTDIR=${1}

# if not already done 
#singularity build bids_validator.sif docker://bids/validator

singularity run -B /home/spinney/project/data/neuroventure/raw/bids:/data /scratch/spinney/containers/bids_validator.sif --verbose /data
