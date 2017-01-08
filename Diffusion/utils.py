# -*- coding: utf-8 -*-

"""
Utility functions for the algorithm
"""

from __future__ import division

import random

import networkx as nx
import numpy as np


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
    for global_utility in np.arange(0, 0.5, 0.01):
        reflexivity_index = logistic(global_utility,
                                     parameters['activation_sharpness'],
                                     parameters['critical_mass'])
        if reflexivity_index > 0.005:
            return global_utility
