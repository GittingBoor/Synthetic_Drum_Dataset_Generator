from __future__ import annotations
from typing import Dict


class Instrument:
    """Beschreibt ein einzelnes Instrument für synthetische Songs.

    Verantwortung:
        Instrument beschreibt ein einzelnes Instrument, das du in deinen
        synthetischen Songs verwendest, z. B. "Electric Piano 1" oder
        "Electric Bass (finger)".
        Es speichert, welche GM-Programnummer das Instrument hat und auf welchem
        Kanal es gespielt wird.
        Außerdem können hier Lautstärke, Panorama und Rolle im Arrangement
        (z. B. "Bass", "Chords", "Lead") hinterlegt werden.
    """

    def __init__(
        self,
        name: str,
        gm_program: int,
        channel: int,
        volume: float,
        pan: float,
        role: str,
    ) -> None:
        """Konstruktor mit allen Attributen des Instrument.

         Args:
            name: Klartext-Name des Instruments (z. B. "Electric Piano 1").
            gm_program: General-MIDI-Programnummer, die dem der Klangtyp festlegt wird.
                (z. B. 4 = Electric Piano 1 gemäß GM-Spezifikation).
            channel: MIDI-Kanal, auf dem das Instrument spielt (0–15,
                Drums später typischerweise Kanal 10 [Index = 9]).
            volume: Lautstärke-Faktor zwischen 0.0 und 1.0
                (z. B. 0.8 für 80 % der Maximal-Lautstärke).
            pan: Panorama-Position, wo das Instrument zu hören ist (auf den Kopfhörern)
                (z. B. -0.3 = leicht links, 0.0 = Mitte, 0.5 = rechts).
            role: Funktion des Instruments im Arrangement
                (z. B. "chords", "bass", "pad", "lead").
        """

        self.name: str = name
        self.gm_program: int = gm_program
        self.channel: int = channel
        self.volume: float = volume
        self.pan: float = pan
        self.role: str = role

    def to_dict(self) -> Dict:
        """Exportiert alle Attribute des Instruments als Dictionary.

        Beschreibung:
            Exportiert alle Attribute als Dictionary, damit du es z. B. in JSON
            speichern oder loggen kannst.

        Returns:
            Dictionary mit allen Attributen dieses Instrument.
        """
        return {
            "name": self.name,
            "gm_program": self.gm_program,
            "channel": self.channel,
            "volume": self.volume,
            "pan": self.pan,
            "role": self.role,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Instrument":
        """Erzeugt ein Instrument-Objekt aus einem Dictionary.

        Beschreibung:
            Erzeugt aus einem Dictionary (z. B. aus einer JSON-Datei)
            wieder ein Instrument-Objekt.

        Args:
            data: Dictionary mit den notwendigen Feldern für ein Instrument.
                  Erwartete Keys: "name", "gm_program", "channel",
                  "volume", "pan", "role".

        Returns:
            Ein neues Instrument-Objekt, basierend auf den Dictionary-Daten.

        Raises:
            KeyError: Wenn ein benötigtes Feld im Dictionary fehlt.
            TypeError / ValueError: Wenn die Werte nicht den erwarteten Typen entsprechen.
        """
        return cls(
            name=data["name"],
            gm_program=int(data["gm_program"]),
            channel=int(data["channel"]),
            volume=float(data["volume"]),
            pan=float(data["pan"]),
            role=data["role"],
        )


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen
# ---------------------------------------------------------------------------


def _create_example_instrument_patch() -> Instrument:
    """Erzeugt ein Beispiel-Instrument für Tests."""
    print("\n[SETUP] Erzeuge Beispiel-Instrument für Tests …")
    patch = Instrument(
        name="Electric Piano 1",
        gm_program=4,
        channel=0,
        volume=0.8,
        pan=0.0,
        role="chords",
    )
    print(
        f"[SETUP] Instrument(name={patch.name!r}, gm_program={patch.gm_program}, "
        f"channel={patch.channel}, volume={patch.volume}, pan={patch.pan}, role={patch.role!r})"
    )
    return patch


def test_instrument_patch_to_dict_basic() -> None:
    """Testet, ob to_dict() alle Felder korrekt exportiert."""
    print("[TEST] test_instrument_patch_to_dict_basic gestartet …")
    patch = _create_example_instrument_patch()
    data = patch.to_dict()
    print(f"  - to_dict() -> {data}")

    assert data["name"] == "Electric Piano 1"
    assert data["gm_program"] == 4
    assert data["channel"] == 0
    assert data["volume"] == 0.8
    assert data["pan"] == 0.0
    assert data["role"] == "chords"

    print("[TEST] test_instrument_patch_to_dict_basic erfolgreich abgeschlossen.\n")


def test_instrument_patch_from_dict_basic() -> None:
    """Testet, ob from_dict() ein korrektes Objekt erzeugt."""
    print("[TEST] test_instrument_patch_from_dict_basic gestartet …")
    data = {
        "name": "Electric Bass (finger)",
        "gm_program": 33,
        "channel": 1,
        "volume": 0.9,
        "pan": -0.2,
        "role": "bass",
    }
    print(f"  - Eingabedaten für from_dict: {data}")
    patch = Instrument.from_dict(data)

    print(
        f"  - Erzeugtes Instrument: "
        f"name={patch.name!r}, gm_program={patch.gm_program}, channel={patch.channel}, "
        f"volume={patch.volume}, pan={patch.pan}, role={patch.role!r}"
    )

    assert patch.name == "Electric Bass (finger)"
    assert patch.gm_program == 33
    assert patch.channel == 1
    assert patch.volume == 0.9
    assert patch.pan == -0.2
    assert patch.role == "bass"

    print("[TEST] test_instrument_patch_from_dict_basic erfolgreich abgeschlossen.\n")


def test_instrument_patch_roundtrip_dict() -> None:
    """Testet, ob to_dict() + from_dict() zusammen verlustfrei sind."""
    print("[TEST] test_instrument_patch_roundtrip_dict gestartet …")
    original = _create_example_instrument_patch()
    data = original.to_dict()
    print(f"  - to_dict() -> {data}")
    restored = Instrument.from_dict(data)

    print(
        "  - Restored Instrument: "
        f"name={restored.name!r}, gm_program={restored.gm_program}, channel={restored.channel}, "
        f"volume={restored.volume}, pan={restored.pan}, role={restored.role!r}"
    )

    assert restored.name == original.name
    assert restored.gm_program == original.gm_program
    assert restored.channel == original.channel
    assert restored.volume == original.volume
    assert restored.pan == original.pan
    assert restored.role == original.role

    print("[TEST] test_instrument_patch_roundtrip_dict erfolgreich abgeschlossen.\n")


def run_all_instrument_patch_tests() -> None:
    """Führt alle Tests für Instrument aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte Instrument-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_instrument_patch_to_dict_basic,
        test_instrument_patch_from_dict_basic,
        test_instrument_patch_roundtrip_dict,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle Instrument-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_instrument_patch_tests()
