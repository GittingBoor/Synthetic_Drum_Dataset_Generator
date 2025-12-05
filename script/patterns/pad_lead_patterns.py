from typing import Dict, List, Tuple

# ------------------------------------------------------------
# Pads
# ------------------------------------------------------------

# (offset_in_quarters, duration_in_quarters, mode)
# mode ∈ {"pad_sustain", "pad_half", "pad_swell", "pad_pulse"}
PadPatternEvent = Tuple[float, float, str]
PadPattern = List[PadPatternEvent]

PAD_PATTERNS_BY_INSTRUMENT: Dict[str, List[PadPattern]] = {
    # --------------------------------------------------------
    # String Ensemble 1 – eher breiter, orchestraler Teppich
    # --------------------------------------------------------
    "String Ensemble 1": [
        # Pattern 1: Ganzer Takt Sustains
        [(0.0, 4.0, "pad_sustain")],

        # Pattern 2: zwei Halbe (1 und 3)
        [(0.0, 2.0, "pad_half"),
         (2.0, 2.0, "pad_half")],

        # Pattern 3: später Swell ab 2+
        [(1.5, 2.5, "pad_swell")],

        # Pattern 4: Sustain, aber mit kurzem Puls am Anfang
        [(0.0, 0.5, "pad_pulse"),
         (0.5, 3.5, "pad_sustain")],

        # Pattern 5: Viertelweise leichte Pulsierung
        [(0.0, 1.0, "pad_pulse"),
         (1.0, 1.0, "pad_pulse"),
         (2.0, 2.0, "pad_sustain")],
    ],

    # --------------------------------------------------------
    # Synth Strings 1 – etwas moderner, etwas mehr Swells
    # --------------------------------------------------------
    "Synth Strings 1": [
        # Pattern 1: Sustains über den ganzen Takt
        [(0.0, 4.0, "pad_sustain")],

        # Pattern 2: späte Swells (ab 2+)
        [(1.5, 1.0, "pad_swell"),
         (2.5, 1.5, "pad_sustain")],

        # Pattern 3: Halbe + Swell
        [(0.0, 2.0, "pad_sustain"),
         (2.0, 1.0, "pad_swell"),
         (3.0, 1.0, "pad_sustain")],

        # Pattern 4: Puls auf 2+ und 4
        [(1.5, 0.5, "pad_pulse"),
         (3.0, 1.0, "pad_pulse")],

        # Pattern 5: Viertelweise kurze Swells
        [(0.0, 1.0, "pad_swell"),
         (1.0, 1.0, "pad_sustain"),
         (2.0, 1.0, "pad_swell"),
         (3.0, 1.0, "pad_sustain")],
    ],

    # --------------------------------------------------------
    # Fallback für andere Pad-Instrumente
    # --------------------------------------------------------
    "default": [
        [(0.0, 4.0, "pad_sustain")],
        [(0.0, 2.0, "pad_half"), (2.0, 2.0, "pad_half")],
        [(1.5, 2.5, "pad_swell")],
        [(0.0, 0.5, "pad_pulse"), (0.5, 3.5, "pad_sustain")],
        [(0.0, 1.0, "pad_sustain"),
         (1.0, 1.0, "pad_pulse"),
         (2.0, 2.0, "pad_sustain")],
    ],
}

# ------------------------------------------------------------
# Leads
# ------------------------------------------------------------

# (offset_in_quarters, duration_in_quarters, rel_scale_step)
# rel_scale_step: 0 = Stufe selbst, 2 = Sekunde drüber, -1 = Halbton drunter, etc.
LeadMotifEvent = Tuple[float, float, int]
LeadPattern = List[LeadMotifEvent]

LEAD_PATTERNS_BY_INSTRUMENT: Dict[str, List[LeadPattern]] = {
    # --------------------------------------------------------
    # Lead 1 (square) – eher simple „Game Lead“-Motive
    # --------------------------------------------------------
    "Lead 1 (square)": [
        # Pattern 1: 4-Noten-Motiv auf 1 in 8teln
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 0.5, 4),
         (1.5, 0.5, 2)],

        # Pattern 2: Start ab Beat 2
        [(1.0, 0.5, 0),
         (1.5, 0.5, 1),
         (2.0, 0.5, 2),
         (2.5, 0.5, 0)],

        # Pattern 3: Abwärts-Linie
        [(0.0, 0.5, 0),
         (0.5, 0.5, -1),
         (1.0, 0.5, -2),
         (1.5, 0.5, 0)],

        # Pattern 4: Langer Auftakt, dann kurze Antwort
        [(0.0, 1.0, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 4)],

        # Pattern 5: Zwei Töne, die sich wiederholen
        [(0.0, 0.5, 0),
         (0.5, 0.5, 3),
         (1.0, 0.5, 0),
         (1.5, 0.5, 3)],
    ],

    # --------------------------------------------------------
    # Lead 2 (sawtooth) – etwas aggressiver
    # --------------------------------------------------------
    "Lead 2 (sawtooth)": [
        # Pattern 1: durchgehende 8tel-Linie
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 0.5, 3),
         (1.5, 0.5, 5),
         (2.0, 0.5, 4),
         (2.5, 0.5, 2),
         (3.0, 0.5, 0),
         (3.5, 0.5, -1)],

        # Pattern 2: kurze, aufwärtsgerichtete Figur
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 0.5, 4),
         (1.5, 0.5, 7)],

        # Pattern 3: „Triller“-artige Figur um den Grundton
        [(0.0, 0.25, 0),
         (0.25, 0.25, 1),
         (0.5, 0.25, 0),
         (0.75, 0.25, -1),
         (1.0, 0.5, 0)],

        # Pattern 4: Offbeat-Motiv
        [(0.5, 0.5, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 4),
         (2.5, 0.5, 2)],

        # Pattern 5: Einfacher „Call“
        [(0.0, 1.0, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 0)],
    ],

    # --------------------------------------------------------
    # Trumpet – etwas melodischer
    # --------------------------------------------------------
    "Trumpet": [
        # Pattern 1: 4-Noten-Motiv mit Terz/Quarte
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 0.5, 4),
         (1.5, 0.5, 5)],

        # Pattern 2: längerer Ton, dann kleine Figur
        [(0.0, 1.0, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 4)],

        # Pattern 3: kleines Abwärts-Motiv
        [(0.0, 0.5, 4),
         (0.5, 0.5, 2),
         (1.0, 0.5, 0),
         (1.5, 0.5, -2)],

        # Pattern 4: Call auf 1, Response ab 3
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (3.0, 0.5, 4),
         (3.5, 0.5, 2)],

        # Pattern 5: kurz-kurz-lang
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 1.0, 4)],
    ],

    # --------------------------------------------------------
    # Alto Sax – etwas smoother
    # --------------------------------------------------------
    "Alto Sax": [
        # Pattern 1: weiche Aufwärtsfigur
        [(0.0, 0.5, 0),
         (0.5, 0.5, 1),
         (1.0, 0.5, 3),
         (1.5, 0.5, 5)],

        # Pattern 2: Nachschlag ab Beat 2
        [(1.0, 0.5, 0),
         (1.5, 0.5, 2),
         (2.0, 0.5, 3),
         (2.5, 0.5, 2)],

        # Pattern 3: „Nach unten seufzen“
        [(0.0, 0.5, 3),
         (0.5, 0.5, 2),
         (1.0, 0.5, 0),
         (1.5, 0.5, -1)],

        # Pattern 4: Call & Response in einem Takt
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (2.0, 0.5, 0),
         (2.5, 0.5, -2)],

        # Pattern 5: längerer Bogen
        [(0.0, 1.0, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 3)],
    ],

    # --------------------------------------------------------
    # Fallback für andere Leads
    # --------------------------------------------------------
    "default": [
        [(0.0, 0.5, 0),
         (0.5, 0.5, 2),
         (1.0, 0.5, 4),
         (1.5, 0.5, 2)],

        [(1.0, 0.5, 0),
         (1.5, 0.5, 1),
         (2.0, 0.5, 2),
         (2.5, 0.5, 0)],

        [(0.0, 0.5, 0),
         (0.5, 0.5, -1),
         (1.0, 0.5, -2),
         (1.5, 0.5, 0)],

        [(0.5, 0.5, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 4),
         (2.5, 0.5, 2)],

        [(0.0, 1.0, 0),
         (1.0, 0.5, 2),
         (1.5, 0.5, 0)],
    ],
}
