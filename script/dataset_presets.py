from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class DatasetPreset:
    """Konfigurations-Preset für einen Datensatzlauf."""
    name: str
    tempo_bpm: float
    time_signature: Tuple[int, int]
    key: str
    style: str
    drum_complexity: float
    ghostnote_probability: float
    fill_probability: float
    swing_amount: float
    pause_probability: float
    min_instruments: int
    max_instruments: int


# Namensschema (Lesbarkeit ohne alle Werte anschauen zu müssen):
# <style>__<key>__T<tempo>__C<low|mid|high>__S<low|mid|high>__I<min>-<max>
#
# C = Drum-Komplexität grob:
#   low  ≈ 0.3
#   mid  ≈ 0.6
#   high ≈ 0.9
#
# S = Swing grob:
#   low  ≈ 0.1
#   mid  ≈ 0.3
#   high ≈ 0.5


DATASET_PRESETS: Dict[str, DatasetPreset] = {
    # ---------- POP, C major ----------
    "pop-straight__C-major__T120__Cmid__Smid__I4-8": DatasetPreset(
        name="pop-straight__C-major__T120__Cmid__Smid__I4-8",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.6,
        ghostnote_probability=0.3,
        fill_probability=0.3,
        swing_amount=0.3,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=8,
    ),
    "pop-straight__C-major__T100__Clow__Slow__I4-6": DatasetPreset(
        name="pop-straight__C-major__T100__Clow__Slow__I4-6",
        tempo_bpm=100.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.3,
        ghostnote_probability=0.2,
        fill_probability=0.2,
        swing_amount=0.1,
        pause_probability=0.5,
        min_instruments=4,
        max_instruments=6,
    ),
    "pop-straight__C-major__T140__Chigh__Smid__I5-8": DatasetPreset(
        name="pop-straight__C-major__T140__Chigh__Smid__I5-8",
        tempo_bpm=140.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.9,
        ghostnote_probability=0.5,
        fill_probability=0.4,
        swing_amount=0.3,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),

    # ---------- POP, A minor ----------
    "pop-straight__A-minor__T110__Cmid__Slow__I4-7": DatasetPreset(
        name="pop-straight__A-minor__T110__Cmid__Slow__I4-7",
        tempo_bpm=110.0,
        time_signature=(4, 4),
        key="A minor",
        style="pop-straight",
        drum_complexity=0.6,
        ghostnote_probability=0.3,
        fill_probability=0.3,
        swing_amount=0.1,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=7,
    ),
    "pop-straight__A-minor__T130__Chigh__Smid__I5-8": DatasetPreset(
        name="pop-straight__A-minor__T130__Chigh__Smid__I5-8",
        tempo_bpm=130.0,
        time_signature=(4, 4),
        key="A minor",
        style="pop-straight",
        drum_complexity=0.9,
        ghostnote_probability=0.5,
        fill_probability=0.4,
        swing_amount=0.3,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),

    # ---------- FUNK ----------
    "funk__C-major__T105__Chigh__Shigh__I4-7": DatasetPreset(
        name="funk__C-major__T105__Chigh__Shigh__I4-7",
        tempo_bpm=105.0,
        time_signature=(4, 4),
        key="C major",
        style="funk",
        drum_complexity=0.9,
        ghostnote_probability=0.6,
        fill_probability=0.4,
        swing_amount=0.5,
        pause_probability=0.3,
        min_instruments=4,
        max_instruments=7,
    ),
    "funk__A-minor__T115__Cmid__Shigh__I4-8": DatasetPreset(
        name="funk__A-minor__T115__Cmid__Shigh__I4-8",
        tempo_bpm=115.0,
        time_signature=(4, 4),
        key="A minor",
        style="funk",
        drum_complexity=0.7,
        ghostnote_probability=0.5,
        fill_probability=0.4,
        swing_amount=0.5,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=8,
    ),

    # ---------- DISCO ----------
    "disco__C-major__T128__Chigh__Smid__I5-8": DatasetPreset(
        name="disco__C-major__T128__Chigh__Smid__I5-8",
        tempo_bpm=128.0,
        time_signature=(4, 4),
        key="C major",
        style="disco",
        drum_complexity=0.9,
        ghostnote_probability=0.4,
        fill_probability=0.5,
        swing_amount=0.3,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),
    "disco__A-minor__T124__Cmid__Smid__I4-7": DatasetPreset(
        name="disco__A-minor__T124__Cmid__Smid__I4-7",
        tempo_bpm=124.0,
        time_signature=(4, 4),
        key="A minor",
        style="disco",
        drum_complexity=0.7,
        ghostnote_probability=0.3,
        fill_probability=0.4,
        swing_amount=0.3,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=7,
    ),

    # ---------- SHUFFLE ----------
    "shuffle__C-major__T95__Cmid__Shigh__I4-6": DatasetPreset(
        name="shuffle__C-major__T95__Cmid__Shigh__I4-6",
        tempo_bpm=95.0,
        time_signature=(4, 4),
        key="C major",
        style="shuffle",
        drum_complexity=0.6,
        ghostnote_probability=0.4,
        fill_probability=0.3,
        swing_amount=0.5,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=6,
    ),
    "shuffle__A-minor__T105__Chigh__Shigh__I5-8": DatasetPreset(
        name="shuffle__A-minor__T105__Chigh__Shigh__I5-8",
        tempo_bpm=105.0,
        time_signature=(4, 4),
        key="A minor",
        style="shuffle",
        drum_complexity=0.9,
        ghostnote_probability=0.5,
        fill_probability=0.4,
        swing_amount=0.5,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),

    # ---------- ROCK ----------
    "rock__C-major__T140__Chigh__Slow__I4-6": DatasetPreset(
        name="rock__C-major__T140__Chigh__Slow__I4-6",
        tempo_bpm=140.0,
        time_signature=(4, 4),
        key="C major",
        style="rock",
        drum_complexity=0.9,
        ghostnote_probability=0.3,
        fill_probability=0.4,
        swing_amount=0.1,
        pause_probability=0.3,
        min_instruments=4,
        max_instruments=6,
    ),
    "rock__A-minor__T150__Chigh__Slow__I4-7": DatasetPreset(
        name="rock__A-minor__T150__Chigh__Slow__I4-7",
        tempo_bpm=150.0,
        time_signature=(4, 4),
        key="A minor",
        style="rock",
        drum_complexity=0.9,
        ghostnote_probability=0.3,
        fill_probability=0.5,
        swing_amount=0.1,
        pause_probability=0.3,
        min_instruments=4,
        max_instruments=7,
    ),

    # ---------- ruhigere POP Varianten ----------
    "pop-straight__C-major__T90__Clow__Slow__I3-5": DatasetPreset(
        name="pop-straight__C-major__T90__Clow__Slow__I3-5",
        tempo_bpm=90.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.3,
        ghostnote_probability=0.2,
        fill_probability=0.2,
        swing_amount=0.1,
        pause_probability=0.5,
        min_instruments=3,
        max_instruments=5,
    ),
    "pop-straight__A-minor__T85__Clow__Slow__I3-5": DatasetPreset(
        name="pop-straight__A-minor__T85__Clow__Slow__I3-5",
        tempo_bpm=85.0,
        time_signature=(4, 4),
        key="A minor",
        style="pop-straight",
        drum_complexity=0.3,
        ghostnote_probability=0.2,
        fill_probability=0.2,
        swing_amount=0.1,
        pause_probability=0.5,
        min_instruments=3,
        max_instruments=5,
    ),

    # ---------- „busy“ POP ----------
    "pop-straight__C-major__T125__Chigh__Smid__I5-8": DatasetPreset(
        name="pop-straight__C-major__T125__Chigh__Smid__I5-8",
        tempo_bpm=125.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.9,
        ghostnote_probability=0.5,
        fill_probability=0.5,
        swing_amount=0.3,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),
    "pop-straight__A-minor__T135__Chigh__Smid__I5-8": DatasetPreset(
        name="pop-straight__A-minor__T135__Chigh__Smid__I5-8",
        tempo_bpm=135.0,
        time_signature=(4, 4),
        key="A minor",
        style="pop-straight",
        drum_complexity=0.9,
        ghostnote_probability=0.5,
        fill_probability=0.5,
        swing_amount=0.3,
        pause_probability=0.3,
        min_instruments=5,
        max_instruments=8,
    ),

    # ---------- leicht geshuffelte POP Varianten ----------
    "pop-straight__C-major__T115__Cmid__Smid__I4-7": DatasetPreset(
        name="pop-straight__C-major__T115__Cmid__Smid__I4-7",
        tempo_bpm=115.0,
        time_signature=(4, 4),
        key="C major",
        style="pop-straight",
        drum_complexity=0.6,
        ghostnote_probability=0.3,
        fill_probability=0.3,
        swing_amount=0.3,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=7,
    ),
    "pop-straight__A-minor__T118__Cmid__Smid__I4-7": DatasetPreset(
        name="pop-straight__A-minor__T118__Cmid__Smid__I4-7",
        tempo_bpm=118.0,
        time_signature=(4, 4),
        key="A minor",
        style="pop-straight",
        drum_complexity=0.6,
        ghostnote_probability=0.3,
        fill_probability=0.3,
        swing_amount=0.3,
        pause_probability=0.4,
        min_instruments=4,
        max_instruments=7,
    ),
}
