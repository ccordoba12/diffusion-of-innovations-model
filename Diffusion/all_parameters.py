# -*- coding: utf-8 -*-

"""
Parameters for the simulation
"""

#==============================================================================
# Parameters to run the analysis
#==============================================================================
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
# 2. Set this variable to '' to not load any
#    file.
PARAMETERS_FILE = 'social_influence_60.txt'
