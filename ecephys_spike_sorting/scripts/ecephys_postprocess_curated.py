# Run mean_waveforms, quality metrics, and TPrime on sessions that we've spikesorted and curated 
from  sglx_multi_run_pipeline_js import run_ecephys 
import sys 
import os
import datetime
from dateutil import parser
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import pandas as pd
import socket
current_pc = socket.gethostname()

if current_pc =='MNB-HARV-D00969':
    ks_dj_pipeline_path = r'C:\Users\xinto\Documents\ks-dj-pipeline'
else:
    ks_dj_pipeline_path = r'C:\Users\joshs\Documents\GitHub\ks-dj-pipeline'
sys.path.append(ks_dj_pipeline_path)

# now import datajoint stuff
from JS_ephys_tables import * 
# from dj_ephys_utils import update_curated_table 

# # first add new sessions to table that keeps track of where we have manually curated spikesorting
# update_curated_table()

# find all sessions that have been curated but do not have adjusted spike times
# then run tprime

# initialize empty lists to collect primary keys and ephys path for sessions that need to be postprocessed
session_keys = []
ephys_paths = []

# establish connection to google sheet
scopes = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\xinto\Documents\ks-dj-pipeline\cy-experiment-data-21e96498a6b7.json", scopes)
file = gspread.authorize(credentials) # authenticate the JSON key with gspread
sheet = file.open("Mouse histology track") #open sheet
all_sheets = sheet.worksheets()

# go through each mouse's google sheet
for this_sheet in all_sheets:
    this_prefix = this_sheet.title[:2]
    this_mouse = int(this_sheet.title[2:])
    records_data = this_sheet.get_all_records()
    sheet_df = pd.DataFrame(records_data)
    if 'Curated' in sheet_df.columns:
        curated_dates = [parser.parse(x).date() for x in sheet_df[sheet_df['Curated']=='y']['Date'].values]
        # for each date, check if adjusted spike times are available
        for this_date in curated_dates: 
            date_reformat = re.sub(r'\W+', '', datetime.datetime.strftime(this_date,'%y%m%d'))
            ece_results_path,run_specs = unpack_dj((SpikeSortingResults() & ('mouse_id = ' + str(this_mouse)) & ('session_date = ' + date_reformat)).fetch('ecephys_output_path','run_specs'))
            all_probes = run_specs[3].split(',')
            for this_probe in range(len(all_probes)):
                session_name = os.path.split(ece_results_path)[-1][6:]
                imec_folder = session_name + '_imec' + all_probes[this_probe]
                ks2_folder = 'imec' + all_probes[this_probe] + '_ks2'
                adj_spikes_file = os.path.join(ece_results_path,imec_folder,ks2_folder,'spike_times_sec_adj.npy')           
                has_adj = os.path.isfile(adj_spikes_file)
                if not has_adj: # append session_keys and ephys path 
                    temp_key = (EphysSession() & ('mouse_id = ' + str(this_mouse)) & ('session_date = ' + date_reformat)).fetch('KEY')[0]
                    temp_path = (EphysSession() & ('mouse_id = ' + str(this_mouse)) & ('session_date = ' + date_reformat)).fetch('ephys_path')[0]
                    if temp_key not in session_keys:
                        session_keys.append(temp_key)
                    if temp_path not in ephys_paths:
                        ephys_paths.append(temp_path)  

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
# Neuron().populate()
# SyncBehaData().populate()
