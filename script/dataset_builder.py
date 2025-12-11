from __future__ import annotations

import sys
from typing import List, Dict, Any
import os
import json
import random

from .audio_renderer import AudioRenderer
from .drum_mapping import DrumMapping
from .drum_pattern_generator import DrumPatternGenerator, DrumEvent
from .harmony_generator import HarmonyGenerator, NoteEvent
from .label_extractor import LabelExtractor, LabelEvent
from .midi_song_builder import MidiSongBuilder
from .song_specification import SongSpecification
from .dataset_example import DatasetExample
from .dataset_presets import DatasetPreset, DATASET_PRESETS
from .band_configuration import BandConfiguration
from .instrument import Instrument


class DatasetBuilder:
    # Typ-Annotationen für PyCharm / Mypy
    output_root_directory: str
    number_of_songs: int
    band_configuration_pool: List[BandConfiguration]

    drum_pattern_generator: DrumPatternGenerator
    harmony_generator: HarmonyGenerator
    midi_song_builder: MidiSongBuilder
    audio_renderer: AudioRenderer
    label_extractor: LabelExtractor

    drum_mapping: DrumMapping

    random_seed: int
    examples: List[DatasetExample]

    min_song_length_seconds: float
    max_song_length_seconds: float

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
            drum_mapping: DrumMapping,
            random_seed: int,
            min_song_length_seconds: float,
            max_song_length_seconds: float,
    ) -> None:
        """Konstruktor für den DatasetBuilder.

        Args:
            output_root_directory: Wurzelverzeichnis für alle erzeugten Daten.
            number_of_songs: Anzahl der Songs pro Preset (oder insgesamt, je nach Logik).
            band_configuration_pool: Optionaler Pool möglicher BandConfigurations.
            drum_pattern_generator: Instanz des DrumPatternGenerator.
            harmony_generator: Instanz des HarmonyGenerator.
            midi_song_builder: Instanz des MidiSongBuilder.
            audio_renderer: Instanz des AudioRenderer.
            label_extractor: Instanz des LabelExtractor.
            drum_mapping: Zentrale DrumMapping-Instanz.
            random_seed: Seed für reproduzierbare Datensatzerstellung.
        """
        self.output_root_directory = os.path.abspath(output_root_directory)
        self.number_of_songs = int(number_of_songs)
        self.band_configuration_pool = list(band_configuration_pool)

        self.drum_pattern_generator = drum_pattern_generator
        self.harmony_generator = harmony_generator
        self.midi_song_builder = midi_song_builder
        self.audio_renderer = audio_renderer
        self.label_extractor = label_extractor

        self.drum_mapping = drum_mapping

        self.random_seed = int(random_seed)
        self.examples = []

        self.min_song_length_seconds = min_song_length_seconds
        self.max_song_length_seconds = max_song_length_seconds

        # Root-Verzeichnis anlegen
        os.makedirs(self.output_root_directory, exist_ok=True)

    def create_drum_mapping(self) -> DrumMapping:
        """Erzeugt ein DrumMapping mit den für dich relevanten Drum-Klassen."""
        note_to_class = {
            # Kicks
            36: "KICK",
            # Snares & Sidestick
            38: "SNARE",
            40: "SNARE",
            37: "SIDESTICK",
            # Hi-Hats
            42: "HH_CLOSED",
            44: "HH_CLOSED",
            46: "HH_OPEN",
            22: "HH_CLOSED",
            26: "HH_OPEN",
            # Toms
            43: "TOM_LOW",
            45: "TOM_LOW",
            47: "TOM_MID",
            48: "TOM_MID",
            50: "TOM_HIGH",
            # Crashes / Rides
            49: "CRASH",
            51: "RIDE",
            53: "RIDE",
        }

        class_to_notes = {
            "KICK": [36],
            "SNARE": [38, 40],
            "SIDESTICK": [37],
            "HH_CLOSED": [42, 44, 22],
            "HH_OPEN": [46, 26],
            "TOM_LOW": [43, 45],
            "TOM_MID": [47, 48],
            "TOM_HIGH": [50],
            "CRASH": [49],
            "RIDE": [51, 53],
        }

        core_classes = [
            "KICK",
            "SNARE",
            "SIDESTICK",
            "HH_CLOSED",
            "HH_OPEN",
            "TOM_LOW",
            "TOM_MID",
            "TOM_HIGH",
            "CRASH",
            "RIDE",
        ]

        return DrumMapping(
            note_to_class=note_to_class,
            class_to_notes=class_to_notes,
            core_classes=core_classes,
        )

    def create_instruments(self) -> List[Instrument]:
        """Definiert die Instrumente, die in der Band benutzt werden.

        Hier kannst du Instrumente hinzufügen / entfernen / anpassen.
        """
        instruments: List[Instrument] = [
            # ------------------------------------------------------------
            # Pianos & Keys
            # ------------------------------------------------------------
            Instrument(
                name="Acoustic Grand Piano",
                gm_program=0,  # GM 1
                channel=0,
                volume=0.9,
                pan=0.0,
                role="chords",
            ),
            Instrument(
                name="Bright Acoustic Piano",
                gm_program=1,  # GM 2
                channel=0,
                volume=0.9,
                pan=0.1,
                role="chords",
            ),
            Instrument(
                name="Electric Piano 1 (Rhodes)",
                gm_program=4,  # GM 5
                channel=1,
                volume=0.9,
                pan=-0.1,
                role="chords",
            ),
            Instrument(
                name="Electric Piano 2 (FM)",
                gm_program=5,  # GM 6
                channel=1,
                volume=0.9,
                pan=0.0,
                role="chords",
            ),
            Instrument(
                name="Drawbar Organ",
                gm_program=16,  # GM 17
                channel=2,
                volume=0.85,
                pan=-0.2,
                role="chords",
            ),

            # ------------------------------------------------------------
            # Gitarren
            # ------------------------------------------------------------
            Instrument(
                name="Acoustic Guitar (steel)",
                gm_program=25,  # GM 26
                channel=3,
                volume=0.85,
                pan=-0.3,
                role="chords",
            ),
            Instrument(
                name="Electric Guitar (jazz)",
                gm_program=26,  # GM 27
                channel=3,
                volume=0.85,
                pan=0.3,
                role="chords",
            ),
            Instrument(
                name="Electric Guitar (clean)",
                gm_program=27,  # GM 28
                channel=4,
                volume=0.85,
                pan=0.2,
                role="chords",
            ),
            Instrument(
                name="Electric Guitar (muted)",
                gm_program=28,  # GM 29
                channel=4,
                volume=0.8,
                pan=-0.2,
                role="chords",
            ),
            Instrument(
                name="Overdriven Guitar",
                gm_program=29,  # GM 30
                channel=5,
                volume=0.9,
                pan=0.0,
                role="lead",
            ),

            # ------------------------------------------------------------
            # Bässe
            # ------------------------------------------------------------
            Instrument(
                name="Electric Bass (finger)",
                gm_program=33,  # GM 34
                channel=6,
                volume=0.9,
                pan=-0.1,
                role="bass",
            ),
            Instrument(
                name="Electric Bass (pick)",
                gm_program=34,  # GM 35
                channel=6,
                volume=0.9,
                pan=0.1,
                role="bass",
            ),
            Instrument(
                name="Synth Bass 1",
                gm_program=38,  # GM 39
                channel=7,
                volume=0.9,
                pan=0.0,
                role="bass",
            ),
            Instrument(
                name="Synth Bass 2",
                gm_program=39,  # GM 40
                channel=7,
                volume=0.9,
                pan=0.0,
                role="bass",
            ),

            # ------------------------------------------------------------
            # Strings & Pads & Leads
            # ------------------------------------------------------------
            Instrument(
                name="String Ensemble 1",
                gm_program=48,  # GM 49
                channel=8,
                volume=0.8,
                pan=-0.1,
                role="pad",
            ),
            Instrument(
                name="Synth Strings 1",
                gm_program=50,  # GM 51
                channel=8,
                volume=0.8,
                pan=0.1,
                role="pad",
            ),
            Instrument(
                name="Lead 1 (square)",
                gm_program=80,  # GM 81
                channel=10,  # (9 wird für Drums genutzt)
                volume=0.85,
                pan=-0.2,
                role="lead",
            ),
            Instrument(
                name="Lead 2 (sawtooth)",
                gm_program=81,  # GM 82
                channel=10,
                volume=0.85,
                pan=0.2,
                role="lead",
            ),

            # ------------------------------------------------------------
            # Brass & Reeds
            # ------------------------------------------------------------
            Instrument(
                name="Trumpet",
                gm_program=56,  # GM 57
                channel=11,
                volume=0.85,
                pan=0.1,
                role="lead",
            ),
            Instrument(
                name="Alto Sax",
                gm_program=65,  # GM 66
                channel=11,
                volume=0.85,
                pan=-0.1,
                role="lead",
            ),
        ]
        return instruments

    def create_band_configuration(self) -> BandConfiguration:
        """Erzeugt eine BandConfiguration mit Drums + den oben definierten Instrumenten."""
        instruments = self.create_instruments()
        band_conf = BandConfiguration(
            drum_channel=9,  # GM-Standard-Drumkanal
            drum_mapping=self.drum_mapping,
            instruments=instruments,
        )
        return band_conf

    @staticmethod
    def create_harmony_generator() -> HarmonyGenerator:
        """Erzeugt einen einfachen HarmonyGenerator mit Standard-Vokabular."""
        scale_vocab = {
            "C major": [0, 2, 4, 5, 7, 9, 11],
            "D major": [2, 4, 6, 7, 9, 11, 1],
            "F major": [5, 7, 9, 10, 0, 2, 4],
            "G major": [7, 9, 11, 0, 2, 4, 6],
            "A major": [9, 11, 1, 2, 4, 6, 8],

            "D minor": [2, 4, 5, 7, 9, 10, 0],
            "E minor": [4, 6, 7, 9, 11, 0, 2],
            "A minor": [9, 11, 0, 2, 4, 5, 7],
        }

        chord_vocab = {
            "maj": [0, 4, 7],
            "min": [0, 3, 7],
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10],
            "7": [0, 4, 7, 10],
            "sus2": [0, 2, 7],
            "sus4": [0, 5, 7],
        }

        return HarmonyGenerator(
            scale_vocab=scale_vocab,
            chord_vocab=chord_vocab
        )

    # ------------------------------------------------------------------
    # Hilfsfunktionen (intern)
    # ------------------------------------------------------------------

    @staticmethod
    def _print_progress(current: int, total: int, bar_width: int = 40) -> None:
        """Einfache Fortschrittsanzeige im Terminal (eine Zeile, wird überschrieben)."""
        if total <= 0:
            return

        fraction = current / total
        filled = int(bar_width * fraction)
        bar = "█" * filled + "-" * (bar_width - filled)
        percent = int(fraction * 100)

        sys.stdout.write(f"\rProgress: |{bar}| {percent:3d}% ({current}/{total})")
        sys.stdout.flush()

        # Am Ende einmal Zeilenumbruch, damit die nächste Ausgabe darunter steht
        if current >= total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _load_existing_index_entries(self, output_root: str) -> list[dict]:
        """Liest eine vorhandene dataset_index.json ein (falls vorhanden).

        Gibt eine Liste von Dict-Einträgen zurück oder eine leere Liste,
        wenn keine oder eine kaputte Datei vorhanden ist.
        """
        index_path = os.path.join(output_root, "dataset_index.json")
        if not os.path.exists(index_path):
            return []

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            # Wenn etwas schiefgeht: so tun, als gäbe es keinen Index
            pass
        return []

    def _determine_start_indices(
            self,
            existing_entries: list[dict],
    ) -> tuple[int, int]:
        """Bestimmt (next_song_index, seed_for_first_new_song).

        - next_song_index: globaler Index für den nächsten Song (1-basiert)
        - seed_for_first_new_song: Random-Seed für den ersten neu erzeugten Song
        """
        if not existing_entries:
            # Noch kein Dataset vorhanden
            next_song_index = 1
            first_seed = self.random_seed
            return next_song_index, first_seed

        # Annahme: bisher immer fortlaufend ohne Lücken erzeugt
        next_song_index = len(existing_entries) + 1

        # Versuche, den Seed aus den bisherigen Einträgen zu lesen
        seeds: list[int] = []
        for entry in existing_entries:
            # je nachdem, wie du den Seed nennst
            seed_value = entry.get("random_seed") or entry.get("seed")
            if isinstance(seed_value, int):
                seeds.append(seed_value)

        if seeds:
            # Einfach den nächsthöheren Seed verwenden
            first_seed = max(seeds) + 1
        else:
            # Fallback: verhalte dich wie früher, nur um bereits existierende
            # Songs nach hinten verschoben
            first_seed = self.random_seed + len(existing_entries)

        return next_song_index, first_seed

    @staticmethod
    def _preset_to_dict(preset: DatasetPreset) -> dict[str, Any]:
        """Serialisiert ein DatasetPreset in ein JSON-freundliches Dict."""
        return {
            "name": preset.name,
            "tempo_bpm": preset.tempo_bpm,
            "time_signature": list(preset.time_signature),
            "key": preset.key,
            "style": preset.style,
            "drum_complexity": preset.drum_complexity,
            "ghostnote_probability": preset.ghostnote_probability,
            "fill_probability": preset.fill_probability,
            "swing_amount": preset.swing_amount,
            "pause_probability": preset.pause_probability,
            "min_instruments": preset.min_instruments,
            "max_instruments": preset.max_instruments,
        }

    @staticmethod
    def _init_dataset_info(dataset_config: dict[str, Any]) -> dict[str, Any]:
        """Erzeugt das Grundgerüst für dataset_info.json."""
        return {
            "dataset_config": dataset_config,  # globale Parameter (Root, Subdirs, Seeds, ...)
            "presets": {},  # wird: name -> {preset-Daten + songs[]}
        }

    def _register_song_in_info(
            self,
            dataset_info: dict[str, Any],
            preset: DatasetPreset,
            song_basename: str,
    ) -> None:
        """Hängt einen Song-Basename an das passende Preset im dataset_info-Objekt an."""
        presets_dict = dataset_info["presets"]

        if preset.name not in presets_dict:
            preset_dict = self._preset_to_dict(preset)
            preset_dict["songs"] = []  # Liste der Song-Basenamen ohne Endungen
            presets_dict[preset.name] = preset_dict

        presets_dict[preset.name]["songs"].append(song_basename)

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

    # -----------------------------------------------------
    # Hilfsmethoden für Verzeichnisse & Pfade
    # -----------------------------------------------------
    def _prepare_output_dirs(self, output_root: str) -> tuple[str, str, str]:
        midi_dir = os.path.join(output_root, "midi")
        audio_dir = os.path.join(output_root, "audio")
        label_dir = os.path.join(output_root, "labels")

        os.makedirs(midi_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(label_dir, exist_ok=True)

        return midi_dir, audio_dir, label_dir

    def _build_paths_for_basename(
            self,
            midi_dir: str,
            audio_dir: str,
            label_dir: str,
            basename: str,
    ) -> tuple[str, str, str]:
        midi_path = os.path.join(midi_dir, f"{basename}.mid")
        audio_path = os.path.join(audio_dir, f"{basename}.wav")
        label_path = os.path.join(label_dir, f"{basename}_labels.json")
        return midi_path, audio_path, label_path

        # -----------------------------------------------------
        # Hilfsmethoden für Songlänge & SongSpecification
        # -----------------------------------------------------

    def _compute_dynamic_number_of_bars(
            self,
            preset: DatasetPreset,
            dataset_config: dict[str, Any],
            global_song_index: int,
    ) -> int:
        rng = random.Random(self.random_seed + global_song_index)

        target_length_sec = rng.uniform(
            dataset_config["min_song_length_seconds"],
            dataset_config["max_song_length_seconds"],
        )

        seconds_per_beat = 60.0 / preset.tempo_bpm
        numerator, denominator = preset.time_signature
        beats_per_bar = numerator * (4.0 / denominator)
        seconds_per_bar = seconds_per_beat * beats_per_bar

        return max(1, int(round(target_length_sec / seconds_per_bar)))

    def _create_band_configuration_for_preset(
            self,
            preset: DatasetPreset,
    ) -> BandConfiguration:
        return BandConfiguration.choose_random_band(
            available_patches=self.create_instruments(),
            min_instruments=preset.min_instruments,
            max_instruments=preset.max_instruments,
            drum_mapping=self.drum_mapping,
            drum_channel=9,
        )

    def _create_song_specification_for_preset(
            self,
            preset: DatasetPreset,
            number_of_bars: int,
            band_configuration: BandConfiguration,
            global_song_index: int,
    ) -> SongSpecification:
        song_spec = SongSpecification(
            song_identifier="",  # wird gleich gesetzt
            tempo_bpm=preset.tempo_bpm,
            time_signature=preset.time_signature,
            number_of_bars=number_of_bars,
            key=preset.key,
            style=preset.style,
            band_configuration=band_configuration,
            random_seed=self.random_seed + global_song_index,
        )
        random.seed(song_spec.random_seed)
        return song_spec

        # -----------------------------------------------------
        # Drums + Harmony
        # -----------------------------------------------------

    def _update_drum_generator_from_preset(self, preset: DatasetPreset) -> None:
        self.drum_pattern_generator.complexity = preset.drum_complexity
        self.drum_pattern_generator.ghostnote_probability = preset.ghostnote_probability
        self.drum_pattern_generator.fill_probability = preset.fill_probability
        self.drum_pattern_generator.swing_amount = preset.swing_amount
        self.drum_pattern_generator.pause_probability = preset.pause_probability

    def _generate_drum_and_note_events(
            self,
            song_spec: SongSpecification,
            band_configuration: BandConfiguration,
    ) -> tuple[List[DrumEvent], List[NoteEvent]]:
        drum_events: List[DrumEvent] = self.drum_pattern_generator.generate_drum_track(
            song_spec
        )

        note_events: List[NoteEvent] = []

        chord_instruments = band_configuration.get_instruments_by_role("chords")
        bass_instruments = band_configuration.get_instruments_by_role("bass")
        pad_instruments = band_configuration.get_instruments_by_role("pad")

        for inst in chord_instruments:
            note_events.extend(
                self.harmony_generator.generate_chord_track(song_spec, inst)
            )

        for inst in bass_instruments:
            note_events.extend(
                self.harmony_generator.generate_bass_track(song_spec, inst)
            )

        if pad_instruments:
            note_events.extend(
                self.harmony_generator.generate_pad_or_lead_tracks(
                    song_spec, pad_instruments
                )
            )

        return drum_events, note_events

        # -----------------------------------------------------
        # MIDI, Audio, Labels, DatasetExample
        # -----------------------------------------------------

    def _build_midi_audio_labels_and_example(
            self,
            song_spec: SongSpecification,
            drum_events: List[DrumEvent],
            note_events: List[NoteEvent],
            midi_path: str,
            audio_path: str,
            label_path: str,
    ) -> DatasetExample:
        # MIDI bauen + speichern
        pm = self.midi_song_builder.build_pretty_midi(
            song_specification=song_spec,
            drum_events=drum_events,
            note_events=note_events,
        )
        self.midi_song_builder.save_midi(pm, midi_path)

        # Audio rendern
        self.audio_renderer.render_midi_to_wav(
            midi_path=midi_path,
            output_wav_path=audio_path,
        )

        # Labels extrahieren
        labels: List[LabelEvent] = self.label_extractor.extract_from_midi(midi_path)
        self.label_extractor.save_labels_json(labels, label_path)

        # DatasetExample erzeugen
        example = DatasetExample(
            song_identifier=song_spec.song_identifier,
            audio_path=audio_path,
            label_path=label_path,
            midi_path=midi_path,
            mix_variant="default",
            song_specification=song_spec,
        )
        return example

        # -----------------------------------------------------
        # dataset_info.json
        # -----------------------------------------------------

    def _write_dataset_info(
            self,
            dataset_info: dict[str, Any],
            output_root: str,
    ) -> None:
        info_path = os.path.join(output_root, "dataset_info.json")
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(dataset_info, f, indent=2, ensure_ascii=False)

    def _load_existing_dataset_info(self, output_root: str) -> dict[str, Any] | None:
        """Lädt eine bestehende dataset_info.json, falls vorhanden.

        Returns:
            Das geladene Dict oder None, wenn keine Datei existiert.
        """
        info_path = os.path.join(output_root, "dataset_info.json")
        if not os.path.exists(info_path):
            return None

        with open(info_path, "r", encoding="utf-8") as f:
            return json.load(f)


    def build_song_basename(
            song_specification: SongSpecification,
            song_index: int,
    ) -> str:
        """Baut den Basisnamen für MIDI/Audio/Labels.

        Format:
            <index>_<key>_<style>_Inst<instrument_count>_BPM<tempo>_Seed<seed>

        Beispiel:
            "0001_C-major_pop-straight_Inst5_BPM120_Seed1234"
        """
        index_str = f"{song_index:04d}"
        key_str = song_specification.key.replace(" ", "-")
        style_str = song_specification.style

        instrument_count = len(song_specification.band_configuration.instruments)

        # BPM als ganze Zahl im Dateinamen
        bpm_int = int(round(song_specification.tempo_bpm))

        seed = song_specification.random_seed

        return (
            f"{index_str}_{key_str}_{style_str}"
            f"_Inst{instrument_count}"
            f"_BPM{bpm_int}"
            f"_Seed{seed}"
        )

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

        possible_styles = [
            "pop_straight",
            "pop_shuffled",
            "funk",
            "rock",
            "disco",
            "shuffle",
            "dance_pop",
            "synth_pop",
            "electropop",
            "indie_pop",
            "rnb_pop",
            "funk_pop",
            "pop_rock",
            "latin_pop",
        ]
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

    def save_index(self, output_root: str) -> None:
        """Schreibt/aktualisiert dataset_index.json im output_root.

        - Wenn bereits eine dataset_index.json existiert, werden die neuen
          Beispiele (self.examples) hinten angehängt.
        - Wenn keine existiert, wird sie neu angelegt.
        """
        index_path = os.path.join(output_root, "dataset_index.json")

        # Bisherige Einträge laden (falls vorhanden)
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                try:
                    index_entries: Any = json.load(f)
                except json.JSONDecodeError:
                    index_entries = []
            if not isinstance(index_entries, list):
                index_entries = []
        else:
            index_entries = []

        # Neue Beispiele anhängen
        new_entries = [ex.to_index_entry() for ex in self.examples]
        index_entries.extend(new_entries)

        # Datei (neu) schreiben
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_entries, f, indent=2, ensure_ascii=False)

    def to_index_entry(self) -> dict:
        return {
            "song_identifier": self.song_identifier,
            "audio_path": self.audio_path,
            "label_path": self.label_path,
            "midi_path": self.midi_path,
            "mix_variant": self.mix_variant,
            "random_seed": self.song_specification.random_seed,
            # ggf. weitere Metadaten
        }

    def build_single_example(
            self,
            index: int,
            song_spec: SongSpecification,
            output_root: str,
    ) -> DatasetExample:
        """Erzeugt genau ein Dataset-Beispiel (MIDI, Audio, Labels + Indexeintrag)."""

        midi_dir = os.path.join(output_root, "midi")
        audio_dir = os.path.join(output_root, "audio")
        label_dir = os.path.join(output_root, "labels")

        os.makedirs(midi_dir, exist_ok=True)
        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(label_dir, exist_ok=True)

        basename = DatasetBuilder.build_song_basename(song_specification=song_spec,
                                                      song_index=index)
        song_spec.song_identifier = basename

        midi_path = os.path.join(midi_dir, f"{basename}.mid")
        audio_path = os.path.join(audio_dir, f"{basename}.wav")
        label_path = os.path.join(label_dir, f"{basename}_labels.json")

        # 6) Drums
        drum_events: List[DrumEvent] = self.drum_pattern_generator.generate_drum_track(
            song_spec
        )

        # 7) Harmonien
        note_events: List[NoteEvent] = []

        band_configuration = song_spec.band_configuration
        chord_instruments = band_configuration.get_instruments_by_role("chords")
        bass_instruments = band_configuration.get_instruments_by_role("bass")
        pad_instruments = band_configuration.get_instruments_by_role("pad")

        for inst in chord_instruments:
            note_events.extend(self.harmony_generator.generate_chord_track(song_spec, inst))

        for inst in bass_instruments:
            note_events.extend(self.harmony_generator.generate_bass_track(song_spec, inst))

        if pad_instruments:
            note_events.extend(
                self.harmony_generator.generate_pad_or_lead_tracks(song_spec, pad_instruments)
            )

        # 8) MIDI
        pm = self.midi_song_builder.build_pretty_midi(
            song_specification=song_spec,
            drum_events=drum_events,
            note_events=note_events,
        )
        self.midi_song_builder.save_midi(pm, midi_path)

        # 9) Audio
        self.audio_renderer.render_midi_to_wav(
            midi_path=midi_path,
            output_wav_path=audio_path,
        )

        # 10) Labels
        labels: List[LabelEvent] = self.label_extractor.extract_from_midi(midi_path)
        self.label_extractor.save_labels_json(labels, label_path)

        # 11) Example
        example = DatasetExample(
            song_identifier=song_spec.song_identifier,
            audio_path=audio_path,
            label_path=label_path,
            midi_path=midi_path,
            mix_variant="default",
            song_specification=song_spec,
        )
        return example

    def build_dataset(
            self,
            presets: List[DatasetPreset],
            output_root: str,
            dataset_config: dict[str, Any],
    ) -> List[DatasetExample]:
        """Erzeugt den kompletten Datensatz und schreibt dataset_info.json."""
        # 1) Output-Verzeichnisse vorbereiten
        midi_dir, audio_dir, label_dir = self._prepare_output_dirs(output_root)

        all_examples: List[DatasetExample] = []

        # 2) Bestehende dataset_info laden (falls vorhanden)
        existing_info = self._load_existing_dataset_info(output_root)

        if existing_info is not None:
            # Weiter auf existierendem Datensatz aufbauen
            dataset_info = existing_info

            # Bisherige Song-Anzahl bestimmen (Summe aller songs-Listen)
            existing_song_count = 0
            for preset_dict in dataset_info.get("presets", {}).values():
                existing_song_count += len(preset_dict.get("songs", []))
        else:
            # Neuer Datensatz
            dataset_info = self._init_dataset_info(dataset_config)
            existing_song_count = 0

        # Startindex für neue Songs (hängt an vorhandene hinten an)
        global_song_index: int = existing_song_count + 1

        # Gesamtanzahl für die Progressbar: alte + neue Songs
        total_songs = existing_song_count + self.number_of_songs * len(presets)

        # 3) Hauptschleife über Presets und Songs
        for preset in presets:
            for _ in range(self.number_of_songs):
                # 3.1) Anzahl Takte wählen
                dynamic_number_of_bars = self._compute_dynamic_number_of_bars(
                    preset=preset,
                    dataset_config=dataset_config,
                    global_song_index=global_song_index,
                )

                # 3.2) BandConfiguration + SongSpecification
                band_configuration = self._create_band_configuration_for_preset(preset)
                song_spec = self._create_song_specification_for_preset(
                    preset=preset,
                    number_of_bars=dynamic_number_of_bars,
                    band_configuration=band_configuration,
                    global_song_index=global_song_index,
                )

                # 3.3) Basename & Pfade
                basename = DatasetBuilder.build_song_basename(
                    song_specification=song_spec,
                    song_index=global_song_index,
                )
                song_spec.song_identifier = basename

                midi_path, audio_path, label_path = self._build_paths_for_basename(
                    midi_dir=midi_dir,
                    audio_dir=audio_dir,
                    label_dir=label_dir,
                    basename=basename,
                )

                # 3.4) Drum-Generator gemäß Preset konfigurieren
                self._update_drum_generator_from_preset(preset)

                # 3.5) Events erzeugen
                drum_events, note_events = self._generate_drum_and_note_events(
                    song_spec=song_spec,
                    band_configuration=band_configuration,
                )

                # 3.6) Dateien erzeugen + DatasetExample bauen
                example = self._build_midi_audio_labels_and_example(
                    song_spec=song_spec,
                    drum_events=drum_events,
                    note_events=note_events,
                    midi_path=midi_path,
                    audio_path=audio_path,
                    label_path=label_path,
                )
                all_examples.append(example)

                # 3.7) Song im dataset_info registrieren
                self._register_song_in_info(
                    dataset_info=dataset_info,
                    preset=preset,
                    song_basename=basename,
                )

                # 3.8) Fortschrittsanzeige
                if total_songs > 0:
                    self._print_progress(global_song_index, total_songs)

                global_song_index += 1

        self.examples = all_examples

        # 4) dataset_info.json schreiben
        self._write_dataset_info(dataset_info=dataset_info, output_root=output_root)

        return all_examples
