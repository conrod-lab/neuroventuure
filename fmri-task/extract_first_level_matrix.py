import argparse
import numpy as np
import pandas as pd 
import glob
import nibabel as nib
from nilearn.reporting import make_glm_report
import os 

from first_level_analysis import *
#from second_level_analysis import *

def get_task_scan_info(task):
    tr = 1.0  # repetition time is 1 second
    n_scans = 128  # the acquisition comprises 128 scans
    frame_times = np.arange(n_scans) * tr  # here are the corresponding frame times
    return tr, n_scans, frame_times

def main(args):
    
    # Your script logic goes here, using the provided arguments
    fmri_file = args.fmri_file
    event_file = args.event_file
    task = args.task
    motions_file = args.motions_file
    outdir = args.outdir

    tr, n_scans, frame_times = get_task_scan_info(args.task)

    # Run first level analysis
    first_level_design_matrix = create_first_level_design_matrix(event_file,task,motions_file,outdir,frame_times)
    # save this to the output direction 
    first_level_design_matrix.to_csv(outdir + '/first_level_design_matrix.csv')

    # Estimate first level GLM
    fmri_img = nib.load(fmri_file)
    first_level_model = estimate_first_level_glm(fmri_img, first_level_design_matrix)

    # Create contrasts for task
    contrasts = create_contrasts(first_level_design_matrix,task)

    # Estimate contrasts (z-scores)
    z_maps = estimate_contrasts(first_level_model, contrasts)

    #TODO: make z-maps variable e.g. another statistic
    for contrast_id, z_map in z_maps.items():
        z_map.to_filename(os.path.join(outdir, f"z_map_{contrast_id}.nii.gz"))

    # Make a report for qc
    report = make_glm_report(
        first_level_model,
        contrasts=contrasts,
        title=f"{task}",
        cluster_threshold=15,
        min_distance=8.0,
        plot_type="glass",
    )
    
    # Save report to output directory
    report.save_as_html(os.path.join(outdir, 'report.html'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('fmri_file', type=str, help='Path to the fmri (nii.gz) file')
    parser.add_argument('event_file', type=str, help='Path to the event file')
    parser.add_argument('task', type=str, help='Name of the task')
    parser.add_argument('motions_file', type=str, help='Path to the motions file')
    parser.add_argument('outdir', type=str, help='Output directory for subject/session')

    args = parser.parse_args()
    main(args)
