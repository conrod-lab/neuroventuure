#!/bin/bash

#set -eu

module load git-annex

BIDSROOT=/home/spinney/project/data/neuroventure/bids
OUTPUT=/scratch/spinney/neuroventure/derivatives/fmriprep
FMRIPREP_DATA=/scratch/spinney/neuroventure/derivatives/fmriprep/sourcedata
#RESULT_FILE=/home/spinney/project/spinney/neuroimaging-preprocessing/data/nv_anat_qc_2023_simplified.csv
RESULT_FILE=/home/spinney/project/spinney/neuroimaging-preprocessing/data/nv_anat_qc_2023_test.csv
LOG_OUTPUT=$OUTPUT/logs/

# activate datalad env
source $SCRATCH/venv_datalad/bin/activate

cp $BIDSROOT/dataset_description.json $FMRIPREP_DATA/

while IFS=, read -r subject session run_combined; do
    # Remove carriage return characters from run_combined
    run_combined=$(echo "$run_combined" | tr -d '\r')
    
    # Copy anat
    # Use find to get the correct paths
    source_paths=($(find "$BIDSROOT/$subject/$session/anat" -name "${run_combined}*"))

    if [ ${#source_paths[@]} -eq 0 ]; then
        echo "Data not found for $subject, $session, $run_combined"
        continue
    fi

    # Generate the destination path for the data with anat subdirectories
    destination_path="${FMRIPREP_DATA}/${subject}/${session}/anat/"

    # Check if the destination directory exists, if not, create it
    if [ ! -d "$destination_path" ]; then
        mkdir -p "$destination_path"
    fi

    for source_path in "${source_paths[@]}"; do
        echo "Unlocking $source_path"
        cd "$(dirname "$source_path")"
        datalad unlock "$source_path"
    done

    # Copy data from source to destination
    #cp -v "${source_paths[@]}" "$destination_path"
    rsync -rhv --info=progress2 "${source_paths[@]}" "$destination_path"

    # Copy func
    # Use find to get the correct paths
    IFS="_" read -ra parts <<< "$run_combined"
    run_part="${parts[-1]}"
    source_paths=($(find "$BIDSROOT/$subject/$session/func" -type f -name "*${run_part}*"))

    if [ ${#source_paths[@]} -eq 0 ]; then
        # Attempt with "run-01" if the initial attempt fails
        source_paths=($(find "$BIDSROOT/$subject/$session/func" -type f -name "*run-01*"))

        if [ ${#source_paths[@]} -eq 0 ]; then
            echo "Data not found for $subject, $session, $run_combined"
            continue
        fi
    fi
    # Generate the destination path for the data with anat subdirectories
    destination_path="${FMRIPREP_DATA}/${subject}/${session}/func/"

    # Check if the destination directory exists, if not, create it
    if [ ! -d "$destination_path" ]; then
        mkdir -p "$destination_path"
    fi

    for source_path in "${source_paths[@]}"; do
        echo "Unlocking $source_path"
        cd "$(dirname "$source_path")"
        datalad unlock "$source_path"
    done

    # Copy data from source to destination
    #cp -v "${source_paths[@]}" "$destination_path"
    rsync -rhv --info=progress2 "${source_paths[@]}" "$destination_path"

done < "$RESULT_FILE"

# find all DICOM directories that start with "voice"
subject_numbers=($(find "$FMRIPREP_DATA" -maxdepth 2 -type d -name "sub-*" | cut -d'-' -f2))
subject_numbers=(019)

mkdir -p ${LOG_OUTPUT}/slurm/

#More ressources
sbatch --array=0-`expr ${#subject_numbers[@]} - 1`%100 \
       --cpus-per-task=8 \
       --mem=50GB \
       --time=12:00:00 \
       --output=${LOG_OUTPUT}/slurm/fmriprep_%A_%a.out \
       --error=${LOG_OUTPUT}/slurm/fmriprep_%A_%a.err \
       /home/spinney/project/spinney/neuroventure/fmriprep/run_fmriprep.sh ${FMRIPREP_DATA} ${OUTPUT} ${subject_numbers[@]}
