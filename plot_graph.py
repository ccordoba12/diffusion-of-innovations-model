# -*- coding: utf-8 -*-

"""
Plot graphs of the evolution of a network for the conceptual paper.
"""

from __future__ import division
import os.path as osp

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
import networkx as nx

from algorithm import generate_initial_conditions, evolution
from utilities import get_adopters, set_seed


CONSUMERS = 50

# Some possible colors to use for seeds and components
SEEDS_COLOR = '#259ae9'
COMPONENTS_COLORS = ['#ff8a00', '#af2294', "#e11c1c", "#2db500", '#3fc6f0']


# =============================================================================
# Main function
# =============================================================================
def plot_graph(graph, parameters, max_time=None):
    """
    Plot networkx graph after certain number of steps in the evolution
    of the algorithm.
    """
    if max_time is not None:
        # We don't need data here, but that's what evolution
        # returns
        data = evolution(graph, parameters, max_time)

    # Get adopters and non-adopters
    adopters = get_adopters(graph)
    non_adopters = list(set(range(CONSUMERS)) - set(adopters))

    # Get connected components of adopters
    subgraph_of_adopters = nx.subgraph(graph, adopters)
    components = list(nx.connected_components(subgraph_of_adopters))
    component_sizes = [len(c) for c in components]
    print(len(adopters), component_sizes)

    # Figure setup
    figsize = (5.5, 5.5)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    # Plot components
    for c in components:
        # Use a single color because it looks better.
        # color = COMPONENTS_COLORS[components.index(c)]
        nx.draw_shell(
            graph,
            ax = ax,
            node_size=180,
            nodelist=c,
            edgelist=[],
            node_color='#d84d8e',
            linewidths=0.5
        )

    # Plot non-adopters
    nx.draw_shell(
        graph,
        ax = ax,
        node_size=180,
        nodelist=non_adopters,
        edge_color= '#58687a',
        node_color='#d2d2d2',
        linewidths=0.5,
        width=1,
    )

    # Set aspect ratio
    ax.set_aspect(1)

    # Remove borders around plot
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
                        hspace = 0, wspace = 0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    #labels = ['Adopters', 'Non-adopters']
    #patches = [mpatches.Patch(color=c, label=l) for c,l in zip(colors, labels)]
    #ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=5,
    #          fontsize=11, handlelength=0.7)

    # Draw edge around nodes
    for c in ax.collections:
        if isinstance(c, PathCollection):
            c.set_edgecolor('black')

    # Save figure
    if max_time is None:
        filename = osp.join('Results', 'graph.svg')
    else:
        filename = osp.join('Results', 'graph-' + str(max_time) + '.svg')
    fig.savefig(filename, bbox_inches='tight', pad_inches = 0)


# =============================================================================
# Plot generation
# =============================================================================
# Parameters for the simulation
parameters = dict(
    number_of_consumers = CONSUMERS,
    social_influence = 0.3,
    randomness = 0.3,
    activation_sharpness = 30,
    level = 1,
    quality = 0.5,
    initial_seed = 0.1,
    critical_mass = 0.5,
    number_of_neighbors = 3,
    marketing_effort = 0.03,
    graph_type = 'small_world',
    use_time_delays = True,
    time_delays_distro = [(15, 0.3), (25, 0.4), (35, 0.3)],
    reflexivity=True
)

# Graph to plot
graph = generate_initial_conditions(parameters)

# Print number of components
global_components = len(list(nx.connected_components(graph)))
print('Number of global components = ' + str(global_components))

# Set seed of adopters
set_seed(graph, parameters)

# Generate plots
plot_graph(graph, parameters)  # At startup
plot_graph(graph, parameters, max_time=15)  # At 15
plot_graph(graph, parameters, max_time=35)  # At 35
