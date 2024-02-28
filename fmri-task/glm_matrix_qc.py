import matplotlib.pyplot as plt
from nilearn.plotting import plot_design_matrix, plot_stat_map


def qc_design_matrix(design_matrix,html_file_path):
    fig, ax1 = plt.subplots(1, 1, figsize=(3, 4))
    ax = plot_design_matrix(design_matrix, ax=ax1)
    ax.set_ylabel("maps")
    ax.set_title("Second level design matrix", fontsize=12)
    plt.tight_layout()
    plt.show()

def plot_threshold_zmap(z_map,threshold):
    fig, ax1 = plt.subplots(1, 1, figsize=(3, 4))
    ax = plot_stat_map(
        z_map,
        threshold=threshold,
        colorbar=True,
        title="Group-level association between motor activity \n"
        "and reading fluency (fdr=0.05)",
    )

    ax.set_ylabel("maps")
    ax.set_title("Second level design matrix", fontsize=12)
    plt.tight_layout()
    plt.show()


