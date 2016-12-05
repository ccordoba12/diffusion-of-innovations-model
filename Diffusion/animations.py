#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 12:31:43 2016

@author: carlos
"""

import networkx as nx

from algorithm import evolution_step


def set_colors(graph):
    """
    Create a list of colors to apply to graph
    
    Adopters are blue and non-adopters are red
    """
    colors = []
    for n in graph.nodes():
        node = graph.node[n]
        if node['adopter'] == 1:
            colors.append('b')
        else:
            colors.append('r')
    
    return colors


def draw_graph(graph, node_positions):
    """Function to draw the graph in which the evolution is occurring"""
    nx.draw_networkx_nodes(graph, node_positions, node_color=set_colors(graph),
                           node_size=50)
    nx.draw_networkx_edges(graph, node_positions, width=0.3, alpha=0.5)


def animate(i, graph, node_positions, parameters, test=False):
    """Function to animate the algorithm evolution"""
    #print(i)
    if test:
        node = graph.node[i]
        node['adopter'] = 1
    else:
        evolution_step(graph, parameters)
    draw_graph(graph, node_positions)
