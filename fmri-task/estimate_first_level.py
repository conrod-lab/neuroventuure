import os 
import re
import json 
import argparse
import nibabel as nib
from nilearn.reporting import make_glm_report
from nilearn.interfaces.fmriprep import load_confounds

from first_level_analysis import *
#from second_level_analysis import *

def tuple_from_string(s):
    if ',' in s:
        return tuple(s.split(','))
    else:
        return (s,)

def bidsify_output(outdir,source_file,key_val,ext):
    # <source_entities>[_keyword-<value>]_<suffix>.<extension
    # e.g. sub-001_ses-01_task-midt_run-01_dm-firstlvl.csv
    pattern = r'(sub-\d+_ses-\d+_task-\w+_run-\d+)'
    match = re.search(pattern, source_file)

    if match:
        source_entity = match.group(1)
    else:
        raise ValueError("bidsify_output::No match found for the expected pattern in the source file.")
    
    return os.path.join(outdir,f"{source_entity}_{key_val}.{ext}")

def get_task_scan_info(event_file):
    # Get the directory path
    directory_path = os.path.dirname(event_file)

    # Get the filename without extension
    filename_without_extension = os.path.splitext(os.path.basename(event_file))[0]

    # Construct the new filename with the desired extension
    new_filename = filename_without_extension.replace("_events", "_bold") + ".json"

    # Construct the new file path
    json_file = os.path.join(directory_path, new_filename)
        
    # Load JSON data from the file
    with open(json_file, 'r') as file:
        data = json.load(file)
        slice_timing = data.get("SliceTiming", None)
        tr = data.get("RepetitionTime", None)

    if tr is None or slice_timing is None:
        raise ValueError("get_task_scan_info::Some necessary information is missing in the JSON file.")

    # Get the length of the slice timing list
    if slice_timing:
        n_scans = len(slice_timing)

    # Convert tr to float
    tr = float(tr)
    
    # Generate frame_times based on tr and n_scans
    #frame_times = np.arange(n_scans) * tr
    frame_times = np.linspace(0, (n_scans - 1) * tr, n_scans)
    return tr, n_scans, frame_times


def main(args):
    
    # Your script logic goes here, using the provided arguments
    fmri_file = args.fmri_file
    event_file = args.event_file
    task = args.task
    confounds_strategy = args.confounds_strategy # must be a tuple e.g. ("motion", "high_pass", "wm_csf")
    outdir = args.outdir

    # this isnt working correctly for frame_times
    tr, n_scans, frame_times = get_task_scan_info(event_file)

    #TODO: load any type of confounds produced by fmriprep
    # confounds is a pandas df and mask is intended
    # for when scrubbing is used (removing bad motion frames)
    confounds, mask = load_confounds(
            fmri_file,
            strategy=confounds_strategy,
            motion="full",
            scrub=5,
            fd_threshold=0.2,
            std_dvars_threshold=3,
            wm_csf="basic",
            global_signal="basic",
            compcor="anat_combined",
            n_compcor="all",
            ica_aroma="full",
            demean=True,
        )  
    n_scans = confounds.shape[0]
    frame_times = np.linspace(0, (n_scans - 1) * tr, n_scans)
    # Run first level analysis
    first_level_design_matrix = create_first_level_design_matrix(event_file,confounds,frame_times)
    # save this to the output direction 
    bids_output_path = bidsify_output(outdir,fmri_file,'dm-firstlvl', 'csv')
    first_level_design_matrix.to_csv(bids_output_path)

    # Estimate first level GLM
    fmri_img = nib.load(fmri_file)
    first_level_model = estimate_first_level_glm(fmri_img, tr, first_level_design_matrix)

    # Create contrasts for task
    contrasts = create_contrasts(first_level_design_matrix,task)

    # Estimate contrasts (z-scores)
    z_maps = estimate_contrasts(first_level_model, contrasts)

    #TODO: make z-maps variable e.g. another statistic
    for contrast_id, z_map in z_maps.items():
        bids_output_path = bidsify_output(outdir,fmri_file,f'zmap-{contrast_id}', 'nii.gz')
        z_map.to_filename(bids_output_path)

    # Make a report for qc
    report = make_glm_report(
        first_level_model,
        contrasts=contrasts,
        title=f"{task}",
        cluster_threshold=0,
        min_distance=8.0,
        plot_type="glass",
    )
    
    # Save report to output directory
    bids_output_path = bidsify_output(outdir,fmri_file,f'report-firstlvl', 'html')
    report.save_as_html(bids_output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('fmri_file', type=str, help='Path to the fmri (nii.gz) file')
    parser.add_argument('event_file', type=str, help='Path to the event file')
    parser.add_argument('task', type=str, help='Name of the task')
    parser.add_argument('confounds_strategy', type=tuple_from_string, default=('motion', 'high_pass', 'wm_csf'),
                        help='Confounds strategy as a tuple (default: ("motion", "high_pass", "wm_csf"))')
    parser.add_argument('outdir', type=str, help='Output directory for subject/session')

    args = parser.parse_args()
    main(args)
