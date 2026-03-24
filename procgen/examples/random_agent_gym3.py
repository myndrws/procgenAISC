"""
Example random agent script using the gymnasium API to demonstrate that procgen works
"""

import procgen  # Import first to register environments
import gymnasium as gym

env = gym.make('procgen-treechop-v0', distribution_mode="easy")
obs, info = env.reset()
step = 0
total_reward = 0

while step < 1000:
    obs, rew, terminated, truncated, info = env.step(env.action_space.sample())
    done = terminated or truncated
    total_reward += rew
    print(f"step {step} reward {rew:.2f} done {done}")
    step += 1
    if done:
        break

print(f"total reward {total_reward:.2f}")
