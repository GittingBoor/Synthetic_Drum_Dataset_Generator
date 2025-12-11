from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"electropop_01_floor_open_hat": {
        # Floor mit Open Hat
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x-------x---",
    },
    "electropop_02_busy_kicks": {
        # Dichte elektronische Kick-Figur
        "KICK": "x-x-x-x-x-x-x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "electropop_03_build_constant_hats": {
        # Dauer-Hats für Build-Up
        "KICK": "x---x---x---x---",
        "SNARE": "--------x-------",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "electropop_04_snare_roll_end": {
        # Snare-Roll auf den letzten 4 Steps
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------xxxx",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "electropop_05_half_time_drop": {
        # Halftime-Feeling im Drop
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "electropop_06_sidechain_like": {
        # Stärker geslicete Kick-Struktur
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "electropop_07_clap_on_234": {
        # Clap-artige Snare auf 2, 3 und 4
        "KICK": "x---x---x---x---",
        "SNARE": "----x---x---x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "electropop_08_crash_and_ride": {
        # Crash auf 1, Ride im Verlauf
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "CRASH": "x---------------",
        "RIDE": "----x---x---x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "electropop_09_sparse_verse": {
        # Minimalistischer Vers
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "electropop_10_pre_drop_fill": {
        # Fills auf den letzten Achteln
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x-xx",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    }
}