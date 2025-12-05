from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import random

from .song_specification import SongSpecification
from .instrument import Instrument

from script.patterns.chord_patterns import (
    CHORD_PATTERNS_BY_ROLE,
    ChordPattern,
)
from script.patterns.bass_patterns import (
    BASS_PATTERNS_BY_INSTRUMENT,
    BassPattern,
)
from script.patterns.pad_lead_patterns import (
    PAD_PATTERNS_BY_INSTRUMENT,
    PadPattern,
    LEAD_PATTERNS_BY_INSTRUMENT,
    LeadPattern,
)

# ---------------------------------------------------------------------------
# Hilfs-Datenstruktur: NoteEvent
# ---------------------------------------------------------------------------

@dataclass
class NoteEvent:
    """Einfache Darstellung eines MIDI-Notenereignisses.

    Attribute:
        start_time: Startzeit der Note in Sekunden.
        end_time: Endzeit der Note in Sekunden.
        pitch: MIDI-Notennummer (z. B. 60 = C4).
        velocity: Anschlagsstärke (0–127).
        channel: MIDI-Kanal (0–15).
    """
    start_time: float
    end_time: float
    pitch: int
    velocity: int
    channel: int


# ---------------------------------------------------------------------------
# HarmonyGenerator
# ---------------------------------------------------------------------------

class HarmonyGenerator:
    """Erzeugt harmonische Begleitspuren (Akkorde, Bass, Pads, Leads).

    Verantwortung:
        HarmonyGenerator erzeugt alle nicht-perkussiven Noten, also Akkorde,
        Basslinien, Pads und eventuell Leads.
        Er nutzt dazu Informationen aus der SongSpecification wie Tonart,
        Stil und Anzahl der Takte.
        So entstehen einfache Pop-Begleitungen, die zu deinen Drum-Patterns passen.
    """

    def __init__(
            self,
            scale_vocab: Dict[str, List[int]],
            chord_vocab: Dict[str, List[int]],
            pattern_templates: Dict[str, Any],
    ) -> None:
        """Konstruktor für den HarmonyGenerator.

        Args:
            scale_vocab: Mapping von Tonarten auf Skalen (MIDI-Offsets relativ zu C),
                z. B. {"C major": [0,2,4,5,7,9,11], "A minor":[9,11,0,2,4,5,7]}.
            chord_vocab: Mapping von Akkordtypen auf Intervallstrukturen
                (z. B. "maj" → [0, 4, 7], "min" → [0,3,7]).
            pattern_templates: Sammlung von Pattern-Templates für Bass, Akkorde usw.
                (in dieser einfachen Version werden sie nur optional verwendet).
        """
        self.scale_vocab = scale_vocab
        self.chord_vocab = chord_vocab
        self.pattern_templates = pattern_templates

    # ------------------------------------------------------------------
    # Interne Hilfsfunktionen
    # ------------------------------------------------------------------

    @staticmethod
    def _roman_to_degree_and_quality(roman: str) -> Tuple[int, str]:
        """Wandelt eine Stufenbezeichnung (z. B. 'vi', 'IV') in (Stufe, Qualität) um.

        Rückgabe:
            degree_index: 0–6 für I–VII
            quality: "maj", "min" oder "dim"
        """
        roman = roman.strip()
        # Dim-Erkennung (z. B. 'ii°' oder 'viio')
        is_dim = "°" in roman or "o" in roman.lower()
        base = (
            roman.replace("°", "")
            .replace("o", "")
            .replace("dim", "")
            .replace("+", "")
        )

        if base.islower():
            quality = "min"
        else:
            quality = "maj"

        if is_dim:
            quality = "dim"

        mapping = {
            "I": 0,
            "II": 1,
            "III": 2,
            "IV": 3,
            "V": 4,
            "VI": 5,
            "VII": 6,
        }
        upper = base.upper()
        if upper not in mapping:
            raise ValueError(f"Unbekannte Stufenbezeichnung: {roman}")

        degree_index = mapping[upper]
        return degree_index, quality

    @staticmethod
    def _bar_and_qnote_duration(tempo_bpm: float, numerator: int, denominator: int) -> Tuple[float, float]:
        """Berechnet Längen von Takten und Viertelnoten in Sekunden."""
        quarter_duration = 60.0 / tempo_bpm
        beats_per_bar = numerator * (4.0 / denominator)
        bar_duration = beats_per_bar * quarter_duration
        return bar_duration, quarter_duration

    def _get_scale_for_key(self, key: str) -> List[int]:
        """Gibt die Skala für eine Tonart zurück, mit Fallback auf 'C major'."""
        if key in self.scale_vocab:
            return self.scale_vocab[key]
        # Fallback, falls die Tonart nicht eingetragen ist
        if "C major" in self.scale_vocab:
            print(f"[HarmonyGenerator] WARNUNG: Tonart '{key}' nicht in scale_vocab. Fallback auf 'C major'.")
            return self.scale_vocab["C major"]
        # Letzter Fallback: irgendein Eintrag
        first_key = next(iter(self.scale_vocab))
        print(f"[HarmonyGenerator] WARNUNG: Tonart '{key}' nicht bekannt. Fallback auf '{first_key}'.")
        return self.scale_vocab[first_key]

    def _get_chord_intervals(self, quality: str) -> List[int]:
        """Gibt zu einer Akkord-Qualität (maj/min/dim) die Intervalle zurück."""
        # Direkter Hit
        if quality in self.chord_vocab:
            return self.chord_vocab[quality]

        # Kleine Heuristik: 'maj7', 'min7' usw. suchen
        for key in self.chord_vocab.keys():
            if quality in key:
                return self.chord_vocab[key]

        # Fallback: ersten Eintrag nehmen
        first_key = next(iter(self.chord_vocab))
        print(
            f"[HarmonyGenerator] WARNUNG: Keine Akkorde für Qualität '{quality}' gefunden. Fallback auf '{first_key}'.")
        return self.chord_vocab[first_key]

    def _get_chord_patterns_for_instrument(self, instrument: Instrument) -> List[ChordPattern]:
        """Wählt die Chord-Patterns aus CHORD_PATTERNS_BY_ROLE passend zum Instrument.

        Mapping-Idee:
            - Namen mit 'piano' oder 'keys' → Rolle 'piano'
            - Namen mit 'guitar' → Rolle 'guitar'
            - Namen mit 'organ' → Rolle 'organ'
            - sonst → 'default'
        """
        name_lower = instrument.name.lower()

        if "piano" in name_lower or "keys" in name_lower:
            role_key = "piano"
        elif "guitar" in name_lower:
            role_key = "guitar"
        elif "organ" in name_lower:
            role_key = "organ"
        else:
            role_key = "default"

        patterns = CHORD_PATTERNS_BY_ROLE.get(role_key)
        if not patterns:
            patterns = CHORD_PATTERNS_BY_ROLE["default"]

        return patterns

    @staticmethod
    def _apply_voice_leading(base_voicing: List[int], prev_voicing: Optional[List[int]]) -> List[int]:
        """Passt die Lage des Akkords so an, dass sich die Stimmen möglichst wenig bewegen.

        Sehr einfache Heuristik:
        - teste den Akkord in Lagen: -12, 0, +12 Halbton (ganzer Akkord verschoben)
        - wähle die Lage mit minimalem durchschnittlichem Abstand zur vorherigen Lage
        """
        if not prev_voicing:
            return base_voicing

        candidates = []
        for shift in (-12, 0, 12):
            shifted = [p + shift for p in base_voicing]
            # Abstand nur über die gemeinsamen Stimmen berechnen
            n = min(len(shifted), len(prev_voicing))
            if n == 0:
                continue
            diff = sum(abs(shifted[i] - prev_voicing[i]) for i in range(n)) / n
            candidates.append((diff, shifted))

        if not candidates:
            return base_voicing

        _, best_voicing = min(candidates, key=lambda x: x[0])
        return best_voicing

    @staticmethod
    def _compute_chord_velocity(
            base_velocity: int,
            offset_in_quarters: float,
            rnd: random.Random,
    ) -> int:
        """Berechnet eine leicht variierte Velocity mit Akzenten auf 1 und 3."""
        # leichte Zufallsstreuung
        jitter = rnd.randint(-8, 8)
        vel = base_velocity + jitter

        # Akzent auf Zählzeit 1 und 3 (offset 0 oder 2)
        if abs(offset_in_quarters - 0.0) < 1e-3 or abs(offset_in_quarters - 2.0) < 1e-3:
            vel += 10

        # clamp
        vel = max(40, min(127, vel))
        return vel

    def _render_block_chord(
            self,
            events: List[NoteEvent],
            voicing: List[int],
            start_time: float,
            end_time: float,
            offset_quarters: float,
            rnd: random.Random,
            base_velocity: int,
            channel: int,
    ) -> None:
        """Rendert einen Block-Akkord: alle Stimmen gleichzeitig."""
        for pitch in voicing:
            velocity = self._compute_chord_velocity(
                base_velocity=base_velocity,
                offset_in_quarters=offset_quarters,
                rnd=rnd,
            )
            events.append(
                NoteEvent(
                    start_time=start_time,
                    end_time=end_time,
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )

    def _render_arp_up(
            self,
            events: List[NoteEvent],
            voicing: List[int],
            start_time: float,
            duration_quarters: float,
            quarter_duration: float,
            offset_quarters: float,
            rnd: random.Random,
            base_velocity: int,
            channel: int,
    ) -> None:
        """Rendert ein einfaches Arpeggio nach oben in 8teln innerhalb des Pattern-Bereichs."""
        step_quarters = 0.5  # 8tel im 4/4
        total_steps = max(1, int(duration_quarters / step_quarters))
        t = start_time
        for step in range(total_steps):
            pitch = voicing[step % len(voicing)]
            velocity = self._compute_chord_velocity(
                base_velocity=base_velocity,
                offset_in_quarters=offset_quarters + step * step_quarters,
                rnd=rnd,
            )
            events.append(
                NoteEvent(
                    start_time=t,
                    end_time=t + step_quarters * quarter_duration * 0.9,
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )
            t += step_quarters * quarter_duration

    def _render_arp_down(
            self,
            events: List[NoteEvent],
            voicing: List[int],
            start_time: float,
            duration_quarters: float,
            quarter_duration: float,
            offset_quarters: float,
            rnd: random.Random,
            base_velocity: int,
            channel: int,
    ) -> None:
        """Arpeggio nach unten (oberste Stimme zuerst, dann abwärts)."""
        step_quarters = 0.5  # 8tel
        total_steps = max(1, int(duration_quarters / step_quarters))
        t = start_time
        rev_voicing = list(reversed(voicing))
        for step in range(total_steps):
            pitch = rev_voicing[step % len(rev_voicing)]
            velocity = self._compute_chord_velocity(
                base_velocity=base_velocity,
                offset_in_quarters=offset_quarters + step * step_quarters,
                rnd=rnd,
            )
            events.append(
                NoteEvent(
                    start_time=t,
                    end_time=t + step_quarters * quarter_duration * 0.9,
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )
            t += step_quarters * quarter_duration

    def _render_top_pulse(
            self,
            events: List[NoteEvent],
            voicing: List[int],
            start_time: float,
            duration_quarters: float,
            quarter_duration: float,
            offset_quarters: float,
            rnd: random.Random,
            base_velocity: int,
            channel: int,
    ) -> None:
        """Rendert nur die oberste Stimme als kurze Puls-Noten (z. B. Gitarren- oder Piano-Comping)."""
        if not voicing:
            return

        top_pitch = max(voicing)
        # Viertel- oder Achtel-Pulse innerhalb der Dauer
        step_quarters = 0.5  # 8tel
        total_steps = max(1, int(duration_quarters / step_quarters))
        t = start_time

        for step in range(total_steps):
            local_offset = offset_quarters + step * step_quarters
            velocity = self._compute_chord_velocity(
                base_velocity=base_velocity,
                offset_in_quarters=local_offset,
                rnd=rnd,
            )
            events.append(
                NoteEvent(
                    start_time=t,
                    end_time=t + step_quarters * quarter_duration * 0.6,
                    pitch=top_pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )
            t += step_quarters * quarter_duration

    def _get_instrument_type_flags(self, instrument: Instrument) -> Tuple[bool, bool, bool]:
        """Erkennt, ob das Instrument wie Gitarre, Piano oder Orgel behandelt werden soll."""
        name_lower = instrument.name.lower()
        is_guitar = "guitar" in name_lower
        is_piano = "piano" in name_lower or "keys" in name_lower
        is_organ = "organ" in name_lower
        return is_guitar, is_piano, is_organ

    @staticmethod
    def _group_patterns_by_arp(
            all_patterns: List[List[Tuple[float, float, str]]]
    ) -> Tuple[List[List[Tuple[float, float, str]]], List[List[Tuple[float, float, str]]]]:
        """Teilt Patterns in Arpeggio-Patterns und Nicht-Arpeggio-Patterns auf."""
        arp_patterns = [
            p for p in all_patterns
            if any(mode in ("arp_up", "arp_down") for _, _, mode in p)
        ]
        non_arp_patterns = [
            p for p in all_patterns
            if all(mode not in ("arp_up", "arp_down") for _, _, mode in p)
        ]
        return arp_patterns, non_arp_patterns

    def _select_pattern_for_bar(
            self,
            is_guitar: bool,
            is_piano: bool,
            is_organ: bool,
            all_patterns: List[List[Tuple[float, float, str]]],
            arp_patterns: List[List[Tuple[float, float, str]]],
            non_arp_patterns: List[List[Tuple[float, float, str]]],
            rnd: random.Random,
    ) -> List[Tuple[float, float, str]]:
        """Wählt für einen Takt ein Pattern abhängig vom Instrument-Typ."""
        if is_guitar and arp_patterns:
            # Gitarren: stark arpeggio-lastig
            if rnd.random() < 0.7:
                return rnd.choice(arp_patterns)
            if non_arp_patterns:
                return rnd.choice(non_arp_patterns)
            return rnd.choice(all_patterns)

        if is_piano and all_patterns:
            # Piano: ausgewogene Mischung (ca. 40% Arp, 60% Block/Synkopen)
            if arp_patterns and rnd.random() < 0.4:
                return rnd.choice(arp_patterns)
            if non_arp_patterns:
                return rnd.choice(non_arp_patterns)
            return rnd.choice(all_patterns)

        if is_organ and all_patterns:
            # Orgel: fast nur lange Akkorde, selten Arpeggio
            if arp_patterns and rnd.random() < 0.1:
                return rnd.choice(arp_patterns)
            if non_arp_patterns:
                return rnd.choice(non_arp_patterns)
            return rnd.choice(all_patterns)

        # alle anderen Instrumente: einfach zufällig
        return rnd.choice(all_patterns)

    def _compute_voicing_for_bar(
            self,
            roman: str,
            scale: List[int],
            base_c_midi: int,
            is_guitar: bool,
            rnd: random.Random,
            prev_voicing: Optional[List[int]],
    ) -> List[int]:
        """Berechnet das Voicing für einen Takt (inkl. optionaler 7 und Voice Leading)."""
        degree_index, quality = self._roman_to_degree_and_quality(roman)
        if degree_index >= len(scale):
            degree_index = degree_index % len(scale)

        # Akkordintervalle bestimmen und manchmal einen 7er-Akkord benutzen
        intervals = self._get_chord_intervals(quality)
        extended_quality = quality + "7"
        if extended_quality in self.chord_vocab and rnd.random() < 0.3:
            intervals = self.chord_vocab[extended_quality]

        # Root-Ton in dieser Tonart
        root_offset_from_c = scale[degree_index]
        root_pitch = base_c_midi + root_offset_from_c

        # Basis-Voicing im Stack (Root + Intervalle)
        base_voicing = [root_pitch + interval for interval in intervals]

        # Gitarren typischerweise eine Oktave höher
        if is_guitar:
            base_voicing = [p + 12 for p in base_voicing]

        # Voice Leading anwenden (ganzen Akkord in nahe Lage schieben)
        voicing = self._apply_voice_leading(base_voicing, prev_voicing)
        return voicing

    def _render_pattern_for_bar(
            self,
            events: List[NoteEvent],
            pattern: List[Tuple[float, float, str]],
            voicing: List[int],
            bar_start_time: float,
            quarter_duration: float,
            rnd: random.Random,
            channel: int,
    ) -> None:
        """Rendert ein Pattern für einen Takt, indem die Mode-spezifischen Renderer aufgerufen werden."""
        for offset_quarters, duration_quarters, mode in pattern:
            start_time = bar_start_time + offset_quarters * quarter_duration
            end_time = start_time + duration_quarters * quarter_duration

            if mode == "block":
                self._render_block_chord(
                    events=events,
                    voicing=voicing,
                    start_time=start_time,
                    end_time=end_time,
                    offset_quarters=offset_quarters,
                    rnd=rnd,
                    base_velocity=90,
                    channel=channel,
                )

            elif mode == "arp_up":
                self._render_arp_up(
                    events=events,
                    voicing=voicing,
                    start_time=start_time,
                    duration_quarters=duration_quarters,
                    quarter_duration=quarter_duration,
                    offset_quarters=offset_quarters,
                    rnd=rnd,
                    base_velocity=80,
                    channel=channel,
                )

            elif mode == "arp_down":
                self._render_arp_down(
                    events=events,
                    voicing=voicing,
                    start_time=start_time,
                    duration_quarters=duration_quarters,
                    quarter_duration=quarter_duration,
                    offset_quarters=offset_quarters,
                    rnd=rnd,
                    base_velocity=80,
                    channel=channel,
                )

            elif mode == "top_pulse":
                self._render_top_pulse(
                    events=events,
                    voicing=voicing,
                    start_time=start_time,
                    duration_quarters=duration_quarters,
                    quarter_duration=quarter_duration,
                    offset_quarters=offset_quarters,
                    rnd=rnd,
                    base_velocity=85,
                    channel=channel,
                )

            else:
                # unbekannter Mode -> sicherer Fallback
                self._render_block_chord(
                    events=events,
                    voicing=voicing,
                    start_time=start_time,
                    end_time=end_time,
                    offset_quarters=offset_quarters,
                    rnd=rnd,
                    base_velocity=90,
                    channel=channel,
                )

    def _get_bass_root_pitch(
            self,
            degree_index: int,
            scale: List[int],
            base_c_midi_bass: int,
    ) -> int:
        """Berechnet den Grundton für den Bass (C2-Bereich)."""
        if degree_index >= len(scale):
            degree_index = degree_index % len(scale)
        root_offset_from_c = scale[degree_index]
        return base_c_midi_bass + root_offset_from_c

    def _select_bass_pattern_type(
            self,
            instrument: Instrument,
            rnd: random.Random,
    ) -> str:
        """Wählt einen Bass-Pattern-Typ abhängig vom Instrument.

        Mögliche Rückgaben:
            - "root_quarters"
            - "root_root_fifth_root"
            - "root_fifth_root_octave"
            - "walking"
        """
        name_lower = instrument.name.lower()
        is_simple = "finger" in name_lower or "acoustic" in name_lower

        x = rnd.random()
        if is_simple:
            # Einfacherer Bass
            if x < 0.6:
                return "root_quarters"
            elif x < 0.85:
                return "root_root_fifth_root"
            else:
                return "root_fifth_root_octave"
        else:
            # Funkiger / Synth-Bass
            if x < 0.3:
                return "root_quarters"
            elif x < 0.6:
                return "root_root_fifth_root"
            elif x < 0.85:
                return "root_fifth_root_octave"
            else:
                return "walking"

    def _render_bass_pattern_template_for_bar(
            self,
            events: List[NoteEvent],
            pattern: BassPattern,
            degree_index: int,
            next_degree_index: int,
            scale: List[int],
            base_c_midi_bass: int,
            bar_start_time: float,
            quarter_duration: float,
            rnd: random.Random,
            channel: int,
    ) -> None:
        """Rendert ein Bass-Pattern-Template für einen Takt."""

        # Root-Töne für aktuellen und nächsten Akkord
        root_pitch = self._get_bass_root_pitch(
            degree_index=degree_index,
            scale=scale,
            base_c_midi_bass=base_c_midi_bass,
        )
        next_root_pitch = self._get_bass_root_pitch(
            degree_index=next_degree_index,
            scale=scale,
            base_c_midi_bass=base_c_midi_bass,
        )

        # diatonische Indizes für Walking
        num_scale_degrees = len(scale)
        cur_scale_idx = degree_index % num_scale_degrees
        next_scale_idx = next_degree_index % num_scale_degrees

        last_pitch: Optional[int] = None

        def add_note(offset_q: float, dur_q: float, pitch: int, base_vel: int) -> None:
            start = bar_start_time + offset_q * quarter_duration
            end = start + dur_q * quarter_duration * 0.95
            velocity = self._compute_chord_velocity(
                base_velocity=base_vel,
                offset_in_quarters=offset_q,
                rnd=rnd,
            )
            events.append(
                NoteEvent(
                    start_time=start,
                    end_time=end,
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )

        for offset_q, dur_q, func in pattern:
            func = func.lower()

            # Pausen werden einfach übersprungen
            if func == "rest":
                continue

            if func == "root":
                pitch = root_pitch

            elif func == "fifth":
                pitch = root_pitch + 7

            elif func == "octave":
                pitch = root_pitch + 12

            elif func == "walk_up":
                # diatonisch eine Stufe hoch
                cur_scale_idx = (cur_scale_idx + 1) % num_scale_degrees
                pitch = base_c_midi_bass + scale[cur_scale_idx]

            elif func == "walk_down":
                # diatonisch eine Stufe runter
                cur_scale_idx = (cur_scale_idx - 1) % num_scale_degrees
                pitch = base_c_midi_bass + scale[cur_scale_idx]

            elif func == "approach_next":
                # Ton kurz vor dem nächsten Root – diatonisch unterhalb oder oberhalb
                direction_up = next_root_pitch >= root_pitch
                if direction_up:
                    candidate_idx = (next_scale_idx - 1) % num_scale_degrees
                else:
                    candidate_idx = (next_scale_idx + 1) % num_scale_degrees
                pitch = base_c_midi_bass + scale[candidate_idx]

                # gelegentlich halbtönig „chromatic“ noch näher ran
                if rnd.random() < 0.25:
                    if direction_up:
                        pitch = next_root_pitch - 1
                    else:
                        pitch = next_root_pitch + 1

            else:
                # unbekannte Funktion → Root als Fallback
                pitch = root_pitch

            # kleine Sicherung: Bass nicht zu hoch wandern lassen
            if pitch > base_c_midi_bass + 24 and rnd.random() < 0.5:
                pitch -= 12
            if pitch < base_c_midi_bass - 12 and rnd.random() < 0.5:
                pitch += 12

            last_pitch = pitch
            add_note(offset_q=offset_q, dur_q=dur_q, pitch=pitch, base_vel=94)

    def _is_pad_instrument(self, instrument: Instrument) -> bool:
        name = instrument.name.lower()
        return (
                instrument.role == "pad"
                or "string" in name
                or "pad" in name
        )

    def _is_lead_instrument(self, instrument: Instrument) -> bool:
        name = instrument.name.lower()
        return (
                instrument.role == "lead"
                or "lead" in name
                or "sax" in name
                or "trumpet" in name
        )

    def _select_pad_voicing_type(
            self,
            instrument: Instrument,
            rnd: random.Random,
    ) -> str:
        """Wählt eine Pad-Voicing-Variante.

        Mögliche Rückgaben:
            - "root7"
            - "third_fifth"
            - "fifth_ninth"
        """
        x = rnd.random()
        if x < 0.4:
            return "root7"
        elif x < 0.75:
            return "third_fifth"
        else:
            return "fifth_ninth"

    def _compute_pad_voicing_for_bar(
            self,
            roman: str,
            scale: List[int],
            base_c_midi_pad: int,
            rnd: random.Random,
            voicing_type: str,
    ) -> List[int]:
        """Berechnet ein 2–3-stimmiges Voicing für Pads."""
        degree_index, quality = self._roman_to_degree_and_quality(roman)
        if degree_index >= len(scale):
            degree_index = degree_index % len(scale)

        intervals = self._get_chord_intervals(quality)
        root_offset_from_c = scale[degree_index]
        root_pitch = base_c_midi_pad + root_offset_from_c
        triad_pitches = [root_pitch + iv for iv in intervals]

        # 7er-Voicing versuchen
        extended_quality = quality + "7"
        if extended_quality in self.chord_vocab:
            ext_intervals = self.chord_vocab[extended_quality]
            ext_pitches = [root_pitch + iv for iv in ext_intervals]
        else:
            ext_pitches = triad_pitches

        if voicing_type == "root7":
            if len(ext_pitches) >= 4:
                return [ext_pitches[0], ext_pitches[-1]]
            return [root_pitch, root_pitch + 10]  # ungefähr min7/maj7

        if voicing_type == "third_fifth":
            if len(triad_pitches) >= 3:
                return triad_pitches[1:3]
            return triad_pitches

        if voicing_type == "fifth_ninth":
            fifth = triad_pitches[2] if len(triad_pitches) >= 3 else root_pitch + 7
            ninth = root_pitch + 14  # 9 = 2 + Oktave
            return [fifth, ninth]

        # Fallback
        return triad_pitches

    def _select_pad_pattern_type(
            self,
            rnd: random.Random,
    ) -> str:
        """Wählt einen Pad-Pattern-Typ pro Takt.

        Mögliche Rückgaben:
            - "sustain" (ganzer Takt)
            - "half_half" (1+3)
            - "late_swell" (z. B. ab 2+)
        """
        x = rnd.random()
        if x < 0.5:
            return "sustain"
        elif x < 0.8:
            return "half_half"
        else:
            return "late_swell"

    def _render_pad_pattern_template_for_bar(
            self,
            events: List[NoteEvent],
            pattern: PadPattern,
            voicing: List[int],
            bar_start_time: float,
            quarter_duration: float,
            rnd: random.Random,
            channel: int,
    ) -> None:
        """Rendert ein Pad-Pattern-Template für einen Takt."""

        for offset_q, dur_q, mode in pattern:
            start_time = bar_start_time + offset_q * quarter_duration
            end_time = start_time + dur_q * quarter_duration

            mode = mode.lower()
            if mode == "pad_sustain":
                base_vel = 70
            elif mode == "pad_half":
                base_vel = 72
            elif mode == "pad_swell":
                base_vel = 75
            elif mode == "pad_pulse":
                base_vel = 78
            else:
                base_vel = 70  # Fallback

            for pitch in voicing:
                velocity = self._compute_chord_velocity(
                    base_velocity=base_vel,
                    offset_in_quarters=offset_q,
                    rnd=rnd,
                )
                events.append(
                    NoteEvent(
                        start_time=start_time,
                        end_time=end_time,
                        pitch=pitch,
                        velocity=velocity,
                        channel=channel,
                    )
                )

    def _select_lead_motif_shape(
            self,
            rnd: random.Random,
    ) -> List[int]:
        """Wählt eine kleine Motiv-Form in Skalen-Schritten (0 = Grundton der Stufe)."""
        motif_shapes = [
            [0, 2, 4, 2],  # aufwärts und zurück
            [0, 1, 2, 0],  # kleine Bewegung um den Grundton
            [0, 2, 3, 2],  # mix aus Terz und Sekunde
            [0, -1, -2, 0],  # abwärts und zurück
        ]
        return rnd.choice(motif_shapes)

    def _render_lead_pattern_template_for_bar(
            self,
            events: List[NoteEvent],
            pattern: LeadPattern,
            roman: str,
            scale: List[int],
            base_c_midi_lead: int,
            bar_start_time: float,
            quarter_duration: float,
            rnd: random.Random,
            channel: int,
    ) -> None:
        """Rendert ein Lead-Pattern-Template für einen Takt."""

        degree_index, _ = self._roman_to_degree_and_quality(roman)
        if degree_index >= len(scale):
            degree_index = degree_index % len(scale)

        num_scale_degrees = len(scale)

        for offset_q, dur_q, rel_step in pattern:
            scale_idx = (degree_index + rel_step) % num_scale_degrees
            offset = scale[scale_idx]
            pitch = base_c_midi_lead + offset

            start_time = bar_start_time + offset_q * quarter_duration
            end_time = start_time + dur_q * quarter_duration * 0.9

            velocity = self._compute_chord_velocity(
                base_velocity=95,
                offset_in_quarters=offset_q,
                rnd=rnd,
            )

            events.append(
                NoteEvent(
                    start_time=start_time,
                    end_time=end_time,
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                )
            )

    def _generate_single_pad_track(
            self,
            progression: List[str],
            scale: List[int],
            bar_duration: float,
            quarter_duration: float,
            instrument: Instrument,
            rnd: random.Random,
    ) -> List[NoteEvent]:
        """Erzeugt eine komplette Pad-Spur für genau EIN Instrument."""
        events: List[NoteEvent] = []

        # Pad-Register: zufällig tiefer oder höher
        base_c_midi_pad = 48 if rnd.random() < 0.5 else 60

        voicing_type = self._select_pad_voicing_type(instrument, rnd)

        # Patterns pro Instrument holen
        pad_patterns = self._get_pad_patterns_for_instrument(instrument)

        for bar_index, roman in enumerate(progression):
            voicing = self._compute_pad_voicing_for_bar(
                roman=roman,
                scale=scale,
                base_c_midi_pad=base_c_midi_pad,
                rnd=rnd,
                voicing_type=voicing_type,
            )

            bar_start_time = bar_index * bar_duration

            # Pattern zufällig pro Takt wählen
            pattern = rnd.choice(pad_patterns)

            self._render_pad_pattern_template_for_bar(
                events=events,
                pattern=pattern,
                voicing=voicing,
                bar_start_time=bar_start_time,
                quarter_duration=quarter_duration,
                rnd=rnd,
                channel=instrument.channel,
            )

        return events

    def _generate_single_lead_track(
            self,
            progression: List[str],
            scale: List[int],
            bar_duration: float,
            quarter_duration: float,
            instrument: Instrument,
            rnd: random.Random,
    ) -> List[NoteEvent]:
        """Erzeugt eine Lead-Spur mit kurzen Motiven (Call & Response) aus Templates."""
        events: List[NoteEvent] = []

        base_c_midi_lead = 72  # C5

        # Instrument-spezifische Motive holen
        lead_patterns = self._get_lead_patterns_for_instrument(instrument)

        for bar_index, roman in enumerate(progression):
            bar_start_time = bar_index * bar_duration

            # Call & Response: gerade Takte = eher Call, ungerade = eher Response/Pause
            if bar_index % 2 == 0:
                # Call-Takt
                if rnd.random() < 0.7:
                    pattern = rnd.choice(lead_patterns)
                    self._render_lead_pattern_template_for_bar(
                        events=events,
                        pattern=pattern,
                        roman=roman,
                        scale=scale,
                        base_c_midi_lead=base_c_midi_lead,
                        bar_start_time=bar_start_time,
                        quarter_duration=quarter_duration,
                        rnd=rnd,
                        channel=instrument.channel,
                    )
            else:
                # Response-Takt
                roll = rnd.random()
                if roll < 0.4:
                    # kurze Antwort
                    pattern = rnd.choice(lead_patterns)
                    self._render_lead_pattern_template_for_bar(
                        events=events,
                        pattern=pattern,
                        roman=roman,
                        scale=scale,
                        base_c_midi_lead=base_c_midi_lead,
                        bar_start_time=bar_start_time,
                        quarter_duration=quarter_duration,
                        rnd=rnd,
                        channel=instrument.channel,
                    )
                # sonst: bewusste Pause

        return events

    def _get_bass_patterns_for_instrument(self, instrument: Instrument) -> List[BassPattern]:
        """Liefert die Bass-Pattern-Liste für dieses Instrument."""
        patterns = BASS_PATTERNS_BY_INSTRUMENT.get(instrument.name)
        if not patterns:
            patterns = BASS_PATTERNS_BY_INSTRUMENT["default"]
        return patterns

    def _get_pad_patterns_for_instrument(self, instrument: Instrument) -> List[PadPattern]:
        """Liefert Pad-Patterns für dieses Instrument."""
        patterns = PAD_PATTERNS_BY_INSTRUMENT.get(instrument.name)
        if not patterns:
            patterns = PAD_PATTERNS_BY_INSTRUMENT["default"]
        return patterns

    def _get_lead_patterns_for_instrument(self, instrument: Instrument) -> List[LeadPattern]:
        """Liefert Lead-Motive für dieses Instrument."""
        patterns = LEAD_PATTERNS_BY_INSTRUMENT.get(instrument.name)
        if not patterns:
            patterns = LEAD_PATTERNS_BY_INSTRUMENT["default"]
        return patterns

    # ------------------------------------------------------------------
    # Öffentliche API
    # ------------------------------------------------------------------

    def choose_chord_progression(
            self,
            song_specification: SongSpecification,
    ) -> List[str]:
        """Wählt eine Akkordfolge für den Song aus.

        Beschreibung:
            Wählt basierend auf Stil und Tonart eine einfache Akkordfolge
            (z. B. ["I", "V", "vi", "IV"]) aus und wiederholt sie,
            bis alle Takte des Songs gefüllt sind.

        Args:
            song_specification: Spezifikation des Songs, für den die Progression
                bestimmt werden soll.

        Returns:
            Liste von Stufenbezeichnungen, die die Akkordfolge pro Takt darstellen.
        """
        style = song_specification.style
        total_bars = song_specification.number_of_bars

        # Sehr einfache Regelbasis, du kannst das später beliebig ausbauen:
        if "funk" in style:
            candidate_progressions = [
                ["I", "IV", "I", "V"],
                ["I", "ii", "IV", "V"],
            ]
        elif "minor" in song_specification.key.lower():
            candidate_progressions = [
                ["i", "VI", "III", "VII"],
                ["i", "iv", "VII", "III"],
            ]
        else:
            # Pop / Default
            candidate_progressions = [
                ["I", "V", "vi", "IV"],
                ["I", "vi", "IV", "V"],
                ["I", "IV", "V", "IV"],
            ]

        # Deterministische Auswahl anhand seed (wenn vorhanden)
        seed = getattr(song_specification, "random_seed", 42)
        rnd = random.Random(seed + 100)  # +100 damit es sich von anderen Generatoren unterscheidet
        base_progression = rnd.choice(candidate_progressions)

        # Jetzt so oft wiederholen, bis wir 'number_of_bars' Takte haben
        repetitions = (total_bars + len(base_progression) - 1) // len(base_progression)
        full_progression = (base_progression * repetitions)[:total_bars]

        return full_progression

    def generate_chord_track(
            self,
            song_specification: SongSpecification,
            instrument: Instrument,
    ) -> List[NoteEvent]:
        """Erzeugt eine dynamischere Akkordspur für ein Instrument.

        - unterschiedliche Rhythmus-Patterns (block, Arpeggios, Synkopen)
        - Voicings mit optionaler 7 und einfachen Umkehrungen
        - Voice Leading (minimale Bewegung zum vorherigen Akkord)
        - Instrument-Typ (Piano/Gitarre/Orgel) steuert Pattern-Auswahl
        - leichte Velocity-Variation mit Akzenten
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        scale = self._get_scale_for_key(key)
        bar_duration, quarter_duration = self._bar_and_qnote_duration(
            tempo, numerator, denominator
        )

        events: List[NoteEvent] = []

        # mittlere Lage für Akkorde (C3 als Basis)
        base_c_midi = 48  # C3

        # Instrument-spezifische Pattern-Liste aus chord_patterns.py
        all_patterns = self._get_chord_patterns_for_instrument(instrument)
        if not all_patterns:
            all_patterns = [[(0.0, 4.0, "block")]]

        # Eigener Zufallsgenerator pro Instrument, damit zwei Chord-Instrumente
        # nicht genau denselben Pattern-Stream haben
        seed = getattr(song_specification, "random_seed", 42)
        rnd = random.Random(seed + instrument.channel * 97)

        prev_voicing: Optional[List[int]] = None

        # Instrument-Typen erkennen
        name_lower = instrument.name.lower()
        is_guitar = "guitar" in name_lower
        is_piano = "piano" in name_lower or "keys" in name_lower
        is_organ = "organ" in name_lower

        # Pattern-Gruppen nach Arpeggio / Nicht-Arpeggio
        arp_patterns = [
            p for p in all_patterns
            if any(mode in ("arp_up", "arp_down") for _, _, mode in p)
        ]
        non_arp_patterns = [
            p for p in all_patterns
            if all(mode not in ("arp_up", "arp_down") for _, _, mode in p)
        ]

        for bar_index, roman in enumerate(progression):
            # Stufe + Qualität (maj/min/dim)
            degree_index, quality = self._roman_to_degree_and_quality(roman)
            if degree_index >= len(scale):
                degree_index = degree_index % len(scale)

            # Akkordintervalle bestimmen, gelegentlich 7er-Akkord
            intervals = self._get_chord_intervals(quality)
            extended_quality = quality + "7"
            if extended_quality in self.chord_vocab and rnd.random() < 0.3:
                intervals = self.chord_vocab[extended_quality]

            # Root-Ton in dieser Tonart
            root_offset_from_c = scale[degree_index]
            root_pitch = base_c_midi + root_offset_from_c

            # Basis-Voicing im Stack (Root + Intervalle)
            base_voicing = [root_pitch + interval for interval in intervals]

            # für Gitarre etwas höher legen
            if is_guitar:
                base_voicing = [p + 12 for p in base_voicing]

            # Voice Leading: auf nahe Lage zum vorherigen Akkord ziehen
            voicing = self._apply_voice_leading(base_voicing, prev_voicing)
            prev_voicing = voicing

            bar_start_time = bar_index * bar_duration

            # ---------------------------------
            # Pattern für diesen Takt auswählen
            # ---------------------------------
            if is_guitar and arp_patterns:
                # Gitarren: stark arpeggio-lastig
                if rnd.random() < 0.7:
                    pattern = rnd.choice(arp_patterns)
                elif non_arp_patterns:
                    pattern = rnd.choice(non_arp_patterns)
                else:
                    pattern = rnd.choice(all_patterns)

            elif is_piano and all_patterns:
                # Piano: Mix aus block/syncopated und Arpeggios
                if arp_patterns and rnd.random() < 0.4:
                    pattern = rnd.choice(arp_patterns)
                elif non_arp_patterns:
                    pattern = rnd.choice(non_arp_patterns)
                else:
                    pattern = rnd.choice(all_patterns)

            elif is_organ and all_patterns:
                # Orgel: fast nur lange Akkorde, selten Arpeggio
                if arp_patterns and rnd.random() < 0.1:
                    pattern = rnd.choice(arp_patterns)
                elif non_arp_patterns:
                    pattern = rnd.choice(non_arp_patterns)
                else:
                    pattern = rnd.choice(all_patterns)

            else:
                # alle anderen Chord-Instrumente
                pattern = rnd.choice(all_patterns)

            # ---------------------------------
            # Pattern ausführen
            # ---------------------------------
            for offset_quarters, duration_quarters, mode in pattern:
                start_time = bar_start_time + offset_quarters * quarter_duration
                end_time = start_time + duration_quarters * quarter_duration

                if mode == "block":
                    self._render_block_chord(
                        events=events,
                        voicing=voicing,
                        start_time=start_time,
                        end_time=end_time,
                        offset_quarters=offset_quarters,
                        rnd=rnd,
                        base_velocity=90,
                        channel=instrument.channel,
                    )

                elif mode == "arp_up":
                    self._render_arp_up(
                        events=events,
                        voicing=voicing,
                        start_time=start_time,
                        duration_quarters=duration_quarters,
                        quarter_duration=quarter_duration,
                        offset_quarters=offset_quarters,
                        rnd=rnd,
                        base_velocity=80,
                        channel=instrument.channel,
                    )

                elif mode == "arp_down":
                    self._render_arp_down(
                        events=events,
                        voicing=voicing,
                        start_time=start_time,
                        duration_quarters=duration_quarters,
                        quarter_duration=quarter_duration,
                        offset_quarters=offset_quarters,
                        rnd=rnd,
                        base_velocity=80,
                        channel=instrument.channel,
                    )

                elif mode == "top_pulse":
                    self._render_top_pulse(
                        events=events,
                        voicing=voicing,
                        start_time=start_time,
                        duration_quarters=duration_quarters,
                        quarter_duration=quarter_duration,
                        offset_quarters=offset_quarters,
                        rnd=rnd,
                        base_velocity=85,
                        channel=instrument.channel,
                    )

                else:
                    # unbekannter Mode -> sicherer Fallback
                    self._render_block_chord(
                        events=events,
                        voicing=voicing,
                        start_time=start_time,
                        end_time=end_time,
                        offset_quarters=offset_quarters,
                        rnd=rnd,
                        base_velocity=90,
                        channel=instrument.channel,
                    )

        return events

    def generate_bass_track(
            self,
            song_specification: SongSpecification,
            instrument: Instrument,
    ) -> List[NoteEvent]:
        """Erzeugt eine dynamische Basslinie mit Pattern-Templates.

        - nutzt instrument-spezifische Bass-Patterns aus bass_patterns.py
        - Patterns enthalten Infos wie "root", "fifth", "octave", "walk_up", "approach_next"
        - berücksichtigt einfachen Walking/Passing in Richtung des nächsten Akkords
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        scale = self._get_scale_for_key(key)
        bar_duration, quarter_duration = self._bar_and_qnote_duration(
            tempo, numerator, denominator
        )

        events: List[NoteEvent] = []
        base_c_midi_bass = 36  # C2

        # RNG pro Bass-Instrument
        seed = getattr(song_specification, "random_seed", 42)
        rnd = random.Random(seed + instrument.channel * 131)

        # Patterns für dieses Instrument holen
        bass_patterns = self._get_bass_patterns_for_instrument(instrument)

        for bar_index, roman in enumerate(progression):
            degree_index, _ = self._roman_to_degree_and_quality(roman)

            # nächsten Akkord (für Approaches)
            if bar_index + 1 < len(progression):
                next_roman = progression[bar_index + 1]
                next_degree_index, _ = self._roman_to_degree_and_quality(next_roman)
            else:
                next_degree_index = degree_index

            bar_start_time = bar_index * bar_duration

            # Pattern zufällig wählen
            pattern = rnd.choice(bass_patterns)

            self._render_bass_pattern_template_for_bar(
                events=events,
                pattern=pattern,
                degree_index=degree_index,
                next_degree_index=next_degree_index,
                scale=scale,
                base_c_midi_bass=base_c_midi_bass,
                bar_start_time=bar_start_time,
                quarter_duration=quarter_duration,
                rnd=rnd,
                channel=instrument.channel,
            )

        return events

    def generate_pad_or_lead_tracks(
            self,
            song_specification: SongSpecification,
            instruments: List[Instrument],
    ) -> List[NoteEvent]:
        """Erzeugt zusätzliche Pad- oder Lead-Spuren.

        Pads:
            - verschiedene Voicings (Root+7, 3+5, 5+9)
            - Patterns wie Sustain, Half-Half, Late-Swell
        Leads:
            - kurze Motive in 8teln
            - Call & Response (Motiv meist alle 2 Takte)
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        scale = self._get_scale_for_key(key)
        bar_duration, quarter_duration = self._bar_and_qnote_duration(
            tempo, numerator, denominator
        )

        all_events: List[NoteEvent] = []

        for instrument in instruments:
            is_pad = self._is_pad_instrument(instrument)
            is_lead = self._is_lead_instrument(instrument)

            if not (is_pad or is_lead):
                continue

            # eigener RNG pro Instrument
            seed = getattr(song_specification, "random_seed", 42)
            rnd = random.Random(seed + instrument.channel * 173)

            if is_pad:
                events = self._generate_single_pad_track(
                    progression=progression,
                    scale=scale,
                    bar_duration=bar_duration,
                    quarter_duration=quarter_duration,
                    instrument=instrument,
                    rnd=rnd,
                )
            else:
                events = self._generate_single_lead_track(
                    progression=progression,
                    scale=scale,
                    bar_duration=bar_duration,
                    quarter_duration=quarter_duration,
                    instrument=instrument,
                    rnd=rnd,
                )

            all_events.extend(events)

        return all_events



