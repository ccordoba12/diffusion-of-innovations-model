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

from utils import compute_activation_time, get_values_from_compute_run


if not os.name == 'nt':
    matplotlib.rc('text', usetex=True)

sns.set_style("whitegrid")


def plot_adopters(data, parameters, axis,
                  par_name=None, par_value=None,
                  cumulative=False, fontsize=15):
    """
    Plot number of adopters against time.

    data: contains the output of compute_run.
    parameters: Parameters of the run.
    axis: Matplotlib axis to add this plot to.
    cumulative: Whether to plot the cumulative number of adopters or not
    fontsize: Font size for legends and tick marks.
    """
    # Data to plot
    no_rx_data = get_values_from_compute_run(data, with_reflexivity=False,
                                             variable='adopters')
    rx_data = get_values_from_compute_run(data, with_reflexivity=True,
                                          variable='adopters')
    activation_time = compute_activation_time(data, parameters)

    if cumulative:
        no_rx_data = map(np.cumsum, no_rx_data)
        rx_data = map(np.cumsum, rx_data)

    # Plots
    sns.tsplot(data=no_rx_data, condition='No Reflexivity', ax=axis)
    sns.tsplot(data=rx_data, color='m', condition='Reflexivity', ax=axis)
    axis.axvline(x=activation_time, linestyle='--', linewidth=1, color='0.4')

    # Plot adjustments
    if par_name is not None and par_value is not None:
        axis.set_title(r'$%s = %s$' % (par_name, str(par_value)),
                       fontsize=fontsize)
    axis.set_xlabel('Time')
    axis.set_ylabel('No. of Adopters')
    axis.set_ylim(bottom=0)
    axis.legend(loc='best', fontsize=fontsize-2)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)


def plot_adopters_type(data, parameters, axis,
                       par_name=None, par_value=None,
                       cumulative=False, fontsize=15,
                       with_reflexivity=True,
                       with_activation_time=True):
    """
    Plot number of type of adopters against time.

    data: Contains the output of compute_run.
    parameters: Parameters of the run.
    axis: Matplotlib axis to add this plot to.
    par_name: Parameter name that we're varying in the simulation.
    par_value: Parameter value that we're varying in the simulation.
    cumulative: Whether to plot the cumulative number of adopters or not.
    fontsize: Font size for legends and tick marks.
    with_reflexivity: Get data with or without reflexivity.
    with_activation_time: Wheter to plot activation time or not.
    """
    # Data to plot
    utility = get_values_from_compute_run(data, with_reflexivity,
                                          variable='adopters_by_utility')
    marketing = get_values_from_compute_run(data, with_reflexivity,
                                            variable='adopters_by_marketing')
    activation_time = compute_activation_time(data, parameters)

    if cumulative:
        utility = map(np.cumsum, utility)
        marketing = map(np.cumsum, marketing)

    # Plots
    sns.tsplot(data=utility, condition='Utility', ax=axis,
               color=sns.xkcd_rgb["tomato"])
    sns.tsplot(data=marketing, condition='Marketing',
               ax=axis, color=sns.xkcd_rgb["soft purple"])
    if with_activation_time:
        axis.axvline(x=activation_time, linestyle='--', linewidth=1,
                     color='0.4')

    # Plot adjustments
    if par_name is not None and par_value is not None:
        axis.set_title(r'$%s = %s$' % (par_name, str(par_value)),
                       fontsize=fontsize)
    axis.set_xlabel('Time')
    axis.set_ylabel('No. of adopters')
    axis.set_ylim(bottom=0)
    axis.legend(loc='best', fontsize=fontsize-2)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)


def plot_global_utility(data, parameters, axis,
                        par_name=None, par_value=None,
                        fontsize=15):
    """
    Plot global utility against time.

    data: Contains the output of compute_run.
    parameters: Parameters of the run.
    axis: Matplotlib axis to add this plot to.
    par_name: Parameter name that we're varying in the simulation.
    par_value: Parameter value that we're varying in the simulation.
    fontsize: Font size for legends and tick marks.
    """
    # Data to plot
    Ug_data = get_values_from_compute_run(data, with_reflexivity=True,
                                          variable='global_utility')
    activation_time = compute_activation_time(data, parameters)

    # Plot adjustments
    if par_name is not None and par_value is not None:
        axis.set_title(r'$%s = %s$' % (par_name, str(par_value)),
                       fontsize=fontsize)
    axis.set_ylabel('$U_G$', fontsize=fontsize)
    axis.tick_params(labelsize=fontsize-2)
    plt.setp(axis.get_xticklabels(), visible=False)

    # Plots
    sns.tsplot(data=Ug_data, color=sns.xkcd_rgb["medium green"], ax=axis)
    axis.axvline(x=activation_time, linestyle='--', linewidth=1, color='0.4')


def multiplot_variable(plot_func, multiple_data, set_of_params, par_name,
                       par_values, cumulative, filename=None, **kwargs):
    """
    Plot several variable graphs in the same plot.

    plot_func: Plot function to use.
    multiple_data: List of data obtained by running compute_run
                   over each entry of set_of_params.
    set_of_params: Set of parameters.
    par_name: Name of the main parameter that we are varying in the simulation.
    par_values: List of values for the main parameter.
                It can only contain 4 values.
    cumulative: Whether to plot cumulative curvers or not.
    filename: Name of the file to save this figure to.
    """
    figsize = (8.5, 8.5)
    fontsize = 11

    fig, axes = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True)

    for ax, d, v, p in zip(axes.flat, multiple_data, par_values, set_of_params):
        plot_func(data=d,
                  parameters=p,
                  axis=ax,
                  par_name=par_name,
                  par_value=v,
                  fontsize=fontsize,
                  cumulative=cumulative,
                  **kwargs)

    # Adjustments to plots
    for ax in axes[0]:
        ax.set_xlabel('')
    for ax in axes[:,1]:
        ax.set_ylabel('')

    if filename:
        fig.savefig(filename, dpi=300, bbox_inches='tight')


def multiplot_adopters_and_global_utility(multiple_data, set_of_params,
                                          par_name, par_values,
                                          cumulative, filename):
    """
    Plot adopters and global utility in the same graph.

    multiple_data: List of data obtained by running compute_run
                   over each entry of set_of_params.
    set_of_params: Set of parameters.
    par_name: Name of the main parameter that we are varying in
              the simulation.
    par_values: List of values for the main parameter.
                It can only contain 4 values.
    activation_value: Global utility activation value.
    cumulative: Whether to plot cumulative adopters curvers or not.
    filename: Name of the file to save this figure to.
    """
    if len(par_values) > 4:
        print("The parameter values list passed to this function "
              "can only contain 4 or less values.")
        return

    figsize = (9, 9)
    fontsize = 11

    fig = plt.figure(figsize=figsize)

    # Grid of 2x2 plots
    outer_grid = gridspec.GridSpec(2, 2, hspace=0.18)

    # Default value for adopters top_ylim plots
    # (This is here to avoid linting complaints)
    top_ylim = 0

    for i, d, v, p in zip(range(4), multiple_data, par_values, set_of_params):
        inner_grid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_grid[i],
                                                      height_ratios=[1, 3.0],
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

        fig.add_subplot(ax_adopters)
        fig.add_subplot(ax_top, sharex=ax_adopters)

        plot_adopters(data=d,
                      parameters=p,
                      axis=ax_adopters,
                      fontsize=fontsize,
                      cumulative=cumulative)

        plot_global_utility(data=d,
                            parameters=p,
                            axis=ax_top,
                            par_name=par_name,
                            par_value=v,
                            fontsize=fontsize)

        # Adjustments to plots
        if i == 0 or i == 1:
            ax_adopters.set_xlabel('')
        if i == 1 or i == 3:
            ax_top.set_ylabel('')
            ax_top.tick_params(pad=15)
            ax_adopters.set_ylabel('')

        # Save top ylim of the first plot to use it for the
        # rest
        if i == 0 and not cumulative:
            top_ylim = ax_adopters.get_ylim()[1]

    fig.savefig(filename, dpi=300, bbox_inches='tight')
