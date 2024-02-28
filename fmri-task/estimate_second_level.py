import argparse
import numpy as np
import pandas as pd 
import glob
import nibabel as nib
from nilearn.reporting import make_glm_report
import os 

from second_level_analysis import *





def main(args):
    
    # Your script logic goes here, using the provided arguments
    fmri_file = args.fmri_file
    event_file = args.event_file
    task = args.task
    motions_file = args.motions_file
    outdir = args.outdir



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('first_level_folder', type=str, help='Path to the output derivative folder from the first level')
    parser.add_argument('task', type=str, help='Name of the task')
    parser.add_argument('motions_file', type=str, help='Path to the motions file')
    parser.add_argument('outdir', type=str, help='Output directory for subject/session')

    args = parser.parse_args()
    main(args)
