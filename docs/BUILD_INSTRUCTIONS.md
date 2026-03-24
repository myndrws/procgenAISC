# Build Instructions for pybind11 Migration

This document provides instructions for building Procgen with the new pybind11 bindings.

## Prerequisites

### System Requirements
- Python 3.7+
- CMake 3.10+
- C++ compiler (gcc, clang, or MSVC)
- Qt5 (for rendering)

### Python Dependencies
```bash
pip install pybind11>=2.11.0 numpy>=1.17.0 gymnasium>=0.29.0
```

Or use conda:
```bash
conda env create -f environment.yml
conda activate procgen
```

## Building from Source

### Option 1: In-place Build (for development)

```bash
# Install dependencies
pip install pybind11 numpy gymnasium

# Build the extension in-place
python setup.py build_ext --inplace

# Test the build
python test_pybind11_migration.py
```

### Option 2: Full Installation

```bash
# Install dependencies
pip install pybind11 numpy gymnasium

# Build and install
pip install -e .

# Test the installation
python test_pybind11_migration.py
```

### Option 3: Manual CMake Build

```bash
cd procgen
mkdir -p .build/release
cd .build/release

# Configure
cmake -DCMAKE_BUILD_TYPE=Release ../..

# Build
cmake --build . --config Release

# The built extension will be in .build/release/
```

## Verifying the Build

### Quick Test

```python
import gymnasium as gym

# Create environment
env = gym.make('procgen-coinrun-v0')

# Test Gymnasium API
obs, info = env.reset(seed=42)
print(f"Observation shape: {obs.shape}")

# Take a step
obs, reward, terminated, truncated, info = env.step(0)
print(f"Reward: {reward}, Done: {terminated}")

env.close()
```

### Full Test Suite

```bash
python test_pybind11_migration.py
```

This will run comprehensive tests covering:
- Import verification
- Environment creation
- Gymnasium API compliance
- State save/load
- Multiple game variants

## Troubleshooting

### pybind11 Not Found

**Error**: `Could not find pybind11`

**Solution**:
```bash
pip install "pybind11[global]"
# Or specify pybind11 location:
export pybind11_DIR=/path/to/pybind11/share/cmake/pybind11
```

### Qt5 Not Found

**Error**: `Could not find Qt5`

**Solution (Linux)**:
```bash
sudo apt-get install qtbase5-dev
```

**Solution (macOS)**:
```bash
brew install qt5
export CMAKE_PREFIX_PATH="/usr/local/opt/qt5"
```

**Solution (conda)**:
```bash
conda install qt=5.12.5
```

### procgen_bindings Import Error

**Error**: `ImportError: cannot import name 'ProcgenVecEnv' from 'procgen.procgen_bindings'`

**Cause**: The C++ extension hasn't been built yet.

**Solution**: Build the extension:
```bash
python setup.py build_ext --inplace
```

### CMake Version Too Old

**Error**: `CMake 3.10 or higher is required`

**Solution (pip)**:
```bash
pip install --upgrade cmake
```

**Solution (conda)**:
```bash
conda install cmake>=3.14
```

### Compiler Errors

**Error**: Compilation errors in C++ code

**Common causes**:
1. Qt5 headers not found
2. C++17 not supported by compiler
3. Missing system libraries

**Solution**:
- Ensure Qt5 is installed
- Use a recent compiler (gcc 7+, clang 5+, MSVC 2017+)
- Check CMake output for specific missing dependencies

## Platform-Specific Notes

### Linux

Should work out of the box with standard build tools:
```bash
sudo apt-get install build-essential cmake qtbase5-dev
pip install pybind11 numpy gymnasium
python setup.py build_ext --inplace
```

### macOS

May need to specify Qt location:
```bash
brew install qt5 cmake
export CMAKE_PREFIX_PATH="/usr/local/opt/qt5"
pip install pybind11 numpy gymnasium
python setup.py build_ext --inplace
```

### Windows

Requires Visual Studio 2017 or later:
```bash
# In Visual Studio Command Prompt:
pip install pybind11 numpy gymnasium
python setup.py build_ext --inplace
```

Qt5 must be in CMAKE_PREFIX_PATH or installed via conda.

## Next Steps

After successful build:

1. Run tests: `python test_pybind11_migration.py`
2. Try examples: `python procgen/examples/random_agent_gym.py`
3. Use with Gymnasium: `import gymnasium as gym; env = gym.make('procgen-coinrun-v0')`

## Migration from gym3

If you have existing code using the gym3-based implementation:

### Old Code (gym3-based)
```python
from procgen.env import ProcgenEnv

env = ProcgenEnv(num_envs=1, env_name='coinrun')
env.act(np.array([action], dtype=np.int32))
rew, obs_dict, first = env.observe()
```

### New Code (pybind11 + Gymnasium)
```python
import gymnasium as gym

env = gym.make('procgen-coinrun-v0')
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(action)
```

Key differences:
- `reset()` returns `(obs, info)` instead of just `obs`
- `step()` returns 5 values: `(obs, reward, terminated, truncated, info)`
- Use `terminated` for natural episode end, `truncated` for time limits
- Seeding via `reset(seed=...)` not `env.seed()`

See https://gymnasium.farama.org/introduction/migration_guide/ for full migration guide.

## Support

If you encounter issues:

1. Check this document for common problems
2. Run `python test_pybind11_migration.py` for diagnostics
3. Check build logs in `procgen/.build/`
4. Open an issue with:
   - Error message
   - Platform/OS
   - Python version
   - Build command used
   - CMake/compiler output
