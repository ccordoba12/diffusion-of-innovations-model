#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 10:45:16 2016

@author: carlos
"""

import os

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from utils import (compute_global_utility_activation_value,
                   get_values_from_compute_run)


if not os.name == 'nt':
    matplotlib.rc('text', usetex=True)

sns.set_style("whitegrid")


def plot_adopters(data, par_name, par_value, axis=None, cumulative=False,
                  fontsize=15):
    """
    Plot number of adopters against time.

    data: contains the output of compute_run.
    par_name: Parameter name that we're varying in the simulation.
    par_value: Parameter value that we're varying in the simulation.
    axis: Matplotlib axis to add this plot (if any).
    cumulative: Whether to plot the cumulative number of adopters or not
    fontsize: Font size for legends and tick marks.
    """
    no_rx_data = get_values_from_compute_run(data, with_reflexivity=False,
                                             variable='adopters')
    rx_data = get_values_from_compute_run(data, with_reflexivity=True,
                                          variable='adopters')

    if cumulative:
        no_rx_data = map(np.cumsum, no_rx_data)
        rx_data = map(np.cumsum, rx_data)

    if axis:
        sns.tsplot(data=no_rx_data, condition='Without Reflexivity', ax=axis)
        sns.tsplot(data=rx_data, color='m', condition='With Reflexivity',
                   ax=axis)
        axis.set_xlabel(r'$%s = %s$' % (par_name, str(par_value)),
                        fontsize=fontsize)
        axis.legend(loc='best', fontsize=fontsize-2)
        axis.tick_params(axis='both', which='major', labelsize=fontsize-2)
    else:
        sns.tsplot(data=no_rx_data, condition='Without Reflexivity')
        sns.tsplot(data=rx_data, color='m', condition='With Reflexivity')
        plt.title(r'$%s = %s$' % (par_name, str(par_value)), fontsize=fontsize)
        plt.legend(loc='best', fontsize=fontsize-2)
        plt.tick_params(axis='both', which='major', labelsize=fontsize-2)


def plot_adopters_type(data, par_name, par_value, axis, cumulative=False,
                       fontsize=15, with_reflexivity=False):
    """
    Plot number of type of adopters against time.

    with_reflexivity: Get data with or without reflexivity
    """
    utility = get_values_from_compute_run(data, with_reflexivity,
                                          variable='adopters_by_utility')
    marketing = get_values_from_compute_run(data, with_reflexivity,
                                            variable='adopters_by_marketing')

    if cumulative:
        utility = map(np.cumsum, utility)
        marketing = map(np.cumsum, marketing)

    sns.tsplot(data=utility, condition='Adopters by utility', ax=axis,
               color=sns.xkcd_rgb["tomato"])
    sns.tsplot(data=marketing, condition='Adopters by marketing',
               ax=axis, color=sns.xkcd_rgb["soft purple"])
    axis.set_xlabel(r'$%s = %s$' % (par_name, str(par_value)),
                    fontsize=fontsize)
    axis.legend(loc='best', fontsize=fontsize-2)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)


def plot_global_utility(data, axis, activation_value, max_time, fontsize):
    """
    Plot global utility against time.

    data: Contains the output of compute_run.
    axis: Matplotlib axis to add this plot to.
    activation_value: First global utility value for which the
                      reflexivity index is greater than zero.
    max_time: Max simulation time.
    """
    Ug_data = get_values_from_compute_run(data, with_reflexivity=True,
                                          variable='global_utility')

    axis.set_ylabel('$U_G$', fontsize=fontsize)

    plt.setp(axis.get_xticklabels(), visible=False)

    sns.tsplot(data=Ug_data, color=sns.xkcd_rgb["medium green"], ax=axis)
    plt.plot([activation_value] * max_time, '--', linewidth=1, color='0.4')
    axis.tick_params(labelsize=fontsize-2)


def multiplot_variable(multiple_data, plot_func, par_name, par_values,
                       cumulative, filename=None, **kwargs):
    """
    Plot several variable graphs in the same plot.

    multiple_data: List of data obtained by running compute_run
                   over each entry of set_of_params.
    par_name: Name of the main parameter that we are varying in the simulation.
    par_values: List of values for the main parameter.
                It can only contain 4 values.
    cumulative: Whether to plot cumulative curvers or not.
    filename: Name of the file to save this figure to.
    """
    if os.name == 'nt':
        figsize = (9, 9)
        fontsize = 11
    else:
        figsize = (10, 10)
        fontsize = 15

    fig, axes = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True)

    for ax, d, v in zip(axes.flat, multiple_data, par_values):
        plot_func(data=d,
                  par_name=par_name,
                  par_value=v,
                  axis=ax,
                  fontsize=fontsize,
                  cumulative=cumulative,
                  **kwargs)

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')


def multiplot_adopters_and_global_utility(multiple_data, set_of_params,
                                          par_name, par_values,
                                          cumulative, filename,
                                          max_time):
    """
    Plot adopters and global utility in the same graph.

    multiple_data: List of data obtained by running compute_run
                   over each entry of set_of_params.
    set_of_params: Set of parameters
    par_name: Name of the main parameter that we are varying in
              the simulation.
    par_values: List of values for the main parameter.
                It can only contain 4 values.
    activation_value: Global utility activation value.
    cumulative: Whether to plot cumulative adopters curvers or not.
    filename: Name of the file to save this figure to.
    max_time: Max time for the simulation.
    """
    if len(par_values) > 4:
        print("The parameter values list passed to this function "
              "can only contain 4 or less values.")
        return

    if os.name == 'nt':
        figsize = (9, 9)
        fontsize = 11
    else:
        figsize = (10, 10)
        fontsize = 15

    fig = plt.figure(figsize=figsize)

    # Grid of 2x2 plots
    outer_grid = gridspec.GridSpec(2, 2, hspace=0.18)

    # Default value for adopters top_ylim plots
    # (This is here to avoid linting complaints)
    top_ylim = 0

    for i, d, v, p in zip(range(4), multiple_data, par_values, set_of_params):
        inner_grid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_grid[i],
                                                      height_ratios=[1, 2.8],
                                                      hspace=0.08)
        ax_top = plt.Subplot(fig, inner_grid[0])
        ax_adopters = plt.Subplot(fig, inner_grid[1])

        # Set ylim for adopters
        if cumulative:
            max_consumers = max([parameters['number_of_consumers']
                                for parameters in set_of_params])
            ax_adopters.set_ylim(top=max_consumers)
        else:
            if i > 0:
                ax_adopters.set_ylim(top=top_ylim)

        # Set ylim and yticks for top axis
        ax_top.set_ylim(top=1)
        ax_top.set_yticks([0, 0.5, 1])

        # Set tick marks per plot
        if i == 0 or i == 1:
            plt.setp(ax_adopters.get_xticklabels(), visible=False)
        if i == 1 or i == 3:
            plt.setp(ax_adopters.get_yticklabels(), visible=False)
        if i == 0 or i == 2:
            plt.setp(ax_top.get_yticklabels(), visible=False)

        # Global utility activation value
        activation_value = compute_global_utility_activation_value(p)

        fig.add_subplot(ax_adopters)
        fig.add_subplot(ax_top, sharex=ax_adopters)

        plot_adopters(data=d,
                      par_name=par_name,
                      par_value=v,
                      axis=ax_adopters,
                      fontsize=fontsize,
                      cumulative=cumulative)

        plot_global_utility(data=d,
                            axis=ax_top,
                            activation_value=activation_value,
                            max_time=max_time,
                            fontsize=fontsize)

        # Adjustments to top plots
        if i == 1 or i == 3:
            ax_top.set_ylabel('')
            ax_top.tick_params(pad=15)

        # Save top ylim of the first plot to use it for the
        # rest
        if i == 0 and not cumulative:
            top_ylim = ax_adopters.get_ylim()[1]

    fig.savefig(filename, dpi=300, bbox_inches='tight')
