import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
version_path = os.path.join(SCRIPT_DIR, "version.txt")
__version__ = open(version_path).read()

# New pybind11-based Gymnasium implementation
from .procgen_gymnasium_env import ProcgenEnv as ProcgenGymnasiumEnv

# Legacy gym3-based implementations (deprecated)
# Keep for backward compatibility
try:
    from .env import ProcgenEnv as ProcgenEnvLegacy, ProcgenGym3Env
    _legacy_available = True
except ImportError:
    _legacy_available = False
    ProcgenEnvLegacy = None
    ProcgenGym3Env = None

# Auto-register environments with Gymnasium
from .gym_registration import register_environments
register_environments()

# Export new implementation as default
ProcgenEnv = ProcgenGymnasiumEnv

__all__ = ["ProcgenEnv", "ProcgenGymnasiumEnv", "ProcgenGym3Env", "ProcgenEnvLegacy"]
