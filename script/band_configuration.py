from __future__ import annotations
from typing import Dict, List
import random

from .drum_mapping import DrumMapping
from .instrument import Instrument


class BandConfiguration:
    """Beschreibt die Bandbesetzung eines Songs.

    Verantwortung:
        BandConfiguration beschreibt, welche Instrumente in einem Song zusammen
        spielen, also quasi die „Bandbesetzung“.
        Sie hält fest, auf welchem Kanal die Drums liegen und welche Instrumente
        (Piano, Bass, Gitarre usw.) im Song verwendet werden.
        Damit kannst du für verschiedene Songs unterschiedliche, aber realistische
        Pop-Besetzungen erzeugen.
    """

    def __init__(
        self,
        drum_channel: int,
        drum_mapping: DrumMapping,
        instruments: List[Instrument],
    ) -> None:
        """Konstruktor für eine BandConfiguration.

        Args:
            drum_channel: MIDI-Kanal für Drums (z. B. 9 als Index für GM-Drumkanal).
            drum_mapping: Instanz von DrumMapping, die das Drum-Klassensystem beschreibt.
            instruments: Liste der Instrument-Objekte in dieser Band.
        """
        self.drum_channel: int = drum_channel
        self.drum_mapping: DrumMapping = drum_mapping
        # Kopie der Liste, damit externe Änderungen die Band nicht unbemerkt verändern.
        self.instruments: List[Instrument] = list(instruments)

    def get_instruments_by_role(self, role: str) -> List[Instrument]:
        """Liefert alle Instrumente mit einer bestimmten Rolle.

        Beschreibung:
            Liefert alle Instrumente, die eine bestimmte Rolle haben
            (z. B. alle "chords"-Instrumente), damit der Harmony-Generator weiß,
            wo Akkorde platziert werden.

        Args:
            role: Name der gesuchten Rolle (z. B. "chords").

        Returns:
            Liste aller Instrument-Objekte mit dieser Rolle.
        """
        return [inst for inst in self.instruments if inst.role == role]

    @classmethod
    def choose_random_band(
        cls,
        available_patches: List[Instrument],
    ) -> "BandConfiguration":
        """Erzeugt zufällig eine sinnvolle Bandbesetzung.

        Beschreibung:
            Erzeugt aus einer Liste möglicher Instrumente zufällig eine sinnvolle
            Bandbesetzung (z. B. immer Bass + Chords + 0–2 zusätzliche Instrumente).

            Hinweis:
                Da hier kein DrumMapping und kein Drumkanal übergeben wird, verwendet
                diese Methode einen einfachen Standard:
                - drum_channel = 9 (Index für GM-Drumkanal)
                - ein leeres DrumMapping (kann später ersetzt werden)

        Args:
            available_patches: Liste aller verfügbaren Instrument-Objekte.

        Returns:
            Eine neue BandConfiguration mit zufällig gewählten Instrumenten.

        Raises:
            ValueError: Wenn keine Instrumente übergeben wurden.
        """
        if not available_patches:
            raise ValueError("Es wurden keine verfügbaren Instrumente übergeben.")

        # Rollen-basierte Auswahl: mindestens ein Bass, mindestens ein Chords, Rest optional.
        bass_instruments = [i for i in available_patches if i.role == "bass"]
        chord_instruments = [i for i in available_patches if i.role == "chords"]
        other_instruments = [
            i for i in available_patches if i.role not in ("bass", "chords")
        ]

        chosen: List[Instrument] = []

        if bass_instruments:
            chosen.append(random.choice(bass_instruments))
        if chord_instruments:
            chosen.append(random.choice(chord_instruments))

        # 0–2 zusätzliche Instrumente (ohne Duplikate)
        if other_instruments:
            max_extras = min(2, len(other_instruments))
            num_extras = random.randint(0, max_extras)
            chosen.extend(random.sample(other_instruments, k=num_extras))

        # Fallback: Falls weder bass noch chords existieren (sehr untypisch), nimm einfach eins.
        if not chosen:
            chosen.append(random.choice(available_patches))

        dummy_drum_mapping = DrumMapping(
            note_to_class={},
            class_to_notes={},
            core_classes=[],
        )

        return cls(
            drum_channel=9,
            drum_mapping=dummy_drum_mapping,
            instruments=chosen,
        )

    def to_dict(self) -> Dict:
        """Exportiert die gesamte Bandkonfiguration als Dictionary.

        Beschreibung:
            Exportiert die gesamte Bandkonfiguration als Dictionary, damit du sie
            speichern oder debuggen kannst.

        Returns:
            Dictionary mit allen relevanten Informationen dieser BandConfiguration.
        """
        return {
            "drum_channel": self.drum_channel,
            "drum_mapping": {
                "note_to_class": self.drum_mapping.note_to_class,
                "class_to_notes": self.drum_mapping.class_to_notes,
                "core_classes": self.drum_mapping.core_classes,
            },
            "instruments": [inst.to_dict() for inst in self.instruments],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BandConfiguration":
        """Baut eine BandConfiguration aus einem Dictionary wieder zusammen.

        Beschreibung:
            Baut aus einem gespeicherten Dictionary eine BandConfiguration wieder
            zusammen.

        Args:
            data: Dictionary mit allen Feldern für eine BandConfiguration.
                  Erwartet wird:
                    - "drum_channel"
                    - "drum_mapping" mit "note_to_class", "class_to_notes", "core_classes"
                    - "instruments": Liste von Instrument-Dicts

        Returns:
            Eine neue BandConfiguration, rekonstruiert aus dem Dictionary.
        """
        drum_mapping_data = data["drum_mapping"]
        drum_mapping = DrumMapping(
            note_to_class=drum_mapping_data["note_to_class"],
            class_to_notes=drum_mapping_data["class_to_notes"],
            core_classes=drum_mapping_data["core_classes"],
        )

        instruments = [
            Instrument.from_dict(inst_data) for inst_data in data["instruments"]
        ]

        return cls(
            drum_channel=int(data["drum_channel"]),
            drum_mapping=drum_mapping,
            instruments=instruments,
        )


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für BandConfiguration
# ---------------------------------------------------------------------------

def _create_test_drum_mapping_for_band_config() -> DrumMapping:
    """Erzeugt ein minimales DrumMapping für BandConfiguration-Tests."""
    print("\n[SETUP] Erzeuge Test-DrumMapping für BandConfiguration …")
    dm = DrumMapping(
        note_to_class={36: "KICK"},
        class_to_notes={"KICK": [36]},
        core_classes=["KICK"],
    )
    print(
        f"[SETUP] DrumMapping(note_to_class={dm.note_to_class}, "
        f"class_to_notes={dm.class_to_notes}, core_classes={dm.core_classes})"
    )
    return dm


def _create_example_instruments_for_band() -> List[Instrument]:
    """Erzeugt eine kleine Liste von Instrumenten mit unterschiedlichen Rollen."""
    print("[SETUP] Erzeuge Beispiel-Instrumente für BandConfiguration …")
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
        Instrument(
            name="Synth Pad",
            gm_program=88,
            channel=2,
            volume=0.7,
            pan=0.2,
            role="pad",
        ),
        Instrument(
            name="Lead Synth",
            gm_program=81,
            channel=3,
            volume=0.8,
            pan=0.1,
            role="lead",
        ),
    ]
    for inst in instruments:
        print(
            f"  - Instrument(name={inst.name!r}, role={inst.role!r}, "
            f"channel={inst.channel}, gm_program={inst.gm_program})"
        )
    print()
    return instruments


def _create_example_band_configuration() -> BandConfiguration:
    """Erzeugt eine Beispiel-BandConfiguration für Tests."""
    print("[SETUP] Erzeuge Beispiel-BandConfiguration …")
    dm = _create_test_drum_mapping_for_band_config()
    instruments = _create_example_instruments_for_band()
    band = BandConfiguration(
        drum_channel=9,
        drum_mapping=dm,
        instruments=instruments,
    )
    print(
        f"[SETUP] BandConfiguration(drum_channel={band.drum_channel}, "
        f"instruments={[i.name for i in band.instruments]})\n"
    )
    return band


def test_get_instruments_by_role() -> None:
    """Testet get_instruments_by_role für verschiedene Rollen."""
    print("[TEST] test_get_instruments_by_role gestartet …")
    band = _create_example_band_configuration()

    chords = band.get_instruments_by_role("chords")
    bass = band.get_instruments_by_role("bass")
    pads = band.get_instruments_by_role("pad")
    unknown = band.get_instruments_by_role("unknown_role")

    print(f"  - chords: {[i.name for i in chords]}")
    print(f"  - bass:   {[i.name for i in bass]}")
    print(f"  - pads:   {[i.name for i in pads]}")
    print(f"  - unknown:{[i.name for i in unknown]}")

    assert len(chords) == 1 and chords[0].role == "chords"
    assert len(bass) == 1 and bass[0].role == "bass"
    assert len(pads) == 1 and pads[0].role == "pad"
    assert len(unknown) == 0

    print("[TEST] test_get_instruments_by_role erfolgreich abgeschlossen.\n")


def test_choose_random_band_contains_bass_and_chords_if_available() -> None:
    """Testet, ob choose_random_band Bass und Chords enthält, wenn verfügbar."""
    print("[TEST] test_choose_random_band_contains_bass_and_chords_if_available gestartet …")
    instruments = _create_example_instruments_for_band()

    random.seed(123)  # für deterministisches Verhalten im Test
    band = BandConfiguration.choose_random_band(instruments)

    roles = [inst.role for inst in band.instruments]
    print(f"  - Gewählte Instrumente: {[inst.name for inst in band.instruments]}")
    print(f"  - Rollen: {roles}")
    print(f"  - drum_channel: {band.drum_channel}")

    assert any(r == "bass" for r in roles), "Es sollte mindestens ein Bass-Instrument geben."
    assert any(r == "chords" for r in roles), "Es sollte mindestens ein Chords-Instrument geben."
    assert band.drum_channel == 9

    print("[TEST] test_choose_random_band_contains_bass_and_chords_if_available erfolgreich abgeschlossen.\n")


def test_band_configuration_to_dict_and_from_dict_roundtrip() -> None:
    """Testet, ob to_dict() und from_dict() zusammen konsistent sind."""
    print("[TEST] test_band_configuration_to_dict_and_from_dict_roundtrip gestartet …")
    original = _create_example_band_configuration()

    data = original.to_dict()
    print(f"  - to_dict() -> {data}")

    restored = BandConfiguration.from_dict(data)
    print(
        f"  - Restored BandConfiguration: drum_channel={restored.drum_channel}, "
        f"instruments={[i.name for i in restored.instruments]}"
    )

    assert restored.drum_channel == original.drum_channel
    assert restored.drum_mapping.note_to_class == original.drum_mapping.note_to_class
    assert restored.drum_mapping.class_to_notes == original.drum_mapping.class_to_notes
    assert restored.drum_mapping.core_classes == original.drum_mapping.core_classes

    original_names = [i.name for i in original.instruments]
    restored_names = [i.name for i in restored.instruments]
    assert restored_names == original_names

    print("[TEST] test_band_configuration_to_dict_and_from_dict_roundtrip erfolgreich abgeschlossen.\n")


def run_all_band_configuration_tests() -> None:
    """Führt alle Tests für BandConfiguration aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte BandConfiguration-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_get_instruments_by_role,
        test_choose_random_band_contains_bass_and_chords_if_available,
        test_band_configuration_to_dict_and_from_dict_roundtrip,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle BandConfiguration-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_band_configuration_tests()
