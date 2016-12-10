#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 10:45:16 2016

@author: carlos
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_adopters(data, par_name, par_value, cumulative= False):
    """
    data contains the output of compute_run
    """
    if cumulative:
        data[0] = map(np.cumsum, data[0])
        data[1] = map(np.cumsum, data[1])

    sns.tsplot(data=data[0], condition='Without Reflexivity')
    sns.tsplot(data=data[1], color='m', condition='With Reflexivity')
    plt.title(r'$%s = %s$' % (par_name, str(par_value)), fontsize=15)
    plt.legend(loc='upper right', fontsize=13)
    plt.tick_params(axis='both', which='major', labelsize=13)
