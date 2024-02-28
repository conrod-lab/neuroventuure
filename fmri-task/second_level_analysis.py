from nilearn.glm.second_level import make_second_level_design_matrix


def create_second_level_design_matrix(conditions, duration, onsets, motion, add_reg_names):
    # Create a design matrix with the hrf model

    #TODO: Figure out which confounds to use (fmriprep )
    design_matrix = make_second_level_design_matrix(
        subjects_label, confounds=None
    )
