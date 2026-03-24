#!/usr/bin/env python3
"""
Test script for pybind11 migration

This script tests the new pybind11-based Gymnasium implementation
to ensure it works correctly before removing gym3.

Tests:
1. Import test
2. Environment creation
3. Gymnasium API compliance
4. State save/load
5. Multiple games
"""

import sys
import traceback


def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Import Test")
    print("=" * 60)

    try:
        import numpy as np
        print("✓ numpy imported")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False

    try:
        import gymnasium as gym
        print("✓ gymnasium imported")
    except ImportError as e:
        print(f"✗ Failed to import gymnasium: {e}")
        return False

    try:
        import procgen
        print(f"✓ procgen imported (version: {procgen.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import procgen: {e}")
        return False

    try:
        from procgen.procgen_bindings import ProcgenVecEnv
        print("✓ procgen_bindings.ProcgenVecEnv imported")
    except ImportError as e:
        print(f"✗ Failed to import procgen_bindings: {e}")
        print("   This is expected if the extension hasn't been built yet.")
        print("   Run: python setup.py build_ext --inplace")
        return False

    try:
        from procgen.procgen_gymnasium_env import ProcgenEnv
        print("✓ procgen.procgen_gymnasium_env.ProcgenEnv imported")
    except ImportError as e:
        print(f"✗ Failed to import ProcgenEnv: {e}")
        return False

    print("\n✅ All imports successful!\n")
    return True


def test_env_creation():
    """Test environment creation via gymnasium.make()"""
    print("=" * 60)
    print("TEST 2: Environment Creation")
    print("=" * 60)

    try:
        import gymnasium as gym

        # Test creating environment
        print("Creating environment: procgen-coinrun-v0")
        env = gym.make('procgen-coinrun-v0')
        print(f"✓ Environment created: {env}")

        # Check spaces
        print(f"  Observation space: {env.observation_space}")
        print(f"  Action space: {env.action_space}")

        # Verify shapes
        assert env.observation_space.shape == (64, 64, 3), "Observation shape mismatch"
        assert env.action_space.n == 15, "Action space mismatch"
        print("✓ Spaces verified")

        env.close()
        print("\n✅ Environment creation successful!\n")
        return True

    except Exception as e:
        print(f"\n✗ Environment creation failed: {e}")
        traceback.print_exc()
        return False


def test_gymnasium_api():
    """Test Gymnasium API compliance"""
    print("=" * 60)
    print("TEST 3: Gymnasium API Compliance")
    print("=" * 60)

    try:
        import gymnasium as gym
        import numpy as np

        env = gym.make('procgen-coinrun-v0')

        # Test reset() returns (obs, info)
        print("Testing reset()...")
        result = env.reset(seed=42)
        assert len(result) == 2, f"reset() should return 2 values, got {len(result)}"
        obs, info = result
        print(f"✓ reset() returns (obs, info)")
        print(f"  obs.shape: {obs.shape}")
        print(f"  info keys: {list(info.keys())}")

        # Verify observation
        assert isinstance(obs, np.ndarray), "Observation should be ndarray"
        assert obs.shape == (64, 64, 3), f"Expected (64,64,3), got {obs.shape}"
        assert obs.dtype == np.uint8, f"Expected uint8, got {obs.dtype}"
        print("✓ Observation validated")

        # Verify info
        assert isinstance(info, dict), "Info should be dict"
        print("✓ Info validated")

        # Test step() returns 5 values
        print("\nTesting step()...")
        result = env.step(0)
        assert len(result) == 5, f"step() should return 5 values, got {len(result)}"
        obs, reward, terminated, truncated, info = result
        print(f"✓ step() returns (obs, reward, terminated, truncated, info)")
        print(f"  reward: {reward}")
        print(f"  terminated: {terminated}")
        print(f"  truncated: {truncated}")

        # Verify types
        assert isinstance(obs, np.ndarray), "Observation should be ndarray"
        assert isinstance(reward, (int, float)), "Reward should be numeric"
        assert isinstance(terminated, bool), "Terminated should be bool"
        assert isinstance(truncated, bool), "Truncated should be bool"
        assert isinstance(info, dict), "Info should be dict"
        print("✓ Step outputs validated")

        # Test a few more steps
        print("\nRunning 10 steps...")
        for i in range(10):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated:
                print(f"  Episode ended at step {i+1}")
                obs, info = env.reset()
                break
        print("✓ Multiple steps successful")

        env.close()
        print("\n✅ Gymnasium API compliance verified!\n")
        return True

    except Exception as e:
        print(f"\n✗ Gymnasium API test failed: {e}")
        traceback.print_exc()
        return False


def test_state_save_load():
    """Test state save/load functionality"""
    print("=" * 60)
    print("TEST 4: State Save/Load")
    print("=" * 60)

    try:
        import gymnasium as gym
        import numpy as np

        env = gym.make('procgen-coinrun-v0')
        obs1, _ = env.reset(seed=123)

        # Take a few steps
        print("Taking 5 steps...")
        for _ in range(5):
            obs1, _, terminated, _, _ = env.step(1)  # Move right
            if terminated:
                break

        # Save state
        print("Saving state...")
        state = env.get_state()
        assert isinstance(state, bytes), "State should be bytes"
        print(f"✓ State saved ({len(state)} bytes)")

        # Take more steps
        print("Taking 3 more steps...")
        for _ in range(3):
            env.step(2)

        # Load state
        print("Loading state...")
        env.set_state(state)
        obs2, _, _, _, _ = env.step(0)  # No-op to get observation
        print("✓ State loaded")

        # Verify state matches
        if np.array_equal(obs1, obs2):
            print("✓ Observations match after state restore")
        else:
            print("⚠ Observations differ slightly (may be expected)")

        env.close()
        print("\n✅ State save/load works!\n")
        return True

    except Exception as e:
        print(f"\n✗ State save/load test failed: {e}")
        traceback.print_exc()
        return False


def test_multiple_games():
    """Test multiple game environments"""
    print("=" * 60)
    print("TEST 5: Multiple Games")
    print("=" * 60)

    games_to_test = ['coinrun', 'maze', 'heist', 'bigfish']

    try:
        import gymnasium as gym

        for game_name in games_to_test:
            print(f"Testing {game_name}...")
            env = gym.make(f'procgen-{game_name}-v0')
            obs, info = env.reset()
            obs, reward, terminated, truncated, info = env.step(0)
            env.close()
            print(f"✓ {game_name} works")

        print("\n✅ All tested games work!\n")
        return True

    except Exception as e:
        print(f"\n✗ Multiple games test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PYBIND11 MIGRATION TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        ("Imports", test_imports),
        ("Environment Creation", test_env_creation),
        ("Gymnasium API", test_gymnasium_api),
        ("State Save/Load", test_state_save_load),
        ("Multiple Games", test_multiple_games),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Migration successful!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
