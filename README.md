# Goal Misgeneralization in Procgen

This is a fork of the modified [procgen benchmark](https://github.com/openai/procgen) repo that implements modifications for the paper [Goal Misgeneralization in Deep Reinforcement Learning](https://github.com/JacobPfau/procgenAISC/tree/master). The original repo was forked from [original repo](https://github.com/openai/procgen). 

I am building on this repo to replicate the tree gridworld environment described in [this paper by Shah et al 2022](https://arxiv.org/abs/2210.01790).

# Game mechanic description/steps

When treechopper collides with a tree, the tree should turn into a tree stump and the treechopper should be rewarded with 1, then the treestump should be decorative and disappear after 10 seconds (this variant means the agent will also have to learn to not interact with treestumps).

The trees should only appear at a given regrowth rate.
They should appear randomly in the grid and not fly in from the side.

## Descriptions of the modified environments

* `coinrun_aisc`: Like `coinrun`, but the coin is placed randomly on ground level instead of at the far right end.
* `coinrun`: Added a flag `--random_percent`, which places the coin randomly in a given percentage of environments. Default 0.
* `heist_aisc_many_chests`: A heavily modified `heist`. Doors are now 'chests' (they do not prevent the agent from passing). Every key can open every chest. The agent is rewarded for opening chests. This version generates twice as many chests as keys. 
* `heist_aisc_many_keys`: Same as `heist_aisc_many_chests`, but instead has twice as many keys as chests.
* `maze_aisc`: Like maze, but the cheese is always to be found in the top right corner.
* `maze_yellowgem`: like maze, but the goal is a yellow gem.
* `maze_redgem_yellowstar`: like maze, but two objects are placed in the maze: a red gem, and a yellow star. The objective is the red gem.
* `maze_yellowstar_redgem`: Identical to `maze_yellowstar_redgem`, but the objective is instead the yellow star.


For both 'Keys and Chests' environments we added two options:
* `--key_penalty`: integer. Every time the agent picks up a key it loses `options.key_penalty / 10` reward.
* `--step_penalty`: integer time penalty. Each step, `options.step_penalty / 1000` is subtracted from the reward.

For more information on the standard environments see the original repository.

## Installation

Below we reproduce the instructions to install from source, copied from the [original repo](https://github.com/openai/procgen).

---

First make sure you have a supported version of python:

```
# run these commands to check for the correct python version
python -c "import sys; assert (3,6,0) <= sys.version_info <= (3,9,0), 'python is incorrect version'; print('ok')"
python -c "import platform; assert platform.architecture()[0] == '64bit', 'python is not 64-bit'; print('ok')"
```

If you want to change the environments or create new ones, you should build from source.  You can get miniconda from https://docs.conda.io/en/latest/miniconda.html if you don't have it, or install the dependencies from [`environment.yml`](environment.yml) manually.  On Windows you will also need "Visual Studio 15 2017" installed.

```
git clone git@github.com:openai/procgen.git
cd procgen
conda env update --name procgen --file environment.yml
conda activate procgen
pip install -e .
# this should say "building procgen...done"
python -c "from procgen import ProcgenGym3Env; ProcgenGym3Env(num=1, env_name='coinrun')"
# this should create a window where you can play the coinrun environment
python -m procgen.interactive
```

The environment code is in C++ and is compiled into a shared library exposing the [`gym3.libenv`](https://github.com/openai/gym3/blob/master/gym3/libenv.h) C interface that is then loaded by python.  The C++ code uses [Qt](https://www.qt.io/) for drawing.
