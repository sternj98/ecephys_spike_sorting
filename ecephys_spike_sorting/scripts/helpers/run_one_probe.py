import os
import shutil
import subprocess
import sys
from helpers import log_from_json


# Given json files for CatGT and modules, all processing unique to this 
# recording session and probe

def runOne( session_id,
                 json_directory,
                 data_directory,
                 run_CatGT,
                 catGT_input_json,
                 catGT_output_json,
                 modules,
                 module_input_json,
                 logFullPath
                 ):
    
    if run_CatGT:
        command = sys.executable + " -W ignore -m ecephys_spike_sorting.modules." + 'catGT_helper' + " --input_json " + catGT_input_json \
		          + " --output_json " + catGT_output_json
        print(command)
        subprocess.check_call(command.split(' '))  
    
    # copy module json file to data directory as record of the input parameters 
    if not os.path.exists(data_directory): # added 12/31/21 JS
        os.makedirs(data_directory)
    shutil.copy(module_input_json, os.path.join(data_directory, session_id + '-input.json'))
    print("made it past json copy")
    for module in modules:
        output_json = os.path.join(json_directory, session_id + '-' + module + '-output.json')  
        command = sys.executable + " -W ignore -m ecephys_spike_sorting.modules." + module + " --input_json " + module_input_json \
		          + " --output_json " + output_json
        print(command)
        subprocess.check_call(command.split(' '))
        
    log_from_json.addEntry(modules, json_directory, session_id, logFullPath)# -*- coding: utf-8 -*-

