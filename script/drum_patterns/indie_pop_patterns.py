from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"indie_pop_01_simple_groove": {
        # Einfacher Indie-Vers
        "KICK": "x-----x---x-----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_02_open_hat_chorus": {
        # Mehr Energie im Chorus
        "KICK": "x---x-----x---x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x---x-------",
    },
    "indie_pop_03_tom_groove": {
        # Toms im Groove
        "KICK": "x---x-----x---x-",
        "SNARE": "--------x-------",
        "TOM_LOW": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_04_lofi_verse": {
        # Zurückhaltend, lofi-artig
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "indie_pop_05_syncopated_kick": {
        # Leicht versetzte Kicks
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_06_crash_intro": {
        # Intro mit Crash
        "KICK": "x---x-------x---",
        "SNARE": "----x-------x---",
        "CRASH": "x---------------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_07_ride_chorus": {
        # Ride anstatt HH im Chorus
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "RIDE": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_08_sparse_toms": {
        # Luftiges Tom-Pattern
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "TOM_LOW": "----x-----------",
        "TOM_MID": "------------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_09_half_time": {
        # Halbzeit-Groove für Bridge
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "indie_pop_10_end_fill": {
        # Kurzer Fill am Taktende
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x-xx",
        "TOM_LOW": "--------------x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    }
}