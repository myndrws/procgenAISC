"""
Gymnasium-compliant Procgen environment

This module provides a clean Gymnasium interface for Procgen environments,
replacing the legacy gym3-based implementation with direct pybind11 bindings.

Usage:
    import gymnasium as gym
    env = gym.make('procgen-coinrun-v0')
    obs, info = env.reset(seed=42)
    obs, reward, terminated, truncated, info = env.step(action)
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Dict, Any, Tuple
import os
import random


# Import will be available after building with pybind11
try:
    from .procgen_bindings import ProcgenVecEnv
except ImportError:
    # Fallback message during development
    import warnings
    warnings.warn(
        "procgen_bindings not found. Build the extension with: python setup.py build_ext --inplace",
        ImportWarning
    )
    ProcgenVecEnv = None


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Distribution mode mapping (matches game.h DistributionMode)
DISTRIBUTION_MODE_DICT = {
    "easy": 0,
    "hard": 1,
    "extreme": 2,
    "memory": 10,
}

# Exploration level seeds (from original env.py)
EXPLORATION_LEVEL_SEEDS = {
    "coinrun": 1949448038,
    "coinrun_mod_wall": 1949448038,
    "coinrun_aisc": 1949448038,
    "caveflyer": 1259048185,
    "leaper": 1318677581,
    "jumper": 1434825276,
    "maze": 158988835,
    "maze_fixed_size": 158988835,
    "maze_aisc": 158988835,
    "maze_yellowline": 158988835,
    "maze_redline_yellowgem": 158988835,
    "maze_yellowstar_redgem": 158988835,
    "heist": 876640971,
    "heist_aisc_many_chests": 876640971,
    "heist_aisc_many_keys": 876640971,
    "climber": 1561126160,
    "ninja": 1123500215,
}


def create_random_seed():
    """Create a random seed, accounting for MPI if available"""
    rand_seed = random.SystemRandom().randint(0, 2 ** 31 - 1)
    try:
        from mpi4py import MPI
        rand_seed = rand_seed - (rand_seed % MPI.COMM_WORLD.size) + MPI.COMM_WORLD.rank
    except ModuleNotFoundError:
        pass
    return rand_seed


class ProcgenEnv(gym.Env):
    """
    Gymnasium-compliant Procgen environment

    Implements full Gymnasium API per https://gymnasium.farama.org/:
    - reset() returns (observation, info)
    - step() returns (observation, reward, terminated, truncated, info)
    - render_mode specified at creation
    - seeding via reset(seed=...)

    Args:
        env_name: Name of the Procgen game (e.g., 'coinrun', 'maze')
        render_mode: Render mode ('rgb_array' or 'human')
        num_levels: Number of unique levels (0 = infinite)
        start_level: Starting level index
        distribution_mode: Difficulty ('easy', 'hard', 'extreme', 'memory')
        center_agent: Whether to center agent in observation
        use_backgrounds: Whether to show background
        use_monochrome_assets: Use monochrome graphics
        restrict_themes: Restrict visual themes
        use_generated_assets: Use procedurally generated assets
        paint_vel_info: Paint velocity info on screen
        random_percent: Randomization percentage
        key_penalty: Penalty for collecting keys (heist)
        step_penalty: Penalty per step
        rand_region: Random region parameter
        continue_after_coin: Continue episode after collecting coin (coinrun)
        num_threads: Number of worker threads (0 = no threading)
    """

    metadata = {"render_modes": ["rgb_array", "human"], "render_fps": 15}

    def __init__(
        self,
        env_name: str,
        render_mode: Optional[str] = None,
        # Level selection
        num_levels: int = 0,
        start_level: int = 0,
        distribution_mode: str = "hard",
        # Visual options
        center_agent: bool = True,
        use_backgrounds: bool = True,
        use_monochrome_assets: bool = False,
        restrict_themes: bool = False,
        use_generated_assets: bool = False,
        paint_vel_info: bool = False,
        # Difficulty modifiers
        random_percent: int = 0,
        key_penalty: int = 0,
        step_penalty: int = 0,
        rand_region: int = 0,
        # Game-specific
        continue_after_coin: bool = False,
        # Performance
        num_threads: int = 0,
        # Internal
        debug: bool = False,
        debug_mode: int = 0,
        **kwargs
    ):
        super().__init__()

        if ProcgenVecEnv is None:
            raise ImportError(
                "procgen_bindings extension not found. "
                "Build it with: python setup.py build_ext --inplace"
            )

        self.env_name = env_name
        self.render_mode = render_mode
        self._render_human = (render_mode == "rgb_array") or (render_mode == "human")

        # Handle exploration mode
        if distribution_mode == "exploration":
            if env_name not in EXPLORATION_LEVEL_SEEDS:
                raise ValueError(f"{env_name} does not support exploration mode")
            distribution_mode = "hard"
            num_levels = 1
            start_level = EXPLORATION_LEVEL_SEEDS[env_name]

        # Get resource root
        resource_root = os.path.join(SCRIPT_DIR, "data", "assets") + os.sep
        if not os.path.exists(resource_root):
            raise FileNotFoundError(f"Resource root not found: {resource_root}")

        # Build options dict for C++
        # Only pass essential options to avoid "unused options" errors
        # Different games consume different options
        self._initial_options = {
            "env_name": env_name,
            "distribution_mode": DISTRIBUTION_MODE_DICT[distribution_mode],
            "num_levels": num_levels,
            "start_level": start_level,
            "num_actions": 15,  # Procgen has 15 discrete actions
            "rand_seed": 0,  # Will be set in reset()
            "num_threads": num_threads,
            "render_human": self._render_human,
            "resource_root": resource_root,
        }

        # Create vectorized environment with 1 env
        self._create_vec_env(create_random_seed())

        # Define Gymnasium spaces
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(64, 64, 3), dtype=np.uint8
        )
        self.action_space = spaces.Discrete(15)

        # Internal state
        self._last_obs = None
        self._last_info = None
        self._episode_return = 0.0
        self._episode_length = 0

    def _create_vec_env(self, seed: int):
        """Create or recreate the vectorized environment with a specific seed"""
        options = self._initial_options.copy()
        options["rand_seed"] = seed
        self.vec_env = ProcgenVecEnv(1, options)

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment

        Args:
            seed: Random seed for reproducibility
            options: Additional options (not used)

        Returns:
            observation: (64, 64, 3) uint8 RGB array
            info: Dictionary with episode information
        """
        print("[DEBUG Python reset()] Starting...")
        super().reset(seed=seed)
        print("[DEBUG Python reset()] super().reset() complete")

        # If seed provided, recreate environment with that seed
        if seed is not None:
            print(f"[DEBUG Python reset()] Recreating vec_env with seed={seed}")
            self._create_vec_env(seed)
            print("[DEBUG Python reset()] vec_env recreated")

        # Reset episode tracking
        self._episode_return = 0.0
        self._episode_length = 0

        # Get initial observation by taking a dummy action
        self.vec_env.set_action(np.array([0], dtype=np.int32))
        self.vec_env.act()
        self.vec_env.observe()

        # Extract observation
        obs = self.vec_env.get_obs()[0]  # Extract single env

        # Extract info
        info_dict = self.vec_env.get_info()
        info = self._extract_info(info_dict)

        self._last_obs = obs
        self._last_info = info

        return obs, info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment

        Args:
            action: Integer action in [0, 14]

        Returns:
            observation: (64, 64, 3) uint8 RGB array
            reward: Float reward for this step
            terminated: Whether episode ended naturally (goal/death)
            truncated: Whether episode was cut off (not used in procgen)
            info: Dictionary with episode information
        """
        # Validate action
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")

        # Set action and step
        self.vec_env.set_action(np.array([action], dtype=np.int32))
        self.vec_env.act()
        self.vec_env.observe()

        # Extract results
        obs = self.vec_env.get_obs()[0]
        reward = float(self.vec_env.get_rewards()[0])
        first = bool(self.vec_env.get_firsts()[0])
        info_dict = self.vec_env.get_info()

        # Build info dict
        info = self._extract_info(info_dict)

        # Track episode stats
        self._episode_return += reward
        self._episode_length += 1

        # In procgen, 'first' flag indicates episode just ended
        # Per Gymnasium API:
        # - terminated: natural end (goal reached, agent died, etc.)
        # - truncated: artificial cutoff (time limit, etc.)
        # Procgen doesn't use time limits, so truncated is always False
        terminated = first
        truncated = False

        # Add episode stats to info when episode ends
        if terminated:
            info["episode"] = {
                "r": self._episode_return,
                "l": self._episode_length,
            }

        self._last_obs = obs
        self._last_info = info

        return obs, reward, terminated, truncated, info

    def _extract_info(self, info_dict: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Extract info for single environment from vectorized info"""
        info = {}
        for key, value in info_dict.items():
            # Skip rgb buffer (used for rendering)
            if key == "rgb":
                continue

            # Extract first element (single env)
            if isinstance(value, np.ndarray):
                if value.ndim > 0:
                    info[key] = value[0] if value.shape[0] > 0 else value
                else:
                    info[key] = value.item()
            else:
                info[key] = value

        return info

    def render(self) -> Optional[np.ndarray]:
        """
        Render the environment

        Returns:
            RGB array if render_mode is "rgb_array" or "human", else None
        """
        if self.render_mode in ["rgb_array", "human"]:
            # Return current observation
            return self._last_obs
        return None

    def close(self):
        """Close the environment and free resources"""
        # pybind11 handles cleanup via C++ destructor
        # VecGame destructor will clean up resources
        pass

    def get_state(self) -> bytes:
        """
        Get serialized state (Procgen-specific extension)

        Returns:
            Serialized state as bytes
        """
        return self.vec_env.get_state(0)

    def set_state(self, state: bytes):
        """
        Set serialized state (Procgen-specific extension)

        Args:
            state: Serialized state bytes from get_state()
        """
        self.vec_env.set_state(0, state)

    def __repr__(self) -> str:
        return f"ProcgenEnv({self.env_name})"
