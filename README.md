# Reflexivity in a diffusion of innovations model

This code tries to replicate the diffusion of innovations model present in

> *Diffusion dynamics in small-world networks with heterogeneous consumers*
from Delre, Sebastiano A., Jager, Wander and Janssen, Marco A.,
Computational and Mathematical Organization Theory, **13**, 2, 2007.

with some modifications.

It also adds new features that try to introduce reflexivity on it.


## Parameters

These are the parameters that control the evolution of the algorithm, and their
corresponding variables in the article:

* Network randomness: $r$
* Average number of neighbors: $k$
* Initial proportion (or seed) of adopters: $\delta$
* Coefficient of social influence: $\beta$
* Quality: $q$
* Total number of consumers: $N$
* Activation sharpness: $\phi$
* Critical mass of adopters: $M_{c}$
* Marketing effort: $e_{1}$
* Level: $L$


## How to run this model

1. Set model parameters for a given run in `all_parameters.py`.
2. Run `run_analysis.py`
3. The results are several plots, a json file with the parameters of simulation
   and a csv file with the percentage of adopters when reflexivity is activated
   in the system. All are saved in a *Results* subdirectory in this same
   directory.
