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



