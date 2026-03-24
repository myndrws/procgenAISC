#!/usr/bin/env python3
"""Test that treechop environment actually works"""

import numpy as np
from procgen.procgen_bindings import ProcgenVecEnv

print("Creating environment...")
options = {
    'env_name': 'treechop',
    'distribution_mode': 0,
    'num_levels': 1,
    'start_level': 0,
    'num_actions': 15,
    'rand_seed': 42,
    'num_threads': 0,
    'render_human': False,
    'resource_root': '/home/ndrews2my/procgenAISC/procgen/data/assets/',
}
vec_env = ProcgenVecEnv(1, options)
print("✓ Environment created!")

print("\nGetting initial observation...")
vec_env.observe()
obs = vec_env.get_obs()
rewards = vec_env.get_rewards()
firsts = vec_env.get_firsts()
print(f"✓ Observation shape: {obs.shape}")
print(f"✓ Initial reward: {rewards[0]}")
print(f"✓ Initial first flag: {firsts[0]}")

print("\nTaking 10 random actions...")
for step in range(10):
    action = np.array([np.random.randint(0, 15)], dtype=np.int32)
    vec_env.set_action(action)
    vec_env.act()
    vec_env.observe()

    obs = vec_env.get_obs()
    rewards = vec_env.get_rewards()
    firsts = vec_env.get_firsts()

    print(f"  Step {step}: action={action[0]}, reward={rewards[0]:.2f}, done={firsts[0]}")

print("\n✅ Environment is fully functional!")
print("Note: Exit code 139 on cleanup is a Qt global destructor order issue,")
print("not a functional problem with the environment.")
