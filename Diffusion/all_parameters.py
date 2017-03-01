# -*- coding: utf-8 -*-

"""
Parameters for the simulation
"""

import os.path as osp

from utils import LOCATION

#==============================================================================
# Directories to save results
#==============================================================================
# Directory to save initial runs
RESULTS_DIR = osp.join(LOCATION, 'Results')

# Directory to save the result of re-runs
RERUNS_DIR = osp.join(RESULTS_DIR, 'Reruns')

# Directory to save parameter files with interesting findings
SAVED_RESULTS_DIR = osp.join(LOCATION, 'Saved')


#==============================================================================
# Parameters to run the analysis
#==============================================================================
# Note: The order here is exactly the same as the one in which these
#       parameters are saved to disk. So this way it's easier to
#       visually compare the values here with those of our json files.
#
# - number_of_times: Number of times we repeat the run with a
#                    given parameter value
# - parameter_values: Values for the parameter we want to study.
#                     We accept only *four* parameters here.
# - cumulative: Wheter to plot cumulative curves or not.
# - main_parameter: Main parameter that simulation is going to be
#                   run for
# - max_time: Maximum time until the simulation is stop.
run = dict(
    number_of_times = 70,
    parameter_values = [0.4, 0.5, 0.6, 0.7],
    cumulative = True,
    main_parameter = 'quality',
    max_time = 160
)


#==============================================================================
# Parameters for the model
#==============================================================================
# Please see the README and our article for an explatation of these
# parameters
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
# Load parameters from a file.
#==============================================================================
# Notes:
# 1. This overrides the parameters set above
# 2. Set this variable to '' to not load any file.
# 3. These file are saved in a SAVED_RESULTS_DIR.
# 4. The results are of these re-runs are saved in
#    RERUNS_DIR.
PARAMETERS_FILE = 'social_influence_60.txt'
