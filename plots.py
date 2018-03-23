#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 10:45:16 2016

@author: carlos
"""

from __future__ import division

import glob
import os
import os.path as osp

import numpy as np
import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import seaborn as sns

from utilities import (compute_activation_time, get_max_adopters,
                       get_values_from_compute_run)


if not os.name == 'nt':
    matplotlib.rc('text', usetex=True)

sns.set_style("whitegrid")


def plot_adopters(data, parameters, axis=None,
                  par_name=None, par_value=None,
                  cumulative=False, fontsize=15,
                  with_reflexivity=None,
                  with_activation_time=True,
                  ylim_bottom=None,
                  ylim_top=None,
                  filename=None):
    """
    Plot number of adopters against time.

    data: contains the output of compute_run.
    parameters: Parameters of the run.
    axis: Matplotlib axis to add this plot to.
    cumulative: Whether to plot the cumulative number of adopters or not
    fontsize: Font size for legends and tick marks.
    with_reflexivity: For compatibility with plot_adopters_type.
    with_activation_time: Wheter to plot activation time or not.
    ylim_bottom: Bottom y-axis limit.
    ylim_top: Top y-axis limit.
    filename: File name to save the plot to.
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

    if axis is None:
        figsize = (5.5, 5.5)
        fig = plt.figure(figsize=figsize)
        axis = fig.add_subplot(111)

    # Plots
    sns.tsplot(data=no_rx_data, condition='No Reflexivity', ax=axis)
    sns.tsplot(data=rx_data, color='m', condition='Reflexivity', ax=axis)
    if with_activation_time:
        axis.axvline(x=activation_time, linestyle='--', linewidth=1,
                     color='0.4')

    # Plot adjustments
    if par_name is not None and par_value is not None:
        axis.set_title(r'$%s = %s$' % (par_name, str(par_value)),
                       fontsize=fontsize)

    axis.set_xlabel('Time')
    axis.set_ylabel('N. of Adopters')

    # Y-axis limits
    if ylim_bottom is not None:
        axis.set_ylim(bottom=ylim_bottom)
    else:
        axis.set_ylim(bottom=0)
    if ylim_top is not None:
        axis.set_ylim(top=ylim_top)

    axis.legend(loc='best', fontsize=fontsize-2)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)

    if filename is not None:
        fig.savefig(filename, dpi=300, bbox_inches='tight')


def plot_adopters_type(data, parameters, axis=None,
                       par_name=None, par_value=None,
                       cumulative=False, fontsize=15,
                       with_reflexivity=True,
                       with_activation_time=True,
                       ylim_bottom=None,
                       ylim_top=None,
                       filename=None):
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
    ylim_bottom: Bottom y-axis limit.
    ylim_top: Top y-axis limit.
    filename: File name to save the plot to.
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

    # Create axis if it doesn't exist
    if axis is None:
        figsize = (5.5, 5.5)
        fig = plt.figure(figsize=figsize)
        axis = fig.add_subplot(111)

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
    axis.set_ylabel('N. of adopters')

    # Y-axis limits
    if ylim_bottom is not None:
        axis.set_ylim(bottom=ylim_bottom)
    else:
        axis.set_ylim(bottom=0)
    if ylim_top is not None:
        axis.set_ylim(top=ylim_top)

    axis.legend(loc='best', fontsize=fontsize-2)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)

    if filename is not None:
        fig.savefig(filename, dpi=300, bbox_inches='tight')


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
    cumulative: Whether to plot cumulative curvers or not.
    filename: Name of the file to save this figure to.
    """
    nvalues = len(par_values)
    fontsize = 11

    # Figure size
    if nvalues == 4:
        figsize = (8.5, 8.5)
    else:
        figsize = (16, 8.5)

    # Number of rows
    if nvalues < 9:
        nrows = 2
    else:
        nrows = 3

    # Number of columns
    if nvalues == 4:
        ncols = 2
    else:
        ncols = int(np.ceil(nvalues/nrows))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize,
                             sharex=True, sharey=True)

    if cumulative:
        max_consumers = [parameters['number_of_consumers']
                         for parameters in set_of_params]
        ylim_top = max(max_consumers)
    else:
        max_adopters = max([get_max_adopters(d) for d in multiple_data])
        ylim_top = round(max_adopters) + 10

    for ax, d, v, p in zip(axes.flat, multiple_data, par_values, set_of_params):
        plot_func(data=d,
                  parameters=p,
                  axis=ax,
                  par_name=par_name,
                  par_value=v,
                  fontsize=fontsize,
                  cumulative=cumulative,
                  ylim_top=ylim_top,
                  **kwargs)

    # Adjustments to plots
    for ax in axes[0]:
        ax.set_xlabel('')
    for ax in axes[:,1]:
        ax.set_ylabel('')

    # Hide last plot is nvalues is even
    if nvalues % 2 == 1:
        last_ax = axes.flat[-1]
        last_ax.set_visible(False)

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


def plot_saddle_points_presence(csv_file, axis=None, with_legend=True):
    """
    Plot a heatmap of Beta vs. q that shows the presence
    or absence of saddle points.

    cvs_file: File that contains the saddle point observations.
    """
    fontsize = 15
    figsize = (5.5, 5.5)

    if axis is None:
        fig = plt.figure(figsize=figsize)
        axis = fig.add_subplot(111)

    # Loading the csv file with the data to be plotted
    df = pd.read_csv(csv_file)
    df = df.set_index('index')

    # Heatmap
    sns.heatmap(df, cbar=False, square=True, cmap="YlGnBu", linewidths=0.06,
                xticklabels=2, yticklabels=2, vmax=1.9, center=0.5, ax=axis)

    # Adjustments
    fname = csv_file.split(osp.sep)[-1]
    title = osp.splitext(fname)[0]
    axis.set_title(title, fontsize=fontsize)
    axis.set_xlabel(r'$\beta$', fontsize=fontsize-1)
    axis.set_ylabel(r'$q$', fontsize=fontsize-1)
    axis.tick_params(axis='both', which='major', labelsize=fontsize-2)

    # Legend
    if with_legend:
        collections = axis.collections[0]
        colors = np.unique(collections.get_facecolors(), axis=0)
        labels = ['Saddle points', 'Bending point', 'No saddle points']
        patches = [mpatches.Patch(color=c, label=l) for c,l in zip(colors, labels)]
        axis.legend(handles=patches, bbox_to_anchor=(1.02, 1), loc=2,
                    borderaxespad=0., fontsize=fontsize-1, handlelength=0.7)


def multiplot_saddle_points_presence(csv_dir):
    """Plot several saddle points presence plots"""
    # Create subplots
    figsize = (17, 5)
    fig, axes = plt.subplots(nrows=1, ncols=3,
                             figsize=figsize,
                             sharex=False, sharey=False,
                             gridspec_kw={'width_ratios': [5, 5, 5]})

    # Get file names to plot
    fnames = glob.glob(osp.join(csv_dir, '*.csv'))

    for ax, fn in zip(axes.flat, fnames):
        plot_saddle_points_presence(fn, axis=ax, with_legend=False)

    # Adjustments
    #for ax in axes.flat[1:]:
    #    ax.set_ylabel('')

    axis = axes.flat[-1]
    collections = axis.collections[0]
    colors = np.unique(collections.get_facecolors(), axis=0)
    labels = ['Saddle points', 'Bending point', 'No saddle points']
    patches = [mpatches.Patch(color=c, label=l) for c,l in zip(colors, labels)]
    axis.legend(handles=patches, bbox_to_anchor=(1.08, 1), loc=2,
                borderaxespad=0., fontsize=14, handlelength=0.7)

    fig.savefig(osp.join(csv_dir, 'saddle-points.png'), dpi=300,
                bbox_inches='tight')
