"""
Example random agent script using the gym3 API to demonstrate that procgen works
"""

from gym3 import types_np
from procgen import ProcgenGym3Env
env = ProcgenGym3Env(num=1, env_name="treechop")
step = 0
total_reward = 0
while True:
    env.act(types_np.sample(env.ac_space, bshape=(env.num,)))
    rew, obs, first = env.observe()
    total_reward += rew
    print(f"step {step} reward {rew} first {first}")
    if rew != 0:
        print("------------------------------------------------------------")
    if step > 0 and first:
        break
    step += 1
print(f"total reward {total_reward}")
