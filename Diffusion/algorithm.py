# -*- coding: utf-8 -*-

"""
Algorithm
"""

from __future__ import division

# Third-party imports
import networkx as nx
import numpy as np

# Local imports
from utils import (clustering_index, get_adopters, get_neighbors, is_adopter,
                   logistic, set_seed, step)


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
        #node['minimal_utility'] = np.random.random()
        
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
    that occurs in a small-world graph
    
    `parameters` is a dictionary that contains the parameters that
    control the evolution.
    """
    
    #minimal_utility = parameters['minimal_utility']
    
    # Adopters before performing the current step
    previous_adopters = get_adopters(graph)
    
    # To save the adopters at this time step
    adopters_at_step = []
    
    # Compute quantities that depend on the global state of the system.
    # Thus they are the same for all agents during this time step
    if parameters['reflexivity']:
        # Compute utility due to indirect social influence
        indirect_utility = clustering_index(graph)

        # Decide which activation function to use.
        if not test:
            activation = logistic
        else:
            activation = step
        
        # Compute reflexivity index
        reflexivity_index = activation(indirect_utility,
                                       parameters['activation_sharpness'],
                                       parameters['critical_mass'])
        #print(reflexivity_index)
    
    
    # Determine which agents adopt
    for node_index in graph.nodes():
        node = graph.node[node_index]

        # -- Adoption due to marketing
        if parameters['marketing_effort']:
            p = np.random.random()
            if not node['adopter'] and (p < parameters['marketing_effort']):
                adopters_at_step.append(node_index)
                continue

        # -- Compute utility due to direct social influence
        # Adopters
        if node['neighbors']:
            neighbors = node['neighbors']
        else:
            neighbors = get_neighbors(graph, node_index, level=parameters['level'])
        adopters_among_neighbors = [x for x in neighbors if is_adopter(graph, x)]

        # Only if a consumer has adopters among his neighbors, he computes
        # his direct utility
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

            # Computing utility Ui
            direct_utility = parameters['social_influence'] * local_influence + \
                             (1 - parameters['social_influence']) * individual_preference
        else:
            direct_utility = 0
        
        # -- Compute utility if reflexivity is on or off
        if parameters['reflexivity']:
            # Compute utility if agent has become aware of a global pattern
            # or not
            alpha = np.random.random()
            if alpha < reflexivity_index:
                utility = direct_utility + indirect_utility - \
                          direct_utility * indirect_utility
            else:
                utility = direct_utility
        else:
            utility = direct_utility
        
        # Decide to adopt if agent's utility is higher than a minimal
        # utility
        minimal_utility = np.random.random()
        if minimal_utility <= utility:
            adopters_at_step.append(node_index)
        
        # print(utility)
        #if utility > node['minimal_utility']: #minimal_utility:
        #    if np.random.random() > node['minimal_utility']:
        #        node['adopter'] = 1
    
    # Update the graph with customers who adopted in this time step
    for node_index in adopters_at_step:
        node = graph.node[node_index]
        node['adopter'] = 1
    
    # Return number of adopters at time t
    current_adopters = get_adopters(graph)
    return len(current_adopters) - len(previous_adopters)


def evolution(graph, parameters, max_time='complete_adoption',
              compute_index=False, test=False):
    """Compute the evolution of the algorithm up to max_time"""
    # Save the adopters at each time during the evolution
    adopters = []
    
    # Compute the aggregation index during the evolution
    if compute_index:
        indexes = []
    
    # Perform the evolution
    if max_time == 'complete_adoption':
        while not all( [is_adopter(graph, x) for x in graph.nodes()] ):
            adopters_at_t = evolution_step(graph, parameters, test)
            adopters.append(adopters_at_t)
            if compute_index:
                indexes.append(clustering_index(graph))
    else:
        for t in range(max_time):
            adopters_at_t = evolution_step(graph, parameters, test)
            adopters.append(adopters_at_t)
    
    if compute_index:
        return indexes
    else:
        return adopters


def compute_run(number_of_times, parameters, max_time='complete_adoption'):
    """
    Compute a run of the algorithm
    
    A run consists in repeating the evolution of the algorithm under
    the same conditions a certain number_of_times
    """
    # Print the parameters of the run
    print(parameters)

    # Perform the run
    no_rx_data = []
    rx_data = []
    for i in range(number_of_times):
        G = generate_initial_conditions(parameters)

        # No reflexivity data
        parameters['reflexivity'] = False
        set_seed(G, parameters)
        adopters_no_rx = evolution(G, parameters, max_time=max_time)
        no_rx_data.append(adopters_no_rx)

        # Reflexivity data
        parameters['reflexivity'] = True
        set_seed(G, parameters, reset=True)
        adopters_rx = evolution(G, parameters, max_time=max_time)
        rx_data.append(adopters_rx)
    
    data = [no_rx_data, rx_data]
    
    # Make the evolution lists of the same length so they can be
    # passed to Seaborn
    if max_time == 'complete_adoption':
        uniform_data = []
        for li in data:
            max_length = max([len(x) for x in li])
            new_li = [x + [0] * (max_length - len(x)) for x in li]
            uniform_data.append(new_li)
        return uniform_data
    else:
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
