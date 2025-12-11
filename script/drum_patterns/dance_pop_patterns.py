from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"dance_pop_01_four_on_floor_basic": {
        # Klassisches Four-on-the-Floor, tighter Pop-Beat
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "dance_pop_02_four_on_floor_offhats": {
        # Offbeat-Hi-Hats für mehr Club-Feeling
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "-x-x-x-x-x-x-x-x",
    },
    "dance_pop_03_synced_kicks": {
        # Synkopierte Kicks, Chorus-tauglich
        "KICK": "x-x---x-x---x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "dance_pop_04_crash_on_one": {
        # Crash auf der 1, typischer Song-Beginn
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "CRASH": "x---------------",
    },
    "dance_pop_05_build_up_eights": {
        # Durchlaufende Achtel-Hats für Build-Ups
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "dance_pop_06_break_with_clap": {
        # Weniger Kicks, Snare/Clap im Vordergrund
        "KICK": "x-------x-------",
        "SNARE": "----x---x---x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "dance_pop_07_prechorus_light": {
        # Leichter Pre-Chorus mit weniger Kick-Dichte
        "KICK": "x---x-------x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-------x-x---",
    },
    "dance_pop_08_drop_dense_kick": {
        # Dichte Kick-Figur im Drop
        "KICK": "x-x-x-x---x-x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "dance_pop_09_open_hat_chorus": {
        # Offene Hats auf 2 und 4
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x-------x---",
    },
    "dance_pop_10_tom_fill_turnaround": {
        # Fill am Ende des Taktes
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "TOM_LOW": "------------x---",
        "TOM_MID": "--------------x-",
    }
}