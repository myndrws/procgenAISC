#!/usr/bin/env python
"""
Smoke test for procgen gymnasium integration
Run with: python test_smoke.py
"""

import procgen
import gymnasium as gym

def test_gymnasium_interface():
    """Test creating environment via gymnasium.make()"""
    print("Testing gymnasium interface...")
    env = gym.make('procgen-treechop-v0', render_mode='rgb_array')

    obs, info = env.reset()
    assert obs.shape == (64, 64, 3), f"Expected shape (64,64,3), got {obs.shape}"

    for _ in range(10):
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        if terminated or truncated:
            obs, info = env.reset()

    env.close()
    print("✓ Gymnasium interface works!")

def test_direct_interface():
    """Test creating environment directly"""
    print("Testing direct ProcgenGym3Env interface...")
    from procgen import ProcgenGym3Env
    import numpy as np

    env = ProcgenGym3Env(num=1, env_name="coinrun", distribution_mode="easy")
    rew, obs, first = env.observe()

    assert 'rgb' in obs, "Expected 'rgb' key in observation"
    assert obs['rgb'].shape == (1, 64, 64, 3), f"Expected shape (1,64,64,3), got {obs['rgb'].shape}"

    for _ in range(10):
        action = np.random.randint(0, 15, size=(1,), dtype=np.int32)
        env.act(action)
        rew, obs, first = env.observe()
        if first[0]:
            break

    print("✓ Direct interface works!")

if __name__ == "__main__":
    print("=" * 60)
    print("Procgen Gymnasium Smoke Test")
    print("=" * 60)

    test_gymnasium_interface()
    test_direct_interface()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
