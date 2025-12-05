from __future__ import annotations
from typing import Dict

from .song_specification import SongSpecification


class DatasetExample:
    """Repräsentiert ein einzelnes Beispiel im Datensatz.

    Verantwortung:
        DatasetExample repräsentiert ein einzelnes Beispiel im Datensatz,
        bestehend aus Audio, Labels und Metadaten.
        Damit hast du eine saubere Struktur, um jeden Clip im Dataset zu
        beschreiben.
        Diese Informationen können später in eine Index-Datei geschrieben werden,
        die deine Trainingspipeline nutzt.
    """

    def __init__(
        self,
        song_identifier: str,
        audio_path: str,
        label_path: str,
        midi_path: str,
        mix_variant: str,
        song_specification: SongSpecification,
    ) -> None:
        """Konstruktor für ein DatasetExample.

        Args:
            song_identifier: Bezeichner des Songs (z. B. "song_0001_pop_c_major").
            audio_path: Pfad zur zugehörigen Audiodatei.
            label_path: Pfad zur zugehörigen Label-Datei.
            midi_path: Pfad zur zugehörigen MIDI-Datei.
            mix_variant: Name der Mix-Variante (z. B. "drums_loud").
            song_specification: Ursprüngliche SongSpecification dieses Beispiels.
        """
        self.song_identifier = song_identifier
        self.audio_path = audio_path
        self.label_path = label_path
        self.midi_path = midi_path
        self.mix_variant = mix_variant
        self.song_specification = song_specification

    def to_index_entry(self) -> Dict:
        """Erzeugt einen Dictionary-Eintrag für eine Index-Datei.

        Beschreibung:
            Erzeugt einen Dictionary-Eintrag mit allen nötigen Informationen
            (Pfaden, Metadaten), der in eine globale Index-Datei aufgenommen
            werden kann.

        Returns:
            Dictionary mit allen Informationen dieses DatasetExample.
        """
        spec = self.song_specification

        # Wir bauen hier bewusst ein eigenes Dict, statt spec.to_dict() aufzurufen,
        # damit das auch funktioniert, wenn z. B. band_configuration = None ist.
        song_spec_dict: Dict = {
            "song_identifier": getattr(spec, "song_identifier", None),
            "tempo_bpm": getattr(spec, "tempo_bpm", None),
            "time_signature": getattr(spec, "time_signature", None),
            "number_of_bars": getattr(spec, "number_of_bars", None),
            "key": getattr(spec, "key", None),
            "style": getattr(spec, "style", None),
            "random_seed": getattr(spec, "random_seed", None),
        }

        return {
            "song_identifier": self.song_identifier,
            "audio_path": self.audio_path,
            "label_path": self.label_path,
            "midi_path": self.midi_path,
            "mix_variant": self.mix_variant,
            "song_specification": song_spec_dict,
        }


# ------------------------------------------------------------------
# test- / Test-Funktionen mit ausführlichen Prints
# ------------------------------------------------------------------


def test_print_dataset_example_info(example: DatasetExample) -> None:
    """test-Hilfe: Gibt alle Felder eines DatasetExample gut lesbar aus."""
    print("\n[test] ---------------- DATASET EXAMPLE -------------------")
    print(f"song_identifier : {example.song_identifier}")
    print(f"audio_path      : {example.audio_path}")
    print(f"label_path      : {example.label_path}")
    print(f"midi_path       : {example.midi_path}")
    print(f"mix_variant     : {example.mix_variant}")

    spec = example.song_specification
    print("[test] SongSpecification (aus Attributen):")
    print(f"    song_identifier: {getattr(spec, 'song_identifier', None)}")
    print(f"    tempo_bpm      : {getattr(spec, 'tempo_bpm', None)}")
    print(f"    time_signature : {getattr(spec, 'time_signature', None)}")
    print(f"    number_of_bars : {getattr(spec, 'number_of_bars', None)}")
    print(f"    key            : {getattr(spec, 'key', None)}")
    print(f"    style          : {getattr(spec, 'style', None)}")
    print(f"    random_seed    : {getattr(spec, 'random_seed', None)}")

    print("[test] ---------------------------------------------------\n")


def test_convert_to_index_entry(example: DatasetExample) -> None:
    """test-Hilfe: Wandelt ein DatasetExample in einen Index-Eintrag um und druckt ihn."""
    print("\n[test] ------------- INDEX ENTRY (Dict) -------------------")
    index_entry = example.to_index_entry()
    for key, value in index_entry.items():
        if key == "song_specification" and isinstance(value, dict):
            print(f"{key}:")
            for k2, v2 in value.items():
                print(f"    {k2}: {v2}")
        else:
            print(f"{key}: {value}")
    print("[test] ---------------------------------------------------\n")


def run_all_DatasetExample_tests() -> None:
    """Führt einfache Tests für DatasetExample aus und druckt ausführliche test-Infos."""
    print("\n[TEST] =====================================================")
    print("[TEST] Starte DatasetExample Tests ...")

    # --- 1) Dummy-SongSpecification bauen ----------------------------------
    # Wichtig: Passe die Parameter genau an deine SongSpecification-Klasse an.
    dummy_song_spec = SongSpecification(
        song_identifier="song_0001_pop_c_major",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        number_of_bars=16,
        key="C major",
        style="pop_straight",
        band_configuration=None,  # für diesen Test ok
        random_seed=42,
    )

    # --- 2) DatasetExample-Objekt anlegen ----------------------------------
    example = DatasetExample(
        song_identifier="song_0001_pop_c_major",
        audio_path="data/audio/song_0001_drums_balanced.wav",
        label_path="data/labels/song_0001_labels.json",
        midi_path="data/midi/song_0001.mid",
        mix_variant="balanced",
        song_specification=dummy_song_spec,
    )

    # --- 3) Infos ausgeben --------------------------------------------------
    print("\n[TEST] --- DatasetExample Felder ---")
    test_print_dataset_example_info(example)

    # --- 4) Index-Eintrag testen -------------------------------------------
    print("\n[TEST] --- DatasetExample -> Index-Eintrag ---")
    test_convert_to_index_entry(example)

    print("\n[TEST] DatasetExample Tests abgeschlossen.")
    print("[TEST] =====================================================\n")


if __name__ == "__main__":
    run_all_DatasetExample_tests()
