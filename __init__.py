from __future__ import annotations

import json
import os
from typing import List

from script.audio_renderer import AudioRenderer
from script.dataset_presets import DatasetPreset, DATASET_PRESETS
from script.drum_mapping import DrumMapping
from script.drum_pattern_generator import DrumPatternGenerator
from script.harmony_generator import HarmonyGenerator
from script.dataset_builder import DatasetBuilder
from script.label_extractor import LabelExtractor
from script.midi_song_builder import MidiSongBuilder

# ---------------------------------------------------------------------------
# SYSTEM-DEPENDENT PATHS AND IO PARAMETERS
# ---------------------------------------------------------------------------

# Root folder for the dataset (will be created automatically)
OUTPUT_ROOT_DIRECTORY = "data/synthetic_drums_dataset_test_1"  # e.g. "data/synthetic_drums_dataset_v1"

# Subfolders (relative to OUTPUT_ROOT_DIRECTORY)
MIDI_SUBDIR = "midi"    # e.g. "midi_files"
AUDIO_SUBDIR = "audio"  # e.g. "wav"
NOTES_SUBDIR = "notes"
NOTE_EVENTS_SUBDIR = "note_events"

# Audio / MIDI rendering backends and rates
SOUNDFONT_PATH = "Assets/GeneralUser-GS.sf2"  # alternative: any valid .sf2 soundfont
AUDIO_SAMPLE_RATE = 16000                     # alternatives: 44100, 48000
AUDIO_RENDER_BACKEND = "fluidsynth"           # alternative: "noop" for dry-run testing

MIDI_SAMPLE_RATE = 16000   # only relevant if you align MIDI and audio in time
MIDI_TICKS_PER_BEAT = 480  # alternative: 960 for higher timing resolution

# ---------------------------------------------------------------------------
# DATASET-WIDE PARAMETERS (APPLY TO ALL SONGS ACROSS ALL PRESETS)
# ---------------------------------------------------------------------------

# Number of songs per preset (total songs = NUMBER_OF_SONGS * NUMBER_OF_PRESETS)
NUMBER_OF_SONGS = 1  # e.g. 5, 50, 100

# Song length in seconds (a random target length in this range will be chosen per song)
MIN_SONG_LENGTH_SECONDS = 20.0  # e.g. 5.0 for very short clips
MAX_SONG_LENGTH_SECONDS = 60.0  # e.g. 120.0 for longer songs

# Global seed for deterministic dataset generation
GLOBAL_RANDOM_SEED = 1234  # change to get a different global randomization

# Label extraction parameters (used for LabelExtractor)
MINIMUM_VELOCITY = 5         # alternative: 1 if you want to keep very soft notes
TIME_UNIT = "seconds"        # alternative: "ticks"
INCLUDE_NON_DRUMS = True     # alternative: False if you want drum-only labels


# Split-Konfiguration für YourMT3 file_lists
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10
SPLIT_SEED = 1234

# Which presets to use when building a full dataset.
# Use names from DATASET_PRESETS.keys().

PRESET_NAMES_TO_USE: List[str] = list(DATASET_PRESETS.keys())

    # "pop-straight__C-major__T120__Cmid__Smid__I4-8",
    # "pop-straight__C-major__T100__Clow__Slow__I4-6",
    # "funk__C-major__T105__Chigh__Shigh__I4-7",
    # "disco__C-major__T128__Chigh__Smid__I5-8",
    # alternative: list(DATASET_PRESETS.keys()) to use all presets

# How many different presets to use when calling build_dataset
NUMBER_OF_PRESETS = len(PRESET_NAMES_TO_USE)  # e.g. 1 (single preset), 4, len(PRESET_NAMES_TO_USE)

# Safety check: NUMBER_OF_PRESETS must not exceed the number of configured preset names
assert NUMBER_OF_PRESETS <= len(PRESET_NAMES_TO_USE), (
    "NUMBER_OF_PRESETS is larger than PRESET_NAMES_TO_USE. "
    "Either reduce NUMBER_OF_PRESETS or add more preset names."
)

dataset_config = {
    "output_root_directory": OUTPUT_ROOT_DIRECTORY,
    "midi_subdir": MIDI_SUBDIR,
    "audio_subdir": AUDIO_SUBDIR,
    "soundfont_path": SOUNDFONT_PATH,
    "audio_sample_rate": AUDIO_SAMPLE_RATE,
    "audio_render_backend": AUDIO_RENDER_BACKEND,
    "midi_sample_rate": MIDI_SAMPLE_RATE,
    "midi_ticks_per_beat": MIDI_TICKS_PER_BEAT,
    "number_of_songs": NUMBER_OF_SONGS,
    "number_of_presets": NUMBER_OF_PRESETS,
    "min_song_length_seconds": MIN_SONG_LENGTH_SECONDS,
    "max_song_length_seconds": MAX_SONG_LENGTH_SECONDS,
    "global_random_seed": GLOBAL_RANDOM_SEED,
    "minimum_velocity": MINIMUM_VELOCITY,
    "time_unit": TIME_UNIT,
    "include_non_drums": INCLUDE_NON_DRUMS,
    "preset_names_to_use": PRESET_NAMES_TO_USE,
    "train_ratio": TRAIN_RATIO,
    "val_ratio": VAL_RATIO,
    "test_ratio": TEST_RATIO,
    "split_seed": SPLIT_SEED,
}

def main() -> None:
    # ------------------------------------------------------------------
    # 1) Basis-Objekte anlegen
    # ------------------------------------------------------------------
    drum_mapping = DrumMapping.create_default()

    drum_pattern_generator = DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=0.5,              # Startwerte, werden pro Preset überschrieben
        ghostnote_probability=0.3,
        fill_probability=0.3,
        swing_amount=0.1,
        pause_probability=0.3,
    )

    # HarmonyGenerator über Hilfsmethode im DatasetBuilder erstellen
    harmony_generator = DatasetBuilder.create_harmony_generator()

    # MidiSongBuilder mit Sample-Rate und Ticks pro Beat
    midi_song_builder = MidiSongBuilder(
        sample_rate=MIDI_SAMPLE_RATE,
        ticks_per_beat=MIDI_TICKS_PER_BEAT,
        drum_mapping=drum_mapping,
    )

    # AudioRenderer mit Soundfont / Backend
    audio_renderer = AudioRenderer(
        soundfont_path=SOUNDFONT_PATH,
        output_sample_rate=AUDIO_SAMPLE_RATE,
        render_backend=AUDIO_RENDER_BACKEND,
    )

    # LabelExtractor mit Velocity-Filter etc.
    label_extractor = LabelExtractor(
        drum_mapping=drum_mapping,
        minimum_velocity=MINIMUM_VELOCITY,
        time_unit=TIME_UNIT,
        include_non_drums=INCLUDE_NON_DRUMS,
    )

    # Presets auswählen
    selected_preset_names = PRESET_NAMES_TO_USE[:NUMBER_OF_PRESETS]
    selected_presets: List[DatasetPreset] = [
        DATASET_PRESETS[name] for name in selected_preset_names
    ]

    # Wenn du band_configuration_pool aktuell nicht nutzt, gib einfach eine leere Liste rein
    band_configuration_pool: List = []

    # ------------------------------------------------------------------
    # 2) DatasetBuilder erstellen
    # ------------------------------------------------------------------
    builder = DatasetBuilder(
        output_root_directory=OUTPUT_ROOT_DIRECTORY,
        number_of_songs=NUMBER_OF_SONGS,
        band_configuration_pool=band_configuration_pool,
        drum_pattern_generator=drum_pattern_generator,
        harmony_generator=harmony_generator,
        midi_song_builder=midi_song_builder,
        audio_renderer=audio_renderer,
        label_extractor=label_extractor,
        drum_mapping=drum_mapping,
        random_seed=GLOBAL_RANDOM_SEED,
        min_song_length_seconds=MIN_SONG_LENGTH_SECONDS,
        max_song_length_seconds=MAX_SONG_LENGTH_SECONDS,
    )

    # ------------------------------------------------------------------
    # 3) Datensatz bauen (ggf. fortsetzen)
    # ------------------------------------------------------------------
    examples = builder.build_dataset(
        presets=selected_presets,
        output_root=OUTPUT_ROOT_DIRECTORY,
        dataset_config=dataset_config,
    )
    # ------------------------------------------------------------------
    # 4) Index-Datei aktualisieren (Append-Logik steckt in builder.save_index)
    # ------------------------------------------------------------------
    builder.save_index(output_root=OUTPUT_ROOT_DIRECTORY)

    index_path = os.path.join(OUTPUT_ROOT_DIRECTORY, "dataset_index.json")

    print("\n============================================================")
    print(f"Fertig! {len(examples)} neue Beispiele wurden erzeugt.")
    print(f"Output-Root: {OUTPUT_ROOT_DIRECTORY}")
    print(f"- MIDI        in: {os.path.join(OUTPUT_ROOT_DIRECTORY, MIDI_SUBDIR)}")
    print(f"- Audio       in: {os.path.join(OUTPUT_ROOT_DIRECTORY, AUDIO_SUBDIR)}")
    print(f"- Notes (.npy) in: {os.path.join(OUTPUT_ROOT_DIRECTORY, NOTES_SUBDIR)}")
    print(f"- NoteEvents   in: {os.path.join(OUTPUT_ROOT_DIRECTORY, NOTE_EVENTS_SUBDIR)}")
    print(f"- YourMT3 idx  in: {os.path.join('data', 'yourmt3_indexes')}")
    print(f"- Index:     {index_path}")
    print("============================================================")




if __name__ == "__main__":
    main()
