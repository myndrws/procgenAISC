# Procgen Documentation

This directory contains comprehensive documentation for the Procgen environment implementation, including the pybind11 migration and Gymnasium integration.

## Documentation Index

### Migration Documentation

#### [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) 🎉
**Status: Complete**
- Comprehensive summary of the gym3 → pybind11 migration
- Details of all changes, fixes, and improvements
- API examples and usage patterns
- Verification test results
- **Start here** if you want to understand what was done

#### [PYBIND11_MIGRATION_PLAN.md](PYBIND11_MIGRATION_PLAN.md) 📋
- Original migration strategy and plan
- Step-by-step implementation approach
- Technical decisions and architecture choices
- Historical document showing the migration process

#### [MIGRATION_STATUS.md](MIGRATION_STATUS.md) 📊
- Legacy status document from during migration
- Debugging steps and issue tracking
- Preserved for historical reference
- See MIGRATION_COMPLETE.md for current status

#### [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) 📝
- High-level summary of migration work
- Quick reference for what changed
- Links to detailed documentation

#### [GYMNASIUM_MIGRATION.md](GYMNASIUM_MIGRATION.md) 🏋️
- Specific details about Gymnasium API implementation
- Differences from gym3 API
- Compliance with Gymnasium standards
- Examples of new API usage

### Build Documentation

#### [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) 🔧
**Essential for developers**
- Complete build instructions from source
- Dependency requirements
- Platform-specific notes (Linux, macOS, Windows)
- Troubleshooting common build issues
- CMake configuration details

### Project Documentation

#### [CHANGES.md](CHANGES.md) 📜
- Version history
- Changelog of modifications
- Game-specific changes
- Feature additions

#### [CONTRIBUTING.md](CONTRIBUTING.md) 🤝
- Guidelines for contributing
- Code style and standards
- Pull request process
- Development workflow

#### [ASSET_LICENSES.md](ASSET_LICENSES.md) ⚖️
- Licensing information for game assets
- Third-party attribution
- Usage rights and restrictions

## Quick Navigation

### I want to...

#### **Use Procgen environments**
→ Start with main [README.md](../README.md) for installation and quick start

#### **Understand the migration**
→ Read [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)

#### **Build from source**
→ Follow [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

#### **Implement Gymnasium environments**
→ See [GYMNASIUM_MIGRATION.md](GYMNASIUM_MIGRATION.md)

#### **Run tests**
→ Check [tests/README.md](../tests/README.md)

#### **Contribute code**
→ Read [CONTRIBUTING.md](CONTRIBUTING.md)

## Key Concepts

### Architecture Overview

```
┌─────────────────────────────────────┐
│   Python (Gymnasium Interface)     │
│   procgen_gymnasium_env.py          │
├─────────────────────────────────────┤
│   pybind11 Bindings                 │
│   procgen_bindings.cpp              │
├─────────────────────────────────────┤
│   C++ Game Engine                   │
│   VecGame, Game classes             │
│   (treechop.cpp, coinrun.cpp, etc.) │
├─────────────────────────────────────┤
│   Qt5 Rendering                     │
│   Asset loading, graphics           │
└─────────────────────────────────────┘
```

### Key Files

**Python Layer:**
- `procgen/__init__.py` - Package initialization
- `procgen/procgen_gymnasium_env.py` - Gymnasium wrapper (ProcgenEnv)
- `procgen/gym_registration.py` - Environment registration

**C++ Bindings:**
- `procgen/src/procgen_bindings.cpp` - pybind11 interface (ProcgenVecEnv)

**C++ Engine:**
- `procgen/src/vecgame.cpp` - Vectorized environment manager
- `procgen/src/game.cpp` - Base game class
- `procgen/src/games/*.cpp` - Individual game implementations

**Build System:**
- `procgen/CMakeLists.txt` - CMake configuration
- `procgen/build.py` - Build script
- `setup.py` - Python package setup

### API Evolution

**Old (gym3):**
```python
from procgen import ProcgenGym3Env
env = ProcgenGym3Env(num=1, env_name="coinrun")
rew, obs, first = env.observe()
env.act(action)
```

**New (Gymnasium):**
```python
import gymnasium as gym
env = gym.make('procgen-coinrun-v0')
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(action)
```

### Migration Benefits

1. **Modern Dependencies**
   - ✅ pybind11 (actively maintained)
   - ✅ Gymnasium (standard API)
   - ❌ gym3 (deprecated, unmaintained)

2. **Better Performance**
   - Zero-copy numpy arrays
   - Direct C++ to Python interface
   - Efficient memory management

3. **Ecosystem Compatibility**
   - Works with Stable-Baselines3
   - Compatible with Ray RLlib
   - Standard Gymnasium API

4. **Type Safety**
   - Compile-time type checking
   - Better error messages
   - IDE autocomplete support

## Documentation Style Guide

### For Writers

When contributing documentation:

1. **Use clear, concise language**
2. **Include code examples**
3. **Add emoji for visual navigation** (optional but helpful)
4. **Link between related documents**
5. **Keep tables of contents updated**
6. **Test all code examples**

### Document Templates

#### Technical Documentation
- Overview section
- Prerequisites
- Step-by-step instructions
- Troubleshooting section
- Related links

#### API Documentation
- Function signatures
- Parameter descriptions
- Return values
- Usage examples
- Common patterns

## Version History

- **2025** - pybind11 migration completed
  - Removed gym3 dependency
  - Added Gymnasium support
  - Created comprehensive test suite

- **2022** - TreeChop environment added
  - Based on Shah et al. 2022 paper
  - Tree respawning mechanics
  - Goal misgeneralization research

- **Original** - Fork from OpenAI Procgen
  - Modified environments for research
  - Additional game variants

## External Resources

### Official Documentation
- [Gymnasium Documentation](https://gymnasium.farama.org/)
- [pybind11 Documentation](https://pybind11.readthedocs.io/)
- [Qt5 Documentation](https://doc.qt.io/qt-5/)

### Research Papers
- [Shah et al. 2022 - Goal Misgeneralization](https://arxiv.org/abs/2210.01790)
- [Original Procgen Paper](https://arxiv.org/abs/1912.01588)
- [Goal Misgeneralization in DRL](https://github.com/JacobPfau/procgenAISC)

### Related Projects
- [OpenAI Procgen](https://github.com/openai/procgen)
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium)

## Getting Help

### Common Questions

**Q: Where do I start?**
A: Main [README.md](../README.md) for installation, then [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) for details.

**Q: How do I build the project?**
A: See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

**Q: What changed in the migration?**
A: See [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)

**Q: How do I use the new API?**
A: See [GYMNASIUM_MIGRATION.md](GYMNASIUM_MIGRATION.md)

**Q: Tests are failing, what do I do?**
A: Check [tests/README.md](../tests/README.md) for troubleshooting

### Support Channels

- **GitHub Issues:** For bugs and feature requests
- **Documentation:** Start with this directory
- **Code Examples:** See `tests/` directory

## Contributing to Documentation

We welcome documentation improvements! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

When updating documentation:
1. Ensure accuracy with current code
2. Test any code examples
3. Update cross-references
4. Keep formatting consistent
5. Add to this README if adding new documents

## License

Documentation follows the same license as the project. See LICENSE file in root directory.

---

**Last Updated:** 2025
**Status:** Active development
**Maintainers:** See CONTRIBUTING.md
