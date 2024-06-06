"""
Example random agent script using the gym3 API to demonstrate that procgen works.
I have modified this example to make the video recorder wrapper run.
I also had to apply a patch to _io.py in ffmpeg because of a consistent keyword error
for the argument 'audio_path', which obviously isn't being set here, but was throwing an
exception. I just added '**kwargs' to def write_frames args to solve this.
I suspect this is due to package dependency issues, but not clear if it's
affecting anyone else.
"""

from gym3 import types_np
from gym3 import VideoRecorderWrapper
from procgen import ProcgenGym3Env
env = ProcgenGym3Env(num=1, env_name="treechop", distribution_mode="easy", render_mode="rgb_array")
env = VideoRecorderWrapper(env=env, directory="./video_testing", info_key="rgb")
# env = gym3.ViewerWrapper(env, info_key="rgb")  # alternative to see what agent is doing in situ
step = 0
total_reward = 0
while True:
    env.act(types_np.sample(env.ac_space, bshape=(env.num,)))
    rew, obs, first = env.observe()
    total_reward += rew
    print(f"step {step} reward {rew} first {first}")
    if step > 0 and first:
        break
    step += 1
print(f"total reward {total_reward}")
