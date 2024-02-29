
import pandas as pd
from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.glm.first_level import FirstLevelModel
import numpy as np

def read_tsv_file(file_path):
    # these are the types of the different trials
    df = pd.read_csv(file_path, sep='\t')
    #TODO: condition or trial_type
    conditions = df['trial_type'].values.tolist() #["c0", "c0", "c0", "c1", "c1", "c1", "c3", "c3", "c3"]
    duration =  df['duration'].values.tolist()  #[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    # these are the corresponding onset times
    onsets =  df['onset'].values.tolist() #[30.0, 70.0, 100.0, 10.0, 30.0, 90.0, 30.0, 40.0, 60.0]
    return conditions, duration, onsets


def read_motion_file(file_path):
    motion = pd.read_csv(file_path) # Get file # np.cumsum(np.random.randn(n_scans, 6), 0)
    add_reg_names = ["tx", "ty", "tz", "rx", "ry", "rz"]
    return motion, add_reg_names


def create_first_level_design_matrix(event_file,confounds,frame_times):
     
    conditions, duration, onsets = read_tsv_file(event_file)
    #motion, add_reg_names = read_motion_file(motions_file)
    
    # Create a design matrix with the hrf model
    events = pd.DataFrame(
    {"trial_type": conditions, "onset": onsets, "duration": duration}
    )

    #TODO: Confirm parameters
    hrf_model = "glover"
    design_matrix = make_first_level_design_matrix(
        frame_times,
        events,
        drift_model="polynomial",
        drift_order=3,
        add_regs=confounds,
        #add_reg_names=add_reg_names,
        hrf_model=hrf_model,
    )
        
    return design_matrix

def estimate_first_level_glm(fmri_img, tr, design_matrix):
    first_level_model = FirstLevelModel(t_r=tr, noise_model='ar1', standardize=False)
    first_level_model = first_level_model.fit(fmri_img, design_matrices=design_matrix)
    return first_level_model


def get_stop_contrasts(basic_contrasts):
    
    contrasts = {
    "stop-go": basic_contrasts["stop"] - basic_contrasts["go"],
    "go-stop": -basic_contrasts["go"] + basic_contrasts["stop"],
    # "effects_of_interest": np.vstack(
    #     (basic_contrasts["stop"], basic_contrasts["go"])
    # ),
    }
    return contrasts

def get_midt_contrasts(basic_contrasts):
    
    contrasts = {
    "faces-scrambled": basic_contrasts["faces"] - basic_contrasts["scrambled"],
    "scrambled-faces": -basic_contrasts["faces"]
    + basic_contrasts["scrambled"],
    "effects_of_interest": np.vstack(
        (basic_contrasts["faces"], basic_contrasts["scrambled"])
    ),
    }
    return contrasts

def create_contrasts(design_matrix,task='stop'):
    contrast_matrix = np.eye(design_matrix.shape[1])
    basic_contrasts = {
        column: contrast_matrix[i]
        for i, column in enumerate(design_matrix.columns)
    }

    if task == 'stop':
        contrasts = get_stop_contrasts(basic_contrasts)
    elif task == 'midt':
        contrasts = get_midt_contrasts(basic_contrasts)
    else:
        contrasts = basic_contrasts

    return contrasts


def estimate_contrasts(first_level_model, contrasts):
    #  output_type can be ‘z_score’, ‘stat’, ‘p_value’, ‘effect_size’, ‘effect_variance’ or ‘all’.
    z_map = {}
    for contrast_id, contrast_val in contrasts.items():
        z_map[contrast_id] = first_level_model.compute_contrast(
            contrast_val, output_type="z_score"
        )
    return z_map