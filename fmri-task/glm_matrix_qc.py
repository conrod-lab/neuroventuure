import matplotlib.pyplot as plt
from nilearn.plotting import plot_design_matrix


def qc_design_matrix(design_matrix,html_file_path):
    fig, ax1 = plt.subplots(1, 1, figsize=(3, 4))
    ax = plot_design_matrix(design_matrix, ax=ax1)
    ax.set_ylabel("maps")
    ax.set_title("Second level design matrix", fontsize=12)
    plt.tight_layout()
    plt.show()


