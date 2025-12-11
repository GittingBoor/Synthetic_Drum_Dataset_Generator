from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
"synth_pop_01_80s_eight_hats": {
        # Achtel-Hats, klassischer 80s-Pop
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "synth_pop_02_clap_on_234": {
        # Etwas dichtere Snare/Clap-Figur
        "KICK": "x---x---x---x---",
        "SNARE": "----x---x---x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "synth_pop_03_sidechain_kick": {
        # Kick etwas zerpflückt für Sidechain-Gefühl
        "KICK": "x--x-x--x--x-x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "synth_pop_04_snare_on_e": {
        # Snare-Variation auf Offbeats
        "KICK": "x---x---x---x---",
        "SNARE": "--x--x-----x--x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "synth_pop_05_open_hat_chorus": {
        # Open Hat in den Chorussen
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "HH_OPEN": "----x-------x---",
    },
    "synth_pop_06_tom_build": {
        # Tom-orientiertes Build-Up
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
        "TOM_LOW": "--x-----x-----x-",
        "TOM_MID": "------x-----x---",
    },
    "synth_pop_07_soft_verse": {
        # Zurückhaltender Vers
        "KICK": "x-------x-------",
        "SNARE": "--------x-------",
        "HH_CLOSED": "x---x---x---x---",
    },
    "synth_pop_08_drive_prechorus": {
        # Mehr Drive im Pre-Chorus
        "KICK": "x---x-x-x---x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "synth_pop_09_syncopated_snare": {
        # Synkopierte Snare-Figur
        "KICK": "x---x---x---x---",
        "SNARE": "--x-----x-----x-",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    },
    "synth_pop_10_clap_fill": {
        # Kleiner Clap-/Snare-Fill am Ende
        "KICK": "x---x---x---x---",
        "SNARE": "----x-------xxxx",
        "HH_CLOSED": "x-x-x-x-x-x-x-x-",
    }
}