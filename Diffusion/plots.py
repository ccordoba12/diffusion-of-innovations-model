#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 10:45:16 2016

@author: carlos
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_adopters(data, par_name, par_value, axis=None, cumulative=False,
                  fontsize=15):
    """
    data contains the output of compute_run
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
        axis.legend(loc='upper right', fontsize=fontsize-2)
        axis.tick_params(axis='both', which='major', labelsize=fontsize-2)
    else:
        sns.tsplot(data=no_rx_data, condition='Without Reflexivity')
        sns.tsplot(data=rx_data, color='m', condition='With Reflexivity')
        plt.title(r'$%s = %s$' % (par_name, str(par_value)), fontsize=fontsize)
        plt.legend(loc='upper right', fontsize=fontsize-2)
        plt.tick_params(axis='both', which='major', labelsize=fontsize-2)
