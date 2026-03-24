import gymnasium as gym
from .env import ENV_NAMES, ProcgenGym3Env


def make_env(render_mode=None, render=False, **kwargs):
    # the render option is kept here for backwards compatibility
    # users should use `render_mode="human"` or `render_mode="rgb_array"`
    if render:
        render_mode = "human"

    kwargs["render_mode"] = render_mode
    if render_mode == "human":
        # For human rendering, set to rgb_array and let gymnasium handle the window
        kwargs["render_mode"] = "rgb_array"

    # Create a wrapper class that adapts ProcgenGym3Env to gymnasium.Env
    from gymnasium import Env
    from gymnasium.spaces import Box, Discrete
    import numpy as np

    class ProcgenGymnasiumEnv(Env):
        metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 15}

        def __init__(self, **env_kwargs):
            super().__init__()
            self.vec_env = ProcgenGym3Env(num=1, num_threads=0, **env_kwargs)

            # Define observation and action spaces
            # Procgen uses 64x64x3 RGB images
            self.observation_space = Box(
                low=0, high=255, shape=(64, 64, 3), dtype=np.uint8
            )
            # Procgen uses 15 discrete actions
            self.action_space = Discrete(15)

            self._render_mode = env_kwargs.get("render_mode")

        def reset(self, seed=None, options=None):
            if seed is not None:
                # Handle seeding if needed
                pass

            # Reset by stepping with a dummy action and getting initial observation
            self.vec_env.act(np.array([0], dtype=np.int32))
            rew, obs_dict, first = self.vec_env.observe()

            obs = obs_dict["rgb"][0]  # Extract single env observation
            info = {}

            return obs, info

        def step(self, action):
            # Send action to vectorized env
            self.vec_env.act(np.array([action], dtype=np.int32))
            rew, obs_dict, first = self.vec_env.observe()

            obs = obs_dict["rgb"][0]
            reward = float(rew[0])
            terminated = bool(first[0])
            truncated = False
            info = {}

            return obs, reward, terminated, truncated, info

        def render(self):
            if self._render_mode == "rgb_array":
                _, obs_dict, _ = self.vec_env.observe()
                return obs_dict["rgb"][0]
            return None

        def close(self):
            if hasattr(self.vec_env, 'close'):
                self.vec_env.close()

    return ProcgenGymnasiumEnv(**kwargs)


def register_environments():
    for env_name in ENV_NAMES:
        gym.register(
            id=f'procgen-{env_name}-v0',
            entry_point='procgen.gym_registration:make_env',
            kwargs={"env_name": env_name},
        )