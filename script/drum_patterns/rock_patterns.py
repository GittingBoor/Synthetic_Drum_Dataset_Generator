from __future__ import annotations
from typing import Dict

STEP_RESOLUTION: int = 16

PATTERNS: Dict[str, Dict[str, str]] = {
    "rock16_01_basic": {
        # 16tel-HH, simple Pop-Rock-Kick + extra Kick auf &4
        "KICK": "x-------x-----x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "rock16_02_syncopated": {
        # mehr Synkopen in der Bassdrum
        "KICK": "x--x--x-x----x--",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "rock16_03_californication_like": {
        # inspiriert von Kick auf 1 und &3, Ghost-Snares dazwischen
        "KICK": "x--------x------",
        "SNARE": "----x-x---x--x-x",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "rock16_04_hat_accents": {
        # HH-Doppelungen als Akzente
        "KICK": "x-----x-x-----x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-xxx-xxx-xxx-xx",
    },
    "rock16_05_broken_hat_riff": {
        # gebrochene HH-Figur, 3-gegen-4-Feeling
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "x-x--x-xx-x--x-x",
    },
    "rock16_06_chorus_drive": {
        # dichter Chorus-Kick
        "KICK": "x-xx--x-x-xx--x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "rock16_07_half_time_feel": {
        # Half-Time-Backbeat auf 3, aber 16tel-HH
        "KICK": "x---x--x----x--x",
        "SNARE": "--------x-------",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
    },
    "rock16_08_pre_chorus_build": {
        # Build-up, viele Kicks am Ende
        "KICK": "x-----x-x-x-x-x-",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxx-xxxxxxx-xx",
    },
    "rock16_09_tom_groove": {
        # 16tel-HH, Tom-Figur auf 3
        "KICK": "x-------x--x----",
        "SNARE": "----x-------x---",
        "HH_CLOSED": "xxxxxxxxxxxxxxxx",
        "TOM_LOW": "--------xxxx----",
    },
    "rock16_10_ride_variant": {
        # Ride-Variante, Open Hat am Ende
        "KICK": "x--x--x-x--x--x-",
        "SNARE": "----x-------x---",
        "RIDE": "xxxxxxxxxxxxxxxx",
        "HH_OPEN": "--------------x-",
    },
}
