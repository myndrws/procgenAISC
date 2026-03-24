# Procgen Test Suite

This directory contains the test suite for the pybind11-based Procgen implementation with Gymnasium integration.

## Test Files

### Core Functionality Tests

#### `test_treechop_minimal.py`
- **Purpose:** Minimal test for environment creation
- **What it tests:** Creating ProcgenVecEnv with minimal options
- **Run:** `uv run tests/test_treechop_minimal.py`
- **Expected:** Environment creates successfully, prints "✅ SUCCESS!"

#### `test_treechop_functional.py`
- **Purpose:** Full environment lifecycle test
- **What it tests:** Environment creation, observation, action execution, stepping
- **Run:** `uv run tests/test_treechop_functional.py`
- **Expected:** 10 steps complete successfully with observations and rewards

### Gymnasium Integration Tests

#### `test_gymnasium_simple.py`
- **Purpose:** Test Gymnasium wrapper without rendering
- **What it tests:**
  - `gym.make()` environment creation
  - `reset()` returns (observation, info)
  - `step()` executes actions
- **Run:** `uv run tests/test_gymnasium_simple.py`
- **Expected:** Environment creates, resets, and steps successfully

#### `test_gymnasium_render.py`
- **Purpose:** Test Gymnasium wrapper with rendering enabled
- **What it tests:**
  - Environment creation with `render_mode='rgb_array'`
  - Observation rendering
- **Run:** `uv run tests/test_gymnasium_render.py`
- **Expected:** Environment works with rendering enabled

#### `test_smoke_gymnasium_only.py`
- **Purpose:** Comprehensive Gymnasium integration smoke test
- **What it tests:**
  - Full environment lifecycle
  - Multiple episodes
  - Reset on termination
  - Observation shapes
- **Run:** `uv run tests/test_smoke_gymnasium_only.py`
- **Expected:** All checks pass, prints "All tests passed! ✓"

### Legacy Tests

#### `test_smoke.py`
- **Purpose:** Original smoke test (includes legacy gym3 interface)
- **Status:** ⚠️ Partially functional - Gymnasium tests pass, gym3 tests fail (expected)
- **Run:** `uv run tests/test_smoke.py`
- **Note:** The `test_direct_interface()` test uses legacy ProcgenGym3Env which is deprecated

#### `test_pybind11_migration.py`
- **Purpose:** Migration validation test from original migration work
- **Status:** Legacy test, superseded by newer tests
- **Note:** May need updates for current implementation

## Running All Tests

### Quick Verification
```bash
# Test basic functionality
uv run tests/test_treechop_functional.py

# Test Gymnasium integration
uv run tests/test_gymnasium_simple.py
uv run tests/test_gymnasium_render.py

# Comprehensive test
uv run tests/test_smoke_gymnasium_only.py
```

### Expected Results
All tests should:
- ✅ Complete without errors
- ✅ Exit with code 0
- ✅ Print success messages

## Test Requirements

- Python 3.9+
- All dependencies from `environment.yml` installed
- Built procgen module (`python -m procgen.build`)
- Assets directory at `procgen/data/assets/`

## Common Issues

### ImportError: procgen_bindings not found
**Solution:** Build the module:
```bash
python -m procgen.build
```

### Segmentation fault on exit
**Cause:** Qt global cleanup order issue (benign)
**Impact:** Only affects immediate destruction without using environment
**Solution:** None needed - tests that properly use environments work fine

### "unused options found" error
**Cause:** Passing game-specific options that the game doesn't recognize
**Solution:** Use minimal option set (see `test_treechop_minimal.py`)

## Writing New Tests

When adding new test files:

1. **Import procgen before gymnasium:**
   ```python
   import procgen  # Register environments
   import gymnasium as gym
   ```

2. **Use minimal options for direct C++ interface:**
   ```python
   options = {
       'env_name': 'treechop',
       'distribution_mode': 0,
       'num_levels': 1,
       'start_level': 0,
       'num_actions': 15,
       'rand_seed': 42,
       'num_threads': 0,
       'render_human': False,
       'resource_root': '/path/to/assets/',
   }
   ```

3. **Use Gymnasium API correctly:**
   ```python
   obs, info = env.reset(seed=42)  # Returns 2 values
   obs, reward, terminated, truncated, info = env.step(action)  # Returns 5 values
   ```

4. **Clean up properly:**
   ```python
   env.close()
   ```

## Test Coverage

Current test coverage focuses on:
- ✅ Environment creation and initialization
- ✅ Gymnasium API compliance
- ✅ Observation shapes and types
- ✅ Action execution
- ✅ Episode termination and reset
- ✅ Rendering functionality
- ✅ State management

Areas for future testing:
- [ ] All 27 game environments
- [ ] Multi-environment vectorization (num_envs > 1)
- [ ] State serialization (get_state/set_state)
- [ ] Thread safety (num_threads > 0)
- [ ] Different distribution modes
- [ ] Episode statistics tracking

## Debugging Tests

### Enable Debug Output
Set debug output in C++ code (already enabled):
- Constructor debug: See environment creation steps
- Buffer allocation debug: See memory allocation details
- Destructor debug: See cleanup process

### Run with UV
```bash
# UV provides better environment isolation
uv run tests/test_name.py

# Alternative: direct python (may have environment issues)
python tests/test_name.py
```

### Check Exit Codes
```bash
uv run tests/test_name.py
echo "Exit code: $?"
# Should be 0 for success
```

## CI/CD Integration

To integrate into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Procgen Tests
  run: |
    uv run tests/test_treechop_functional.py
    uv run tests/test_gymnasium_simple.py
    uv run tests/test_gymnasium_render.py
    uv run tests/test_smoke_gymnasium_only.py
```

## Contact

For test-related issues or questions, please open an issue on GitHub.
