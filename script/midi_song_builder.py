from __future__ import annotations
from typing import List
import os
import pretty_midi

from .song_specification import SongSpecification
from .drum_mapping import DrumMapping
from .band_configuration import BandConfiguration
from .instrument import Instrument

class MidiSongBuilder:
    """Baut aus Events eine standardkonforme MIDI-Datei.

    Verantwortung:
        MidiSongBuilder nimmt alle erzeugten Events (Drums + Harmonien) und
        baut daraus eine echte MIDI-Datei (z. B. mit pretty_midi).
        Er kümmert sich um Ticks, Tempo, Kanäle und Program-Changes für jedes
        Instrument.
        Damit hast du am Ende eine standardkonforme MIDI-Datei, die du rendern
        und für Labels verwenden kannst.
    """

    def __init__(
        self,
        sample_rate: int,
        ticks_per_beat: int,
        drum_mapping: DrumMapping,
    ) -> None:
        """Konstruktor für den MidiSongBuilder.

        Args:
            sample_rate: Samplerate, um Timing mit Audio abzugleichen
                (z. B. 16000 oder 44100).
            ticks_per_beat: Auflösung in Ticks pro Viertelnote (z. B. 480).
            drum_mapping: Zentrale DrumMapping-Instanz zur Konvertierung von
                Drum-Klassen in konkrete MIDI-Noten.
        """
        self.sample_rate: int = int(sample_rate)
        self.ticks_per_beat: int = int(ticks_per_beat)
        self.drum_mapping: DrumMapping = drum_mapping

    # --------------------------------------------------------------------- #
    # Hilfsfunktion für Timing
    # --------------------------------------------------------------------- #

    @staticmethod
    def _compute_timing(song_specification: SongSpecification) -> tuple[float, float, float]:
        """Hilfsfunktion: Liefert (beats_per_bar, seconds_per_beat, seconds_per_bar)."""
        numerator, denominator = song_specification.time_signature
        beats_per_bar = numerator * (4.0 / float(denominator))
        seconds_per_beat = 60.0 / song_specification.tempo_bpm
        seconds_per_bar = beats_per_bar * seconds_per_beat
        return beats_per_bar, seconds_per_beat, seconds_per_bar

    # --------------------------------------------------------------------- #
    # Öffentliche API
    # --------------------------------------------------------------------- #

    def build_pretty_midi(
        self,
        song_specification: SongSpecification,
        drum_events: List["DrumEvent"],
        note_events: List["NoteEvent"],
    ) -> pretty_midi.PrettyMIDI:
        """Erzeugt ein PrettyMIDI-Objekt aus allen Events.

        Beschreibung:
            Kombiniert alle Events und erzeugt ein PrettyMIDI-Objekt mit Tracks,
            Kanälen, Program-Changes und korrekten Noten.

            Annahmen über Event-Strukturen:
                DrumEvent:
                    - time_sec: float (Onset in Sekunden)
                    - drum_class: str (z. B. "KICK", "SNARE")
                    - velocity: int (1–127)
                NoteEvent:
                    - start_time: float (Onset in Sekunden)
                    - end_time: float (Offset in Sekunden)
                    - pitch: int (MIDI-Notennummer)
                    - velocity: int (1–127)
                    - channel: int (0–15; Zuordnung zu Instrumenten)

        Args:
            song_specification: Spezifikation des Songs.
            drum_events: Liste aller DrumEvent-Objekte (Drum-Spur).
            note_events: Liste aller NoteEvent-Objekte (harmonische Spuren).

        Returns:
            Ein PrettyMIDI-Objekt, das den kompletten Song repräsentiert.
        """
        # PrettyMIDI-Objekt mit gewünschter Auflösung und Tempo
        pm = pretty_midi.PrettyMIDI(
            resolution=self.ticks_per_beat,
            initial_tempo=song_specification.tempo_bpm,
        )

        # -------------------- Drums -------------------- #
        # Ein Drum-Instrument (GM: Channel 10, in pretty_midi via is_drum=True)
        drum_instrument = pretty_midi.Instrument(
            program=0,  # ignoriert, wenn is_drum=True
            is_drum=True,
            name="Drums",
        )

        for ev in sorted(drum_events, key=lambda e: e.time_sec):
            # Hole eine repräsentative Note für die Drum-Klasse
            try:
                pitch = self.drum_mapping.get_primary_note_for_class(ev.drum_class)
            except KeyError:
                # Unbekannte Drum-Klasse -> überspringen
                continue

            start = float(ev.time_sec)
            # Kurze Dauer für Drums, z. B. 50 ms
            end = start + 0.05

            note = pretty_midi.Note(
                velocity=int(ev.velocity),
                pitch=int(pitch),
                start=start,
                end=end,
            )
            drum_instrument.notes.append(note)

        if drum_instrument.notes:
            pm.instruments.append(drum_instrument)

        # -------------------- Harmonische Instrumente -------------------- #
                # Map: channel -> pretty_midi.Instrument
        channel_to_instrument: dict[int, pretty_midi.Instrument] = {}

        # Aus der BandConfiguration Instrumente anlegen (falls vorhanden)
        band_conf: BandConfiguration = song_specification.band_configuration
        for inst in band_conf.instruments:
            # Wir nehmen pro Kanal das erste Instrument, das wir finden.
            if inst.channel in channel_to_instrument:
                continue
            pm_inst = pretty_midi.Instrument(
                program=int(inst.gm_program),
                is_drum=False,
                name=inst.name,
            )
            channel_to_instrument[inst.channel] = pm_inst

        # Falls NoteEvents Kanäle nutzen, für die wir noch kein Instrument haben,
        # legen wir ein generisches Instrument an.
        for ne in note_events:
            ch = int(ne.channel)
            if ch not in channel_to_instrument:
                pm_inst = pretty_midi.Instrument(
                    program=0,
                    is_drum=False,
                    name=f"Channel_{ch}",
                )
                channel_to_instrument[ch] = pm_inst

        # Noten in die entsprechenden Instrumente einfügen
        for ne in note_events:
            ch = int(ne.channel)
            pm_inst = channel_to_instrument[ch]

            note = pretty_midi.Note(
                velocity=int(ne.velocity),
                pitch=int(ne.pitch),
                start=float(ne.start_time),
                end=float(ne.end_time),
            )
            pm_inst.notes.append(note)

        # Nur Instrumente mit Noten hinzufügen
        for inst in channel_to_instrument.values():
            if inst.notes:
                pm.instruments.append(inst)

        return pm

    def save_midi(self, pretty_midi_object: pretty_midi.PrettyMIDI, path: str) -> None:
        """Speichert ein PrettyMIDI-Objekt als .mid-Datei.

        Beschreibung:
            Speichert das erzeugte PrettyMIDI-Objekt als .mid-Datei auf der
            Festplatte.

        Args:
            pretty_midi_object: Das zu speichernde PrettyMIDI-Objekt.
            path: Zielpfad der zu schreibenden MIDI-Datei.
        """
        # Sicherstellen, dass der Zielordner existiert
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        pretty_midi_object.write(path)

    def compute_bar_positions(
        self,
        song_specification: SongSpecification,
    ) -> List[float]:
        """Berechnet Startzeiten aller Takte in Sekunden.

        Beschreibung:
            Berechnet die Startzeiten aller Takte in Sekunden und gibt sie als
            Liste zurück (hilfreich für Fills, Struktur etc.).

        Args:
            song_specification: Spezifikation des Songs.

        Returns:
            Liste der Taktstartzeiten in Sekunden (Länge = number_of_bars).
        """
        _, _, seconds_per_bar = self._compute_timing(song_specification)
        positions = [
            bar_index * seconds_per_bar
            for bar_index in range(song_specification.number_of_bars)
        ]
        return positions


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für MidiSongBuilder
# ---------------------------------------------------------------------------

# Für Tests brauchen wir DrumEvent und NoteEvent-Strukturen.
# Wir definieren einfache Dummy-Klassen, die das gleiche Interface haben.


class _TestDrumEvent:
    def __init__(self, time_sec: float, drum_class: str, velocity: int) -> None:
        self.time_sec = time_sec
        self.drum_class = drum_class
        self.velocity = velocity


class _TestNoteEvent:
    def __init__(
        self,
        start_time: float,
        end_time: float,
        pitch: int,
        velocity: int,
        channel: int,
    ) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.pitch = pitch
        self.velocity = velocity
        self.channel = channel

