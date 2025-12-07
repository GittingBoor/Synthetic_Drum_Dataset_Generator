from __future__ import annotations
from typing import Dict, List


class DrumMapping:
    """Verwaltet das Mapping zwischen MIDI-Notennummern und Drum-Klassen.

    Verantwortung:
        DrumMapping verwaltet alle Informationen darüber, welche MIDI-Notennummer
        zu welcher Drum-Klasse gehört (z. B. 36 → "KICK").
        Sie sorgt dafür, dass du an einer zentralen Stelle definierst, welche Drums
        du im Datensatz verwendest.
        Außerdem hilft sie dabei, aus Roh-MIDI-Daten saubere, konsistente Drum-Klassen
        für dein Training zu erzeugen.
    """

    def __init__(
        self,
        note_to_class: Dict[int, str],
        class_to_notes: Dict[str, List[int]],
        core_classes: List[str],
    ) -> None:
        """Konstruktor mit allen benötigten Attributen.

        Args:
            note_to_class: Mapping von MIDI-Notennummern zu Drum-Klassen
                (z. B. {36: "KICK", 38: "SNARE"}).
            class_to_notes: Mapping von Drum-Klassen zu einer Liste von MIDI-Notennummern
                (z. B. {"SNARE": [38, 40]}).
            core_classes: Liste der Kern-Drum-Klassen, die im Datensatz verwendet werden.
        """
        self.note_to_class: Dict[int, str] = dict(note_to_class)
        self.class_to_notes: Dict[str, List[int]] = {
            drum_class: list(notes) for drum_class, notes in class_to_notes.items()
        }
        self.core_classes: List[str] = list(core_classes)

    def map_note_to_class(self, note: int) -> str | None:
        """Gibt für eine MIDI-Notennummer die zugehörige Drum-Klasse zurück.

        Beschreibung:
            Gibt für eine MIDI-Notennummer (z. B. 38) die dazugehörige Drum-Klasse
            (z. B. "SNARE") zurück oder None, wenn die Note nicht unterstützt wird.

        Args:
            note: MIDI-Notennummer, die gemappt werden soll.

        Returns:
            Die zugehörige Drum-Klasse oder None, falls die Note nicht unterstützt wird.
        """
        return self.note_to_class.get(note)

    def get_primary_note_for_class(self, drum_class: str) -> int:
        """Liefert eine Haupt-MIDI-Note zu einer Drum-Klasse.

        Beschreibung:
            Liefert für eine Drum-Klasse (z. B. "SNARE") eine „Haupt“-MIDI-Note
            (z. B. 38), die du zum Generieren neuer Patterns benutzen kannst.

        Args:
            drum_class: Name der Drum-Klasse (z. B. "SNARE").

        Returns:
            Eine repräsentative MIDI-Notennummer für diese Drum-Klasse.

        Raises:
            KeyError: Wenn die Drum-Klasse unbekannt ist oder keine Noten zugeordnet sind.
        """
        if drum_class not in self.class_to_notes:
            raise KeyError(f"Unbekannte Drum-Klasse: {drum_class!r}")
        notes = self.class_to_notes[drum_class]
        if not notes:
            raise KeyError(f"Drum-Klasse {drum_class!r} hat keine zugeordneten Noten.")
        # Wir interpretieren die erste Note als „Primary“-Note.
        return notes[0]

    def is_supported_note(self, note: int) -> bool:
        """Prüft, ob eine MIDI-Note im Mapping definiert ist.

        Beschreibung:
            Prüft, ob eine MIDI-Note (z. B. 60) in deiner Mapping-Tabelle
            definiert ist und somit im Datensatz berücksichtigt werden soll.

        Args:
            note: MIDI-Notennummer, die geprüft werden soll.

        Returns:
            True, wenn die Note unterstützt wird, sonst False.
        """
        return note in self.note_to_class

    def list_supported_classes(self) -> List[str]:
        """Gibt eine Liste aller unterstützen Drum-Klassen zurück.

        Beschreibung:
            Gibt eine Liste aller Drum-Klassen zurück, die in core_classes bzw.
            im Mapping definiert sind.

        Returns:
            Liste aller Drum-Klassen.
        """
        classes: set[str] = set(self.core_classes)
        classes.update(self.note_to_class.values())
        classes.update(self.class_to_notes.keys())
        # Sortierung, damit das Ergebnis stabil / testbar ist.
        return sorted(classes)

    @classmethod
    def create_default(cls) -> DrumMapping:
        """Erzeugt ein Standard-DrumMapping für GM-Drums.

        Dieses Mapping deckt die wichtigsten Klassen für KICK, SNARE, HIHAT,
        TOMS, CRASH und RIDE ab und kann als Default für das Dataset genutzt werden.
        """

        # Zentrale Definition: von Klasse -> Liste MIDI-Noten
        class_to_notes: Dict[str, List[int]] = {
            "KICK": [36],  # Bass Drum 1
            "SNARE": [38, 40],  # Acoustic / Electric Snare
            "HH_CLOSED": [42],  # Closed Hi-Hat
            "HH_OPEN": [46],  # Open Hi-Hat
            "TOM_LOW": [45, 47],  # Low / Low-Mid Tom
            "TOM_MID": [48, 50],  # Hi-Mid / High Tom
            "TOM_HIGH": [50],  # (alternativ anderer High-Tom)
            "CRASH": [49, 57],  # Crash Cymbal 1 / 2
            "RIDE": [51, 59],  # Ride Cymbal 1 / 2
        }

        # Inverses Mapping: von Note -> Klasse
        note_to_class: Dict[int, str] = {}
        for drum_class, notes in class_to_notes.items():
            for note in notes:
                note_to_class[note] = drum_class

        # Kernklassen (für Training etc.)
        core_classes: List[str] = [
            "KICK",
            "SNARE",
            "HH_CLOSED",
            "HH_OPEN",
            "TOM_LOW",
            "TOM_MID",
            "TOM_HIGH",
            "CRASH",
            "RIDE",
        ]

        return cls(
            note_to_class=note_to_class,
            class_to_notes=class_to_notes,
            core_classes=core_classes,
        )