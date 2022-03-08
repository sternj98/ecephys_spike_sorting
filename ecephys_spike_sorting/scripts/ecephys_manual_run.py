from sglx_multi_run_pipeline_js import run_ecephys 
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
from dj_ephys_utils import reformat_np_dir,update_Date
from CY_schema_table import *
from JS_ephys_tables import * 
from dynChoice import *

# run ecephys manually specifying npx directory
results_directory = r'Z:\HarveyLab\Tier1\Cindy\ProcessedEphys'


# reformat sglx sessions within DJ-compatible nested directory structure
reformat_np_dir()
# add new dates to Date() manual table
update_Date()
# update BehaSession and EphysSession tables
BehaSession().populate()
EphysSession().populate()
SwitchingBehavior().populate()

# Look for ephys sessions that don't have spikesorting results
session_keys , ephys_paths = (EphysSession() & "session_date >= '2022-03-04'").fetch("KEY","ephys_path")
print(session_keys)

modules = ['kilosort_helper','kilosort_postprocessing']
run_CatGT = True
runTPrime = False

for this_key,this_unprocessed_np_path in zip(session_keys,ephys_paths): 
    print("Processing session at: ",this_unprocessed_np_path)
    run_ecephys(this_unprocessed_np_path,results_directory,modules = modules,run_CatGT = run_CatGT,runTPrime = runTPrime)