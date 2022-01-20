import datajoint as dj
import os
import shutil 
import numpy as np
from pathlib import Path 

import ecephys_spike_sorting.common.SGLXMetaToCoords as SGLXMeta

def dj_config_cy():
    dj.config['database.host'] = '10.119.248.29'
    dj.config['database.user'] = 'josh'
    dj.config['database.password'] = 'vr135'
    dj.conn()

def reformat_np_dir(ephys_server_path = r'Z:\HarveyLab\Tier1\Cindy\EphysData'): 
    """
        Reformat directory structure of neuropixels data collected with spikeglx, assuming that folders fomatted: 
        
            {prefix}{mouse_id}_{recording area}_{date}_g0 
        
        are saved in the ephys_server_path. 
        
        Moves data to: 
        
            ephys_server_path/{prefix}/{mouse_id}/{recording area}/{date}/{time}
            
        and adds a probe_area_time.txt file
    """
    ephys_subdirs = os.listdir(ephys_server_path)
    for subdir in ephys_subdirs: 
        if len(os.listdir(os.path.join(ephys_server_path,subdir))) > 0:
            if np.any([x[:-1] == subdir + '_imec' for x in os.listdir(os.path.join(ephys_server_path,subdir))]): 
                print("reformatting directory structure for new neuropixels data at: %s"%os.path.join(ephys_server_path,subdir))
                prefix_mouseID , target , date , gate = subdir.split('_') # assumes this format of filename
                finding_id = [prefix_mouseID[k].isnumeric() for k in range(len(prefix_mouseID))]
                id_ix = [i for i, x in enumerate(finding_id) if x == True][0]
                prefix = prefix_mouseID[:id_ix]
                mouseID = prefix_mouseID[id_ix:]
                print(prefix,mouseID, target , date , gate)
                # now read metafile to get the time of the recording
                nidq_meta_name = [x for x in os.listdir(os.path.join(ephys_server_path,subdir)) if x[-9:] == 'nidq.meta'][0]
                nidq_meta_path = os.path.join(ephys_server_path,subdir,nidq_meta_name)
                if os.path.exists(nidq_meta_path):
                    nidq_meta_dict = readMeta(Path(nidq_meta_path))
                    time = nidq_meta_dict['fileCreateTime'][nidq_meta_dict['fileCreateTime'].find("T")+1:].replace(':','')
                    print(prefix,mouseID, target , date ,time ,  gate)
                else: 
                    print("couldn't find .nidq.meta!")
                    break

                # make new path and move data 
                old_path = os.path.join(ephys_server_path,subdir)
                new_path = os.path.join(ephys_server_path,prefix,mouseID,date[2:],time,subdir) # note that sglx saves the century as well; ie 2022 instead of 22; reformat
                print("Moving %s to %s (might take a sec)"%(old_path,new_path))
                if os.path.exists(new_path) == False:
                    shutil.move(old_path,new_path) # move directory
                    # now save area, probe, time
                    probe_area_time = ["NP1",target,time]
                    probe_area_time_path = os.path.join(ephys_server_path,prefix,mouseID,date[2:],time,'probe_area_time.txt')
                    probe_area_time_file = open(probe_area_time_path, "w")
                    for attribute in probe_area_time:
                        probe_area_time_file.write(attribute + "\t")