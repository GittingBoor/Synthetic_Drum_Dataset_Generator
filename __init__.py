from __future__ import annotations

import json
import os
import random
from typing import List

from script.drum_mapping import DrumMapping
from script.instrument import Instrument
from script.band_configuration import BandConfiguration
from script.song_specification import SongSpecification
from script.drum_pattern_generator import DrumPatternGenerator, DrumEvent
from script.harmony_generator import HarmonyGenerator, NoteEvent
from script.midi_song_builder import MidiSongBuilder
from script.audio_renderer import AudioRenderer
from script.label_extractor import LabelExtractor, LabelEvent
from script.dataset_example import DatasetExample


# ---------------------------------------------------------------------------
# KONFIGURATION – HIER STELLST DU ALLES EIN
# (Tempo, Anzahl Songs, Instrumente, Output-Pfade, …)
# ---------------------------------------------------------------------------

# Wurzelordner für den Datensatz (wird automatisch angelegt)
OUTPUT_ROOT_DIRECTORY = "data/synthetic_drums_dataset"

# Unterordner (relativ zu OUTPUT_ROOT_DIRECTORY)
MIDI_SUBDIR = "midi"
AUDIO_SUBDIR = "audio"
LABEL_SUBDIR = "labels"

# Anzahl der zu generierenden Songs
NUMBER_OF_SONGS = 5  # <- HIER anpassen

# Feste Musikalische Parameter (kannst du anpassen)
FIXED_TEMPO_BPM = 120.0
FIXED_TIME_SIGNATURE = (4, 4)
FIXED_NUMBER_OF_BARS = 16
FIXED_KEY = "C major"
FIXED_STYLE = "pop_straight"

# Globaler Seed für deterministische Generierung
GLOBAL_RANDOM_SEED = 1234

# MIDI/Audio-Parameter
MIDI_SAMPLE_RATE = 16000
MIDI_TICKS_PER_BEAT = 480

SOUNDFONT_PATH = "Assets/GeneralUser-GS.sf2"  # ggf. echten Pfad setzen
AUDIO_SAMPLE_RATE = 16000
AUDIO_RENDER_BACKEND = "fluidsynth"  # "noop" erzeugt Dummy-WAVs zum Testen

# Drum-Generator-Parameter
DRUM_COMPLEXITY = 0.5
GHOSTNOTE_PROBABILITY = 0.2
FILL_PROBABILITY = 0.3
SWING_AMOUNT = 0.1

# Label-Extraktion
MINIMUM_VELOCITY = 5
TIME_UNIT = "seconds"
INCLUDE_NON_DRUMS = True


# ---------------------------------------------------------------------------
# Hilfsfunktionen zum Erzeugen der zentralen Objekte
# ---------------------------------------------------------------------------

def create_drum_mapping() -> DrumMapping:
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


def create_instruments() -> List[Instrument]:
    """Definiert die Instrumente, die in der Band benutzt werden.

    Hier kannst du Instrumente hinzufügen / entfernen / anpassen.
    """
    instruments: List[Instrument] = [
        # ------------------------------------------------------------
        # Pianos & Keys
        # ------------------------------------------------------------
        Instrument(
            name="Acoustic Grand Piano",
            gm_program=0,   # GM 1
            channel=0,
            volume=0.9,
            pan=0.0,
            role="chords",
        ),
        Instrument(
            name="Bright Acoustic Piano",
            gm_program=1,   # GM 2
            channel=0,
            volume=0.9,
            pan=0.1,
            role="chords",
        ),
        Instrument(
            name="Electric Piano 1 (Rhodes)",
            gm_program=4,   # GM 5
            channel=1,
            volume=0.9,
            pan=-0.1,
            role="chords",
        ),
        Instrument(
            name="Electric Piano 2 (FM)",
            gm_program=5,   # GM 6
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
            channel=10,     # (9 wird für Drums genutzt)
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


def create_band_configuration(drum_mapping: DrumMapping) -> BandConfiguration:
    """Erzeugt eine BandConfiguration mit Drums + den oben definierten Instrumenten."""
    instruments = create_instruments()
    band_conf = BandConfiguration(
        drum_channel=9,  # GM-Standard-Drumkanal
        drum_mapping=drum_mapping,
        instruments=instruments,
    )
    return band_conf


def create_harmony_generator() -> HarmonyGenerator:
    """Erzeugt einen einfachen HarmonyGenerator mit Standard-Vokabular."""
    scale_vocab = {
        "C major": [0, 2, 4, 5, 7, 9, 11],
        "A minor": [9, 11, 0, 2, 4, 5, 7],
    }

    chord_vocab = {
        "maj": [0, 4, 7],
        "min": [0, 3, 7],
        "maj7": [0, 4, 7, 11],
        "min7": [0, 3, 7, 10],
    }

    pattern_templates = {
        "pop_bass_8th": {},
        "pop_chords_4bar": {},
        "pop_pad_whole": {},
    }

    return HarmonyGenerator(
        scale_vocab=scale_vocab,
        chord_vocab=chord_vocab,
        pattern_templates=pattern_templates,
    )


def create_drum_pattern_generator(drum_mapping: DrumMapping) -> DrumPatternGenerator:
    """Erzeugt den DrumPatternGenerator mit den oben definierten Parametern."""
    return DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=DRUM_COMPLEXITY,
        ghostnote_probability=GHOSTNOTE_PROBABILITY,
        fill_probability=FILL_PROBABILITY,
        swing_amount=SWING_AMOUNT,
    )


def create_midi_song_builder(drum_mapping: DrumMapping) -> MidiSongBuilder:
    """Erzeugt den MidiSongBuilder."""
    return MidiSongBuilder(
        sample_rate=MIDI_SAMPLE_RATE,
        ticks_per_beat=MIDI_TICKS_PER_BEAT,
        drum_mapping=drum_mapping,
    )


def create_audio_renderer() -> AudioRenderer:
    """Erzeugt den AudioRenderer.

    Achtung:
        Mit Backend 'noop' werden nur leere WAV-Dateien erzeugt (zum Testen).
        Für echtes Rendering musst du später die Implementierung in
        AudioRenderer.render_midi_to_wav an dein Setup anpassen.
    """
    return AudioRenderer(
        soundfont_path=SOUNDFONT_PATH,
        output_sample_rate=AUDIO_SAMPLE_RATE,
        render_backend=AUDIO_RENDER_BACKEND,
    )


def create_label_extractor(drum_mapping: DrumMapping) -> LabelExtractor:
    """Erzeugt den LabelExtractor."""
    return LabelExtractor(
        drum_mapping=drum_mapping,
        minimum_velocity=MINIMUM_VELOCITY,
        time_unit=TIME_UNIT,
        include_non_drums=INCLUDE_NON_DRUMS,
    )


# ---------------------------------------------------------------------------
# Pipeline für EINEN Song
# ---------------------------------------------------------------------------

def build_single_example(
    index: int,
    drum_mapping: DrumMapping,
    band_configuration: BandConfiguration,
    drum_pattern_generator: DrumPatternGenerator,
    harmony_generator: HarmonyGenerator,
    midi_builder: MidiSongBuilder,
    audio_renderer: AudioRenderer,
    label_extractor: LabelExtractor,
    output_root: str,
) -> DatasetExample:
    """Erzeugt genau ein Dataset-Beispiel (MIDI, Audio, Labels + Indexeintrag)."""

    # Song-ID und Pfade
    song_id = f"song_{index:04d}"
    song_identifier = f"{song_id}_{FIXED_STYLE.lower()}_{FIXED_KEY.replace(' ', '_').lower()}"

    midi_dir = os.path.join(output_root, MIDI_SUBDIR)
    audio_dir = os.path.join(output_root, AUDIO_SUBDIR)
    label_dir = os.path.join(output_root, LABEL_SUBDIR)

    os.makedirs(midi_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    midi_path = os.path.join(midi_dir, f"{song_id}.mid")
    audio_path = os.path.join(audio_dir, f"{song_id}_mix_0dB.wav")
    label_path = os.path.join(label_dir, f"{song_id}_labels.json")

    # SongSpecification erzeugen
    random_seed = GLOBAL_RANDOM_SEED + index
    song_spec = SongSpecification(
        song_identifier=song_identifier,
        tempo_bpm=FIXED_TEMPO_BPM,
        time_signature=FIXED_TIME_SIGNATURE,
        number_of_bars=FIXED_NUMBER_OF_BARS,
        key=FIXED_KEY,
        style=FIXED_STYLE,
        band_configuration=band_configuration,
        random_seed=random_seed,
    )

    # Für deterministisches Verhalten: Python-RNG seeden
    random.seed(song_spec.random_seed)

    # Drum-Events erzeugen
    drum_events: List[DrumEvent] = drum_pattern_generator.generate_drum_track(song_spec)

    # Harmonische Events erzeugen (Chord + Bass + ggf. Pad)
    note_events: List[NoteEvent] = []

    chord_instruments = band_configuration.get_instruments_by_role("chords")
    bass_instruments = band_configuration.get_instruments_by_role("bass")
    pad_instruments = band_configuration.get_instruments_by_role("pad")

    for inst in chord_instruments:
        note_events.extend(
            harmony_generator.generate_chord_track(song_spec, inst)
        )

    for inst in bass_instruments:
        note_events.extend(
            harmony_generator.generate_bass_track(song_spec, inst)
        )

    if pad_instruments:
        note_events.extend(
            harmony_generator.generate_pad_or_lead_tracks(song_spec, pad_instruments)
        )

    # MIDI bauen und speichern
    pm = midi_builder.build_pretty_midi(
        song_specification=song_spec,
        drum_events=drum_events,
        note_events=note_events,
    )
    midi_builder.save_midi(pm, midi_path)

    # Audio rendern
    audio_renderer.render_midi_to_wav(midi_path=midi_path, output_wav_path=audio_path)

    # Labels extrahieren und speichern
    labels: List[LabelEvent] = label_extractor.extract_from_midi(midi_path)
    label_extractor.save_labels_json(labels, label_path)

    # DatasetExample erzeugen (für Index)
    example = DatasetExample(
        song_identifier=song_identifier,
        audio_path=audio_path,
        label_path=label_path,
        midi_path=midi_path,
        mix_variant="balanced",
        song_specification=song_spec,
    )

    return example


# ---------------------------------------------------------------------------
# Hauptfunktion: erzeugt den kompletten Datensatz
# ---------------------------------------------------------------------------

def main() -> None:
    """Erzeugt NUMBER_OF_SONGS Beispiele und schreibt alles auf die Platte."""
    print("============================================================")
    print("Starte synthetische Drum-Dataset-Generierung …")
    print("============================================================")

    # Zentrale Objekte
    drum_mapping = create_drum_mapping()
    band_configuration = create_band_configuration(drum_mapping)
    harmony_generator = create_harmony_generator()
    drum_pattern_generator = create_drum_pattern_generator(drum_mapping)
    midi_builder = create_midi_song_builder(drum_mapping)
    audio_renderer = create_audio_renderer()
    label_extractor = create_label_extractor(drum_mapping)

    os.makedirs(OUTPUT_ROOT_DIRECTORY, exist_ok=True)

    examples: List[DatasetExample] = []

    for i in range(NUMBER_OF_SONGS):
        print(f"\n[INFO] Generiere Song {i + 1}/{NUMBER_OF_SONGS} …")
        example = build_single_example(
            index=i,
            drum_mapping=drum_mapping,
            band_configuration=band_configuration,
            drum_pattern_generator=drum_pattern_generator,
            harmony_generator=harmony_generator,
            midi_builder=midi_builder,
            audio_renderer=audio_renderer,
            label_extractor=label_extractor,
            output_root=OUTPUT_ROOT_DIRECTORY,
        )
        examples.append(example)
        print(f"[OK] Song {example.song_identifier!r} generiert.")

    # Index schreiben
    index_path = os.path.join(OUTPUT_ROOT_DIRECTORY, "dataset_index.json")
    index_entries = [ex.to_index_entry() for ex in examples]

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_entries, f, indent=2, ensure_ascii=False)

    print("\n============================================================")
    print(f"Fertig! {len(examples)} Beispiele wurden erzeugt.")
    print(f"Output-Root: {OUTPUT_ROOT_DIRECTORY}")
    print(f"- MIDI  in: {os.path.join(OUTPUT_ROOT_DIRECTORY, MIDI_SUBDIR)}")
    print(f"- Audio in: {os.path.join(OUTPUT_ROOT_DIRECTORY, AUDIO_SUBDIR)}")
    print(f"- Labels in: {os.path.join(OUTPUT_ROOT_DIRECTORY, LABEL_SUBDIR)}")
    print(f"- Index: {index_path}")
    print("============================================================")


if __name__ == "__main__":
    main()
