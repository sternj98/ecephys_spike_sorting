# Run mean_waveforms, quality metrics, and TPrime on sessions that we've spikesorted and curated 
from  sglx_multi_run_pipeline_js import run_ecephys 
import sys 
import os
import datetime
import socket
current_pc = socket.gethostname()

if current_pc =='MNB-HARV-D00969':
    ks_dj_pipeline_path = r'C:\Users\xinto\Documents\ks-dj-pipeline'
else:
    ks_dj_pipeline_path = r'C:\Users\joshs\Documents\GitHub\ks-dj-pipeline'
sys.path.append(ks_dj_pipeline_path)

# now import datajoint stuff
from JS_ephys_tables import * 
# from CY_utils import update_curated_table 

# # first add new sessions to table that keeps track of where we have manually curated spikesorting
# update_curated_table()

# Look for ephys sessions that are curated but we haven't performed post-processing on yet
session_keys , ephys_paths = ((EphysSession() & "probe = 'NP1'") & CuratedSession() - SyncBehaData()).fetch("KEY","ephys_path")

# parameters for running ecephys
modules = ['mean_waveforms','quality_metrics']
run_CatGT = False
runTPrime = True
results_directory = r'Z:\HarveyLab\Tier1\Cindy\ProcessedEphys'

# Go through and post-process
print("Now beginning post-processing of new curated sessions")
for this_key,this_unprocessed_np_path in zip(session_keys,ephys_paths): 
    if this_key['session_date'] >= datetime.date(2022,2,7): 
        print("Post-processing session at: ",this_unprocessed_np_path)
        run_ecephys(this_unprocessed_np_path,results_directory,modules = modules,run_CatGT = run_CatGT, runTPrime = runTPrime)

        print("Finished post-processing session: ",this_key) 
    else: 
        print("skipping this entry due to lower NI sample rate: ", this_key)

# update Neuron and SyncBehaData tables
Neuron().populate()
SyncBehaData().populate()
