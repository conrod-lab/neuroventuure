def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes

def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    ##### list keys for t1w, dwi, rs-fMRI, task-fMRI ###########

    t1w = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_run-{item:02d}_T1w')
    func_rest = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_run-{item:02d}_bold')
    func_task_STOP = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-stop_run-{item:02d}_bold')
    func_task_MIDT = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-midt_run-{item:02d}_bold')
    # dwi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-{item:02d}_dwi')
    fmap_mag =  create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude')
    fmap_phase = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff')
    dwi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-{item:02d}_dwi')    
    #dwi22 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-{item:02d}_acq-22d_dwi')
    #dwi23 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-{item:02d}_acq-23d_dwi')
    #dwi24 = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-{item:02d}_acq-24d_dwi')
    # dwi22_adc = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dwi_acq-dir22adc')
    # dwi22_tracew = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dwi_acq-dir22tracew')
    # dwi22_fa = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_dwi_acq-dir22fa')
    

    #info = {t1w: [], func_rest: [], func_task_STOP: [], func_task_MIDT: [], dwi22: [], dwi23: [], dwi24: []}
    info = {t1w: [], func_rest: [], func_task_STOP: [], func_task_MIDT: [], fmap_mag:[], fmap_phase:[], dwi: []}

    for s in seqinfo:
        protocol_name = s.protocol_name.strip()
        # series_num_str = s.series_id.split('-', 1)[0]
        # if not series_num_str.isdecimal():
        #     raise ValueError(
        #         f"This heuristic can operate only on data when series_id has form <series-number>-<something else>, "
        #         f"and <series-number> is a numeric number. Got series_id={s.series_id}")
        
        # series_num = int(series_num_str)
        # T1w
        #if protocol_name == 'T1 SAG MPRAGE grappa2' and s.dim1 == 256:
        
        if 'T1' in protocol_name and s.dim4 == 1 and s.sequence_name in ["*tfl3d1_ns","*tfl3d1_16ns"] and not any(it in s.image_type for it in ["DERIVED", "PHYSIO"]):
            info[t1w].append(s.series_id)

        # rs-fMRI
        if 'REST' in protocol_name and s.dim1 == 64 and not any(it in s.image_type for it in ["DERIVED", "PHYSIO"]):
        #if (protocol_name == 'Axial BOLD 3.5mm ISO_RESTING' or protocol_name == 'BOLD MOSAIC 64_REST')and s.dim1 == 64:
            info[func_rest].append(s.series_id)

        # task-fMRI
        if 'STOP' in protocol_name and s.dim1 == 64 and not any(it in s.image_type for it in ["DERIVED", "PHYSIO"]):
        #if protocol_name == 'BOLD MOSAIC 64_STOP' and s.dim1 == 64:
            info[func_task_STOP].append(s.series_id)
        if 'MIDT' in protocol_name and s.dim1 == 64:
        #if protocol_name == 'BOLD MOSAIC 64_MIDT'and s.dim1 == 64:
            info[func_task_MIDT].append(s.series_id)
        # fmap
        if  ('fm2d2r' in s.sequence_name) and any(it in s.image_type for it in [ "M"]):
            info[fmap_mag].append(s.series_id)
        if  ('fm2d2r' in s.sequence_name) and any(it in s.image_type for it in [ "P"]):
            info[fmap_phase].append(s.series_id)   

        if (("ep_b" in s.sequence_name) or ("ez_b" in s.sequence_name) or ("epse2d1_110" in s.sequence_name)) and not any(it in s.image_type for it in ["DERIVED", "PHYSIO"]):
            info[dwi].append(s.series_id)

    return info
