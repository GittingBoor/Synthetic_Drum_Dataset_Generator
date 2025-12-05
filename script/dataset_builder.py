from __future__ import annotations
from typing import List, Dict, Any
import os
import json
import random

from .band_configuration import BandConfiguration
from .drum_pattern_generator import DrumPatternGenerator
from .harmony_generator import HarmonyGenerator
from .midi_song_builder import MidiSongBuilder
from .audio_renderer import AudioRenderer
from .label_extractor import LabelExtractor
from .song_specification import SongSpecification
from .dataset_example import DatasetExample


class DatasetBuilder:
    """Orchestriert die Generierung des gesamten Datensatzes.

    Verantwortung:
        DatasetBuilder ist der „Orchestrator“, der die komplette Pipeline steuert:
        SongSpecification erzeugen, Drums und Harmonien generieren, MIDI bauen,
        Audio rendern, Labels erzeugen und alles als Datensatz ablegen.
        Er kümmert sich darum, number_of_songs Beispiele zu erzeugen und eine
        Index-Datei zu schreiben.
        Damit kannst du mit einem einzigen Aufruf deinen kompletten synthetischen
        Drum-Datensatz erstellen.
    """

    def __init__(
        self,
        output_root_directory: str,
        number_of_songs: int,
        band_configuration_pool: List[BandConfiguration],
        drum_pattern_generator: DrumPatternGenerator,
        harmony_generator: HarmonyGenerator,
        midi_song_builder: MidiSongBuilder,
        audio_renderer: AudioRenderer,
        label_extractor: LabelExtractor,
        random_seed: int,
    ) -> None:
        """Konstruktor für den DatasetBuilder.

        Args:
            output_root_directory: Wurzelverzeichnis für alle erzeugten Daten.
            number_of_songs: Anzahl der zu generierenden Songs.
            band_configuration_pool: Liste möglicher BandConfiguration-Varianten.
            drum_pattern_generator: Instanz des DrumPatternGenerator.
            harmony_generator: Instanz des HarmonyGenerator.
            midi_song_builder: Instanz des MidiSongBuilder.
            audio_renderer: Instanz des AudioRenderer.
            label_extractor: Instanz des LabelExtractor.
            random_seed: Seed für reproduzierbare Datensatzerstellung.
        """
        self.output_root_directory = output_root_directory
        self.number_of_songs = number_of_songs
        self.band_configuration_pool = band_configuration_pool
        self.drum_pattern_generator = drum_pattern_generator
        self.harmony_generator = harmony_generator
        self.midi_song_builder = midi_song_builder
        self.audio_renderer = audio_renderer
        self.label_extractor = label_extractor
        self.random_seed = random_seed

        # Liste aller erzeugten Beispiele
        self.examples: List[DatasetExample] = []

        # Root-Verzeichnis anlegen
        os.makedirs(self.output_root_directory, exist_ok=True)

    # ------------------------------------------------------------------
    # Hilfsfunktionen (intern)
    # ------------------------------------------------------------------

    def _ensure_output_subdirs(self) -> Dict[str, str]:
        """Stellt sicher, dass audio/, midi/ und labels/ existieren."""
        audio_dir = os.path.join(self.output_root_directory, "audio")
        midi_dir = os.path.join(self.output_root_directory, "midi")
        label_dir = os.path.join(self.output_root_directory, "labels")

        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(midi_dir, exist_ok=True)
        os.makedirs(label_dir, exist_ok=True)

        return {
            "audio": audio_dir,
            "midi": midi_dir,
            "labels": label_dir,
        }

    # ------------------------------------------------------------------
    # Öffentliche API
    # ------------------------------------------------------------------

    def generate_song_specification(self, index: int) -> SongSpecification:
        """Erzeugt eine SongSpecification für einen einzelnen Song.

        Beschreibung:
            Erstellt für einen Song eine neue SongSpecification (z. B. mit
            zufälliger Tonart, Tempo und Bandkonfiguration), abhängig vom Index
            und Seed.

        Args:
            index: Laufindex des Songs (z. B. 0, 1, 2, ...).

        Returns:
            Eine neue SongSpecification für diesen Song.
        """
        # Eigener Random-Generator pro Index, damit reproduzierbar
        rnd = random.Random(self.random_seed + index)

        song_identifier = f"song_{index:04d}"

        tempo_bpm = rnd.uniform(90.0, 140.0)  # 90–140 BPM
        time_signature = rnd.choice([(4, 4), (3, 4)])
        number_of_bars = rnd.choice([8, 12, 16])

        possible_keys = ["C major", "G major", "F major", "A minor", "E minor"]
        key = rnd.choice(possible_keys)

        possible_styles = ["pop_straight", "pop_shuffled", "funk"]
        style = rnd.choice(possible_styles)

        # Band-Konfiguration wählen, falls vorhanden
        if self.band_configuration_pool:
            band_configuration = rnd.choice(self.band_configuration_pool)
        else:
            band_configuration = None  # type: ignore[assignment]

        song_spec = SongSpecification(
            song_identifier=song_identifier,
            tempo_bpm=tempo_bpm,
            time_signature=time_signature,
            number_of_bars=number_of_bars,
            key=key,
            style=style,
            band_configuration=band_configuration,
            random_seed=self.random_seed,
        )

        return song_spec

    def generate_single_example(
        self,
        song_specification: SongSpecification,
    ) -> DatasetExample:
        """Erzeugt ein einzelnes DatasetExample mit allen Dateien.

        Beschreibung:
            Führt alle Schritte für genau einen Song aus (Drums generieren,
            Harmonien generieren, MIDI bauen, Audio rendern, Labels extrahieren)
            und verpackt das Ergebnis in ein DatasetExample.

        Args:
            song_specification: Spezifikation des Songs, der generiert werden soll.

        Returns:
            Ein vollständig erzeugtes DatasetExample.
        """
        dirs = self._ensure_output_subdirs()
        song_id = song_specification.song_identifier

        # Pfade festlegen
        midi_path = os.path.join(dirs["midi"], f"{song_id}.mid")
        audio_path = os.path.join(dirs["audio"], f"{song_id}.wav")
        label_path = os.path.join(dirs["labels"], f"{song_id}_labels.json")
        mix_variant = "default"

        # 1) Drum-Events generieren
        drum_events = self.drum_pattern_generator.generate_drum_track(song_specification)

        # 2) Harmonien generieren (falls Band-Konfiguration vorhanden)
        note_events: List[Any] = []

        band_cfg = getattr(song_specification, "band_configuration", None)

        if band_cfg is not None:
            # Versuche, Rollen zu nutzen, falls BandConfiguration so etwas bietet
            chords_instruments: List[Any] = []
            bass_instruments: List[Any] = []
            pad_instruments: List[Any] = []

            if hasattr(band_cfg, "get_instruments_by_role"):
                chords_instruments = band_cfg.get_instruments_by_role("chords")
                bass_instruments = band_cfg.get_instruments_by_role("bass")
                pad_instruments = band_cfg.get_instruments_by_role("pad")
            else:
                # Falls es diese Methode nicht gibt, nimm einfach alle Instrumente als "chords"
                chords_instruments = getattr(band_cfg, "instruments", [])

            # Akkordspur (nur erstes Chord-Instrument, um es einfach zu halten)
            if chords_instruments:
                chord_instr = chords_instruments[0]
                chord_events = self.harmony_generator.generate_chord_track(
                    song_specification,
                    chord_instr,
                )
                note_events.extend(chord_events)

            # Bassspur
            if bass_instruments:
                bass_instr = bass_instruments[0]
                bass_events = self.harmony_generator.generate_bass_track(
                    song_specification,
                    bass_instr,
                )
                note_events.extend(bass_events)

            # Pads/Leads
            if pad_instruments:
                pad_events = self.harmony_generator.generate_pad_or_lead_tracks(
                    song_specification,
                    pad_instruments,
                )
                note_events.extend(pad_events)

        # 3) MIDI-Datei bauen und speichern
        pretty_midi_obj = self.midi_song_builder.build_pretty_midi(
            song_specification,
            drum_events,
            note_events,
        )
        self.midi_song_builder.save_midi(pretty_midi_obj, midi_path)

        # 4) Audio rendern
        self.audio_renderer.render_midi_to_wav(midi_path, audio_path)

        # 5) Labels erzeugen und speichern
        labels = self.label_extractor.extract_from_midi(midi_path)
        self.label_extractor.save_labels_json(labels, label_path)

        # 6) DatasetExample erzeugen
        example = DatasetExample(
            song_identifier=song_id,
            audio_path=audio_path,
            label_path=label_path,
            midi_path=midi_path,
            mix_variant=mix_variant,
            song_specification=song_specification,
        )

        return example

    def build_dataset(self) -> List[DatasetExample]:
        """Erzeugt den kompletten Datensatz.

        Beschreibung:
            Erzeugt number_of_songs Beispiele, speichert alle Daten (MIDI, Audio,
            Labels) und gibt die Liste aller DatasetExample zurück.

        Returns:
            Liste aller erzeugten DatasetExample-Objekte.
        """
        self.examples = []

        for idx in range(self.number_of_songs):
            print(f"[DatasetBuilder] Generiere Song {idx + 1}/{self.number_of_songs} ...")
            song_spec = self.generate_song_specification(idx)
            example = self.generate_single_example(song_spec)
            self.examples.append(example)

        print(f"[DatasetBuilder] Fertig. Anzahl Beispiele: {len(self.examples)}")
        return self.examples

    def save_index(self, path: str) -> None:
        """Schreibt eine zentrale Index-Datei für den Datensatz.

        Beschreibung:
            Schreibt eine zentrale Index-Datei (z. B. "dataset_index.json"), in
            der alle Beispiele mit ihren Pfaden und Metadaten verzeichnet sind.

        Args:
            path: Zielpfad für die Index-Datei.
        """
        if not self.examples:
            print("[DatasetBuilder] WARNUNG: Keine Beispiele vorhanden. Index wird leer geschrieben.")

        index_entries = [ex.to_index_entry() for ex in self.examples]

        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(index_entries, f, indent=2, ensure_ascii=False)

        print(f"[DatasetBuilder] Index-Datei geschrieben: {path}")


# ------------------------------------------------------------------
# test- / Test-Funktionen (außerhalb der Klasse)
# ------------------------------------------------------------------


class FakeDrumPatternGenerator:
    """Einfache Fake-Version für Tests (erzeugt keine echten Patterns)."""

    def generate_drum_track(self, song_specification: SongSpecification) -> List[Any]:
        print(f"[test] FakeDrumPatternGenerator.generate_drum_track für {song_specification.song_identifier}")
        return []


class FakeHarmonyGenerator:
    """Einfache Fake-Version für Tests (erzeugt keine echten Noten)."""

    def choose_chord_progression(self, song_specification: SongSpecification) -> List[str]:
        return ["I", "V", "vi", "IV"]

    def generate_chord_track(self, song_specification: SongSpecification, instrument: Any) -> List[Any]:
        print(f"[test] FakeHarmonyGenerator.generate_chord_track für {song_specification.song_identifier}")
        return []

    def generate_bass_track(self, song_specification: SongSpecification, instrument: Any) -> List[Any]:
        print(f"[test] FakeHarmonyGenerator.generate_bass_track für {song_specification.song_identifier}")
        return []

    def generate_pad_or_lead_tracks(self, song_specification: SongSpecification, instruments: List[Any]) -> List[Any]:
        print(f"[test] FakeHarmonyGenerator.generate_pad_or_lead_tracks für {song_specification.song_identifier}")
        return []


class FakeMidiSongBuilder:
    """Einfache Fake-Version für Tests (schreibt Dummy-MIDI-Datei)."""

    def build_pretty_midi(self, song_specification: SongSpecification, drum_events: List[Any], note_events: List[Any]) -> Any:
        print(f"[test] FakeMidiSongBuilder.build_pretty_midi für {song_specification.song_identifier}")
        return {"dummy": "midi_object"}

    def save_midi(self, pretty_midi_object: Any, path: str) -> None:
        print(f"[test] FakeMidiSongBuilder.save_midi -> {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(b"")  # leere Datei als Platzhalter


class FakeAudioRenderer:
    """Einfache Fake-Version für Tests (schreibt Dummy-WAV-Datei)."""

    def render_midi_to_wav(self, midi_path: str, output_wav_path: str) -> None:
        print(f"[test] FakeAudioRenderer.render_midi_to_wav: {midi_path} -> {output_wav_path}")
        os.makedirs(os.path.dirname(output_wav_path), exist_ok=True)
        with open(output_wav_path, "wb") as f:
            f.write(b"")  # leere Datei als Platzhalter


class FakeLabelExtractor:
    """Einfache Fake-Version für Tests (schreibt Dummy-Label-Datei)."""

    def extract_from_midi(self, midi_path: str) -> List[Dict[str, Any]]:
        print(f"[test] FakeLabelExtractor.extract_from_midi: {midi_path}")
        return [{"dummy_label": True}]

    def save_labels_json(self, labels: List[Dict[str, Any]], path: str) -> None:
        print(f"[test] FakeLabelExtractor.save_labels_json -> {path}")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2, ensure_ascii=False)


