# Reflexivity in a diffusion of innovations model

Source code for the article "Reflexivity in a diffusion of innovations model"
by Carlos Cordoba and Cesar García-Díaz.


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
* Time delay distribution: $f(d)$


## How to run this code

1. Install Anaconda
2. Install `anaconda-project` with `conda install anaconda-project`.
3. Clone this repository and cd to its root.
4. Run in a system terminal (cmd.exe): `anaconda-project run` to
   install its dependencies (this code has only been tested on
   Windows).
5. Run `activate envs\default`
6. Set the model parameters for a given run in `all_parameters.py`.
7. Run `python run_analysis.py`
8. The results are several plots, a json file with the parameters of simulation
   and a csv file with the percentage of adopters when reflexivity is activated
   in the system. All are saved in a *Results* subdirectory in this same
   directory.
