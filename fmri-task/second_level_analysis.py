from nilearn.glm.second_level import make_second_level_design_matrix
from nilearn.glm.second_level import SecondLevelModel


def create_second_level_design_matrix(subjects_label,confounds=None):
    # Create a design matrix with the hrf model

    #TODO: Figure out which confounds to use (fmriprep )
    design_matrix = make_second_level_design_matrix(
        subjects_label, confounds
    )

    # design_matrix = pd.DataFrame(
    #     np.hstack((tested_var, np.ones_like(tested_var))),
    #     columns=["fluency", "intercept"],
    # ) 

    return design_matrix

def estimate_second_level_glm(contrast_map_filenames, design_matrix):

    model = SecondLevelModel(smoothing_fwhm=5.0, n_jobs=2)
    model.fit(contrast_map_filenames, design_matrix=design_matrix)
    return model