# -*- coding: utf-8 -*-

"""
Utility functions for the algorithm
"""

from __future__ import division

import json
import os.path as osp
import random

import networkx as nx
import numpy as np


LOCATION = osp.dirname(osp.abspath(__file__))


def get_neighbors(graph, node, level):
    """Get neighbors of a given node up to a certain level"""

    min_level = int(level)
    if min_level < level:
        max_level = min_level + 1
        percentaje = level - min_level
    else:
        max_level = level
        percentaje = 0

    # All neighbors up to max_level
    all_neighbors = nx.single_source_shortest_path_length(graph, node,
                                                          cutoff=max_level)

    if percentaje > 0:
        neighbors_min_level = [k for (k, v) in all_neighbors.items() if (1 <= v <= min_level)]
        neighbors_max_level = [k for (k, v) in all_neighbors.items() if v == max_level]
        n = np.round(len(neighbors_max_level) * percentaje)
        additional_neighbors = random.sample(neighbors_max_level, int(n))
        neighbors = neighbors_min_level + additional_neighbors
    else:
        neighbors = [k for (k, v) in all_neighbors.items() if (1 <= v <= max_level)]

    return neighbors


def is_adopter(graph, node):
    """Return True if a node is an adopter"""
    return graph.node[node]['adopter'] == 1


def get_adopters(graph):
    """Get the nodes that are adopters in the graph"""
    return [x for x in graph.nodes() if is_adopter(graph, x)]


def speed_of_diffusion(adopters):
    """
    Compute the velocity of diffusion $rho$
    
    This is done according to equation 6 in the article
    """
    T = len(adopters)
    cumulative_adopters = np.cumsum(adopters)
    return (1/T) * ( sum(cumulative_adopters) / sum(adopters) )


def homophily_index(graph):
    """
    Return the number of cross-gender edges over the total number of edges
    
    Cross-gender edges mean edges between adopters and non-adopters
    """
    cross_gender_edges = []
    for e in graph.edges():
        i = e[0]
        j = e[1]
        if is_adopter(graph, i) and \
          not is_adopter(graph, j) or is_adopter(graph, j) and \
          not is_adopter(graph, i):
            cross_gender_edges.append(e)
    
    #print( len(cross_gender_edges), len(graph.edges()) )
    return len(cross_gender_edges) / len(graph.edges())


def compute_global_utility(graph):
    """
    Return an index that quantifies how big the size of adopter
    clusters is in the entire population of consumers. We call this
    index 'Global utility' in our article.

    This index computes the cluster-size-weighted average of adopter
    clusters divided by the total number of consumers

    So it goes from 0 to 1 and it's always increasing.
    """
    N = len(graph.nodes())
    adopters = get_adopters(graph)
    
    clusters = nx.subgraph(graph, adopters)
    cluster_sizes = [len(c) for c in nx.connected_components(clusters) if len(c) > 1]
    if cluster_sizes:
        # The weight of each cluster depends on its size
        weights = np.array(cluster_sizes) / N
        # Compute the weighted average
        weigthed_average = np.average(cluster_sizes, weights=weights)
        # Since the index needs to go between 0 and 1, we need to divide between N
        # again
        utility = weigthed_average / N
        return utility
    else:
        return 0


def logistic(x, k, x0):
    """
    Logistic function
    
    See https://en.wikipedia.org/wiki/Logistic_function for
    its parameters
    """
    if x == 0:
        return 0
    else:
        return 1 / ( 1 + np.exp(-k * (x - x0)) )


def step(x, k, x0):
    """
    Step function
    
    Taken from http://stackoverflow.com/a/28892278/438386
    
    k is not needed but it's added here to have the same interface as
    the logistic function above
    """
    return 1. * (x > x0)


def set_seed(graph, parameters, reset=False):
    """Set initial seed of adopters"""
    # Set all adopters to 0
    if reset:
        for node_index in graph.nodes():
            node = graph.node[node_index]
            node['adopter'] = 0
    
    seed = np.round(len(graph.nodes()) * parameters['initial_seed'])
    initial_adopters = random.sample(graph.nodes(), int(seed))
        
    for node_index in initial_adopters:
        node = graph.node[node_index]
        node['adopter'] = 1


def compute_global_utility_activation_value(parameters):
    """
    Compute the first value of global utility that makes the
    reflexivity index greater than zero.

    This is the point at which reflexivity starts to be relevant
    in the difussion process (but very slightly at the beginning
    though)
    """
    step = 1e-6
    for global_utility in np.arange(0, parameters['critical_mass'], step):
        reflexivity_index = logistic(global_utility,
                                     parameters['activation_sharpness'],
                                     parameters['critical_mass'])
        if reflexivity_index > step and global_utility > 0.01:
            return global_utility


def load_parameters_from_file(param_file):
    """Load parameters of run_analysis.py saved as json files."""
    with open(param_file, 'r') as f:
        parameters = json.loads(f.read())
    return parameters


def get_values_from_compute_run(data, with_reflexivity, variable):
    """
    Get all values for a particular variable in data.

    data: A list of Pandas panels, which must be the result of
          compute_run.
    with_reflexivity: True or False, depending if we want
                      to get the values with or without
                      reflexivity.
    variable: Name of the variable we want to get values
              from. Possible variables are defined in
              evolution_step.

    Returns: A list of lists containing the values we want
             to get from compute_run.
    """
    if with_reflexivity:
        rx_field = 'rx'
    else:
        rx_field = 'no_rx'

    try:
        values = [list(d[rx_field][variable]) for d in data]
        return values
    except KeyError:
        print("Variable %s is not part of the collected data" % variable)


def mean_global_utility_series(data):
    """
    Get the mean time series of Ug for the data generated by compute_run.

    data: Contains the output of compute_run.

    Returns: A Numpy array where each value corresponds to the Ug mean
             in a given instant of time, computed for all generated
             runs.
    """
    # Get all values for the global utility
    Ug = get_values_from_compute_run(data, with_reflexivity=True,
                                     variable='global_utility')

    # Get a mean series for Ug
    Ug_mean = np.mean(np.array(Ug), axis=0)

    return Ug_mean


def compute_activation_time(data, parameters):
    """
    Get the time when adoption takes off because of reflexivity.

    data: Contains the output of compute_run.
    parameters: List of parameters found in all_parameters.py

    Returns: The approximate time when adption takes off.
    """
    # Compute mean global utility for all runs
    Ug_mean = mean_global_utility_series(data)

    # Get Ug activation value (i.e. value when adoption takes off
    # because of reflexivity)
    activation_value = compute_global_utility_activation_value(parameters)

    # Compute the activation time as the number of ticks before
    # Ug is greater than activation_value.
    activation_time = len(Ug_mean[Ug_mean < activation_value])

    return activation_time


def get_adopters_percentaje_upto_activation(data, parameters):
    """
    Get the percentaje of adopters up to point where global
    utility makes the reflexivity index greater than zero.

    data: Contains the output of compute_run.
    parameters: List of parameters found in all_parameters.py
    """
    # Get reflexivity activation time
    activation_time = compute_activation_time(data, parameters)

    # Get adopters
    adopters = get_values_from_compute_run(data, with_reflexivity=True,
                                           variable='adopters')

    # Get a mean series for adopters
    adopters_mean = np.mean(np.array(adopters), axis=0)

    # Get adopters up to activation
    adopters_upto_activation = np.sum(adopters_mean[:activation_time])

    # Get percentaje of adopters up to activation
    percentaje = adopters_upto_activation/parameters['number_of_consumers']

    return percentaje * 100


def get_max_adopters(data):
    """
    Get the mean maximum of adopters in a given run

    data: Contains the output of compute_run.
    """
    # Get adopters
    adopters = get_values_from_compute_run(data, with_reflexivity=True,
                                           variable='adopters')

    # Get the mean value in each time step for all runs
    mean_per_time = np.mean(np.array(adopters), axis=0)

    return np.max(mean_per_time)
