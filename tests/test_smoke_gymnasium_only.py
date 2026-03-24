#!/usr/bin/env python
"""
Smoke test for procgen gymnasium integration (Gymnasium only)
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

if __name__ == "__main__":
    print("=" * 60)
    print("Procgen Gymnasium Smoke Test")
    print("=" * 60)

    test_gymnasium_interface()

    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
