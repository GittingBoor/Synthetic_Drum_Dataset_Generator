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

def _create_example_drum_mapping() -> DrumMapping:
    """Erzeugt eine DrumMapping-Instanz mit relevanten Drum-Klassen."""
    note_to_class = {
        36: "KICK",
        38: "SNARE",
        42: "HH_CLOSED",
        49: "CRASH",
    }
    class_to_notes = {
        "KICK": [36],
        "SNARE": [38],
        "HH_CLOSED": [42],
        "CRASH": [49],
    }
    core_classes = ["KICK", "SNARE", "HH_CLOSED", "CRASH"]
    return DrumMapping(
        note_to_class=note_to_class,
        class_to_notes=class_to_notes,
        core_classes=core_classes,
    )


def _create_example_song_spec_for_midi() -> SongSpecification:
    """Erzeugt eine einfache SongSpecification mit BandConfiguration für Tests."""
    drum_mapping = _create_example_drum_mapping()
    instruments = [
        Instrument(
            name="Acoustic Grand Piano",
            gm_program=0,
            channel=0,
            volume=0.9,
            pan=0.0,
            role="chords",
        ),
        Instrument(
            name="Electric Bass (finger)",
            gm_program=33,
            channel=1,
            volume=0.9,
            pan=-0.1,
            role="bass",
        ),
    ]
    band_conf = BandConfiguration(
        drum_channel=9,
        drum_mapping=drum_mapping,
        instruments=instruments,
    )

    song_spec = SongSpecification(
        song_identifier="song_midi_test",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        number_of_bars=4,
        key="C major",
        style="pop_straight",
        band_configuration=band_conf,
        random_seed=1,
    )
    return song_spec


def test_compute_bar_positions_basic() -> None:
    """Testet, ob compute_bar_positions die erwarteten Taktstartzeiten liefert."""
    print("[TEST] test_compute_bar_positions_basic gestartet …")
    song_spec = _create_example_song_spec_for_midi()
    drum_mapping = song_spec.band_configuration.drum_mapping
    builder = MidiSongBuilder(
        sample_rate=16000,
        ticks_per_beat=480,
        drum_mapping=drum_mapping,
    )

    positions = builder.compute_bar_positions(song_spec)
    print(f"  - Bar-Positionen: {positions}")

    # 4/4, 120 BPM -> 4 Schläge pro Takt, 0.5 s pro Schlag, 2 s pro Takt
    expected = [0.0, 2.0, 4.0, 6.0]
    assert len(positions) == song_spec.number_of_bars
    for p, e in zip(positions, expected):
        assert abs(p - e) < 1e-6, f"Erwartet {e}, bekommen {p}"

    print("[TEST] test_compute_bar_positions_basic erfolgreich abgeschlossen.\n")


def test_build_pretty_midi_creates_instruments_and_notes() -> None:
    """Testet, ob build_pretty_midi Drum- und Nicht-Drum-Spuren mit Noten erzeugt."""
    print("[TEST] test_build_pretty_midi_creates_instruments_and_notes gestartet …")
    song_spec = _create_example_song_spec_for_midi()
    drum_mapping = song_spec.band_configuration.drum_mapping
    builder = MidiSongBuilder(
        sample_rate=16000,
        ticks_per_beat=480,
        drum_mapping=drum_mapping,
    )

    # DrumEvents: Kick auf 0.0, Snare auf 0.5, Hi-Hat auf 0.0
    drum_events = [
        _TestDrumEvent(time_sec=0.0, drum_class="KICK", velocity=100),
        _TestDrumEvent(time_sec=0.5, drum_class="SNARE", velocity=95),
        _TestDrumEvent(time_sec=0.0, drum_class="HH_CLOSED", velocity=80),
    ]

    # NoteEvents: einfache C-Dur-Akkorde auf Kanal 0 und Bass auf Kanal 1
    note_events = [
        _TestNoteEvent(
            start_time=0.0,
            end_time=1.0,
            pitch=60,
            velocity=90,
            channel=0,
        ),
        _TestNoteEvent(
            start_time=1.0,
            end_time=2.0,
            pitch=64,
            velocity=90,
            channel=0,
        ),
        _TestNoteEvent(
            start_time=0.0,
            end_time=2.0,
            pitch=36,
            velocity=100,
            channel=1,
        ),
    ]

    pm = builder.build_pretty_midi(song_spec, drum_events, note_events)
    print(f"  - Anzahl Instrumente im PrettyMIDI: {len(pm.instruments)}")
    assert isinstance(pm, pretty_midi.PrettyMIDI)
    assert len(pm.instruments) > 0

    drum_tracks = [inst for inst in pm.instruments if inst.is_drum]
    non_drum_tracks = [inst for inst in pm.instruments if not inst.is_drum]

    print(f"  - Drum-Tracks: {len(drum_tracks)}")
    print(f"  - Non-Drum-Tracks: {len(non_drum_tracks)}")

    assert len(drum_tracks) == 1
    assert len(drum_tracks[0].notes) >= 2  # Kick + Snare + evtl. mehr

    assert len(non_drum_tracks) >= 1
    total_non_drum_notes = sum(len(inst.notes) for inst in non_drum_tracks)
    assert total_non_drum_notes >= 3

    print("[TEST] test_build_pretty_midi_creates_instruments_and_notes erfolgreich abgeschlossen.\n")


def test_save_midi_writes_file() -> None:
    """Testet, ob save_midi eine .mid-Datei erzeugt."""
    print("[TEST] test_save_midi_writes_file gestartet …")
    song_spec = _create_example_song_spec_for_midi()
    drum_mapping = song_spec.band_configuration.drum_mapping
    builder = MidiSongBuilder(
        sample_rate=16000,
        ticks_per_beat=480,
        drum_mapping=drum_mapping,
    )

    # Minimaler Inhalt
    pm = pretty_midi.PrettyMIDI()
    test_path = "test_output_midi_song_builder.mid"

    # Datei vorher löschen, falls vorhanden
    if os.path.exists(test_path):
        os.remove(test_path)

    builder.save_midi(pm, test_path)

    print(f"  - Existiert Datei {test_path}: {os.path.exists(test_path)}")
    assert os.path.exists(test_path), "MIDI-Datei wurde nicht geschrieben."
    assert os.path.getsize(test_path) > 0, "MIDI-Datei ist leer."

    # Aufräumen
    os.remove(test_path)
    print("[TEST] test_save_midi_writes_file erfolgreich abgeschlossen.\n")


def run_all_midi_song_builder_tests() -> None:
    """Führt alle Tests für MidiSongBuilder aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte MidiSongBuilder-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_compute_bar_positions_basic,
        test_build_pretty_midi_creates_instruments_and_notes,
        test_save_midi_writes_file,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle MidiSongBuilder-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_midi_song_builder_tests()
