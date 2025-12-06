from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
    "shuffle_01_basic_half_time": {
        # Half-Time-Backbeat (Snare auf 3), „shufflige“ HHs
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_02_rosanna_flavor": {
        # angelehnt an Rosanna-Feeling: ghostige Snares, synkopierte Kicks
        "KICK": "x-x-----x-x---x-",
        "SNARE": "------x-x-x---x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_03_purdie_like": {
        # viele Ghostnotes, inspiriert vom Purdie-Shuffle
        "KICK": "x-----x-x-----x-",
        "SNARE": "--x--x-xx-x--x-x",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_04_light_verse": {
        # leichte Vers-Variante mit wenigen Ghosts
        "KICK": "x-------x-------",
        "SNARE": "--------x-----x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_05_heavy_chorus": {
        # dichterer Chorus, Crash auf der 3
        "KICK": "x-x-----x-x---x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "CRASH": "--------x-------",
    },
    "shuffle_06_tom_fill": {
        # Tom-Fill in der zweiten Hälfte
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "TOM_LOW": "---------xx-----",
        "TOM_MID": "----------xx----",
    },
    "shuffle_07_ride": {
        # Ride-Shuffle mit Half-Time-Backbeat
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "RIDE": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_08_ghost_ladder": {
        # viele Ghostnotes Richtung Backbeat
        "KICK": "x-x-----x-x---x-",
        "SNARE": "--x-x-xxx-x-x-xx",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_09_straight_kick_shuffled_hat": {
        # Kick wie Straight-Pop, aber HH im Shuffle
        "KICK": "x-----x-x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "shuffle_10_breakdown": {
        # Breakdown: nur Kick 1 + ghostige Snares
        "KICK": "x---------------",
        "SNARE": "--x-x-x-x---x-x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
}
