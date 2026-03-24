# TreeChop for Goal Misgeneralisation with Procgen

This is a fork of the modified [procgen benchmark](https://github.com/openai/procgen) repo that implements modifications for the paper [Goal Misgeneralization in Deep Reinforcement Learning](https://github.com/JacobPfau/procgenAISC/tree/master). The original repo was forked from [OpenAI's procgen benchmark repo](https://github.com/openai/procgen).

I am building on this repo to replicate the tree gridworld environment described in [this paper by Shah et al 2022](https://arxiv.org/abs/2210.01790).

## ✅ Migration to Gymnasium Complete

**This repository has been successfully migrated from gym3 to pybind11 with full Gymnasium API support.**

- 🎯 Modern, maintained dependencies (pybind11, Gymnasium)
- 🚀 Zero-copy numpy buffer sharing for performance
- 📦 Full Gymnasium API compliance
- ✨ Compatible with modern RL frameworks (Stable-Baselines3, etc.)

See [docs/MIGRATION_COMPLETE.md](docs/MIGRATION_COMPLETE.md) for full migration details.

### Quick Start with Gymnasium

```python
import gymnasium as gym

# Create environment
env = gym.make('procgen-treechop-v0', render_mode='rgb_array')

# Reset and interact
obs, info = env.reset(seed=42)
for _ in range(100):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()

env.close()
```

# TreeChop game mechanic 

The treechopper chops down trees, and these respawn at a given rate, in a single never-ending procgen episode. I have built this environment based on the description by [Shah et al 2022](https://arxiv.org/abs/2210.01790):

>Environment: 10 × 10 gridworld with entities (initially): agent, 10 trees. The agent is provided the
full gridworld as a 12 × 12 × 2 one-hot encoded image in its observations. Chopping a tree provides
+1 reward. If there are fewer than 10 trees, the probability of a new tree spawning at a random empty
location is given by:
r = max(rmin, rmax × log(1 + ncurrent)/ log(1 + nmax))
where rmin and rmax are the minimum and maximum respawn rates, and ncurrent and nmax are the
current and maximum number of trees. In the experiment shown in Figure 3 we set rmin = 10−6
, rmax = 0.3, and nmax = 10. 

I have also currently included a 'recovery period' where the trees do not respawn immediately; if this is absent, trees respawn at a rate faster than which the agent can get to them to chop them down. As an extension, the game may also be modified to include treestumps as a non-rewarding distraction.

## Running

You will need the requirements specified in the forked repos to install procgen. Then, you will be able to run TreeChop with the following:

`python -m procgen.interactive --env-name treechop --distribution-mode easy
`

## Demo of the tree gridworld TreeChop

https://github.com/myndrws/procgenAISC/assets/24572054/05c8c88d-bc78-4e8d-96d6-52d785493d81

## Documentation

- 📚 [Migration Complete](docs/MIGRATION_COMPLETE.md) - Full details of gym3 → pybind11 migration
- 🔧 [Build Instructions](docs/BUILD_INSTRUCTIONS.md) - Detailed build and troubleshooting guide
- 📋 [Migration Plan](docs/PYBIND11_MIGRATION_PLAN.md) - Original migration strategy
- 📝 [Gymnasium Migration](docs/GYMNASIUM_MIGRATION.md) - Gymnasium API implementation notes
- 🧪 [Testing Guide](tests/README.md) - How to run the test suite
- 📄 [Changes](docs/CHANGES.md) - Version history and modifications
- 🤝 [Contributing](docs/CONTRIBUTING.md) - How to contribute

## Testing

Run the test suite to verify your installation:

```bash
# Test basic functionality
uv run tests/test_treechop_functional.py

# Test Gymnasium interface
uv run tests/test_gymnasium_simple.py
uv run tests/test_gymnasium_render.py

# Full smoke tests
uv run tests/test_smoke_gymnasium_only.py
```

All tests should pass with exit code 0.

----------------------------------------------

# README from the original forked repos

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

### Requirements

- Python 3.9 (64-bit)
- CMake 3.10+
- Qt5 development libraries
- pybind11 2.11.0+
- Gymnasium 0.26.0+

### Install from Source

```bash
# Clone the repository
git clone https://github.com/myndrws/procgenAISC.git
cd procgenAISC

# Create conda environment
conda env update --name procgen --file environment.yml
conda activate procgen

# Build and install
pip install -e .

# Test the installation
python -c "import gymnasium as gym; env = gym.make('procgen-treechop-v0'); print('✓ Installation successful!')"

# Run interactive mode
python -m procgen.interactive --env-name treechop --distribution-mode easy
```

### Architecture

The environment code is in C++ and compiled into a shared library (`libenv.so`) using pybind11. The Python bindings expose the `ProcgenVecEnv` class which wraps the C++ `VecGame` implementation. The Gymnasium wrapper (`procgen_gymnasium_env.py`) provides a standard RL interface. Qt5 is used for rendering.

For detailed build instructions, see [docs/BUILD_INSTRUCTIONS.md](docs/BUILD_INSTRUCTIONS.md).
