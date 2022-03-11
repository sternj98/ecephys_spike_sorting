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
from CY_schema_table import *
from JS_ephys_tables import * 


# run preprocessing for depth estimation on ephys data
EphysDepthPreprocess().populate()
