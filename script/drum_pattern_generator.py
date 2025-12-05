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


