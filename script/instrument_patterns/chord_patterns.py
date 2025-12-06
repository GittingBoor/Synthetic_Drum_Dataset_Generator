from typing import Dict, List, Tuple

# (offset_in_quarters, duration_in_quarters, mode)
ChordPatternEvent = Tuple[float, float, str]
ChordPattern = List[ChordPatternEvent]

CHORD_PATTERNS_BY_ROLE: Dict[str, List[ChordPattern]] = {
    # ------------------------------------------------------------
    # Piano: block chords, etwas Synkope & leichte Arpeggios
    # ------------------------------------------------------------
    "piano": [
        # Pattern 1: ganzer Akkord auf 1 (Ganznote)
        [(0.0, 4.0, "block")],

        # Pattern 2: zweimal pro Takt auf 1 und 3
        [(0.0, 2.0, "block"),
         (2.0, 2.0, "block")],

        # Pattern 3: leichte Synkope (1, 2+, 3)
        [(0.0, 1.0, "block"),
         (1.5, 0.5, "block"),
         (2.0, 1.0, "block")],

        # Pattern 4: erste Takt-Hälfte Arpeggio, zweite Hälfte Blockchord
        [(0.0, 2.0, "arp_up"),
         (2.0, 2.0, "block")],

        # Pattern 5: dezentes „Top-Note“-Comping über den ganzen Takt
        # (Piano spielt nur die Oberstimme als Puls)
        [(0.5, 3.5, "top_pulse")],
    ],

    # ------------------------------------------------------------
    # Gitarre: Arpeggios + Offbeat-Comping, eher rhythmisch
    # ------------------------------------------------------------
    "guitar": [
        # Pattern 1: ganzer Takt 8tel-Arpeggio (sehr lebendig)
        [(0.0, 4.0, "arp_up")],

        # Pattern 2: erste Hälfte Arpeggio, zweite Hälfte Offbeat-Stabs
        [(0.0, 2.0, "arp_up"),
         (2.5, 0.5, "block"),
         (3.5, 0.5, "block")],

        # Pattern 3: Schlag auf 1, dann Arpeggio im Rest des Taktes
        [(0.0, 1.0, "block"),
         (1.0, 3.0, "arp_up")],

        # Pattern 4: „funkiger“ Comping-Takt, viele Offbeats, kurze Stabs
        [(0.5, 0.5, "block"),
         (1.0, 0.5, "block"),
         (2.0, 0.5, "block"),
         (2.5, 0.5, "block"),
         (3.5, 0.5, "block")],

        # Pattern 5: Arpeggio nach unten über den ganzen Takt
        [(0.0, 4.0, "arp_down")],

        # Pattern 6: nur die Oberstimme als rhythmische Achtel-Pulse
        [(0.0, 4.0, "top_pulse")],
    ],

    # ------------------------------------------------------------
    # Orgel: überwiegend gehaltene Akkorde, dezente Bewegung
    # ------------------------------------------------------------
    "organ": [
        # Pattern 1: Ganznote
        [(0.0, 4.0, "block")],

        # Pattern 2: zwei halbe Noten (1 und 3)
        [(0.0, 2.0, "block"),
         (2.0, 2.0, "block")],

        # Pattern 3: vier Viertel-Stabs (klassischer Orgel-Teppich mit leichter Bewegung)
        [(0.0, 1.0, "block"),
         (1.0, 1.0, "block"),
         (2.0, 1.0, "block"),
         (3.0, 1.0, "block")],

        # Pattern 4: langer Akkord, kleine Arpeggio-Verzierung am Ende
        [(0.0, 3.0, "block"),
         (3.0, 1.0, "arp_down")],

        # Pattern 5: sanfte Pulsierung der Oberstimme über den Takt
        [(0.0, 4.0, "top_pulse")],
    ],

    # ------------------------------------------------------------
    # Fallback für alles andere mit Rolle "chords"
    # (z. B. Strings, Pads, andere Keys)
    # ------------------------------------------------------------
    "default": [
        # Pattern 1: klassischer Ganzton-Akkord
        [(0.0, 4.0, "block")],

        # Pattern 2: zwei halbe Akkorde (1 und 3)
        [(0.0, 2.0, "block"),
         (2.0, 2.0, "block")],

        # Pattern 3: synkopierter Takt (1, 2+, 3)
        [(0.0, 1.0, "block"),
         (1.5, 0.5, "block"),
         (2.0, 1.0, "block")],

        # Pattern 4: sanftes Arpeggio über den ganzen Takt
        [(0.0, 4.0, "arp_up")],

        # Pattern 5: block chord am Anfang, danach nur Oberstimme pulsierend
        [(0.0, 1.0, "block"),
         (1.0, 3.0, "top_pulse")],
    ],
}
