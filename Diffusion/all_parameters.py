# -*- coding: utf-8 -*-

"""
Parameters for the simulation
"""

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
# Load parameters from a file in SAVED_RESULTS_DIR.
#==============================================================================
# Notes:
# 1. This overrides the parameters set above
# 2. Set this variable to '' to not load any file.
# 3. It's assumed that these file are saved in a
#    *Saved* subdirectory inside this directory.
PARAMETERS_FILE = 'social_influence_60.txt'
