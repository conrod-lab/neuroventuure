import glob
import os
import nibabel as nib
from nilearn import plotting
from scipy.stats import norm
from nilearn.glm import threshold_stats_img
from nilearn.reporting import get_clusters_table
import matplotlib.pyplot as plt
from nilearn.plotting import plot_stat_map, show
from nilearn.image import concat_imgs, mean_img
from nilearn.datasets import fetch_icbm152_brain_gm_mask
from nilearn.maskers import NiftiSpheresMasker
import numpy as np 
import pandas as pd
from nilearn.maskers import NiftiMasker


class ClusterAnalysis:

    def __init__(self, fmri_dir, task, space, contrast, correction_type, alpha, cluster_threshold):
        self.fmri_dir = fmri_dir
        self.task = task
        self.space = space
        self.contrast = contrast
        self.correction_type = correction_type
        self.alpha = alpha
        self.cluster_threshold = cluster_threshold
        self.zmaps = {}
        self.fmri_data = self.get_fmri_data()
        self.zmap_files = self.get_zmap_files()
        self.zmaps = self.load_zmaps()
        self.clean_map, self.threshold = self.correction()
        self.clusters = self.get_clusters()
        self.top_cluster = self.get_top_cluster()
        self.pcc_coords = self.get_pcc_coords()
        self.filename = self.save_zmap()
        self.seed_time_series = self.extract_seed_timeseries()
        self.plot_seed_timecourse

def get_fmri_data(fmri_dir,task='stop',space='MNI152NLin2009cAsym'):
    # get the fmri data
    fmri_file = glob.glob(f'{fmri_dir}/*{task}*{space}*bold.nii.gz')
    # read the file using nibabel
    fmri_img = nib.load(fmri_file[0])
    return fmri_img


def plot_seed_timecourse(frametimes,seed_time_series, event_onsets):

    fig = plt.figure(figsize=(9, 3))
    ax = fig.add_subplot(111)
    ax.plot(frametimes, seed_time_series, linewidth=2, label="seed region")

    # Add markers for event onsets
    # for onset in event_onsets:
    #     plt.axvline(x=onset, color='r', linestyle='--', alpha=0.5)  # Add a vertical line at each event onset

    ax.legend(loc=2)
    ax.set_title("Time course of the seed region")
    plt.show()

def extract_seed_timeseries(fmri_dir, pcc_coords,event_onsets,confound_filename):
    fmri_data = get_fmri_data(fmri_dir,task='stop',space='MNI152NLin2009cAsym')
    n_scans = fmri_data.shape[-1]
    t_r = 2.5
    frametimes = np.linspace(0, (n_scans - 1) * t_r, n_scans)

    seed_masker = NiftiSpheresMasker(
        [pcc_coords],
        radius=8,
        detrend=True,
        standardize="zscore_sample",
        low_pass=0.1,
        high_pass=0.01,
        t_r=t_r,
        memory="nilearn_cache",
        memory_level=1,
        verbose=0,
    )
    df=pd.read_csv(confound_filename,sep='\t')
    df=df.replace(np.nan,0)
    seed_time_series = seed_masker.fit_transform(fmri_data,confounds=df)
    plot_seed_timecourse(frametimes,seed_time_series,event_onsets)    

    brain_masker = NiftiMasker(
        smoothing_fwhm=6,
        detrend=True,
        standardize="zscore_sample",
        standardize_confounds="zscore_sample",
        low_pass=0.1,
        high_pass=0.01,
        t_r=2,
        memory="nilearn_cache",
        memory_level=1,
        verbose=0,
    )

    brain_time_series = brain_masker.fit_transform(
        fmri_data, confounds=df
    )    
    plt.plot(brain_time_series[:, [10, 45, 100, 5000, 10000]])
    plt.title("Time series from 5 random voxels")
    plt.xlabel("Scan number")
    plt.ylabel("Normalized signal")
    plt.tight_layout()
    plt.show()

    seed_to_voxel_correlations = (
        np.dot(brain_time_series.T, seed_time_series) / seed_time_series.shape[0]
    )

    print(
        "Seed-to-voxel correlation shape: (%s, %s)"
        % seed_to_voxel_correlations.shape
    )
    print(
        "Seed-to-voxel correlation: min = %.3f; max = %.3f"
        % (seed_to_voxel_correlations.min(), seed_to_voxel_correlations.max())
    )

    seed_to_voxel_correlations_img = brain_masker.inverse_transform(
        seed_to_voxel_correlations.T
    )
    display = plotting.plot_stat_map(
        seed_to_voxel_correlations_img,
        threshold=0.5,
        vmax=1,
        cut_coords=pcc_coords[0],
        title="Seed-to-voxel correlation (PCC seed)",
    )
    display.add_markers(
        marker_coords=pcc_coords, marker_color="g", marker_size=300
    )
    # At last, we save the plot as pdf.
    from pathlib import Path

    # output_dir = Path.cwd() / "results" / "plot_seed_to_voxel_correlation"
    # output_dir.mkdir(exist_ok=True, parents=True)
    # print(f"Output will be saved to: {output_dir}")

    # display.savefig(output_dir / "pcc_seed_correlation.pdf")    


def correction(correction_type="bonferroni",alpha=0.05,cluster_threshold=10):
    
        # correction types: bonferroni, fdr, fpr
    if correction_type == "fdr":
            
        clean_map, threshold = threshold_stats_img(
            z_map, 
            alpha=alpha, 
            height_control=correction_type,
            cluster_threshold=cluster_threshold
        )
    else:
         clean_map, threshold = threshold_stats_img(
            z_map, 
            alpha=alpha, 
            height_control=correction_type,
        )

    return clean_map,threshold

def get_clusters(zmap,threshold,cluster_threshold=10):
    table = get_clusters_table(
        zmap, stat_threshold=threshold, cluster_threshold=cluster_threshold
    )    
    return table


def plot_zmap(z_map,contrast_id,threshold=0.001,clean_map=None):

    bg_img = fetch_icbm152_brain_gm_mask()

    #for contrast_id, z_map in zmaps.items():
    #_threshold = norm.isf(threshold)
    plotting.plot_glass_brain(
    clean_map,
    colorbar=True,
    threshold=threshold,
    title=f'Nilearn Z map of {contrast_id} (unc p<{alpha})',
    plot_abs=False,
    display_mode="ortho",
    )    

    plot_stat_map(
        clean_map,
        bg_img=bg_img,
        threshold=threshold,
        display_mode="z",
        cut_coords=3,
        black_bg=True,
        title=f"Contrast: {contrast_id} ({correction_type}={alpha})",
    )

# read the zmaps nii.gz files from an input directory
zmaps = {}


# correction type: bonferroni, fdr, fpr
correction_type = "fpr"
alpha = 0.001
task = 'stop'
contrast = 'stopsuccess-stopfail'
# if using fdr or filtering based on cluster size
cluster_threshold = 10
zmap_files = glob.glob(f'/Users/seanspinney/projects/neuroventure/fmri-task/output/*zmap*{contrast}*.nii.gz')
event_file = f"/Users/seanspinney/data/neuroventure/sub-019/ses-01/func/sub-019_ses-01_task-{task}_run-01_events.tsv"
confounder_file = f"/Users/seanspinney/data/neuroventure-derivatives/fmriprep/sub-019/ses-01/func/sub-019_ses-01_task-{task}_run-01_desc-confounds_timeseries.tsv"
fmri_dir = "/Users/seanspinney/data/neuroventure-derivatives/fmriprep/sub-019/ses-01/func"
# load the zimap nii.gz using nibabel

for zmap_file in zmap_files:
    z_map = nib.load(zmap_file)
    file_parts = zmap_file.split('_')
    contrast_id = file_parts[-1].split('.')[0]#.split('-')[1]
    zmaps[contrast_id] = z_map


# open event file with pandas

events = pd.read_csv(event_file,sep='\t')
events.head()

contrast_events = events[events['trial_type']=='stopsuccess']

for contrast_id, z_map in zmaps.items():
    
    clean_map, threshold = correction(correction_type=correction_type,alpha=alpha,cluster_threshold=10)
    plot_zmap(z_map,contrast_id,threshold=threshold,clean_map=clean_map)   
    
    # get cluster table
    clusters = get_clusters(z_map,threshold,cluster_threshold)

    # sort by Peak Stat
    clusters = clusters.sort_values(by='Peak Stat',ascending=False)

    # get x,y,z coordinates of the top 1 cluster
    top_cluster = clusters.iloc[0]
    pcc_coords = (top_cluster['X'],top_cluster['Y'],top_cluster['Z'])
    
    # Posterior Cingulate Cortex (PCC)
    #pcc_coords = (0, -52, 18)
    filename = f"/Users/seanspinney/projects/neuroventure/fmri-task/output/con-{contrast_id}_top1cluster.png"
    display = plotting.plot_stat_map(
            z_map, threshold=3.0, title="Seed based GLM", cut_coords=pcc_coords
        )
    display.add_markers(
            marker_coords=[pcc_coords], marker_color="g", marker_size=300
        )
    display.savefig(filename)
    print(f"Save z-map in '{filename}'.")                                    

    event_onsets = contrast_events['onset'].values
    #extract_seed_timeseries(fmri_dir, pcc_coords, event_onsets, confounder_file)
    # get the top cluster id and location 
    #print(clusters.head())
