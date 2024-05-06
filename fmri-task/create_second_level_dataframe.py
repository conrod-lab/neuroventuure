import pandas as pd
import os
import argparse
import nibabel as nib
from nilearn import datasets
from nilearn.input_data import NiftiLabelsMasker

def extract_roi_values(bids_root, keyword, output_dir, covariates_excel, second_level_confounds, max_files=None):

    bids_root = "/home/spinney/project/data/neuroventure/derivatives/fmri-task"
    keyword = "stop_run-01_zmap-stopsuccess-stopfail"
    output_dir = "/scratch/spinney"
    covariates_excel = "/scratch/spinney/nv_covariates.xlsx"
    second_level_confounds = "/home/spinney/project/data/neuroventure/derivatives/fmri-task/second_level_confounds.csv"
    max_files = None

    # Read second level confounds CSV
    df = pd.read_csv(second_level_confounds, sep=' ')
    df.columns = ['subject_id', 'session_id']
    df = df.drop_duplicates()
    df = df.sort_values(by='subject_id')
    print(f"Done reading 2nd level confounds file of shape {df.shape}")
    # Read covariates Excel file
    covariates = pd.read_excel(covariates_excel)
    covariates = covariates.drop([0])
    covariates['subject_id'] = covariates['ID'].apply(lambda x: 'sub-{:03d}'.format(x))
    covariates['session_id'] = covariates['Time'].apply(lambda x: 'ses-{:02d}'.format(x))
    covariates = pd.merge(df, covariates, on=['subject_id', 'session_id'], how='left')
    print(f"Done reading covariates file of shape {covariates.shape}")
    # Find relevant files in the BIDS dataset directory
    files = []
    for root, dirs, filenames in os.walk(bids_root):
        for filename in filenames:
            if keyword in filename and filename.endswith('.nii.gz'):
                files.append(os.path.join(root, filename))
    print(f"Found {len(files)} nii.gz contrast files with keyword {keyword}")
    # Load the AAL atlas
    aal_atlas = datasets.fetch_atlas_aal()
    aal_img = nib.load(aal_atlas.maps)
    #covariates['HasfMRI'] = 0
    # Iterate through files and extract ROI values
    roi_df_list = []
    for idx, file_path in enumerate(files):
        if max_files is not None and idx >= max_files:
            break

        subject_id = os.path.basename(file_path).split('_')[0]
        session_id = os.path.basename(file_path).split('_')[1]

        print(f"Processing {file_path}...")

        # Load the contrast map
        contrast_map_img = nib.load(file_path)

        # Initialize masker with AAL atlas
        masker = NiftiLabelsMasker(labels_img=aal_img, standardize=False)

        # Extract ROI values
        roi_values = masker.fit_transform(contrast_map_img)

        roi_values_dict = dict(zip(aal_atlas.labels, [r[0] for r in roi_values.T]))
        roi_values_dict = {'subject_id': subject_id, 'session_id': session_id, **roi_values_dict}
        roi_df_list.append(roi_values_dict)

    # Save covariates DataFrame
    output_path = os.path.join(output_dir, 'roi_values.csv')
    roi_df = pd.DataFrame(roi_df_list)
    covariates = pd.merge(covariates, roi_df, on=['subject_id', 'session_id'], how='left')
    covariates = covariates.drop(['ID', 'Time'], axis=1)
    print(f"Final dataframe shape: {covariates.shape}")
    covariates.to_csv(output_path, index=False)
    print(f"ROI values saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract ROI values from contrast maps in a BIDS dataset.')
    parser.add_argument('--bids_root', type=str, default="", help='Path to the root directory of the BIDS dataset')
    parser.add_argument('--keyword', type=str, default='task-stop', help='Keyword to search for in filenames (default: "task-stop")')
    parser.add_argument('--output_dir', type=str, default='.', help='Output directory for the ROI values CSV file (default: current directory)')
    parser.add_argument('--covariates_excel', type=str, required=False, help='Full path to the covariates Excel file')
    parser.add_argument('--second_level_confounds', type=str, required=False, help='Full path to the second level confounds CSV file')
    parser.add_argument('--max_files', type=int, default=None, help='Maximum number of files to process before saving (default: process all files)')
    args = parser.parse_args()
    print("Ok. Starting")
    extract_roi_values(args.bids_root, args.keyword, args.output_dir, args.covariates_excel, args.second_level_confounds, args.max_files)
