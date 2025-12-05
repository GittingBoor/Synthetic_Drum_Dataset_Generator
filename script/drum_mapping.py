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


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen
# ---------------------------------------------------------------------------

def _create_example_drum_mapping() -> DrumMapping:
    """Erzeugt eine Beispiel-DrumMapping-Instanz für Tests mit allen relevanten Drums."""
    # Zentrales Mapping: jede MIDI-Note → Drum-Klasse
    note_to_class = {
        # Kicks
        36: "KICK",

        # Snares & Sidestick
        38: "SNARE",
        40: "SNARE",
        37: "SIDESTICK",

        # Hi-Hats
        42: "HH_CLOSED",
        44: "HH_CLOSED",  # Pedal Hi-Hat → zu Closed zusammengefasst
        46: "HH_OPEN",
        22: "HH_CLOSED",  # Roland-Variante → Closed
        26: "HH_OPEN",    # Roland-Variante → Open

        # Toms
        43: "TOM_LOW",    # High Floor Tom
        45: "TOM_LOW",    # Low Tom
        47: "TOM_MID",    # Low-Mid Tom
        48: "TOM_MID",    # Hi-Mid Tom
        50: "TOM_HIGH",   # High Tom

        # Crashes / Rides
        49: "CRASH",      # Crash Cymbal 1
        51: "RIDE",       # Ride Cymbal 1
        53: "RIDE",       # Ride Bell
    }

    # Inverse Mapping: Drum-Klasse → Liste von MIDI-Noten (für Primary-Note, Pattern-Generierung etc.)
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

    # Relevante Klassen für dein System
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

def test_map_note_to_class_known_note() -> None:
    """Testet, ob map_note_to_class für alle relevanten Noten korrekt funktioniert."""
    print("[TEST] test_map_note_to_class_known_note gestartet …")
    dm = _create_example_drum_mapping()

    test_cases = {
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

    for note, expected_class in test_cases.items():
        result = dm.map_note_to_class(note)
        print(f"  - map_note_to_class({note}) -> {result!r} (erwartet: {expected_class!r})")
        assert result == expected_class, (
            f"map_note_to_class({note}) sollte {expected_class!r} liefern, "
            f"aber war {result!r}."
        )

    print("[TEST] test_map_note_to_class_known_note erfolgreich abgeschlossen.\n")


def test_map_note_to_class_unknown_note() -> None:
    """Testet, ob map_note_to_class für unbekannte Noten None zurückgibt."""
    print("[TEST] test_map_note_to_class_unknown_note gestartet …")
    dm = _create_example_drum_mapping()

    unknown_notes = [60, 1]

    for note in unknown_notes:
        result = dm.map_note_to_class(note)
        print(f"  - map_note_to_class({note}) -> {result!r} (erwartet: None)")
        assert result is None, (
            f"map_note_to_class({note}) sollte None liefern, war aber {result!r}."
        )

    print("[TEST] test_map_note_to_class_unknown_note erfolgreich abgeschlossen.\n")


def test_get_primary_note_for_class_basic() -> None:
    """Testet get_primary_note_for_class für alle relevanten Klassen."""
    print("[TEST] test_get_primary_note_for_class_basic gestartet …")
    dm = _create_example_drum_mapping()

    test_cases = {
        "KICK": 36,
        "SNARE": 38,
        "SIDESTICK": 37,
        "HH_CLOSED": 42,
        "HH_OPEN": 46,
        "TOM_LOW": 43,
        "TOM_MID": 47,
        "TOM_HIGH": 50,
        "CRASH": 49,
        "RIDE": 51,
    }

    for drum_class, expected_primary in test_cases.items():
        result = dm.get_primary_note_for_class(drum_class)
        print(
            f"  - get_primary_note_for_class({drum_class!r}) "
            f"-> {result} (erwartet: {expected_primary})"
        )
        assert result == expected_primary, (
            f"Primary-Note für {drum_class!r} sollte {expected_primary} sein, "
            f"war aber {result}."
        )

    print("[TEST] test_get_primary_note_for_class_basic erfolgreich abgeschlossen.\n")


def test_get_primary_note_for_class_raises_for_unknown() -> None:
    """Testet, ob get_primary_note_for_class für unbekannte Klassen einen Fehler wirft."""
    print("[TEST] test_get_primary_note_for_class_raises_for_unknown gestartet …")
    dm = _create_example_drum_mapping()
    unknown_class = "UNKNOWN_CLASS"
    print(f"  - Erwartet: KeyError bei get_primary_note_for_class({unknown_class!r})")

    try:
        _ = dm.get_primary_note_for_class(unknown_class)
    except KeyError as e:
        print(f"    -> KeyError wie erwartet gefangen: {e}")
    else:
        raise AssertionError(
            "Erwarteter KeyError für unbekannte Drum-Klasse ist ausgeblieben."
        )

    print("[TEST] test_get_primary_note_for_class_raises_for_unknown erfolgreich abgeschlossen.\n")


def test_is_supported_note() -> None:
    """Testet is_supported_note für relevante und irrelevante Noten."""
    print("[TEST] test_is_supported_note gestartet …")
    dm = _create_example_drum_mapping()

    test_cases = {
        # Relevante Drums (sollten True sein)
        36: True,
        38: True,
        37: True,
        42: True,
        44: True,
        46: True,
        22: True,
        26: True,
        43: True,
        45: True,
        47: True,
        48: True,
        50: True,
        49: True,
        51: True,
        53: True,

        # Irgendwelche anderen Noten (sollten False sein)
        35: False,
        39: False,
        60: False,
        0: False,
    }

    for note, expected in test_cases.items():
        result = dm.is_supported_note(note)
        print(f"  - is_supported_note({note}) -> {result} (erwartet: {expected})")
        assert result is expected, (
            f"is_supported_note({note}) sollte {expected} sein, war aber {result}."
        )

    print("[TEST] test_is_supported_note erfolgreich abgeschlossen.\n")


def test_list_supported_classes_includes_core_and_mapping() -> None:
    """Testet, ob list_supported_classes alle relevanten Drum-Klassen enthält."""
    print("[TEST] test_list_supported_classes_includes_core_and_mapping gestartet …")
    dm = _create_example_drum_mapping()
    classes = dm.list_supported_classes()

    print(f"  - list_supported_classes() -> {classes}")

    # Alle Klassen aus core_classes sollten enthalten sein.
    for c in dm.core_classes:
        print(f"    * Prüfe Core-Klasse {c!r} …")
        assert c in classes, f"Core-Klasse {c!r} fehlt in list_supported_classes."

    # Alle Klassen aus note_to_class und class_to_notes sollten enthalten sein.
    for c in dm.note_to_class.values():
        print(f"    * Prüfe Klasse aus note_to_class {c!r} …")
        assert c in classes, (
            f"Klasse {c!r} aus note_to_class fehlt in list_supported_classes."
        )

    for c in dm.class_to_notes.keys():
        print(f"    * Prüfe Klasse aus class_to_notes {c!r} …")
        assert c in classes, (
            f"Klasse {c!r} aus class_to_notes fehlt in list_supported_classes."
        )

    print("[TEST] test_list_supported_classes_includes_core_and_mapping erfolgreich abgeschlossen.\n")


def run_all_drum_mapping_tests() -> None:
    """Führt alle Tests für DrumMapping aus und gibt eine ausführliche Zusammenfassung aus."""
    print("============================================================")
    print("Starte DrumMapping-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_map_note_to_class_known_note,
        test_map_note_to_class_unknown_note,
        test_get_primary_note_for_class_basic,
        test_get_primary_note_for_class_raises_for_unknown,
        test_is_supported_note,
        test_list_supported_classes_includes_core_and_mapping,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle DrumMapping-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    # Einfacher Test-Runner, falls die Datei direkt ausgeführt wird.
    run_all_drum_mapping_tests()
