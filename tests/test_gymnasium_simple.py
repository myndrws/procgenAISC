#!/usr/bin/env python3
"""Simple test of Gymnasium wrapper without rendering"""

import procgen  # Register environments
import gymnasium as gym

print("Creating environment without render_mode...")
env = gym.make('procgen-treechop-v0')
print("✓ Environment created!")

print("\nCalling reset()...")
obs, info = env.reset()
print(f"✓ Reset successful! obs.shape={obs.shape}")

print("\nTaking 5 steps...")
for i in range(5):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"  Step {i}: reward={reward:.2f}, terminated={terminated}")
    if terminated:
        obs, info = env.reset()

env.close()
print("\n✅ Gymnasium wrapper works!")
