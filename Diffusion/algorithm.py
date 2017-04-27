# -*- coding: utf-8 -*-

"""
Algorithm
"""

from __future__ import division

# Third-party imports
import networkx as nx
import numpy as np

# Local imports
from utils import (compute_global_utility, get_adopters, get_neighbors,
                   is_adopter, logistic, set_seed, step)


def generate_initial_conditions(parameters):
    """
    Initial conditions for the simulation
    
    Create the graph on which the diffusion occurs and set additional
    attributes for its node
    
     `parameters` is a dictionary that contains the parameters that control
     the evolution.
    """
    # Graph creation
    G = nx.generators.watts_strogatz_graph(parameters['number_of_consumers'],
                                           parameters['number_of_neighbors'],
                                           parameters['randomness'])
    
    # Graph properties
    for node_index in G.nodes():
        node = G.node[node_index]
        node['adopter'] = 0                      # 1 is adopter, 0 non-adopter
        node['preference'] = np.random.random()  # pi
        node['minimal_utility'] = np.random.random() # Umin,i
        node['reflexivity'] = np.random.random() # \alpha_{i}
        
        # Neighbors never change if the level is an int
        if int(parameters['level']) - parameters['level'] == 0:
            node['neighbors'] = get_neighbors(G, node_index, parameters['level'])
        else:
            node['neighbors'] = []
    
    # Create a seed of initial adopters if there's no marketing
    # if not parameters['marketing_effort']:
    #    set_seed(G, parameters)
    
    return G


def evolution_step(graph, parameters, test=False):
    """
    Function that computes the evolution step of the diffusion process
    that occurs in a small-world graph with a given set of parameters
    
    parameters: Dictionary that contains the parameters that control
    the evolution.
    test: Test with a step function instead of the logistic one for
    the reflexivity_index.

    Returns: The number of adopters in a given time step.
    """

    # To save the adopters at this time step
    adopters_at_step = []
    
    # Compute quantities that depend on the global state of the system.
    # Thus they are the same for all agents during this time step
    if parameters['reflexivity']:
        # Compute utility due to global influence
        global_utility = compute_global_utility(graph)

        # Decide which activation function to use.
        if not test:
            activation = logistic
        else:
            activation = step
        
        # Compute reflexivity index
        reflexivity_index = activation(global_utility,
                                       parameters['activation_sharpness'],
                                       parameters['critical_mass'])
        #print(reflexivity_index)
    
    
    # Determine which agents adopt
    for node_index in graph.nodes():
        node = graph.node[node_index]

        # Continue to next node if the current one is
        # already an adopter
        if node['adopter'] == 1:
            continue

        # -- Compute utility due to local influence
        # Adopters
        if node['neighbors']:
            neighbors = node['neighbors']
        else:
            neighbors = get_neighbors(graph, node_index, level=parameters['level'])
        adopters_among_neighbors = [x for x in neighbors if is_adopter(graph, x)]

        # Only if a consumer has adopters among his neighbors, he computes
        # his local utility
        if len(adopters_among_neighbors) > 0:

            # Ai value
            adopters_percentaje = len(adopters_among_neighbors) / len(neighbors)

            # Computing xi
            if adopters_percentaje > parameters['adopters_threshold']:
                local_influence = 1
            else:
                local_influence = 0
            
            # Set individual preference (yi)
            if parameters['quality'] >= node['preference']:
                individual_preference = 1
            else:
                individual_preference = 0

            # Computing local utility ULi
            local_utility = parameters['social_influence'] * local_influence + \
                             (1 - parameters['social_influence']) * individual_preference
        else:
            local_utility = 0
        
        # -- Compute utility if reflexivity is on or off
        if parameters['reflexivity']:
            # Compute utility if agent has become aware of a global pattern
            # or not
            if node['reflexivity'] < reflexivity_index:
                utility = local_utility + global_utility - \
                          local_utility * global_utility
            else:
                utility = local_utility
        else:
            utility = local_utility

        # -- Decide to adopt if
        # Agent's utility is higher than a minimal utility
        if utility >= node['minimal_utility']:
            adopters_at_step.append(node_index)
        # or marketing influences the agent
        elif parameters['marketing_effort'] and \
          len(adopters_among_neighbors) > 0:
            prob_adoption = np.random.random()
            if prob_adoption < parameters['marketing_effort']:
                adopters_at_step.append(node_index)

    # Update the graph with customers who adopted in this time step
    for node_index in adopters_at_step:
        node = graph.node[node_index]
        node['adopter'] = 1
    
    # Return number of adopters at this step
    return len(adopters_at_step)


def evolution(graph, parameters, max_time, test=False):
    """
    Compute the evolution of the algorithm up to max_time.

    Return: A dictionary with the number of adopters and the global
    utility per time step.
    """
    # Save the adopters at each time during the evolution
    adopters = []
    
    # Compute the clustering index during the evolution
    global_utility = []
    
    # Perform the evolution
    for t in range(max_time):
        adopters_at_t = evolution_step(graph, parameters, test)
        adopters.append(adopters_at_t)
        global_utility.append(compute_global_utility(graph))
    
    data = {'adopters': adopters, 'global_utility': global_utility}
    return data


def single_run(parameters, max_time):
    """
    Compute a single run (with and without reflexivity) of the algorithm
    under the same conditions.

    parameters: Dictionary of parameters for the algorithm.
    max_time: Time to stop the algorithm.

    Return: A dictionary with the number of adopters with and without
    reflexivity.
    """
    parameters = parameters.copy()
    G = generate_initial_conditions(parameters)

    # No reflexivity data
    parameters['reflexivity'] = False
    set_seed(G, parameters)
    data_no_rx = evolution(G, parameters, max_time)

    # Reflexivity data
    parameters['reflexivity'] = True
    set_seed(G, parameters, reset=True)
    data_rx = evolution(G, parameters, max_time)

    return {'no_rx': data_no_rx,
            'rx': data_rx}


def compute_run(number_of_times, parameters, max_time, dview=None):
    """
    Compute a run of the algorithm.
    
    A run consists in repeating the evolution of the algorithm under
    the same conditions a certain number_of_times.

    dview is direct view instance from an ipyparallel cluster.
    """

    # Perform the run
    if dview is None:
        raw_data = map(lambda x: single_run(parameters, max_time),
                       range(number_of_times))
    else:
        raw_data = dview.map_sync(lambda x: single_run(parameters, max_time),
                                  range(number_of_times))

    data = {'no_rx': [d['no_rx'] for d in raw_data],
            'rx': [d['rx'] for d in raw_data]}

    return data


def generate_parameters(parameters, name, values):
    """
    Generate a list of parameters for compute_run to do sensitivity analysis

    name: Name of the parameter
    values: A list of values for the given parameter we want to change
    """
    set_of_parameters = []
    for val in values:
        new_parameters = parameters.copy()
        new_parameters[name] = val
        set_of_parameters.append(new_parameters)
    return set_of_parameters
