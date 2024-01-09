#!/bin/bash

set -eu

# where the DICOMs are located
DCMROOT=/home/spinney/project/data/neuroventure/sourcedata/dicoms/

# single subject test
#DCMROOT=/scratch/spinney/neuroventure/raw/dicoms_clean
# where we want to output the data
OUTPUT=/scratch/spinney/neuroventure/raw/bids

# find all DICOM directories
DCMDIRS=( $(find ${DCMROOT} -maxdepth 2 -type d -name "ses-*" ) )
#filtered_paths=( $(find ${DCMROOT} -maxdepth 2 -type d -name "ses-*" ) )

#subject_session_to_filter=("sub-018/ses-02" "sub-050/ses-03" "sub-059/ses-03" "sub-072/ses-01" "sub-073/ses-03" "sub-079/ses-01" "sub-086/ses-01" "sub-099/ses-02" "sub-120/ses-01" "sub-155/ses-02")

subject_session_to_filter=("sub-130/ses-03" "sub-147/ses-03")

#subject_session_to_filter=("sub-062/ses-01")

# Array to store filtered paths
filtered_paths=()

# Loop through the array of paths
for path in "${DCMDIRS[@]}"; do
  # Extract the subject_session from the path
  subject_session=$(echo "$path" | grep -oP 'sub-\d+/ses-\d+')

  # Check if the subject_session is in the list to be filtered
  if [[ " ${subject_session_to_filter[@]} " =~ " ${subject_session} " ]]; then
    filtered_paths+=("$path")
  fi
done

# Print the filtered paths
for path in "${filtered_paths[@]}"; do
  echo "$path"
done

# submit to another script as a job array on SLURM
#sbatch --array=0-`expr ${#DCMDIRS[@]} - 1` /home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/models/run_heudiconv.sh ${OUTPUT} ${DCMDIRS[@]}

# sbatch --cpus-per-task=1 --mem=2GB --output=/scratch/spinney/neuroventure/raw/tmp/output/heudiconv_%A.out --error=/scratch/spinney/neuroventure/raw/tmp/error/heudiconv_%A.err \
#   /home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/models/run_heudiconv.sh ${OUTPUT} "${DCMDIRS[@]}"

#More ressources
sbatch --array=0-`expr ${#filtered_paths[@]} - 1`%100 \
       --cpus-per-task=1 \
       --mem=2GB \
       --output=/home/spinney/scratch/neuroventure/raw/tmp/output/heudiconv/heudiconv_%A_%a.out \
       --error=/home/spinney/scratch/neuroventure/raw/tmp/error/heudiconv/heudiconv_%A_%a.err \
       /home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/models/heudiconv/run_heudiconv.sh ${OUTPUT} ${filtered_paths[@]}

