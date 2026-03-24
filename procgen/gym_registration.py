import gymnasium as gym

# List of all Procgen game environments
ENV_NAMES = [
    "bigfish",
    "treechop",
    "bossfight",
    "caveflyer",
    "chaser",
    "climber",
    "coinrun",
    "coinrun_mod_wall",
    "coinrun_aisc",
    "dodgeball",
    "fruitbot",
    "heist",
    "heist_aisc_many_chests",
    "heist_aisc_many_keys",
    "jumper",
    "leaper",
    "maze",
    "maze_fixed_size",
    "maze_aisc",
    "maze_yellowline",
    "maze_redline_yellowgem",
    "maze_yellowstar_redgem",
    "miner",
    "ninja",
    "plunder",
    "starpilot",
]


def register_environments():
    """Register all Procgen environments with Gymnasium"""
    for env_name in ENV_NAMES:
        gym.register(
            id=f'procgen-{env_name}-v0',
            entry_point='procgen.procgen_gymnasium_env:ProcgenEnv',
            kwargs={"env_name": env_name},
        )


# Auto-register environments on import
register_environments()