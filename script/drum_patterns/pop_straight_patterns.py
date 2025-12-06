from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

# PATTERNS: pattern name -> drum_class -> 16-step string ('x' = Hit, '-' = Pause)
PATTERNS: Dict[str, Dict[str, str]] = {
    "pop_straight_01_basic": {
        # Kick auf 1 und 3, Snare 2/4, Hi-Hat Achtel
        "KICK": "x-------x-------",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_straight_02_kick_syncopated": {
        # Zusätzliche Kicks auf &2 und &4, Crash auf 1
        "KICK": "x-----x-x-----x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "CRASH": "x---------------",
    },
    "pop_straight_03_drive": {
        # Kick auf 1, &1, 3, &3, Open Hat auf &4
        "KICK": "x-x-----x-x-----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "--------------x-",
    },
    "pop_straight_04_syncopated": {
        # Mehr Synkopen (a1, &2, a3)
        "KICK": "x--x--x-x--x----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_straight_05_16th_hats": {
        # 16tel-HiHats, etwas busier Kick
        "KICK": "x--x--x-x-----x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "pop_straight_06_sidestick_verse": {
        # Vers-artig: Sidestick auf 2, Snare auf 4
        "KICK": "x-----x-x-------",
        "SNARE": "------------x---",
        "SIDESTICK": "----x-----------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "pop_straight_07_pre_chorus": {
        # dichterer Pre-Chorus, Open Hat Akzent vor 4
        "KICK": "x--x--x-x-x---x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "-------------x--",
    },
    "pop_straight_08_chorus_four_on_floor": {
        # Four-on-the-floor Kick, Ride statt HH, Crash auf 1
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "RIDE": "x-x-x-x-x-x-x-x-",
        "CRASH": "x---------------",
    },
    "pop_straight_09_tom_pickup": {
        # Tom-Lauf am Ende des Takts als Pickup
        "KICK": "x-------x-------",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "TOM_LOW": "------------x---",
        "TOM_MID": "-------------x--",
        "TOM_HIGH": "--------------x-",
    },
    "pop_straight_10_broken_hats": {
        # Gebrochene HH-Figur, moderner Pop-Vibe
        "KICK": "x-----x-x-----x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
}
