from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"pop_rock_01_standard_rock": {
        # Standard-Pop-Rock-Beat
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_02_drive_eights": {
        # Voll durchgezogene Achtel-Hats
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "pop_rock_03_double_kick": {
        # Doppelte Kick vor der Snare
        "KICK": "x--x-x--x--x-x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_04_crash_on_chorus": {
        # Crash auf 1, sonst HH
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "CRASH": "x---------------",
        "HH_CLOSED": "-x-x-x-x-x-x-x-x",
    },
    "pop_rock_05_tom_build": {
        # Toms für Pre-Chorus/Build-Up
        "KICK": "x---x---x---x---",
        "SNARE": "--------x-------",
        "TOM_LOW": "----x-----x---x-",
        "TOM_MID": "------x-----x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_06_half_time": {
        # Halftime-Feeling
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_07_ride_chorus": {
        # Ride statt HH im Chorus
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "RIDE": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_08_verse_sparse": {
        # Reduzierter Vers
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "pop_rock_09_fill_end": {
        # Rock-Fill am Ende
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------xxxx",
        "TOM_LOW": "----------x-x-x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_rock_10_double_time_bridge": {
        # Double-Time-Bridge
        "KICK": "x-x-x-x-x-x-x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    }
}