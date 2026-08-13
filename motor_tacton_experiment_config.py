"""
DRV2605 tacton experiment pool configuration.

TACTON_POOL defines which tactons enter the experiment and how many times each
appears in the test phase. CHOICE_LABELS defines what participants see.
"""

# Enabled tactons from esp32_motor_drv2605_tacton_server.py:
# 1, 4, 5, 8, 9, 10 are DRV2605 haptic icons; 11 is Rough Slip.
TACTON_POOL = {
    1: 3,
    4: 3,
    5: 3,
    8: 3,
    9: 3,
    10: 3,
    11: 3,
}

# Participant-visible labels. Replace these with the final labels you need.
CHOICE_LABELS = {
    1: ".",
    4: ". .",
    5: ". . . .",
    8: "—— .",
    9: "—— . ——",
    10: ". ——",
    11: "~~~~~",
}

# Rough Slip playback duration for tacton 11.
ROUGH_SLIP_DURATION_MS = 2000

# Maximum replay count per test trial.
MAX_REPLAYS = 3

# Maximum learning plays per tacton. This is independent of TACTON_POOL counts.
LEARNING_MAX_PLAYS = 5

# None means true random order; set an integer to make trial order reproducible.
RANDOM_SEED = None

# CSV outputs.
RESULTS_CSV = "motor_drv2605_tacton_experiment_results.csv"
SEQUENCE_CSV_TEMPLATE = "motor_drv2605_tacton_experiment_sequence_{session_id}.csv"
LEARNING_CSV = "motor_drv2605_tacton_learning_results.csv"
