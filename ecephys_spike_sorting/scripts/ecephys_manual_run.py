from sglx_multi_run_pipeline_js import run_ecephys 
import sys 
import os

# run ecephys manually specifying npx directory
npx_directory = r'Z:\HarveyLab\Tier1\Cindy\EphysData\CY\24\220114\165552'

results_directory = r'Z:\HarveyLab\Tier1\Cindy\ProcessedEphys'

run_ecephys(npx_directory,results_directory)