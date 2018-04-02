# -*- coding: utf-8 -*-

"""
Run a complete analysis for a give parameter
"""

import atexit
import csv
import glob
import json
import os
import os.path as osp
import time
import subprocess

from ipyparallel import Client
from IPython.core.getipython import get_ipython

from algorithm import compute_run, generate_parameters
from plots import (multiplot_variable, plot_adopters, plot_adopters_type,
                   multiplot_adopters_and_global_utility)
from all_parameters import (PARAMETERS_FILE, RESULTS_DIR, RERUNS_DIR,
                            SAVED_RESULTS_DIR, output)
from utilities import (load_parameters_from_file,
                       get_adopters_percentaje_upto_activation)


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
# It's going to be of the form main_parameter_#.json
if not PARAMETERS_FILE:
    name = osp.join(RESULTS_DIR, run['main_parameter'] + '_')
    number = len(glob.glob(name + '*.json'))
    filename = name + str(number) + '.json'

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
        # Get ipcluster path
        ipcluster_path = osp.join('.', 'envs', 'default', '{}', 'ipcluster')
        if os.name == 'nt':
            ipcluster_path = ipcluster_path.format('Scripts')
        else:
            ipcluster_path = ipcluster_path.format('bin')

        proc = subprocess.Popen([ipcluster_path, "start", "-n", "8"])
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
    get_ipython().magic('px %reset -f')
    get_ipython().magic('px %reload_ext autoreload')
    get_ipython().magic('px %autoreload 2')

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
    number = len(glob.glob(osp.join(RERUNS_DIR, name) + '*[!types].png'))
    filename = name + str(number)
    filename = osp.join(RERUNS_DIR, filename)
else:
    filename = osp.splitext(filename)[0]


# Generate plots
if output['plot_adopters_and_global_utility']:
    multiplot_adopters_and_global_utility(
        multiple_data=data,
        set_of_params=set_of_parameters,
        par_name=article_parameters[run['main_parameter']],
        par_values=run['parameter_values'],
        cumulative=run['cumulative'],
        filename=filename + '.png'
    )

# Plot adopters with and without reflexivity
if output['plot_adopters']:
    multiplot_variable(plot_func=plot_adopters,
                       multiple_data=data,
                       set_of_params=set_of_parameters,
                       par_name=article_parameters[run['main_parameter']],
                       par_values=run['parameter_values'],
                       cumulative=run['cumulative'],
                       filename=filename + '_adopters.png',
                       ylim_bottom=None,
                       show_activation_time=True)

# Plot adopters per utility and marketing
if output['plot_adopters_type']:
    multiplot_variable(plot_func=plot_adopters_type,
                       multiple_data=data,
                       set_of_params=set_of_parameters,
                       par_name=article_parameters[run['main_parameter']],
                       par_values=run['parameter_values'],
                       cumulative=run['cumulative'],
                       filename=filename + '_types.png',
                       ylim_bottom=None,
                       show_activation_time=False)


#==============================================================================
# Save adopters percentaje up to activation to a csv file
#==============================================================================
if output['save_adopters_percentage']:
    with open(filename + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([run['main_parameter'], 'Percentaje'])
        for d, p, v in zip(data, set_of_parameters, run['parameter_values']):
            percentaje = get_adopters_percentaje_upto_activation(d, p)
            writer.writerow([v, percentaje])
