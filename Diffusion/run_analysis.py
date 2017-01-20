# -*- coding: utf-8 -*-

"""
Run a complete analysis for a give parameter
"""

import atexit
import glob
import json
import os
import os.path as osp
import time
import subprocess

from ipyparallel import Client

from algorithm import compute_run, generate_parameters
from plots import multiplot_adopters_and_global_utility
from utils import LOCATION


#==============================================================================
# Parameters
#==============================================================================
# Parameters to run the analysis
run = dict(
    number_of_times = 70,
    parameter_values = [0.4, 0.5, 0.6, 0.7],
    cumulative = True,
    main_parameter = 'quality',
    max_time = 160
)

# Parameters for the model
parameters = dict(
    number_of_consumers = 1000,
    social_influence = 0.7,
    randomness = 0.01,
    activation_sharpness = 40,
    level = 1,
    quality = 0.5,
    initial_seed = 0.001,
    critical_mass = 0.5,
    number_of_neighbors = 8,
    adopters_threshold = 0.5,
    marketing_effort = 0,
)


#==============================================================================
# Mapping of parameter names to the names in our article
#==============================================================================
article_parameters = dict(
    randomness = 'r',
    number_of_neighbors = 'k',
    adopters_threshold = 'h',
    social_influence = r'\beta',
    quality = 'q',
    number_of_consumers = 'N',
    activation_sharpness = r'\phi',
    critical_mass = 'M_c',
)


#==============================================================================
# Save parameters in a "Results" directory, placed next to this file
#==============================================================================
RESULTS_DIR = osp.join(LOCATION, 'Results')

# Create the directory
if not osp.isdir(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Create file name to save parameters
# It's going to be of the form main_parameter_#.txt
name = osp.join(RESULTS_DIR, run['main_parameter'] + '_')
number = len(glob.glob(name + '*.txt'))
filename = name + str(number) + '.txt'

# Create a dict with all the needed paramaters
all_parameters = dict(
    run=run,
    parameters=parameters
)

# Save all parameters
with open(filename, 'w') as f:
    json.dump(all_parameters, f, indent=4)


#==============================================================================
# Main variables
#==============================================================================
# Remove the parameter we want to study
parameters.pop(run['main_parameter'])

# Start IPyparallel cluster
try:
    rc = Client()
    dview = rc[:]
except:
    try:
        proc = subprocess.Popen(["ipcluster", "start", "-n", "8"])
        atexit.register(proc.terminate)
        time.sleep(20)
        rc = Client()
        dview = rc[:]
    except:
        dview = None

#==============================================================================
# Simulation
#==============================================================================
# Generating different sets of parameters
set_of_parameters = generate_parameters(parameters,
                                        run['main_parameter'],
                                        run['parameter_values'])

# Reset the engines
if dview is not None:
    get_ipython().magic('px %reset -f')  # analysis:ignore

# Run the simulation
data = []
for p in set_of_parameters:
    print(len(data))
    p_data = compute_run(number_of_times=run['number_of_times'],
                         parameters=p,
                         max_time=run['max_time'],
                         dview=dview)
    data.append(p_data)


#==============================================================================
# Plotting
#==============================================================================

fig_filename = osp.splitext(filename)[0] + '.png'

multiplot_adopters_and_global_utility(
    data=data,
    set_of_params=set_of_parameters,
    par_name=article_parameters[run['main_parameter']],
    par_values=run['parameter_values'],
    cumulative=run['cumulative'],
    filename=fig_filename,
    max_time=run['max_time'])
