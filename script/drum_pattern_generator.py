from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import random

import numpy as np
import muspy

from .drum_mapping import DrumMapping
from .song_specification import SongSpecification
from .band_configuration import BandConfiguration
from .instrument import Instrument

from .drum_patterns import (
    pop_straight_patterns,
    rock_patterns,
    funk_patterns,
    disco_patterns,
    shuffle_patterns,
)


@dataclass
class DrumEvent:
    """Repräsentiert ein einzelnes Drum-Ereignis."""
    time_sec: float
    drum_class: str
    velocity: int


class DrumPatternGenerator:
    """Erzeugt Drum-Pattern für eine gegebene SongSpecification."""

    def __init__(
            self,
            drum_mapping: DrumMapping,
            complexity: float,
            ghostnote_probability: float,
            fill_probability: float,
            swing_amount: float,
            pause_probability: float,
    ) -> None:
        """Konstruktor mit allen Parametern für die Drum-Generierung.

        pause_probability:
            Basiswahrscheinlichkeit (0–1), dass in einem Takt eine kurze Pause
            eingefügt wird (unabhängig von der Komplexität).
        """
        self.drum_mapping: DrumMapping = drum_mapping
        self.complexity: float = float(complexity)
        self.ghostnote_probability: float = float(ghostnote_probability)
        self.fill_probability: float = float(fill_probability)
        self.swing_amount: float = float(swing_amount)
        self.pause_probability: float = float(pause_probability)
        self.step_resolution: int = 16  # 16 Steps pro Takt (1 e & a etc.)

    # ------------------------------------------------------------------ #
    # Hilfsfunktionen für Pattern-Auswahl und -Mutation
    # ------------------------------------------------------------------ #

    def _select_pattern_library(
        self, style: str | None
    ) -> tuple[Dict[str, Dict[str, str]], int]:
        """Wählt je nach Stil das passende Pattern-Lexikon aus."""
        style = (style or "").lower()

        if "funk" in style:
            return funk_patterns.PATTERNS, funk_patterns.STEP_RESOLUTION
        if "disco" in style:
            return disco_patterns.PATTERNS, disco_patterns.STEP_RESOLUTION
        if "shuffle" in style:
            return (
                shuffle_patterns.PATTERNS,
                shuffle_patterns.STEP_RESOLUTION,
            )
        if "rock" in style:
            return (
                rock_patterns.PATTERNS,
                rock_patterns.STEP_RESOLUTION,
            )

        # Default: moderner Pop
        return pop_straight_patterns.PATTERNS, pop_straight_patterns.STEP_RESOLUTION

    @staticmethod
    def _pattern_str_to_array(pattern: str, subdivisions: int) -> np.ndarray:
        """Konvertiert 'x'/'-' Patternstring in ein bool-Array der Länge subdivisions."""
        arr = np.zeros(subdivisions, dtype=bool)
        for i, ch in enumerate(pattern[:subdivisions]):
            arr[i] = (ch.lower() == "x")
        return arr

    def _pattern_dict_to_arrays(
        self, pattern_dict: Dict[str, str], subdivisions: int
    ) -> Dict[str, np.ndarray]:
        """Wandelt ein Pattern (drum_class -> String) in drum_class -> bool-Array um."""
        return {
            drum_class: self._pattern_str_to_array(step_str, subdivisions)
            for drum_class, step_str in pattern_dict.items()
        }

    def _mutate_bar_arrays(
            self,
            arrays: dict[str, np.ndarray],
            complexity: float,
    ) -> dict[str, np.ndarray]:
        """Mutiert ein Bar-Pattern (Shift, Toggles, HH-Reduktion, evtl. Open Hats)."""
        if complexity <= 0.0:
            return {k: v.copy() for k, v in arrays.items()}

        mutated: dict[str, np.ndarray] = {}
        shift_prob = 0.4 * complexity  # vorher 0.3
        toggle_prob = 0.6 * complexity  # vorher 0.4
        hh_open_merge: np.ndarray | None = None

        for drum_class, arr in arrays.items():
            a = arr.copy()

            # --- 1) kleine Shifts (alles leicht nach links/rechts versetzen) ---
            if random.random() < shift_prob and a.any():
                max_shift = 2  # bis zu 2 Steps
                shift = random.randint(-max_shift, max_shift)
                if shift != 0:
                    indices = np.flatnonzero(a)
                    new_a = np.zeros_like(a)
                    new_idx = indices + shift
                    new_idx = new_idx[(new_idx >= 0) & (new_idx < len(a))]
                    new_a[new_idx] = True
                    a = new_a

            # --- 2) Hits ein-/ausschalten (deutlich mehr Variation) ---
            if random.random() < toggle_prob:
                n_toggles = max(1, int(len(a) * 0.1 * (0.5 + complexity)))
                for _ in range(n_toggles):
                    idx = random.randrange(len(a))
                    a[idx] = ~a[idx]

            # --- 3) Spezielle Behandlung für geschlossene Hi-Hat ---
            if drum_class == "HH_CLOSED":
                fill_ratio = a.mean()

                # a) Wenn extrem dicht (z.B. 16tel-Dauerfeuer) → dünner machen
                if fill_ratio > 0.7:
                    mode = random.choice(["eighths", "offbeat", "broken"])
                    if mode == "eighths":
                        # Nur jede 2. 16tel behalten → Achtel
                        a[1::2] = False
                    elif mode == "offbeat":
                        # Nur Offbeats behalten
                        a[::2] = False
                    else:  # "broken"
                        # Gebrochenes Muster als Maske
                        mask = np.array(
                            [1, 0, 1, 0, 0, 1, 0, 0,
                             1, 0, 1, 0, 0, 1, 0, 0],
                            dtype=bool,
                        )
                        if len(mask) != len(a):
                            mask = np.resize(mask, a.shape)
                        a = a & mask

                # b) Bei hoher complexity ein paar geschlossene HH → Open HH
                if complexity > 0.5 and a.any():
                    open_prob = 0.3 * complexity
                    if random.random() < open_prob:
                        idxs = np.flatnonzero(a)
                        n_open = max(1, int(len(idxs) * 0.2 * complexity))
                        open_idxs = np.random.choice(idxs, size=n_open, replace=False)
                        a_open = np.zeros_like(a)
                        a_open[open_idxs] = True
                        a[open_idxs] = False
                        if hh_open_merge is None:
                            hh_open_merge = a_open
                        else:
                            hh_open_merge = hh_open_merge | a_open

            mutated[drum_class] = a

        # Falls wir neue Open-Hats erzeugt haben:
        if hh_open_merge is not None:
            existing = mutated.get("HH_OPEN")
            if existing is None:
                mutated["HH_OPEN"] = hh_open_merge
            else:
                mutated["HH_OPEN"] = existing | hh_open_merge

        return mutated

    def _arrays_to_events(
        self,
        arrays: Dict[str, np.ndarray],
        bar_start: float,
        seconds_per_bar: float,
    ) -> List[DrumEvent]:
        """Konvertiert ein Bar-Pattern (Arrays) in DrumEvents."""
        events: List[DrumEvent] = []
        subdivisions = self.step_resolution
        step_duration = seconds_per_bar / subdivisions

        base_velocity = {
            "KICK": 100,
            "SNARE": 95,
            "SIDESTICK": 85,
            "HH_CLOSED": 80,
            "HH_OPEN": 85,
            "TOM_LOW": 100,
            "TOM_MID": 100,
            "TOM_HIGH": 100,
            "RIDE": 80,
            "CRASH": 110,
        }

        for drum_class, arr in arrays.items():
            vel = base_velocity.get(drum_class, 90)
            for step_idx, is_hit in enumerate(arr):
                if not is_hit:
                    continue
                time_sec = bar_start + step_idx * step_duration
                events.append(
                    DrumEvent(
                        time_sec=time_sec,
                        drum_class=drum_class,
                        velocity=vel,
                    )
                )
        return events

    @staticmethod
    def _compute_timing(song_spec: SongSpecification) -> tuple[float, float, float]:
        """Hilfsfunktion: Liefert (beats_per_bar, seconds_per_beat, seconds_per_bar)."""
        numerator, denominator = song_spec.time_signature
        beats_per_bar = numerator * (4.0 / float(denominator))
        seconds_per_beat = 60.0 / song_spec.tempo_bpm
        seconds_per_bar = beats_per_bar * seconds_per_beat
        return beats_per_bar, seconds_per_beat, seconds_per_bar

    def _add_ghostnotes_for_bar(
            self,
            snare_steps: np.ndarray | None,
            bar_start: float,
            seconds_per_bar: float,
    ) -> list[DrumEvent]:
        """Fügt abhängig von complexity/ghostnote_probability Snare-Ghostnotes hinzu."""
        if (
                self.ghostnote_probability <= 0.0
                or self.complexity <= 0.2
                or snare_steps is None
        ):
            return []

        subdivisions = self.step_resolution
        step_duration = seconds_per_bar / subdivisions
        events: list[DrumEvent] = []

        # stärkere Abhängigkeit von complexity
        base_p = self.ghostnote_probability * (0.2 + 0.8 * (self.complexity ** 1.2))

        for idx in range(subdivisions):
            if snare_steps[idx]:
                continue  # keine Ghostnote direkt auf dem Backbeat
            neighborhood = snare_steps[max(0, idx - 2): min(subdivisions, idx + 3)]
            if not neighborhood.any():
                continue
            if random.random() < base_p:
                time_sec = bar_start + idx * step_duration
                events.append(
                    DrumEvent(
                        time_sec=time_sec,
                        drum_class="SNARE",
                        velocity=45 if self.complexity < 0.8 else 50,
                    )
                )

        return events

    def _choose_pattern_name(
        self,
        patterns_dict: dict[str, dict[str, str]],
    ) -> str:
        """Wählt ein Pattern abhängig von complexity (dichter vs. simpler)."""
        names = list(patterns_dict.keys())
        densities: list[float] = []

        for name in names:
            pat = patterns_dict[name]
            # Dichte = Anzahl Hits (x) über alle Drums
            density = sum(s.count("x") for s in pat.values())
            densities.append(float(density) if density > 0 else 1.0)

        densities_arr = np.array(densities, dtype=float)
        max_d = float(densities_arr.max())
        if max_d <= 0:
            return random.choice(names)

        # Gewichte: bei hoher complexity → dichter Patterns bevorzugen,
        # bei niedriger complexity → eher einfache Patterns.
        norm = densities_arr / max_d
        # Exponent macht die Kurve "spitzer" bei hoher Komplexität
        exp = 0.5 + 1.5 * self.complexity
        weights_dense = norm**exp
        weights_simple = (1.0 - norm) ** exp
        # Mische zwischen "simpel" und "dicht" je nach complexity
        weights = (1.0 - self.complexity) * weights_simple + self.complexity * weights_dense
        weights = weights / weights.sum()

        # Kleine Chance auf komplett random Pattern, damit es nicht zu berechenbar wird
        if random.random() < 0.1 * self.complexity:
            return random.choice(names)

        r = random.random()
        cum = 0.0
        for name, w in zip(names, weights):
            cum += w
            if r <= cum:
                return name
        return names[-1]

    def _insert_random_pause(
        self,
        arrays: dict[str, np.ndarray],
    ) -> dict[str, np.ndarray]:
        """Fügt optional eine kurze globale Pause (alle Drums) in den Takt ein.

        Die Pausenlänge wird so gewählt, dass 1/4 und 1/8 am häufigsten vorkommen,
        1/16 und 1/2 dagegen eher selten. Die Wahrscheinlichkeit hängt nur von
        self.pause_probability ab, NICHT von der Komplexität.
        """
        if self.pause_probability <= 0.0 or not arrays:
            return arrays

        # Entscheide überhaupt, ob in diesem Takt eine Pause kommt
        if random.random() > self.pause_probability:
            return arrays

        subdivisions = self.step_resolution
        if subdivisions <= 0:
            return arrays

        # Mögliche Pausenlängen (in Steps) mit Gewichtung:
        # 1/16 (selten), 1/8, 1/4 (am häufigsten), 1/2 (selten)
        len_16 = max(1, subdivisions // 16)
        len_8 = max(1, subdivisions // 8)
        len_4 = max(1, subdivisions // 4)
        len_2 = max(1, subdivisions // 2)

        pause_lengths = [len_16, len_8, len_4, len_2]
        pause_weights = [0.05, 0.35, 0.45, 0.15]  # sum ~ 1.0

        r = random.random()
        cum = 0.0
        chosen_len = pause_lengths[-1]
        for length, w in zip(pause_lengths, pause_weights):
            cum += w
            if r <= cum:
                chosen_len = length
                break

        # Startposition für die Pause wählen
        max_start = max(0, subdivisions - chosen_len)
        if max_start <= 0:
            start = 0
        else:
            start = random.randint(0, max_start)

        end = start + chosen_len

        # In allen Drum-Spuren die gewählten Steps stummschalten
        paused: dict[str, np.ndarray] = {}
        for drum_class, arr in arrays.items():
            a = arr.copy()
            a[start:end] = False
            paused[drum_class] = a

        return paused

    def _mutate_bar_arrays(
            self,
            arrays: dict[str, np.ndarray],
            complexity: float,
    ) -> dict[str, np.ndarray]:
        """Mutiert ein Bar-Pattern (Shift, Toggles, HH-Reduktion, evtl. Open Hats, Pausen)."""
        # Auch bei complexity <= 0 sollen Pausen möglich sein → erst Kopie, danach Pause.
        if complexity <= 0.0:
            base = {k: v.copy() for k, v in arrays.items()}
            return self._insert_random_pause(base)

        mutated: dict[str, np.ndarray] = {}
        shift_prob = 0.4 * complexity  # vorher 0.3
        toggle_prob = 0.6 * complexity  # vorher 0.4
        hh_open_merge: np.ndarray | None = None

        for drum_class, arr in arrays.items():
            a = arr.copy()

            # --- 1) kleine Shifts (alles leicht nach links/rechts versetzen) ---
            if random.random() < shift_prob and a.any():
                max_shift = 2  # bis zu 2 Steps
                shift = random.randint(-max_shift, max_shift)
                if shift != 0:
                    indices = np.flatnonzero(a)
                    new_a = np.zeros_like(a)
                    new_idx = indices + shift
                    new_idx = new_idx[(new_idx >= 0) & (new_idx < len(a))]
                    new_a[new_idx] = True
                    a = new_a

            # --- 2) Hits ein-/ausschalten (deutlich mehr Variation) ---
            if random.random() < toggle_prob:
                n_toggles = max(1, int(len(a) * 0.1 * (0.5 + complexity)))
                for _ in range(n_toggles):
                    idx = random.randrange(len(a))
                    a[idx] = ~a[idx]

            # --- 3) Spezielle Behandlung für geschlossene Hi-Hat ---
            if drum_class == "HH_CLOSED":
                fill_ratio = a.mean()

                # a) Wenn extrem dicht (z.B. 16tel-Dauerfeuer) → dünner machen
                if fill_ratio > 0.7:
                    mode = random.choice(["eighths", "offbeat", "broken"])
                    if mode == "eighths":
                        # Nur jede 2. 16tel behalten → Achtel
                        a[1::2] = False
                    elif mode == "offbeat":
                        # Nur Offbeats behalten
                        a[::2] = False
                    else:  # "broken"
                        # Gebrochenes Muster als Maske
                        mask = np.array(
                            [1, 0, 1, 0, 0, 1, 0, 0,
                             1, 0, 1, 0, 0, 1, 0, 0],
                            dtype=bool,
                        )
                        if len(mask) != len(a):
                            mask = np.resize(mask, a.shape)
                        a = a & mask

                # b) Bei hoher complexity ein paar geschlossene HH → Open HH
                if complexity > 0.5 and a.any():
                    open_prob = 0.3 * complexity
                    if random.random() < open_prob:
                        idxs = np.flatnonzero(a)
                        n_open = max(1, int(len(idxs) * 0.2 * complexity))
                        open_idxs = np.random.choice(idxs, size=n_open, replace=False)
                        a_open = np.zeros_like(a)
                        a_open[open_idxs] = True
                        a[open_idxs] = False
                        if hh_open_merge is None:
                            hh_open_merge = a_open
                        else:
                            hh_open_merge = hh_open_merge | a_open

            mutated[drum_class] = a

        # Falls wir neue Open-Hats erzeugt haben:
        if hh_open_merge is not None:
            existing = mutated.get("HH_OPEN")
            if existing is None:
                mutated["HH_OPEN"] = hh_open_merge
            else:
                mutated["HH_OPEN"] = existing | hh_open_merge

        # Zum Schluss unabhängig von complexity ggf. eine kurze Pause einfügen
        mutated = self._insert_random_pause(mutated)

        return mutated

    # ------------------------------------------------------------------ #
    # Öffentliche API
    # ------------------------------------------------------------------ #

    def generate_drum_track(
            self,
            song_specification: SongSpecification,
    ) -> list[DrumEvent]:
        """Erzeugt eine Drum-Spur für den gesamten Song anhand von Pattern-Templates."""
        _, _, seconds_per_bar = self._compute_timing(song_specification)
        patterns_dict, step_res = self._select_pattern_library(
            getattr(song_specification, "style", None)
        )

        self.step_resolution = step_res
        events: list[DrumEvent] = []

        for bar_index in range(song_specification.number_of_bars):
            bar_start = bar_index * seconds_per_bar

            # Pattern abhängig von complexity (dicht vs. simpel) auswählen
            pattern_name = self._choose_pattern_name(patterns_dict)
            base_pattern_strs = patterns_dict[pattern_name]

            # String -> Arrays, Mutationen, Events erzeugen
            arrays = self._pattern_dict_to_arrays(
                base_pattern_strs, self.step_resolution
            )
            arrays = self._mutate_bar_arrays(arrays, self.complexity)
            events.extend(self._arrays_to_events(arrays, bar_start, seconds_per_bar))

            # Ghostnotes pro Takt ergänzen (wenn SNARE existiert)
            snare_steps = arrays.get("SNARE")
            events.extend(
                self._add_ghostnotes_for_bar(
                    snare_steps=snare_steps,
                    bar_start=bar_start,
                    seconds_per_bar=seconds_per_bar,
                )
            )

        return events

    def generate_fill(
        self,
        song_specification: SongSpecification,
        start_bar: int,
        number_of_bars: int,
    ) -> List[DrumEvent]:
        """Erstellt Drum-Fills für einen bestimmten Abschnitt (Tom-Läufe + Crash)."""
        _, _, seconds_per_bar = self._compute_timing(song_specification)
        subdivisions = self.step_resolution
        step_duration = seconds_per_bar / subdivisions

        events: List[DrumEvent] = []
        tom_cycle = ["TOM_LOW", "TOM_MID", "TOM_HIGH"]

        for local_bar in range(number_of_bars):
            global_bar = start_bar + local_bar
            bar_start = global_bar * seconds_per_bar

            # einfacher „laufender“ Fill über 16tel mit leichter Variation
            steps = np.zeros(subdivisions, dtype=bool)
            # Grundgerüst: auf jeder 2. oder 3. 16tel ein Schlag
            spacing = 2 if self.complexity < 0.6 else 1
            steps[::spacing] = True

            # kleine Variation: zufällige Steps deaktivieren
            if self.complexity > 0.3:
                for _ in range(int(subdivisions * 0.1 * self.complexity)):
                    idx = random.randrange(subdivisions)
                    steps[idx] = not steps[idx]

            for step_idx, is_hit in enumerate(steps):
                if not is_hit:
                    continue
                drum_class = tom_cycle[(local_bar + step_idx) % len(tom_cycle)]
                time_sec = bar_start + step_idx * step_duration
                events.append(
                    DrumEvent(
                        time_sec=time_sec,
                        drum_class=drum_class,
                        velocity=100,
                    )
                )

        # Crash auf der "1" nach dem Fill-Ende
        end_bar_start = (start_bar + number_of_bars) * seconds_per_bar
        events.append(
            DrumEvent(
                time_sec=end_bar_start,
                drum_class="CRASH",
                velocity=110,
            )
        )

        return events


