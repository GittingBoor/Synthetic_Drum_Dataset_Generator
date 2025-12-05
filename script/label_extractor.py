from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List
import json
import os

import pretty_midi

from .drum_mapping import DrumMapping


@dataclass
class LabelEvent:
    """Repräsentiert ein einzelnes Label-Ereignis (z. B. eine Note im Ground-Truth)."""
    instrument_class: str  # z. B. "KICK", "SNARE", "Piano"
    onset: float           # Startzeit (Sekunden)
    offset: float          # Endzeit (Sekunden)
    velocity: int          # MIDI-Velocity (1–127)
    is_drum: bool          # True für Drums, False für andere Instrumente


class LabelExtractor:
    """Extrahiert Ground-Truth-Labels aus MIDI-Dateien.

    Verantwortung:
        LabelExtractor liest eine MIDI-Datei ein und erzeugt daraus die
        Ground-Truth-Labels (Notenereignisse mit Onset, Offset, Velocity, Klasse).
        Er sorgt dafür, dass Drums anhand deines DrumMapping erkannt und in deine
        gewünschten Klassen übersetzt werden.
        Außerdem kann er Labels im Format speichern, das du für YourMT3+ brauchst
        (z. B. JSON, NoteSequence-artig).
    """

    def __init__(
        self,
        drum_mapping: DrumMapping,
        minimum_velocity: int,
        time_unit: str,
        include_non_drums: bool,
    ) -> None:
        """Konstruktor für den LabelExtractor.

        Args:
            drum_mapping: Zentrale Mapping-Instanz, um Drum-Noten in Klassen
                zu übersetzen.
            minimum_velocity: Untere Grenze der Velocity, um extrem leise Noten
                zu filtern (z. B. 5).
            time_unit: Zeiteinheit für die Labels (z. B. "seconds").
                       Aktuell wird nur "seconds" unterstützt.
            include_non_drums: True, wenn auch andere Instrumente gelabelt werden
                sollen, sonst False.
        """
        self.drum_mapping: DrumMapping = drum_mapping
        self.minimum_velocity: int = int(minimum_velocity)
        self.time_unit: str = time_unit
        self.include_non_drums: bool = include_non_drums

    def _convert_time(self, pm: pretty_midi.PrettyMIDI, t: float) -> float:
        """Konvertiert Zeit t gemäß self.time_unit.

        Aktuell:
            - "seconds": gibt t unverändert zurück
            - andere Werte: NotImplementedError
        """
        if self.time_unit == "seconds":
            return float(t)
        raise NotImplementedError(
            f"time_unit {self.time_unit!r} wird derzeit nicht unterstützt. "
            "Verwende 'seconds' für diese Version des LabelExtractor."
        )

    def extract_from_midi(self, midi_path: str) -> List[LabelEvent]:
        """Extrahiert Labels aus einer MIDI-Datei.

        Beschreibung:
            Liest alle Noten aus einer MIDI-Datei ein, berechnet Onset/Offset/
            Velocity und gibt sie als Liste von Label-Events zurück.

        Args:
            midi_path: Pfad zur Eingabe-MIDI-Datei.

        Returns:
            Liste von LabelEvent-Objekten mit allen extrahierten Labels.
        """
        pm = pretty_midi.PrettyMIDI(midi_path)
        labels: List[LabelEvent] = []

        for instrument in pm.instruments:
            is_drum_inst = bool(instrument.is_drum)

            # Nicht-Drums ggf. überspringen
            if not is_drum_inst and not self.include_non_drums:
                continue

            for note in instrument.notes:
                if note.velocity < self.minimum_velocity:
                    continue

                onset = self._convert_time(pm, note.start)
                offset = self._convert_time(pm, note.end)

                if is_drum_inst:
                    drum_class = self.drum_mapping.map_note_to_class(note.pitch)
                    # Unbekannte Drum-Noten überspringen
                    if drum_class is None:
                        continue
                    instrument_class = drum_class
                    is_drum_flag = True
                else:
                    # Für Nicht-Drums verwenden wir den Instrumentnamen als Klasse
                    instrument_class = instrument.name or "NON_DRUM"
                    is_drum_flag = False

                labels.append(
                    LabelEvent(
                        instrument_class=instrument_class,
                        onset=onset,
                        offset=offset,
                        velocity=int(note.velocity),
                        is_drum=is_drum_flag,
                    )
                )

        return labels

    def filter_to_drums(self, labels: List[LabelEvent]) -> List[LabelEvent]:
        """Filtert eine Label-Liste auf Drum-Ereignisse.

        Beschreibung:
            Filtert eine Label-Liste so, dass nur Drum-Ereignisse übrig bleiben
            (z. B. für Drum-spezifische Trainingsläufe).

        Args:
            labels: Liste aller LabelEvent-Objekte.

        Returns:
            Neue Liste von LabelEvent-Objekten, die nur Drum-Labels enthält.
        """
        return [label for label in labels if label.is_drum]

    def save_labels_json(self, labels: List[LabelEvent], path: str) -> None:
        """Speichert Labels als JSON-Datei.

        Beschreibung:
            Speichert eine Liste von Labels als JSON-Datei auf der Festplatte.

        Args:
            labels: Liste der zu speichernden LabelEvent-Objekte.
            path: Zielpfad für die JSON-Datei.
        """
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        data = [asdict(label) for label in labels]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_labels_note_sequence_format(
        self,
        labels: List[LabelEvent],
        path: str,
    ) -> None:
        """Speichert Labels im NoteSequence-/YourMT3-ähnlichen Format.

        Beschreibung:
            Speichert die Labels in einem Format, das sich an das NoteSequence-/
            YourMT3-Format anlehnt (z. B. für direkte Weiterverarbeitung in der
            Pipeline).

            Vereinfachtes Format:
                {
                  "time_unit": "seconds",
                  "notes": [
                    {
                      "instrument_class": ...,
                      "onset": ...,
                      "offset": ...,
                      "velocity": ...,
                      "is_drum": ...
                    },
                    ...
                  ]
                }

        Args:
            labels: Liste der zu speichernden LabelEvent-Objekte.
            path: Zielpfad für die Ausgabedatei.
        """
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        data = {
            "time_unit": self.time_unit,
            "notes": [asdict(label) for label in labels],
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für LabelExtractor
# ---------------------------------------------------------------------------

def _create_example_drum_mapping_for_labels() -> DrumMapping:
    """Erzeugt eine einfache DrumMapping-Instanz für LabelExtractor-Tests."""
    print("\n[SETUP] Erzeuge Test-DrumMapping für LabelExtractor …")
    note_to_class = {
        36: "KICK",
        38: "SNARE",
    }
    class_to_notes = {
        "KICK": [36],
        "SNARE": [38],
    }
    core_classes = ["KICK", "SNARE"]

    dm = DrumMapping(
        note_to_class=note_to_class,
        class_to_notes=class_to_notes,
        core_classes=core_classes,
    )
    print(
        f"[SETUP] DrumMapping(note_to_class={dm.note_to_class}, "
        f"class_to_notes={dm.class_to_notes}, core_classes={dm.core_classes})"
    )
    return dm


def _create_test_midi_file_for_labels(path: str) -> None:
    """Erzeugt eine kleine Test-MIDI-Datei mit Drum- und Nicht-Drum-Noten."""
    print(f"[SETUP] Erzeuge Test-MIDI-Datei unter {path!r} …")
    pm = pretty_midi.PrettyMIDI()

    # Drum-Instrument
    drum_inst = pretty_midi.Instrument(program=0, is_drum=True, name="Drums")
    drum_inst.notes.append(
        pretty_midi.Note(velocity=100, pitch=36, start=0.0, end=0.5)  # KICK
    )
    drum_inst.notes.append(
        pretty_midi.Note(velocity=90, pitch=38, start=1.0, end=1.5)   # SNARE
    )

    # Nicht-Drum-Instrument (z. B. Piano)
    piano_inst = pretty_midi.Instrument(program=0, is_drum=False, name="Piano")
    piano_inst.notes.append(
        pretty_midi.Note(velocity=80, pitch=60, start=0.0, end=0.5)
    )

    pm.instruments.append(drum_inst)
    pm.instruments.append(piano_inst)

    pm.write(path)
    print("[SETUP] Test-MIDI-Datei erfolgreich geschrieben.\n")


def test_extract_from_midi_includes_drums_and_non_drums() -> None:
    """Testet, ob extract_from_midi Drum- und Nicht-Drum-Labels erzeugt."""
    print("[TEST] test_extract_from_midi_includes_drums_and_non_drums gestartet …")
    dm = _create_example_drum_mapping_for_labels()
    extractor = LabelExtractor(
        drum_mapping=dm,
        minimum_velocity=1,
        time_unit="seconds",
        include_non_drums=True,
    )

    midi_path = "test_labels_input.mid"
    _create_test_midi_file_for_labels(midi_path)

    labels = extractor.extract_from_midi(midi_path)
    print(f"  - Anzahl extrahierter Labels: {len(labels)}")
    for lbl in labels:
        print(f"    * {lbl}")

    # Erwartet: 3 Labels (2 Drums, 1 Piano)
    assert len(labels) == 3, "Es sollten 3 Labels extrahiert werden."

    classes = {l.instrument_class for l in labels}
    print(f"  - Gefundene instrument_class-Werte: {classes}")
    assert "KICK" in classes
    assert "SNARE" in classes
    assert "Piano" in classes

    # Zeiten sollten alle >= 0 sein
    for l in labels:
        assert l.onset >= 0.0
        assert l.offset >= l.onset

    # Aufräumen
    os.remove(midi_path)

    print("[TEST] test_extract_from_midi_includes_drums_and_non_drums erfolgreich abgeschlossen.\n")


def test_filter_to_drums_only_keeps_drum_labels() -> None:
    """Testet, ob filter_to_drums nur Drum-Labels übrig lässt."""
    print("[TEST] test_filter_to_drums_only_keeps_drum_labels gestartet …")
    dm = _create_example_drum_mapping_for_labels()
    extractor = LabelExtractor(
        drum_mapping=dm,
        minimum_velocity=1,
        time_unit="seconds",
        include_non_drums=True,
    )

    midi_path = "test_labels_input.mid"
    _create_test_midi_file_for_labels(midi_path)

    labels = extractor.extract_from_midi(midi_path)
    drum_labels = extractor.filter_to_drums(labels)

    print(f"  - Gesamtlabels: {len(labels)}, Drum-Labels: {len(drum_labels)}")
    for l in drum_labels:
        print(f"    * DRUM: {l}")

    # Es sollten nur die beiden Drum-Noten übrig bleiben
    assert len(drum_labels) == 2
    assert all(l.is_drum for l in drum_labels)
    drum_classes = {l.instrument_class for l in drum_labels}
    assert drum_classes == {"KICK", "SNARE"}

    os.remove(midi_path)

    print("[TEST] test_filter_to_drums_only_keeps_drum_labels erfolgreich abgeschlossen.\n")


def test_save_labels_json_creates_file() -> None:
    """Testet, ob save_labels_json eine lesbare JSON-Datei schreibt."""
    print("[TEST] test_save_labels_json_creates_file gestartet …")
    dm = _create_example_drum_mapping_for_labels()
    extractor = LabelExtractor(
        drum_mapping=dm,
        minimum_velocity=1,
        time_unit="seconds",
        include_non_drums=True,
    )

    midi_path = "test_labels_input.mid"
    json_path = "test_labels_output.json"
    _create_test_midi_file_for_labels(midi_path)

    labels = extractor.extract_from_midi(midi_path)
    extractor.save_labels_json(labels, json_path)

    print(f"  - Existiert {json_path}: {os.path.exists(json_path)}")
    assert os.path.exists(json_path), "JSON-Datei wurde nicht erzeugt."

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  - JSON-Inhalt (erste Einträge): {data[:2] if isinstance(data, list) else data}")
    assert isinstance(data, list)
    assert len(data) == len(labels)
    # check a key
    assert "instrument_class" in data[0]

    # Aufräumen
    os.remove(midi_path)
    os.remove(json_path)

    print("[TEST] test_save_labels_json_creates_file erfolgreich abgeschlossen.\n")


def test_save_labels_note_sequence_format_creates_file() -> None:
    """Testet, ob save_labels_note_sequence_format eine strukturierte Datei schreibt."""
    print("[TEST] test_save_labels_note_sequence_format_creates_file gestartet …")
    dm = _create_example_drum_mapping_for_labels()
    extractor = LabelExtractor(
        drum_mapping=dm,
        minimum_velocity=1,
        time_unit="seconds",
        include_non_drums=True,
    )

    midi_path = "test_labels_input.mid"
    ns_path = "test_labels_notes.json"
    _create_test_midi_file_for_labels(midi_path)

    labels = extractor.extract_from_midi(midi_path)
    extractor.save_labels_note_sequence_format(labels, ns_path)

    print(f"  - Existiert {ns_path}: {os.path.exists(ns_path)}")
    assert os.path.exists(ns_path), "NoteSequence-Datei wurde nicht erzeugt."

    with open(ns_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"  - NoteSequence-ähnlicher Inhalt: {data}")
    assert isinstance(data, dict)
    assert data.get("time_unit") == "seconds"
    assert "notes" in data
    assert isinstance(data["notes"], list)
    assert len(data["notes"]) == len(labels)

    # Aufräumen
    os.remove(midi_path)
    os.remove(ns_path)

    print("[TEST] test_save_labels_note_sequence_format_creates_file erfolgreich abgeschlossen.\n")


def run_all_label_extractor_tests() -> None:
    """Führt alle Tests für LabelExtractor aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte LabelExtractor-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_extract_from_midi_includes_drums_and_non_drums,
        test_filter_to_drums_only_keeps_drum_labels,
        test_save_labels_json_creates_file,
        test_save_labels_note_sequence_format_creates_file,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle LabelExtractor-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_label_extractor_tests()
