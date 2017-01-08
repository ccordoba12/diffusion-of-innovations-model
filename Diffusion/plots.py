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
    no_rx_data = [d['adopters'] for d in data['no_rx']]
    rx_data = [d['adopters'] for d in data['rx']]

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


def plot_global_utility(data, axis, activation_value, max_time):
    """
    Plot global utility against time.

    data: Contains the output of compute_run.
    axis: Matplotlib axis to add this plot to.
    activation_value: First global utility value for which the
                      reflexivity index is greater than zero.
    max_time: Max simulation time.
    """
    rx_data = [d['global_utility'] for d in data['rx']]

    axis.yaxis.grid(False)
    axis.set_ylabel('$U_G$')

    plt.setp(axis.get_xticklabels(), visible=False)
    plt.setp(axis.get_yticklabels(), visible=False)
    plt.setp(axis.yaxis.get_majorticklines(), visible=False)
    plt.setp(axis.yaxis.get_minorticklines(), visible=False)

    sns.tsplot(data=rx_data, color=sns.xkcd_rgb["medium green"], ax=axis)
    plt.plot([activation_value] * max_time, '--', linewidth=1, color='0.5')


def multiplot_adopters(data, par_name, par_values, cumulative, filename):
    """
    Plot several adopter graphs in the same plot.

    data: data of compute_run.
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

    f, axes = plt.subplots(2, 2, figsize=figsize, sharex=True, sharey=True)

    for ax, d, v in zip(axes.flat, data, par_values):
        plot_adopters(data=d,
                      par_name=par_name,
                      par_value=v,
                      axis=ax,
                      fontsize=fontsize,
                      cumulative=cumulative)

    f.tight_layout()
    f.savefig(filename, dpi=f.dpi)


def multiplot_adopters_and_global_utility(data, par_name, par_values,
                                          activation_value, cumulative,
                                          filename, max_time):
    """
    Plot adopters and global utility in the same graph.

    data: data of compute_run.
    par_name: Name of the main parameter that we are varying in the simulation.
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
    outer_grid = gridspec.GridSpec(2, 2, hspace=0.15)

    # Default value for adopters top_ylim plots
    # (This is here to avoid linting complaints)
    top_ylim = 0

    for i, d, v in zip(range(4), data, par_values):
        inner_grid = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=outer_grid[i],
                                                      height_ratios=[1, 2.6],
                                                      hspace=0.02)
        ax_top = plt.Subplot(fig, inner_grid[0])
        ax_adopters = plt.Subplot(fig, inner_grid[1])

        # Set ylim for adopters plot
        if i > 0:
            ax_adopters.set_ylim(top=top_ylim)

        # Set tick marks per plot
        if i == 0 or i == 1:
            plt.setp(ax_adopters.get_xticklabels(), visible=False)
        if i == 1 or i == 3:
            plt.setp(ax_adopters.get_yticklabels(), visible=False)

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
                            max_time=max_time)

        # Save top ylim of the first plot to use it for the
        # rest
        if i == 0:
            top_ylim = ax_adopters.get_ylim()[1]

    fig.savefig(filename, dpi=fig.dpi)
