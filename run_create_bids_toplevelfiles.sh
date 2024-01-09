#!/bin/bash
set -eu

module load StdEnv/2020 apptainer/1.1.8

OUTDIR=${1}
#OUTPUT=/scratch/spinney/neuroventure/raw/bids
#IMG="/singularity-images/heudiconv-latest-dev.sif"
IMG="${SCRATCH}/containers/heudiconv-latest-dev.sif"
HEURISTICDIR="/home/spinney/projects/def-patricia/spinney/neuroimaging-preprocessing/src/data"

CMD="singularity run -B ${OUTDIR}:/output -B ${HEURISTICDIR}/heuristics_neuroventure.py:/heuristics_neuroventure.py:ro --no-home ${IMG} --files /output -f /heuristics_neuroventure.py --command populate-templates"

#CMD="singularity run -B ${OUTDIR}:/output --no-home ${IMG} --files /output -f reproin --command populate-templates"

printf "Command:\n${CMD}\n"
${CMD}
echo "Successful process"
