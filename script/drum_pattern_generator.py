from __future__ import annotations
from dataclasses import dataclass
from typing import List
import random

from .drum_mapping import DrumMapping
from .song_specification import SongSpecification
from .band_configuration import BandConfiguration
from .instrument import Instrument


@dataclass
class DrumEvent:
    """Repräsentiert ein einzelnes Drum-Ereignis."""
    time_sec: float
    drum_class: str
    velocity: int


class DrumPatternGenerator:
    """Erzeugt Drum-Pattern für eine gegebene SongSpecification.

    Verantwortung:
        DrumPatternGenerator ist dafür zuständig, aus einer SongSpecification
        passende Drum-Pattern zu erzeugen.
        Er entscheidet, wann Kick, Snare, Hi-Hat, Toms und Becken gespielt werden,
        inklusive Ghostnotes und Fills.
        Er kann außerdem Timing und Velocity „menschlicher“ machen (Humanisierung).
    """

    def __init__(
        self,
        drum_mapping: DrumMapping,
        complexity: float,
        ghostnote_probability: float,
        fill_probability: float,
        swing_amount: float,
    ) -> None:
        """Konstruktor mit allen Parametern für die Drum-Generierung.

        Args:
            drum_mapping: Instanz von DrumMapping zur Abbildung von Drum-Klassen
                auf konkrete MIDI-Noten (wird später beim MIDI-Bau genutzt).
            complexity: Komplexitätsgrad der Grooves (z. B. 0.3 simpel, 0.8 komplex).
            ghostnote_probability: Wahrscheinlichkeit für Ghostnotes bei Snare (0–1).
            fill_probability: Wahrscheinlichkeit für Fills in bestimmten Takten (0–1).
            swing_amount: Stärke des Swing-/Shuffle-Effekts bzw. Timing-Humanisierung
                (z. B. 0.0 = kein Swing, 0.2 = leicht verschobene Offbeats).
        """
        self.drum_mapping: DrumMapping = drum_mapping
        self.complexity: float = float(complexity)
        self.ghostnote_probability: float = float(ghostnote_probability)
        self.fill_probability: float = float(fill_probability)
        self.swing_amount: float = float(swing_amount)

    # --------------------------------------------------------------------- #
    # Hilfsfunktionen intern
    # --------------------------------------------------------------------- #

    @staticmethod
    def _compute_timing(song_spec: SongSpecification) -> tuple[float, float, float]:
        """Hilfsfunktion: Liefert (beats_per_bar, seconds_per_beat, seconds_per_bar)."""
        numerator, denominator = song_spec.time_signature
        beats_per_bar = numerator * (4.0 / float(denominator))
        seconds_per_beat = 60.0 / song_spec.tempo_bpm
        seconds_per_bar = beats_per_bar * seconds_per_beat
        return beats_per_bar, seconds_per_beat, seconds_per_bar

    # --------------------------------------------------------------------- #
    # Öffentliche API
    # --------------------------------------------------------------------- #

    def generate_drum_track(
        self,
        song_specification: SongSpecification,
    ) -> List[DrumEvent]:
        """Erzeugt eine Drum-Spur für den gesamten Song.

        Beschreibung:
            Erzeugt für den ganzen Song eine Liste von Drum-Events (mit Zeit,
            Klasse und Velocity) basierend auf Stil, Tempo, Anzahl Takte usw.

            Vereinfachtes Pattern (4/4-Pop-Groove):
                - Kick auf Beat 1 jedes Takts
                - Snare auf Beat 2 und 4 (falls genügend Beats vorhanden)
                - Geschlossene Hi-Hat auf jeden Beat
                - Optional Ghostnotes auf Snare-Offbeats abhängig von ghostnote_probability

        Args:
            song_specification: Spezifikation des Songs, für den die Drums
                generiert werden sollen.

        Returns:
            Liste von DrumEvent-Objekten für den gesamten Song.
        """
        beats_per_bar, seconds_per_beat, seconds_per_bar = self._compute_timing(
            song_specification
        )

        events: List[DrumEvent] = []

        # Wir gehen von typischen Zählzeiten aus, die auch für 3/4 usw. funktionieren.
        for bar_index in range(song_specification.number_of_bars):
            bar_start = bar_index * seconds_per_bar

            for beat_index in range(int(beats_per_bar)):
                beat_time = bar_start + beat_index * seconds_per_beat

                # Kick auf Beat 1 (index 0)
                if beat_index == 0:
                    events.append(
                        DrumEvent(
                            time_sec=beat_time,
                            drum_class="KICK",
                            velocity=100,
                        )
                    )

                # Snare auf Beat 2 und 4 (bei mindestens 4 Beats pro Takt)
                if int(beats_per_bar) >= 4 and beat_index in (1, 3):
                    events.append(
                        DrumEvent(
                            time_sec=beat_time,
                            drum_class="SNARE",
                            velocity=95,
                        )
                    )

                # Hi-Hat Closed auf jeden Beat
                events.append(
                    DrumEvent(
                        time_sec=beat_time,
                        drum_class="HH_CLOSED",
                        velocity=80,
                    )
                )

                # Ghostnotes auf den "Offbeats" (z. B. zwischen Beat 2 und 3)
                if (
                    self.ghostnote_probability > 0.0
                    and int(beats_per_bar) >= 4
                ):
                    offbeat_time = beat_time + 0.5 * seconds_per_beat
                    if offbeat_time < (bar_start + seconds_per_bar):
                        if random.random() < self.ghostnote_probability:
                            events.append(
                                DrumEvent(
                                    time_sec=offbeat_time,
                                    drum_class="SNARE",
                                    velocity=60,  # leiser = Ghostnote
                                )
                            )

        return events

    def generate_fill(
        self,
        song_specification: SongSpecification,
        start_bar: int,
        number_of_bars: int,
    ) -> List[DrumEvent]:
        """Erstellt Drum-Fills für einen bestimmten Abschnitt.

        Beschreibung:
            Erstellt gezielt Drum-Fills für einen bestimmten Abschnitt
            (z. B. Takte 7–8) und gibt sie als eigene Event-Liste zurück.

            Vereinfachtes Fill:
                - Pro Takt Toms auf jedem Beat (Low/Mid/High rotiert)
                - Am Ende des letzten Takts ein Crash

            Hinweis:
                start_bar wird 0-basiert interpretiert (0 = erster Takt).

        Args:
            song_specification: Spezifikation des Songs.
            start_bar: Starttakt des Fills (0-basiert).
            number_of_bars: Anzahl der Takte, die als Fill dienen sollen.

        Returns:
            Liste von DrumEvent-Objekten, die das Fill repräsentieren.
        """
        beats_per_bar, seconds_per_beat, seconds_per_bar = self._compute_timing(
            song_specification
        )

        events: List[DrumEvent] = []
        tom_cycle = ["TOM_LOW", "TOM_MID", "TOM_HIGH"]

        for local_bar in range(number_of_bars):
            global_bar = start_bar + local_bar
            bar_start = global_bar * seconds_per_bar

            for beat_index in range(int(beats_per_bar)):
                beat_time = bar_start + beat_index * seconds_per_beat
                drum_class = tom_cycle[(local_bar + beat_index) % len(tom_cycle)]
                events.append(
                    DrumEvent(
                        time_sec=beat_time,
                        drum_class=drum_class,
                        velocity=100,
                    )
                )

        # Crash auf der "1" nach dem Fill-Ende
        end_bar_start = (start_bar + number_of_bars) * seconds_per_bar
        events.append(
            DrumEvent(
                time_sec=end_bar_start,
                drum_class="CRASH",
                velocity=110,
            )
        )

        return events

    def humanize_timing(self, events: List[DrumEvent]) -> List[DrumEvent]:
        """Humanisiert das Timing der Drum-Events.

        Beschreibung:
            Verschiebt die exakten Zeiten der Drum-Events minimal, um ein
            menschlicheres Timing zu simulieren.

            Vereinfachung:
                Die Verschiebung ist zufällig in einem kleinen Bereich um 0,
                wobei swing_amount als grober Faktor für die maximale Abweichung dient.

        Args:
            events: Liste von DrumEvent-Objekten, deren Timing humanisiert
                werden soll.

        Returns:
            Neue Liste von DrumEvent-Objekten mit leicht verändertem Timing.
        """
        if self.swing_amount <= 0.0:
            # Keine Humanisierung, einfach Kopie zurückgeben
            return [DrumEvent(e.time_sec, e.drum_class, e.velocity) for e in events]

        # Maximaler Shift in Sekunden (heuristisch, nicht physikalisch korrekt)
        max_shift = 0.02 * self.swing_amount  # bis zu ca. 20 ms * swing_amount

        humanized: List[DrumEvent] = []
        for e in events:
            shift = random.uniform(-max_shift, max_shift)
            new_time = max(0.0, e.time_sec + shift)
            humanized.append(
                DrumEvent(
                    time_sec=new_time,
                    drum_class=e.drum_class,
                    velocity=e.velocity,
                )
            )
        return humanized

    def humanize_velocity(self, events: List[DrumEvent]) -> List[DrumEvent]:
        """Humanisiert die Anschlagstärke der Drum-Events.

        Beschreibung:
            Verändert die Anschlagstärken der Drum-Events leicht, damit es
            nicht wie eine starre Drum-Maschine klingt.

            Vereinfachung:
                Die Velocity wird um einen kleinen, zufälligen Betrag skaliert
                und auf den gültigen MIDI-Bereich [1, 127] geclipped.

        Args:
            events: Liste von DrumEvent-Objekten, deren Velocity angepasst
                werden soll.

        Returns:
            Neue Liste von DrumEvent-Objekten mit humanisierter Velocity.
        """
        if self.complexity <= 0.0:
            # Keine Humanisierung, einfach Kopie zurückgeben
            return [DrumEvent(e.time_sec, e.drum_class, e.velocity) for e in events]

        # Schwankungsbereich: ±15 % der ursprünglichen Velocity
        max_factor_delta = 0.15

        humanized: List[DrumEvent] = []
        for e in events:
            factor = 1.0 + random.uniform(-max_factor_delta, max_factor_delta)
            new_vel = int(round(e.velocity * factor))
            new_vel = max(1, min(127, new_vel))
            humanized.append(
                DrumEvent(
                    time_sec=e.time_sec,
                    drum_class=e.drum_class,
                    velocity=new_vel,
                )
            )
        return humanized


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für DrumPatternGenerator
# ---------------------------------------------------------------------------

def _create_example_drum_mapping() -> DrumMapping:
    """Erzeugt eine DrumMapping-Instanz mit allen relevanten Drum-Klassen."""
    note_to_class = {
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


def _create_test_band_configuration_for_drums() -> BandConfiguration:
    """Erzeugt eine einfache BandConfiguration für Drum-Tests."""
    dm = _create_example_drum_mapping()
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
    ]
    return BandConfiguration(
        drum_channel=9,
        drum_mapping=dm,
        instruments=instruments,
    )


def _create_example_song_spec_for_drums() -> SongSpecification:
    """Erzeugt eine einfache SongSpecification für Drum-Tests."""
    band_conf = _create_test_band_configuration_for_drums()
    return SongSpecification(
        song_identifier="song_drum_test",
        tempo_bpm=120.0,
        time_signature=(4, 4),
        number_of_bars=8,
        key="C major",
        style="pop_straight",
        band_configuration=band_conf,
        random_seed=123,
    )


def test_generate_drum_track_basic() -> None:
    """Testet, ob generate_drum_track grundlegend funktioniert."""
    print("[TEST] test_generate_drum_track_basic gestartet …")
    song_spec = _create_example_song_spec_for_drums()
    drum_mapping = song_spec.band_configuration.drum_mapping

    random.seed(42)
    generator = DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=0.5,
        ghostnote_probability=0.2,
        fill_probability=0.3,
        swing_amount=0.1,
    )

    events = generator.generate_drum_track(song_spec)

    print(f"  - Anzahl erzeugter DrumEvents: {len(events)}")
    assert len(events) > 0, "Es sollten DrumEvents erzeugt werden."

    # Sicherstellen, dass KICK, SNARE und HH_CLOSED vorkommen
    classes = {e.drum_class for e in events}
    print(f"  - Enthaltene Drum-Klassen: {classes}")
    assert "KICK" in classes
    assert "SNARE" in classes
    assert "HH_CLOSED" in classes

    # Zeitbereich prüfen
    max_time = max(e.time_sec for e in events)
    expected_duration = song_spec.get_duration_seconds()
    print(f"  - Max time: {max_time}, erwartete Songdauer: {expected_duration}")
    assert 0.0 <= max_time <= expected_duration + 0.5

    print("[TEST] test_generate_drum_track_basic erfolgreich abgeschlossen.\n")


def test_generate_fill_within_range() -> None:
    """Testet, ob generate_fill Events im erwarteten Zeitbereich erzeugt."""
    print("[TEST] test_generate_fill_within_range gestartet …")
    song_spec = _create_example_song_spec_for_drums()
    drum_mapping = song_spec.band_configuration.drum_mapping

    random.seed(7)
    generator = DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=0.5,
        ghostnote_probability=0.0,
        fill_probability=0.0,
        swing_amount=0.0,
    )

    start_bar = 4
    number_of_bars = 2
    events = generator.generate_fill(song_spec, start_bar=start_bar, number_of_bars=number_of_bars)

    print(f"  - Anzahl Fill-Events: {len(events)}")
    assert len(events) > 0, "Fill sollte Events erzeugen."

    beats_per_bar, seconds_per_beat, seconds_per_bar = generator._compute_timing(song_spec)

    fill_start_time = start_bar * seconds_per_bar
    fill_end_time = (start_bar + number_of_bars) * seconds_per_bar

    times = [e.time_sec for e in events]
    print(f"  - Zeitbereich Fill: min={min(times)}, max={max(times)}")
    print(f"  - Erwarteter Fill-Bereich: [{fill_start_time}, {fill_end_time}] "
          f"+ Crash auf {fill_end_time}")

    # Alle Tom-Events im Bereich [fill_start_time, fill_end_time)
    tom_events = [e for e in events if e.drum_class.startswith("TOM")]
    for e in tom_events:
        assert fill_start_time <= e.time_sec < fill_end_time

    # Crash muss exakt am Ende des Fills liegen
    crash_events = [e for e in events if e.drum_class == "CRASH"]
    assert len(crash_events) == 1
    assert abs(crash_events[0].time_sec - fill_end_time) < 1e-6

    print("[TEST] test_generate_fill_within_range erfolgreich abgeschlossen.\n")


def test_humanize_timing_changes_times_but_not_classes() -> None:
    """Testet, ob humanize_timing Zeiten verändert, aber Klassen beibehält."""
    print("[TEST] test_humanize_timing_changes_times_but_not_classes gestartet …")
    events = [
        DrumEvent(time_sec=1.0, drum_class="KICK", velocity=100),
        DrumEvent(time_sec=1.5, drum_class="SNARE", velocity=95),
        DrumEvent(time_sec=2.0, drum_class="HH_CLOSED", velocity=80),
    ]

    drum_mapping = _create_example_drum_mapping()
    random.seed(123)
    generator = DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=0.5,
        ghostnote_probability=0.0,
        fill_probability=0.0,
        swing_amount=0.5,
    )

    humanized = generator.humanize_timing(events)

    original_times = [e.time_sec for e in events]
    new_times = [e.time_sec for e in humanized]
    print(f"  - Originalzeiten: {original_times}")
    print(f"  - Humanized-Zeiten: {new_times}")

    assert len(humanized) == len(events)
    assert [e.drum_class for e in humanized] == [e.drum_class for e in events]

    # Mindestens eine Zeit sollte sich verändert haben
    assert any(o != n for o, n in zip(original_times, new_times))

    print("[TEST] test_humanize_timing_changes_times_but_not_classes erfolgreich abgeschlossen.\n")


def test_humanize_velocity_changes_values_and_stays_in_range() -> None:
    """Testet, ob humanize_velocity Velocity-Werte ändert und im gültigen Bereich hält."""
    print("[TEST] test_humanize_velocity_changes_values_and_stays_in_range gestartet …")
    events = [
        DrumEvent(time_sec=1.0, drum_class="KICK", velocity=100),
        DrumEvent(time_sec=1.5, drum_class="SNARE", velocity=90),
        DrumEvent(time_sec=2.0, drum_class="HH_CLOSED", velocity=80),
    ]

    drum_mapping = _create_example_drum_mapping()
    random.seed(999)
    generator = DrumPatternGenerator(
        drum_mapping=drum_mapping,
        complexity=1.0,
        ghostnote_probability=0.0,
        fill_probability=0.0,
        swing_amount=0.0,
    )

    humanized = generator.humanize_velocity(events)

    original_velocities = [e.velocity for e in events]
    new_velocities = [e.velocity for e in humanized]
    print(f"  - Original-Velocities: {original_velocities}")
    print(f"  - Humanized-Velocities: {new_velocities}")

    assert len(humanized) == len(events)
    # Werte müssen im gültigen Bereich [1, 127] liegen
    assert all(1 <= v <= 127 for v in new_velocities)

    # Mindestens eine Velocity sollte sich verändert haben
    assert any(o != n for o, n in zip(original_velocities, new_velocities))

    print("[TEST] test_humanize_velocity_changes_values_and_stays_in_range erfolgreich abgeschlossen.\n")


def run_all_drum_pattern_generator_tests() -> None:
    """Führt alle Tests für DrumPatternGenerator aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte DrumPatternGenerator-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_generate_drum_track_basic,
        test_generate_fill_within_range,
        test_humanize_timing_changes_times_but_not_classes,
        test_humanize_velocity_changes_values_and_stays_in_range,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle DrumPatternGenerator-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_drum_pattern_generator_tests()
