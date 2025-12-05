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


