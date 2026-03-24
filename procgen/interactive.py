#!/usr/bin/env python
import argparse

from procgen import ProcgenGym3Env
from .env import ENV_NAMES
import numpy as np

class ProcgenInteractive:
    """
    Simplified interactive interface for Procgen
    Note: This is a basic implementation. For full interactive features,
    consider using gymnasium's play utilities or pygame.
    """
    def __init__(self, env, **kwargs):
        self.env = env
        self._saved_state = None

    def handle_key_event(self, keys_clicked, keys_pressed):
        """Handle save/load state with F1 key"""
        if "LEFT_SHIFT" in keys_pressed and "F1" in keys_clicked:
            print("save state")
            if hasattr(self.env, 'get_state'):
                self._saved_state = self.env.get_state()
        elif "F1" in keys_clicked:
            print("load state")
            if self._saved_state is not None and hasattr(self.env, 'set_state'):
                self.env.set_state(self._saved_state)

    def run(self):
        """Run the interactive environment"""
        print("Interactive mode - use arrow keys to control")
        print("Press F1 to load state, Shift+F1 to save state")
        print("Note: Full interactive support requires pygame integration")
        # Basic implementation - full pygame integration would go here
        pass


def make_interactive(vision, record_dir, **kwargs):
    """Create an interactive Procgen environment"""
    if vision == "human":
        kwargs["render_mode"] = "rgb_array"

    env = ProcgenGym3Env(num=1, **kwargs)

    if record_dir is not None:
        print(f"Note: Video recording to {record_dir} is not yet implemented")
        print("Consider using gymnasium's video recorder wrapper instead")

    return ProcgenInteractive(env)


def main():
    default_str = "(default: %(default)s)"
    parser = argparse.ArgumentParser(
        description="Interactive version of Procgen allowing you to play the games"
    )
    parser.add_argument(
        "--vision",
        default="human",
        choices=["agent", "human"],
        help="level of fidelity of observation " + default_str,
    )
    parser.add_argument("--record-dir", help="directory to record movies to")
    parser.add_argument(
        "--distribution-mode",
        default="hard",
        help="which distribution mode to use for the level generation " + default_str,
    )
    parser.add_argument(
        "--env-name",
        default="heist_aisc_many_chests",
        help="name of game to create " + default_str,
        choices=ENV_NAMES + ["coinrun_old"],
    )
    parser.add_argument(
        "--level-seed", type=int, help="select an individual level to use"
    )

    advanced_group = parser.add_argument_group("advanced optional switch arguments")
    advanced_group.add_argument(
        "--rand-region",
        default=0,
        type=int,
        help="Size of area to randomize cheese location over",
    )
    advanced_group.add_argument(
        "--random-percent",
        default=0,
        type=int,
        help="How often to randomize the level construction",
    )
    advanced_group.add_argument(
        "--key-penalty",
        default=0,
        type=int,
        help="Penalty for picking up keys (divided by 10)",
    )
    advanced_group.add_argument(
        "--step-penalty",
        default=0,
        type=int,
        help="Time penalty per step (divided by 1000)",
    )
    advanced_group.add_argument(
        "--continue-after-coin",
        action="store_true",
        help="If true, don't end the level when coin is collected",
    )
    advanced_group.add_argument(
        "--paint-vel-info",
        action="store_true",
        default=False,
        help="paint player velocity info in the top left corner",
    )
    advanced_group.add_argument(
        "--use-generated-assets",
        action="store_true",
        default=False,
        help="use randomly generated assets in place of human designed assets",
    )
    advanced_group.add_argument(
        "--uncenter-agent",
        action="store_true",
        default=False,
        help="display the full level for games that center the observation to the agent",
    )
    advanced_group.add_argument(
        "--disable-backgrounds",
        action="store_true",
        default=False,
        help="disable human designed backgrounds",
    )
    advanced_group.add_argument(
        "--restrict-themes",
        action="store_true",
        default=False,
        help="restricts games that use multiple themes to use a single theme",
    )
    advanced_group.add_argument(
        "--use-monochrome-assets",
        action="store_true",
        default=False,
        help="use monochromatic rectangles instead of human designed assets",
    )

    args = parser.parse_args()

    kwargs = {
        "paint_vel_info": args.paint_vel_info,
        "use_generated_assets": args.use_generated_assets,
        "center_agent": not args.uncenter_agent,
        "use_backgrounds": not args.disable_backgrounds,
        "restrict_themes": args.restrict_themes,
        "use_monochrome_assets": args.use_monochrome_assets,
        "random_percent": args.random_percent,
        "rand_region": args.rand_region,
        "key_penalty": args.key_penalty,
        "step_penalty": args.step_penalty,
        "continue_after_coin": args.continue_after_coin,
    }
    
    if args.env_name != "coinrun_old":
        kwargs["distribution_mode"] = args.distribution_mode
    if args.level_seed is not None:
        kwargs["start_level"] = args.level_seed
        kwargs["num_levels"] = 1
    ia = make_interactive(
        args.vision, record_dir=args.record_dir, env_name=args.env_name, **kwargs
    )
    
    ia.run()


if __name__ == "__main__":
    main()
