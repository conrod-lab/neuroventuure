import argparse
import numpy as np
import pandas as pd 
import glob
import nibabel as nib
from nilearn.reporting import make_glm_report
from nilearn.glm import threshold_stats_img
import os 

from second_level_analysis import *
from glm_matrix_qc import *

def get_cmaps(num_subjects):

    return cmaps


def main(args):
    
    # Your script logic goes here, using the provided arguments
    first_level_folder = args.first_level_folder
    num_subjects = args.num_subjects
    task = args.task
    outdir = args.outdir

    # get all contrasts from every subject into one list
    
    cmaps = get_cmaps(first_level_folder,num_subjects) 

    # get any other second level variables for design matrix
    # you can either pass a full path to a phenotype/<name of df variables>.tsv
    # OR use the participants.tsv combined with 
    #tested_var = get_extra_variables(variable_names)
    design_matrix = create_second_level_design_matrix(subjects_label,confounds)

    # estimate second level glm 
    z_map = estimate_second_level_glm(cmaps, design_matrix)

    # FDR
    _, threshold = threshold_stats_img(z_map, alpha=0.05, height_control="fdr")    

    # plot threshold map 
    plot_threshold_zmap(z_map,threshold)

    # Save stuff 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('first_level_folder', type=str, help='Path to the output derivative folder from the first level')
    parser.add_argument('task', type=str, help='Name of the task')
    parser.add_argument('outdir', type=str, help='Output directory for second-level analysis')

    args = parser.parse_args()
    main(args)
