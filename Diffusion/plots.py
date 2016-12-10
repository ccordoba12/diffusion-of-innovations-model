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
    if cumulative:
        data[0] = map(np.cumsum, data[0])
        data[1] = map(np.cumsum, data[1])

    if axis:
        sns.tsplot(data=data[0], condition='Without Reflexivity', ax=axis)
        sns.tsplot(data=data[1], color='m', condition='With Reflexivity',
                   ax=axis)
        axis.set_title(r'$%s = %s$' % (par_name, str(par_value)),
                       fontsize=fontsize)
        axis.legend(loc='upper right', fontsize=fontsize-2)
        axis.tick_params(axis='both', which='major', labelsize=fontsize-2)
    else:
        sns.tsplot(data=data[0], condition='Without Reflexivity')
        sns.tsplot(data=data[1], color='m', condition='With Reflexivity')
        plt.title(r'$%s = %s$' % (par_name, str(par_value)), fontsize=fontsize)
        plt.legend(loc='upper right', fontsize=fontsize-2)
        plt.tick_params(axis='both', which='major', labelsize=fontsize-2)
