from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"funk_pop_01_syncopated": {
        # Funky Kick-Syncopes
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "funk_pop_02_snare_offbeat": {
        # Snare auf „e“ und „a“
        "KICK": "x--x--x---x-x---",
        "SNARE": "--x---x-----x-x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "funk_pop_03_busydrums": {
        # Sehr busy, viel Bewegung
        "KICK": "x-x-x---x-x---x-",
        "SNARE": "--x---x---x---x-",
        "HH_CLOSED": "x-xx-xx-xx-xx-x-",
    },
    "funk_pop_04_minimal_hat": {
        # Funk mit minimalen Hats
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "funk_pop_05_tight_verse": {
        # Straffer Funk-Vers
        "KICK": "x--x----x--x----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "funk_pop_06_chorus_open_hat": {
        # Open Hats im Chorus
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x-------x---",
    },
    "funk_pop_07_tom_answer": {
        # Toms als Antwort auf Snare
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "----x-------x---",
        "TOM_LOW": "------x---------",
        "TOM_MID": "------------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "funk_pop_08_ghost_grid": {
        # Ghost-Snare als Raster
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "x-x-x-x-x-x-x-x-",
        "HH_CLOSED": "x---x---x---x---",
    },
    "funk_pop_09_half_time_chorus": {
        # Halftime-Chorus mit Funk-Kicks
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "funk_pop_10_fill_on_last_bar": {
        # Fill-lastiger Takt
        "KICK": "x--x--x-x--x-x--",
        "SNARE": "----x-------xxxx",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "TOM_LOW": "--------------x-",
    }
}