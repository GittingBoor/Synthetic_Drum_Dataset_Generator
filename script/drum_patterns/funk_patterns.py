from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
    "funk_01_basic": {
        # 16tel-HH, typisch synkopierte Funk-Kicks
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "funk_02_linear_flavor": {
        # eher linear, Hände füllen viele 16tel
        "KICK": "x-xx----x-xx----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "-x-xx-x--x-xx-x-",
    },
    "funk_03_ghosts_between": {
        # Ghost-Snares zwischen 2 und 3
        "KICK": "x-----x-x--x----",
        "SNARE": "----x-x---x-x-x-",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "funk_04_open_hat_offbeats": {
        # Open-HH auf Offbeats 2 und 4
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "------x-------x-",
    },
    "funk_05_sparse_hat_busy_kick": {
        # wenige HH-Schläge, sehr busy Kick
        "KICK": "x-xx-x-xx-xx-x-x",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "funk_06_snare_displaced": {
        # Snares teils von 2/4 verschoben
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "-----x----x-x--x",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "funk_07_hat_barks": {
        # kurze Open-HH-Barks
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
        "HH_OPEN": "---x--x----x--x-",
    },
    "funk_08_tom_linear": {
        # lineare Tom-Läufe um Schlag 3
        "KICK": "x--x----x--x----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
        "TOM_LOW": "--------xx------",
        "TOM_MID": "----------xx----",
    },
    "funk_09_busy_hands": {
        # Hände füllen fast alle 16tel mit Snare+HH
        "KICK": "x-----x-x-----x-",
        "SNARE": "--x-x-x--x-xx-x-",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "funk_10_ghost_ladder": {
        # „Ladder“ aus Ghostnotes in Richtung Backbeat
        "KICK": "x-xx--x-x-xx--x-",
        "SNARE": "--x-x-xx--x-x-xx",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
}
