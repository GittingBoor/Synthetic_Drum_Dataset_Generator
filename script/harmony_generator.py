from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import random

from .song_specification import SongSpecification
from .instrument import Instrument


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
        """Erzeugt eine Akkordspur für ein Instrument.

        Beschreibung:
            Erzeugt eine Akkordspur (z. B. für Piano oder Pad) mit Startzeiten,
            Dauern und Tonhöhen, die zur gewählten Progression passen.

        Args:
            song_specification: Spezifikation des Songs.
            instrument: Instrument, das die Akkorde spielt.

        Returns:
            Liste von NoteEvent-Objekten für die Akkordspur.
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        # Skala der Tonart holen
        scale = self._get_scale_for_key(key)

        # Dauer pro Takt berechnen
        bar_duration, _ = self._bar_and_qnote_duration(tempo, numerator, denominator)

        events: List[NoteEvent] = []

        # Wir legen die Akkorde in einer mittleren Lage (C3 als Referenz)
        base_c_midi = 48  # C3

        for bar_index, roman in enumerate(progression):
            degree_index, quality = self._roman_to_degree_and_quality(roman)
            chord_intervals = self._get_chord_intervals(quality)

            # Root-Pitch-Class aus der Skala
            if degree_index >= len(scale):
                print(f"[HarmonyGenerator] WARNUNG: degree_index {degree_index} außerhalb der Skala, Fallback auf 0.")
                degree_index = 0
            root_offset_from_c = scale[degree_index]
            root_pitch = base_c_midi + root_offset_from_c

            # Start/Ende der Note
            start_time = bar_index * bar_duration
            end_time = start_time + bar_duration

            # Akkord-Noten erzeugen
            for interval in chord_intervals:
                pitch = root_pitch + interval
                note = NoteEvent(
                    start_time=start_time,
                    end_time=end_time,
                    pitch=pitch,
                    velocity=90,
                    channel=instrument.channel,
                )
                events.append(note)

        return events

    def generate_bass_track(
            self,
            song_specification: SongSpecification,
            instrument: Instrument,
    ) -> List[NoteEvent]:
        """Erzeugt eine Basslinie passend zur Akkordfolge.

        Beschreibung:
            Baut eine einfache Basslinie mit Root-Noten (Viertelnoten),
            passend zur Akkordfolge und zum ausgewählten Bass-Instrument.

        Args:
            song_specification: Spezifikation des Songs.
            instrument: Instrument des Bass-Instruments.

        Returns:
            Liste von NoteEvent-Objekten für die Bassspur.
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        scale = self._get_scale_for_key(key)
        bar_duration, quarter_duration = self._bar_and_qnote_duration(tempo, numerator, denominator)

        events: List[NoteEvent] = []

        # Bass eine Oktave unter den Akkorden
        base_c_midi = 36  # C2

        for bar_index, roman in enumerate(progression):
            degree_index, _ = self._roman_to_degree_and_quality(roman)

            if degree_index >= len(scale):
                print(
                    f"[HarmonyGenerator] WARNUNG (Bass): degree_index {degree_index} außerhalb der Skala, Fallback auf 0.")
                degree_index = 0

            root_offset_from_c = scale[degree_index]
            root_pitch = base_c_midi + root_offset_from_c

            bar_start_time = bar_index * bar_duration

            # Sehr simples Pattern: Viertelnoten auf der Grundtonhöhe
            beats_per_bar = int(numerator * (4.0 / denominator))
            for beat in range(beats_per_bar):
                start_time = bar_start_time + beat * quarter_duration
                end_time = start_time + quarter_duration * 0.9  # leicht kürzer, damit es nicht klebt
                note = NoteEvent(
                    start_time=start_time,
                    end_time=end_time,
                    pitch=root_pitch,
                    velocity=95,
                    channel=instrument.channel,
                )
                events.append(note)

        return events

    def generate_pad_or_lead_tracks(
            self,
            song_specification: SongSpecification,
            instruments: List[Instrument],
    ) -> List[NoteEvent]:
        """Erzeugt zusätzliche Pad- oder Lead-Spuren.

        Beschreibung:
            Generiert sehr einfache Pad-Linien: pro Takt eine lang gehaltene Note,
            z. B. die Quinte des Akkords.
            (Leads könntest du später separat komplexer machen.)

        Args:
            song_specification: Spezifikation des Songs.
            instruments: Liste der Instrument-Objekte, die Pads/Leads spielen.

        Returns:
            Liste von NoteEvent-Objekten für die zusätzlichen Spuren.
        """
        progression = self.choose_chord_progression(song_specification)
        key = song_specification.key
        numerator, denominator = song_specification.time_signature
        tempo = song_specification.tempo_bpm

        scale = self._get_scale_for_key(key)
        bar_duration, _ = self._bar_and_qnote_duration(tempo, numerator, denominator)

        events: List[NoteEvent] = []

        base_c_midi = 60  # C4 für Pads/Leads etwas höher

        for bar_index, roman in enumerate(progression):
            degree_index, quality = self._roman_to_degree_and_quality(roman)
            chord_intervals = self._get_chord_intervals(quality)

            if degree_index >= len(scale):
                print(
                    f"[HarmonyGenerator] WARNUNG (Pad): degree_index {degree_index} außerhalb der Skala, Fallback auf 0.")
                degree_index = 0

            root_offset_from_c = scale[degree_index]
            root_pitch = base_c_midi + root_offset_from_c

            start_time = bar_index * bar_duration
            end_time = start_time + bar_duration

            # Wir nehmen für das Pad einfach die Quinte (falls vorhanden),
            # ansonsten den Grundton
            fifth_interval = 7
            fifth_pitch = root_pitch + fifth_interval if fifth_interval in chord_intervals else root_pitch

            for instr in instruments:
                note = NoteEvent(
                    start_time=start_time,
                    end_time=end_time,
                    pitch=fifth_pitch,
                    velocity=70,
                    channel=instr.channel,
                )
                events.append(note)

        return events

# ------------------------------------------------------------------
# test- / Test-Funktionen mit ausführlichen Prints
# ------------------------------------------------------------------


def test_print_chord_progression(
    harmony_generator: HarmonyGenerator,
    song_specification: SongSpecification,
) -> None:
    """test-Hilfe: Druckt die gewählte Akkordfolge mit Zusatzinfos."""
    print("\n[test] ---------------- CHORD PROGRESSION ----------------")
    print(f"Song: {song_specification.song_identifier}")
    print(f"Tonart: {song_specification.key}, Stil: {song_specification.style}")
    print(f"Takte: {song_specification.number_of_bars}")
    progression = harmony_generator.choose_chord_progression(song_specification)
    for i, roman in enumerate(progression):
        degree_index, quality = harmony_generator._roman_to_degree_and_quality(roman)
        print(f"  Takt {i + 1:02d}: {roman:>3}  -> degree_index={degree_index}, quality={quality}")
    print("[test] ---------------------------------------------------\n")


def test_print_chord_track_summary(
    harmony_generator: HarmonyGenerator,
    song_specification: SongSpecification,
    instrument: Instrument,
    max_bars: int = 8,
) -> None:
    """test-Hilfe: Erzeugt eine Akkordspur und zeigt die ersten Takte ausführlich an."""
    chord_events = harmony_generator.generate_chord_track(song_specification, instrument)
    bar_duration, _ = harmony_generator._bar_and_qnote_duration(
        song_specification.tempo_bpm,
        *song_specification.time_signature
    )
    progression = harmony_generator.choose_chord_progression(song_specification)

    print("\n[test] ---------------- CHORD TRACK ----------------------")
    print(f"Instrument: {instrument.name} (Channel {instrument.channel})")
    print(f"Bar-Dauer: {bar_duration:.3f} s")
    print("Erste Akkord-Takte:")

    # Events pro Takt gruppieren (nur für test)
    bars_to_show = min(max_bars, song_specification.number_of_bars)
    for bar_idx in range(bars_to_show):
        bar_start = bar_idx * bar_duration
        bar_end = bar_start + bar_duration
        bar_events = [
            ev for ev in chord_events
            if bar_start <= ev.start_time < bar_end
        ]
        print(f"\n  Takt {bar_idx + 1:02d} ({progression[bar_idx]}):")
        for ev in bar_events:
            print(
                f"    Note: pitch={ev.pitch:3d}, "
                f"start={ev.start_time:6.3f}s, end={ev.end_time:6.3f}s, vel={ev.velocity}"
            )

    print("\n[test] Gesamte Anzahl Akkord-Noten:", len(chord_events))
    print("[test] ---------------------------------------------------\n")


def test_print_bass_track_summary(
    harmony_generator: HarmonyGenerator,
    song_specification: SongSpecification,
    instrument: Instrument,
    max_bars: int = 8,
) -> None:
    """test-Hilfe: Erzeugt eine Bassspur und zeigt die ersten Takte ausführlich an."""
    bass_events = harmony_generator.generate_bass_track(song_specification, instrument)
    bar_duration, quarter_duration = harmony_generator._bar_and_qnote_duration(
        song_specification.tempo_bpm,
        *song_specification.time_signature
    )
    progression = harmony_generator.choose_chord_progression(song_specification)

    print("\n[test] ---------------- BASS TRACK -----------------------")
    print(f"Instrument: {instrument.name} (Channel {instrument.channel})")
    print(f"Bar-Dauer: {bar_duration:.3f} s, Viertel: {quarter_duration:.3f} s")
    print("Erste Bass-Takte:")

    bars_to_show = min(max_bars, song_specification.number_of_bars)
    for bar_idx in range(bars_to_show):
        bar_start = bar_idx * bar_duration
        bar_end = bar_start + bar_duration
        bar_events = [
            ev for ev in bass_events
            if bar_start <= ev.start_time < bar_end
        ]
        print(f"\n  Takt {bar_idx + 1:02d} ({progression[bar_idx]}):")
        for ev in bar_events:
            print(
                f"    Note: pitch={ev.pitch:3d}, "
                f"start={ev.start_time:6.3f}s, end={ev.end_time:6.3f}s, vel={ev.velocity}"
            )

    print("\n[test] Gesamte Anzahl Bass-Noten:", len(bass_events))
    print("[test] ---------------------------------------------------\n")


def run_all_HarmonyGenerator_tests() -> None:
    """Führt einfache Tests für den HarmonyGenerator aus und druckt ausführliche test-Infos."""
    print("\n[TEST] =====================================================")
    print("[TEST] Starte HarmonyGenerator Tests ...")

    # --- 1) Kleine Test-Vokabulare -----------------------------------------
    scale_vocab = {
        "C major": [0, 2, 4, 5, 7, 9, 11],
        "A minor": [9, 11, 0, 2, 4, 5, 7],
    }
    chord_vocab = {
        "maj": [0, 4, 7],
        "min": [0, 3, 7],
        "dim": [0, 3, 6],
    }
    pattern_templates = {}  # aktuell nicht genutzt, aber für später reserviert

    hg = HarmonyGenerator(scale_vocab, chord_vocab, pattern_templates)

    # --- 2) SongSpecification-Testobjekt -----------------------------------
    # Hinweis: band_configuration=None ist hier okay, weil HarmonyGenerator sie nicht nutzt.
    song_spec = SongSpecification(
        song_identifier="test_song_harmony",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        number_of_bars=8,
        key="C major",
        style="pop_straight",
        band_configuration=None,  # type: ignore[arg-type]
        random_seed=42,
    )

    # --- 3) Test-Instrumente -----------------------------------------------
    piano = Instrument(
        name="Acoustic Grand Piano",
        gm_program=0,
        channel=0,
        volume=0.9,
        pan=0.0,
        role="chords",
    )
    bass = Instrument(
        name="Electric Bass (finger)",
        gm_program=33,
        channel=1,
        volume=0.9,
        pan=0.0,
        role="bass",
    )
    pad = Instrument(
        name="Warm Pad",
        gm_program=88,
        channel=2,
        volume=0.7,
        pan=0.0,
        role="pad",
    )

    # --- 4) Akkordfolge testen ---------------------------------------------
    print("\n[TEST] --- Akkordfolge (Chord Progression) ---")
    test_print_chord_progression(hg, song_spec)

    # --- 5) Akkordspur testen ----------------------------------------------
    print("\n[TEST] --- Akkordspur (Piano) ---")
    test_print_chord_track_summary(hg, song_spec, piano)

    # --- 6) Bassspur testen -------------------------------------------------
    print("\n[TEST] --- Bassspur (Bass) ---")
    test_print_bass_track_summary(hg, song_spec, bass)

    # --- 7) Pad-/Lead-Spur testen ------------------------------------------
    print("\n[TEST] --- Pad-Spur (einfacher Test) ---")
    pad_events = hg.generate_pad_or_lead_tracks(song_spec, [pad])
    print(f"[TEST] Anzahl erzeugter Pad-Noten: {len(pad_events)}")
    print("[TEST] Erste Pad-Noten (max. 16):")
    for ev in pad_events[:16]:
        print(
            f"    Pad: pitch={ev.pitch}, "
            f"start={ev.start_time:.3f}s, end={ev.end_time:.3f}s, "
            f"vel={ev.velocity}, channel={ev.channel}"
        )

    print("\n[TEST] HarmonyGenerator Tests abgeschlossen.")
    print("[TEST] =====================================================\n")


if __name__ == "__main__":
    run_all_HarmonyGenerator_tests()

