from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"rnb_pop_01_laid_back": {
        # Leicht nach hinten gelehnt
        "KICK": "x-----x---x--x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "rnb_pop_02_half_time": {
        # Halftime-Snare auf 3
        "KICK": "x-------x-----x-",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "rnb_pop_03_ghost_snare": {
        # Ghostnotes auf der Snare
        "KICK": "x-----x-x---x---",
        "SNARE": "--x--x---x---x--",
        "HH_CLOSED": "x---x---x---x---",
    },
    "rnb_pop_04_sparse_verse": {
        # Viel Raum für Vocals
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "rnb_pop_05_triplet_flavor": {
        # Angedeutetes Triolen-Feeling im Raster
        "KICK": "x--x--x-----x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "rnb_pop_06_clap_backbeat": {
        # Dicker Backbeat
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "rnb_pop_07_snare_on_a": {
        # Snare-Varianten auf Offbeats
        "KICK": "x---x---x---x---",
        "SNARE": "---x---x---x----",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "rnb_pop_08_hat_groove": {
        # Hats mit kleinen Lücken
        "KICK": "x-----x---x--x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xx-xxx-xxx-xxx-x",
    },
    "rnb_pop_09_tom_pickups": {
        # Toms als Pickup-Notes
        "KICK": "x-----x---x--x--",
        "SNARE": "----x-------x---",
        "TOM_LOW": "------x---------",
        "TOM_MID": "------------x---",
        "HH_CLOSED": "x---x---x---x---",
    },
    "rnb_pop_10_bridge_half_time": {
        # Halftime-Bridge mit Ghostnotes
        "KICK": "x-------x-----x-",
        "SNARE": "--x---x-x---x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    }
}