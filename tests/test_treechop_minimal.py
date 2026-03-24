#!/usr/bin/env python3
"""Minimal test for treechop"""

import sys
import signal

# Set timeout
def timeout_handler(signum, frame):
    print("\n[TIMEOUT] Test timed out after 5 seconds")
    sys.exit(1)

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(5)

try:
    print("Step 1: Importing procgen_bindings...")
    from procgen.procgen_bindings import ProcgenVecEnv
    print("  ✓ Import successful")

    print("\nStep 2: Creating options dict...")
    # Minimal options based on procgen/examples/random_agent_gym3.py
    options = {
        'env_name': 'treechop',
        'distribution_mode': 0,  # EasyMode
        'num_levels': 1,
        'start_level': 0,
        'num_actions': 15,
        'rand_seed': 42,
        'num_threads': 0,
        'render_human': False,
        'resource_root': '/home/ndrews2my/procgenAISC/procgen/data/assets/',
    }
    print("  ✓ Options created")

    print("\nStep 3: Creating ProcgenVecEnv...")
    vec_env = ProcgenVecEnv(1, options)
    print("  ✓ VecEnv created!")

    print("\n✅ SUCCESS! Environment created without crash")
    signal.alarm(0)  # Cancel alarm

except Exception as e:
    print(f"\n❌ FAILED with exception: {e}")
    import traceback
    traceback.print_exc()
    signal.alarm(0)
    sys.exit(1)
