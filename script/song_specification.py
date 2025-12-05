from __future__ import annotations
from typing import Dict, Tuple, List

from .band_configuration import BandConfiguration
from .drum_mapping import DrumMapping
from .instrument import Instrument


class SongSpecification:
    """Beschreibt einen kompletten synthetischen Song auf Parameter-Ebene.

    Verantwortung:
        SongSpecification beschreibt einen kompletten synthetischen Song,
        bevor Noten generiert werden.
        Sie legt fest: Tempo, Taktart, Länge, Tonart, Stil und welche
        Band-Konfiguration verwendet wird.
        Damit kannst du später reproduzierbar den gleichen Song (Struktur)
        nochmal generieren, wenn du denselben Seed nutzt.
    """

    def __init__(
        self,
        song_identifier: str,
        tempo_bpm: float,
        time_signature: Tuple[int, int],
        number_of_bars: int,
        key: str,
        style: str,
        band_configuration: BandConfiguration,
        random_seed: int,
    ) -> None:
        """Konstruktor mit allen Song-Parametern.

        Args:
            song_identifier: Eindeutiger Bezeichner des Songs
                (z. B. "song_0001_pop_c_major").
            tempo_bpm: Tempo in Schlägen pro Minute (z. B. 120.0).
            time_signature: Taktart als (Zähler, Nenner), z. B. (4, 4).
            number_of_bars: Anzahl der Takte (z. B. 16).
            key: Tonart des Songs (z. B. "C major", "A minor").
            style: Stilbeschreibung (z. B. "pop_straight", "funk").
            band_configuration: Verwendete BandConfiguration für diesen Song.
            random_seed: Seed für deterministische Generierung.
        """
        self.song_identifier: str = song_identifier
        self.tempo_bpm: float = float(tempo_bpm)
        self.time_signature: Tuple[int, int] = (
            int(time_signature[0]),
            int(time_signature[1]),
        )
        self.number_of_bars: int = int(number_of_bars)
        self.key: str = key
        self.style: str = style
        self.band_configuration: BandConfiguration = band_configuration
        self.random_seed: int = int(random_seed)

    def get_duration_seconds(self) -> float:
        """Berechnet die Gesamtdauer des Songs in Sekunden.

        Beschreibung:
            Berechnet die Gesamtdauer des Songs in Sekunden anhand von Tempo,
            Taktart und Anzahl der Takte.

            Annahme:
                Das Tempo bezieht sich auf Viertelnoten.
                Die Anzahl der Viertelnoten pro Takt ergibt sich aus:
                beats_per_bar = Zähler * (4 / Nenner)

        Returns:
            Dauer des Songs in Sekunden.
        """
        numerator, denominator = self.time_signature

        # Wie viele Viertelnoten-equivalente Schläge pro Takt?
        beats_per_bar = numerator * (4.0 / float(denominator))

        total_beats = self.number_of_bars * beats_per_bar
        seconds_per_beat = 60.0 / self.tempo_bpm

        duration_seconds = total_beats * seconds_per_beat
        return duration_seconds

    def to_dict(self) -> Dict:
        """Exportiert alle Song-Parameter als Dictionary.

        Beschreibung:
            Exportiert alle Song-Parameter als Dictionary, um sie z. B. in
            eine JSON-Logdatei zu schreiben.

        Returns:
            Dictionary mit allen Parametern dieser SongSpecification.
        """
        return {
            "song_identifier": self.song_identifier,
            "tempo_bpm": self.tempo_bpm,
            "time_signature": {
                "numerator": self.time_signature[0],
                "denominator": self.time_signature[1],
            },
            "number_of_bars": self.number_of_bars,
            "key": self.key,
            "style": self.style,
            "band_configuration": self.band_configuration.to_dict(),
            "random_seed": self.random_seed,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SongSpecification":
        """Baut eine SongSpecification aus einem Dictionary wieder auf.

        Beschreibung:
            Baut aus einem gespeicherten Dictionary eine SongSpecification
            wieder auf.

        Args:
            data: Dictionary mit den gespeicherten Song-Parametern.
                  Erwartet wird u. a.:
                    - "song_identifier"
                    - "tempo_bpm"
                    - "time_signature" mit "numerator", "denominator"
                    - "number_of_bars"
                    - "key"
                    - "style"
                    - "band_configuration" (Dictionary)
                    - "random_seed"

        Returns:
            Eine neue SongSpecification, rekonstruiert aus dem Dictionary.
        """
        ts_data = data["time_signature"]
        time_signature = (int(ts_data["numerator"]), int(ts_data["denominator"]))

        band_conf = BandConfiguration.from_dict(data["band_configuration"])

        return cls(
            song_identifier=data["song_identifier"],
            tempo_bpm=float(data["tempo_bpm"]),
            time_signature=time_signature,
            number_of_bars=int(data["number_of_bars"]),
            key=data["key"],
            style=data["style"],
            band_configuration=band_conf,
            random_seed=int(data["random_seed"]),
        )


