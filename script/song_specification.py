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


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für SongSpecification
# ---------------------------------------------------------------------------

def _create_test_drum_mapping_for_song_spec() -> DrumMapping:
    """Erzeugt ein minimales DrumMapping für SongSpecification-Tests."""
    print("\n[SETUP] Erzeuge Test-DrumMapping für SongSpecification …")
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


def _create_test_band_configuration_for_song_spec() -> BandConfiguration:
    """Erzeugt eine einfache BandConfiguration für SongSpecification-Tests."""
    print("[SETUP] Erzeuge Test-BandConfiguration für SongSpecification …")
    dm = _create_test_drum_mapping_for_song_spec()

    instruments: List[Instrument] = [
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
    ]
    band_conf = BandConfiguration(
        drum_channel=9,
        drum_mapping=dm,
        instruments=instruments,
    )

    print(
        f"[SETUP] BandConfiguration(drum_channel={band_conf.drum_channel}, "
        f"instruments={[i.name for i in band_conf.instruments]})\n"
    )
    return band_conf


def _create_example_song_specification() -> SongSpecification:
    """Erzeugt eine Beispiel-SongSpecification für Tests."""
    print("[SETUP] Erzeuge Beispiel-SongSpecification …")
    band_conf = _create_test_band_configuration_for_song_spec()
    song_spec = SongSpecification(
        song_identifier="song_0001_pop_c_major",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        number_of_bars=16,
        key="C major",
        style="pop_straight",
        band_configuration=band_conf,
        random_seed=42,
    )
    print(
        f"[SETUP] SongSpecification(id={song_spec.song_identifier!r}, "
        f"tempo={song_spec.tempo_bpm}, time_signature={song_spec.time_signature}, "
        f"bars={song_spec.number_of_bars}, key={song_spec.key!r}, style={song_spec.style!r})\n"
    )
    return song_spec


def test_get_duration_seconds_4_4_120bpm() -> None:
    """Testet die Dauerberechnung für 4/4-Takt bei 120 BPM."""
    print("[TEST] test_get_duration_seconds_4_4_120bpm gestartet …")
    song_spec = _create_example_song_specification()

    duration = song_spec.get_duration_seconds()
    print(f"  - Berechnete Dauer: {duration} Sekunden")

    # 16 Takte, 4/4, 120 BPM:
    # beats_per_bar = 4 * (4 / 4) = 4
    # total_beats = 16 * 4 = 64
    # seconds_per_beat = 60 / 120 = 0.5
    # duration = 64 * 0.5 = 32
    expected = 32.0
    assert abs(duration - expected) < 1e-6, (
        f"Erwartete Dauer {expected}, aber berechnet wurde {duration}."
    )

    print("[TEST] test_get_duration_seconds_4_4_120bpm erfolgreich abgeschlossen.\n")


def test_get_duration_seconds_3_4_90bpm() -> None:
    """Testet die Dauerberechnung für 3/4-Takt bei 90 BPM."""
    print("[TEST] test_get_duration_seconds_3_4_90bpm gestartet …")
    band_conf = _create_test_band_configuration_for_song_spec()
    song_spec = SongSpecification(
        song_identifier="song_0002_pop_c_major",
        tempo_bpm=90.0,
        time_signature=(3, 4),
        number_of_bars=8,
        key="C major",
        style="pop_waltz",
        band_configuration=band_conf,
        random_seed=7,
    )

    duration = song_spec.get_duration_seconds()
    print(f"  - Berechnete Dauer: {duration} Sekunden")

    # 8 Takte, 3/4, 90 BPM:
    # beats_per_bar = 3 * (4 / 4) = 3
    # total_beats = 8 * 3 = 24
    # seconds_per_beat = 60 / 90 = 2/3
    # duration = 24 * (2/3) = 16
    expected = 16.0
    assert abs(duration - expected) < 1e-6, (
        f"Erwartete Dauer {expected}, aber berechnet wurde {duration}."
    )

    print("[TEST] test_get_duration_seconds_3_4_90bpm erfolgreich abgeschlossen.\n")


def test_song_specification_to_dict_and_from_dict_roundtrip() -> None:
    """Testet, ob to_dict() und from_dict() zusammen konsistent sind."""
    print("[TEST] test_song_specification_to_dict_and_from_dict_roundtrip gestartet …")
    original = _create_example_song_specification()

    data = original.to_dict()
    print(f"  - to_dict() -> {data}")

    restored = SongSpecification.from_dict(data)
    print(
        f"  - Restored SongSpecification: id={restored.song_identifier!r}, "
        f"tempo={restored.tempo_bpm}, time_signature={restored.time_signature}, "
        f"bars={restored.number_of_bars}, key={restored.key!r}, style={restored.style!r}"
    )

    assert restored.song_identifier == original.song_identifier
    assert abs(restored.tempo_bpm - original.tempo_bpm) < 1e-9
    assert restored.time_signature == original.time_signature
    assert restored.number_of_bars == original.number_of_bars
    assert restored.key == original.key
    assert restored.style == original.style
    assert restored.random_seed == original.random_seed

    # BandConfiguration grob vergleichen (z. B. Instrument-Namen)
    orig_instruments = [i.name for i in original.band_configuration.instruments]
    rest_instruments = [i.name for i in restored.band_configuration.instruments]
    assert orig_instruments == rest_instruments

    print("[TEST] test_song_specification_to_dict_and_from_dict_roundtrip erfolgreich abgeschlossen.\n")


def run_all_song_specification_tests() -> None:
    """Führt alle Tests für SongSpecification aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte SongSpecification-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_get_duration_seconds_4_4_120bpm,
        test_get_duration_seconds_3_4_90bpm,
        test_song_specification_to_dict_and_from_dict_roundtrip,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle SongSpecification-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_song_specification_tests()
