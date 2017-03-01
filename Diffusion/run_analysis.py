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
from all_parameters import PARAMETERS_FILE
from utils import LOCATION, load_parameters_from_file


#==============================================================================
# Main constants
#==============================================================================
RESULTS_DIR = osp.join(LOCATION, 'Results')
SAVED_RESULTS_DIR = osp.join(LOCATION, 'Saved')
RERUNS_DIR = osp.join(RESULTS_DIR, 'Reruns')


#==============================================================================
# Load parameters from a file to re-run a previous analysis
#==============================================================================
if PARAMETERS_FILE:
    f = osp.join(SAVED_RESULTS_DIR, PARAMETERS_FILE)
    if osp.isfile(f):
        all_parameters = load_parameters_from_file(f)
        run = all_parameters['run']
        parameters = all_parameters['parameters']
    else:
        raise Exception('{} does not exist'.format(f))
else:
    # If there's no parameters file to load, used the parameters
    # saved in all_parameters
    from all_parameters import parameters, run


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
# Create the results directory
if not osp.isdir(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# Create the reruns directory
if not osp.isdir(RERUNS_DIR):
    os.makedirs(RERUNS_DIR)

# Create file name to save parameters
# It's going to be of the form main_parameter_#.txt
if not PARAMETERS_FILE:
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
# File to save the fig
if PARAMETERS_FILE:
    name = osp.splitext(PARAMETERS_FILE)[0] + '_'
    number = len(glob.glob(osp.join(RERUNS_DIR, name) + '*.png'))
    filename = name + str(number) + '.png'
    fig_filename = osp.join(RERUNS_DIR, filename)
else:
    fig_filename = osp.splitext(filename)[0] + '.png'


# Generate plot
multiplot_adopters_and_global_utility(
    data=data,
    set_of_params=set_of_parameters,
    par_name=article_parameters[run['main_parameter']],
    par_values=run['parameter_values'],
    cumulative=run['cumulative'],
    filename=fig_filename,
    max_time=run['max_time'])
