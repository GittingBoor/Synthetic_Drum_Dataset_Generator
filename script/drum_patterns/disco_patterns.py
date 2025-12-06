from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
    "disco_01_classic": {
        # Four-on-the-floor + Offbeat Open Hats
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_02_pure_offbeat_open": {
        # Closed nur auf Downbeats, Open auf Offbeats
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_03_ride_chorus": {
        # Ride spielt Puls, Open-HH Offbeats
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "RIDE": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_04_kick_anticipations": {
        # Kick mit Antizipationen, immer noch Disco-Groove
        "KICK": "x-xxx-xxx-xxx-xx",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_05_snare_strong": {
        # Standard-Disco mit starkem Backbeat
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "disco_06_breakdown": {
        # Breakdown: kein Snare auf 2, nur auf 4 + Offbeat-Open-Hats
        "KICK": "x---x---x---x---",
        "SNARE": "------------x---",
        "HH_CLOSED": "----------------",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_07_buildup_16th": {
        # 16tel-HH als Build-Up
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
    "disco_08_big_chorus": {
        # Großer Chorus: Crash auf jeder 1
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
        "CRASH": "x---x---x---x---",
    },
    "disco_09_tom_fill": {
        # Tom-Fill in Beat 4
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
        "TOM_LOW": "------------xx--",
        "TOM_MID": "--------------xx",
    },
    "disco_10_ride_bell": {
        # Ride-Bell Offbeats + Open-HH Offbeats
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "RIDE": "-x-x-x-x-x-x-x-x",
        "HH_OPEN": "-x-x-x-x-x-x-x-x",
    },
}
