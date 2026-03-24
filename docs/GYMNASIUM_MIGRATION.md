# Gymnasium Migration Summary

This document summarizes the migration from `gym`/`gym3` to `gymnasium` for the procgenAISC repository.

## Overview

The Python interface layer has been updated to use `gymnasium` (the maintained fork of OpenAI Gym) while keeping the C++ game code unchanged. The implementation maintains compatibility with `gym3` for the C interface layer.

## Key Changes

### 1. Dependencies (setup.py and environment.yml)
- **Removed**: `gym>=0.15.0,<1.0.0`
- **Added**: `gymnasium>=0.29.0`
- **Kept**: `gym3>=0.3.3,<1.0.0` (for C interface via CFFI)
- Updated version constraints to use ranges instead of pinned versions
- Updated Python requirement to `>=3.7,<3.10` (gymnasium compatibility)

### 2. Environment Registration (procgen/gym_registration.py)
- Changed from `gym.envs.registration.register` to `gymnasium.register`
- Removed gym3-specific wrappers (`ToGymEnv`, `ViewerWrapper`, `ExtractDictObWrapper`)
- Created `ProcgenGymnasiumEnv` wrapper class that:
  - Inherits from `gymnasium.Env`
  - Wraps `ProcgenGym3Env` (the vectorized environment)
  - Implements gymnasium's API: `reset()` returns `(obs, info)`, `step()` returns `(obs, reward, terminated, truncated, info)`
  - Supports `render_mode="rgb_array"` and `render_mode="human"`

### 3. Environment Interface (procgen/env.py)
- Kept `BaseProcgenEnv` inheriting from `gym3.libenv.CEnv` (C interface unchanged)
- Kept `ProcgenGym3Env` for direct vectorized environment access
- Updated `ProcgenEnv` function to return `ProcgenGym3Env` directly (removed `ToBaselinesVecEnv` wrapper)

### 4. Build System (procgen/build.py)
- Updated to import `gym3.libenv` for header directory
- Added optimization to skip rebuild if library already exists
- No changes to C++ build process

### 5. Example Scripts
- **procgen/examples/random_agent_gym.py**: Updated to use `gymnasium` API
  - Added `import procgen` before `import gymnasium` to ensure environments are registered
  - Updated to new gymnasium API with `(obs, info)` return from `reset()`
  - Updated to new gymnasium API with `(obs, reward, terminated, truncated, info)` return from `step()`

- **procgen/examples/random_agent_gym3.py**: Simplified to use direct `ProcgenGym3Env` API
  - Removed `gym3` utility dependencies
  - Uses numpy for random actions directly

### 6. Interactive Mode (procgen/interactive.py)
- Simplified `ProcgenInteractive` class (removed gym3.Interactive dependency)
- Basic save/load state support maintained
- Full pygame integration would require additional work

### 7. libenv Header (procgen/data/libenv/libenv.h)
- Created compatible libenv.h header for C++ compilation
- Matches gym3's libenv interface (version 1)
- Defines all necessary structs: `libenv_options`, `libenv_tensortype`, `libenv_buffers`

## Usage Examples

### Gymnasium Interface (Recommended)
```python
import procgen  # Required to register environments
import gymnasium as gym

env = gym.make('procgen-treechop-v0', render_mode='rgb_array')
obs, info = env.reset()

for _ in range(100):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        obs, info = env.reset()

env.close()
```

### Direct ProcgenGym3Env Interface
```python
from procgen import ProcgenGym3Env
import numpy as np

env = ProcgenGym3Env(num=1, env_name="treechop", distribution_mode="easy")
rew, obs, first = env.observe()

for _ in range(100):
    action = np.random.randint(0, 15, size=(1,), dtype=np.int32)
    env.act(action)
    rew, obs, first = env.observe()
    if first[0]:
        break
```

## Testing

Run the smoke test:
```bash
python test_treechop.py
```

Run examples:
```bash
python procgen/examples/random_agent_gym.py
python procgen/examples/random_agent_gym3.py
```

## What Changed vs What Stayed the Same

### Changed
- Python interface now uses `gymnasium` instead of `gym`
- Environment registration uses gymnasium's registry
- API signatures follow gymnasium conventions (terminated/truncated instead of done)
- Removed dependency on gym3 wrappers (`ToGymEnv`, etc.)

### Stayed the Same
- All C++ game code unchanged
- C interface (libenv) unchanged
- `gym3.libenv.CEnv` still used for C bindings (via CFFI)
- Vectorized environment implementation (`ProcgenGym3Env`)
- All game mechanics and environments
- State save/load functionality

## Notes

- The migration keeps `gym3` as a dependency specifically for its `libenv` C interface (CFFI-based)
- This is a pragmatic approach that avoids rewriting the C interface layer
- The C++ code continues to use the libenv interface without modifications
- For users, the main change is importing `gymnasium` instead of `gym` and using the updated API
