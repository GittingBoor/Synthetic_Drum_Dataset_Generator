from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"latin_pop_01_clave_like": {
        # Clave-inspirierter Backbeat
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-----x---x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_02_tom_groove": {
        # Toms tragen den Groove
        "KICK": "x--x--x---x-----",
        "SNARE": "--------x-------",
        "TOM_LOW": "----x-----x---x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_03_open_hat_offbeat": {
        # Open Hats auf Offbeats
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-----x---x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x-----x-----",
    },
    "latin_pop_04_samba_flavor": {
        # Etwas Samba-inspiriert im 16tel-Raster
        "KICK": "x-x---x-x---x---",
        "SNARE": "----x-----x---x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_05_percussive_toms": {
        # Mehr Toms, weniger Snare
        "KICK": "x--x--x---x-----",
        "SNARE": "--------x-------",
        "TOM_LOW": "--x-----x-----x-",
        "TOM_MID": "------x-----x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_06_crash_intro": {
        # Intro mit Crash
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-----x---x-",
        "CRASH": "x---------------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_07_ride_pattern": {
        # Ride-Betonung statt HH
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-----x---x-",
        "RIDE": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_08_sparse_verse": {
        # Vers mit viel Luft
        "KICK": "x--------x------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "latin_pop_09_half_time": {
        # Latin-Halftime-Variante
        "KICK": "x--x--x---x-----",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "latin_pop_10_fill_turnaround": {
        # Fill am Ende des Taktes
        "KICK": "x--x--x---x-----",
        "SNARE": "----x-----x--xx-",
        "TOM_LOW": "------------x---",
        "TOM_MID": "--------------x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    }
}