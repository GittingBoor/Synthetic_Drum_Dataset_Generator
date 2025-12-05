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
            min_instruments: int = 4,
            max_instruments: int = 8,
            drum_mapping: DrumMapping | None = None,
            drum_channel: int = 9,
    ) -> "BandConfiguration":
        """Erzeugt zufällig eine sinnvolle Bandbesetzung.

        Beschreibung:
            Wählt aus einer Liste möglicher Instrumente eine zufällige Band,
            bestehend aus mind. einem Chords-, Bass-, Pad- und Lead-Instrument.
            Die Gesamtgröße der Band liegt zwischen min_instruments und
            max_instruments (Standard: 4–8 Instrumente).

            Hinweis:
                Wenn kein DrumMapping übergeben wird, wird ein Dummy-Mapping
                verwendet. In deinem Pipeline-Code kannst du ein echtes
                DrumMapping übergeben.
        """
        if not available_patches:
            raise ValueError("Es wurden keine verfügbaren Instrumente übergeben.")

        # min_instruments darf nicht kleiner als 4 sein
        if min_instruments < 4:
            min_instruments = 4
        if max_instruments < min_instruments:
            max_instruments = min_instruments

        # Verfügbare Instrumente nach Rollen gruppieren
        chords = [i for i in available_patches if i.role == "chords"]
        basses = [i for i in available_patches if i.role == "bass"]
        pads = [i for i in available_patches if i.role == "pad"]
        leads = [i for i in available_patches if i.role == "lead"]

        # Sicherstellen, dass jede benötigte Rolle überhaupt existiert
        for role_name, lst in [
            ("chords", chords),
            ("bass", basses),
            ("pad", pads),
            ("lead", leads),
        ]:
            if not lst:
                raise ValueError(
                    f"Es sind keine Instrumente mit Rolle {role_name!r} in available_patches vorhanden."
                )

        # Obergrenze durch verfügbare Patches begrenzen
        max_possible = min(len(available_patches), max_instruments)
        if max_possible < 4:
            raise ValueError(
                "Nicht genug Instrumente verfügbar, um mindestens 4 zu wählen."
            )

        # Bandgröße zufällig zwischen min_instruments und max_possible
        band_size = random.randint(min_instruments, max_possible)

        chosen: List[Instrument] = []

        # Mindestens je ein Instrument pro Rolle wählen
        chosen.append(random.choice(chords))
        chosen.append(random.choice(basses))
        chosen.append(random.choice(pads))
        chosen.append(random.choice(leads))

        # Restliche Slots mit zufälligen Chords/Bass/Pad auffüllen (keine extra Leads)
        remaining_slots = band_size - len(chosen)
        if remaining_slots > 0:
            extras_pool = [
                i
                for i in available_patches
                if i.role in ("chords", "bass", "pad") and i not in chosen
            ]
            if extras_pool:
                k = min(remaining_slots, len(extras_pool))
                chosen.extend(random.sample(extras_pool, k=k))

        # Falls kein DrumMapping übergeben wurde: Dummy verwenden
        if drum_mapping is None:
            drum_mapping = DrumMapping(
                note_to_class={},
                class_to_notes={},
                core_classes=[],
            )

        return cls(
            drum_channel=drum_channel,
            drum_mapping=drum_mapping,
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



