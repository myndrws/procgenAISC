"""
Example random agent script demonstrating procgen with direct ProcgenGym3Env usage.
Note: This uses the internal API. For standard gymnasium usage, see random_agent_gym.py
"""

import numpy as np
from procgen import ProcgenGym3Env

env = ProcgenGym3Env(num=1, env_name="treechop", distribution_mode="easy", render_mode="rgb_array")

step = 0
total_reward = 0

# Initial observation
rew, obs, first = env.observe()

while True:
    # Sample random action
    action = np.random.randint(0, 15, size=(env.num,), dtype=np.int32)
    env.act(action)
    rew, obs, first = env.observe()

    total_reward += rew[0]
    print(f"step {step} reward {rew[0]:.2f} first {first[0]}")

    if step > 0 and first[0]:
        break
    step += 1

print(f"total reward {total_reward:.2f}")
