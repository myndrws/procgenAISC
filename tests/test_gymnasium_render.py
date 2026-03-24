#!/usr/bin/env python3
"""Test Gymnasium wrapper WITH rendering"""

import procgen
import gymnasium as gym

print("Creating environment with render_mode='rgb_array'...")
try:
    env = gym.make('procgen-treechop-v0', render_mode='rgb_array')
    print("✓ Environment created!")

    print("\nCalling reset()...")
    obs, info = env.reset()
    print(f"✓ Reset successful! obs.shape={obs.shape}")

    print("\nTaking 1 step...")
    obs, reward, terminated, truncated, info = env.step(0)
    print(f"✓ Step successful! reward={reward:.2f}")

    env.close()
    print("\n✅ Rendering works!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
