import argparse
import nilearn
from nilearn.glm import threshold_stats_img
import os 
from second_level_analysis import get_cmaps, create_second_level_design_matrix, estimate_second_level_glm
from nilearn.image import index_img, new_img_like

# Define input parameters
base_subject_folder = '/home/subhasri/projects/def-patricia/data/neuroventure/derivatives/fmri-task'
task = 'stop'
output_directory = '/home/subhasri/scratch/fmri-stop/second_level_analysis'

# List of session numbers
ses_list = ["01", "02", "03"]

# Loop through each subject folder
for subject_folder in os.listdir(base_subject_folder):
    if subject_folder.startswith("sub-"):
        subject_folder_path = os.path.join(base_subject_folder, subject_folder)
        
        print(f"Processing data for subject: {subject_folder}")
        
        # Loop through each session for the current subject
        for ses in ses_list:
            # Get session folder for the current subject and session
            session_folder = os.path.join(subject_folder_path, f"ses-{ses}")

            # Get z_map_type based on files ending with .nii.gz in the session folder
            z_map_files = [f for f in os.listdir(session_folder) if f.endswith('.nii.gz')]
            z_map_type = os.path.splitext(z_map_files[0])[0] if z_map_files else None

            if z_map_type:
                print(f"Found z_map_type for subject {subject_folder}, ses-{ses}: {z_map_type}")
            else:
                print(f"No Z-map files found for subject {subject_folder}, ses-{ses}.")

            if z_map_type:
                # Get all contrast maps of the specified type for the specified session
                contrast_maps = get_cmaps(session_folder, ses, z_map_type)

                # Create design matrix
                design_matrix = create_second_level_design_matrix(range(len(contrast_maps)))

                # Perform second-level GLM
                z_maps = estimate_second_level_glm(contrast_maps, design_matrix)

                # Perform thresholding
                _, threshold = threshold_stats_img(z_maps, alpha=0.05, height_control="fdr")

                # Plot thresholded Z-map
                # did not run this as i removed the plot_threshold_zmap function from the second_level_analysis.py file as it was runing on the cluster
                #plot_threshold_zmap(z_maps, threshold)

                # Save outputs to the specified output directory
                session_output_dir = os.path.join(output_directory, f"{subject_folder}_ses-{ses}")
                os.makedirs(session_output_dir, exist_ok=True)

                for idx, z_map in enumerate(z_maps):
                    # Construct the filename for the Z-map
                    filename = f'{task}_{subject_folder}_ses-{ses}_zmap_{idx + 1}.nii.gz'
                    output_path = os.path.join(session_output_dir, filename)

                    # Save the Z-map to the output directory
                    z_map.to_filename(output_path)

                print(f"Z-maps for subject {subject_folder}, ses-{ses} saved to: {session_output_dir}")
            else:
                print(f"Z-map type not found for subject {subject_folder}, ses-{ses}. Please check the session folder.")



