import numpy as np
import pandas as pd
from nilearn.glm.second_level import make_second_level_design_matrix
from nilearn.glm.second_level import SecondLevelModel
from nilearn.glm import threshold_stats_img
from nilearn.plotting import plot_stat_map

import os

def get_cmaps(base_subject_folder, ses, z_map_type):
    cmaps = []
    
    # Loop through subject folders
    for subject_folder in os.listdir(base_subject_folder):
        subject_folder_path = os.path.join(base_subject_folder, subject_folder)
        
        # Check if subject_folder_path is a directory and starts with "sub"
        if os.path.isdir(subject_folder_path) and subject_folder.startswith("sub"):
            # Get the session folder path for the specified session
            session_folder_path = os.path.join(subject_folder_path, f"ses-{ses}")
            
            # Check if session_folder_path exists
            if os.path.isdir(session_folder_path):
                # Get Z-map files of the specified type in the session folder
                z_map_files = [f for f in os.listdir(session_folder_path) if f.endswith('.nii.gz') and z_map_type in f]
                
                # Assuming you want to use all Z-map files
                for z_map_file in z_map_files:
                    z_map_path = os.path.join(session_folder_path, z_map_file)
                    cmaps.append(z_map_path)
                        
    return cmaps


def create_second_level_design_matrix(subjects_label, confounds=None):
    # Create a design matrix with the hrf model
    design_matrix = make_second_level_design_matrix(
        subjects_label, confounds
    )

    return design_matrix

def estimate_second_level_glm(contrast_map_filenames, design_matrix):
    model = SecondLevelModel(smoothing_fwhm=5.0, n_jobs=2)
    model.fit(contrast_map_filenames, design_matrix=design_matrix)

    # Extract the Z-maps
    z_maps = model.compute_contrast(output_type='z_score')

    return z_maps
