from typing import Dict, List, Tuple

# (offset_in_quarters, duration_in_quarters, function)
# function ∈ {"root", "fifth", "octave", "approach_next", "walk_up", "walk_down", "rest"}
BassPatternEvent = Tuple[float, float, str]
BassPattern = List[BassPatternEvent]


BASS_PATTERNS_BY_INSTRUMENT: Dict[str, List[BassPattern]] = {
    # ------------------------------------------------------------
    # Electric Bass (finger) – eher „solide“ und ruhig
    # ------------------------------------------------------------
    "Electric Bass (finger)": [
        # Pattern 1: einfache Root-Viertelnoten
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "root")],

        # Pattern 2: Root–Root–Fifth–Root
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "fifth"),
         (3.0, 1.0, "root")],

        # Pattern 3: Root–Fifth–Root–Octave
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "fifth"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "octave")],

        # Pattern 4: Root auf 1 und 3, Annäherung zum nächsten Akkord am Ende
        [(0.0, 2.0, "root"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "approach_next")],

        # Pattern 5: leichte 8tel-Bewegung mit Annäherung
        [(0.0, 0.5, "root"),
         (0.5, 0.5, "root"),
         (1.0, 1.0, "root"),
         (2.0, 0.5, "root"),
         (2.5, 0.5, "fifth"),
         (3.0, 0.5, "root"),
         (3.5, 0.5, "approach_next")],
    ],

    # ------------------------------------------------------------
    # Electric Bass (pick) – etwas „knackiger“, mehr Synkopen
    # ------------------------------------------------------------
    "Electric Bass (pick)": [
        # Pattern 1: Root-Viertel, aber mit Antizipation auf 4+
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "root"),
         (3.5, 0.5, "approach_next")],

        # Pattern 2: Root–Root–Fifth–Octave
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "fifth"),
         (3.0, 1.0, "octave")],

        # Pattern 3: 8tel-Groove: Root–Root–Fifth–Fifth
        [(0.0, 0.5, "root"),
         (0.5, 0.5, "root"),
         (1.0, 0.5, "fifth"),
         (1.5, 0.5, "fifth"),
         (2.0, 0.5, "root"),
         (2.5, 0.5, "root"),
         (3.0, 0.5, "fifth"),
         (3.5, 0.5, "approach_next")],

        # Pattern 4: Root auf 1, dann „Walking“-Art Richtung nächstem Akkord
        [(0.0, 1.0, "root"),
         (1.0, 0.5, "walk_up"),
         (1.5, 0.5, "walk_up"),
         (2.0, 0.5, "walk_up"),
         (2.5, 0.5, "walk_up"),
         (3.0, 0.5, "walk_up"),
         (3.5, 0.5, "approach_next")],

        # Pattern 5: Offbeat-Betonungen mit Quintensprüngen
        [(0.5, 0.5, "root"),
         (1.5, 0.5, "root"),
         (2.0, 0.5, "fifth"),
         (2.5, 0.5, "fifth"),
         (3.0, 0.5, "root"),
         (3.5, 0.5, "approach_next")],
    ],

    # ------------------------------------------------------------
    # Synth Bass 1 – moderner, mehr 8tel und Bewegung
    # ------------------------------------------------------------
    "Synth Bass 1": [
        # Pattern 1: durchgehende 8tel-Root
        [(0.0, 0.5, "root"),
         (0.5, 0.5, "root"),
         (1.0, 0.5, "root"),
         (1.5, 0.5, "root"),
         (2.0, 0.5, "root"),
         (2.5, 0.5, "root"),
         (3.0, 0.5, "root"),
         (3.5, 0.5, "root")],

        # Pattern 2: Root/Fifth-Oszillation
        [(0.0, 0.5, "root"),
         (0.5, 0.5, "fifth"),
         (1.0, 0.5, "root"),
         (1.5, 0.5, "fifth"),
         (2.0, 0.5, "root"),
         (2.5, 0.5, "fifth"),
         (3.0, 0.5, "root"),
         (3.5, 0.5, "approach_next")],

        # Pattern 3: Root–Fifth–Octave-Lick
        [(0.0, 1.0, "root"),
         (1.0, 0.5, "fifth"),
         (1.5, 0.5, "octave"),
         (2.0, 0.5, "fifth"),
         (2.5, 0.5, "root"),
         (3.0, 1.0, "approach_next")],

        # Pattern 4: Walking-Style hoch
        [(0.0, 0.5, "walk_up"),
         (0.5, 0.5, "walk_up"),
         (1.0, 0.5, "walk_up"),
         (1.5, 0.5, "walk_up"),
         (2.0, 0.5, "walk_up"),
         (2.5, 0.5, "walk_up"),
         (3.0, 0.5, "walk_up"),
         (3.5, 0.5, "approach_next")],

        # Pattern 5: Walking-Style runter
        [(0.0, 0.5, "walk_down"),
         (0.5, 0.5, "walk_down"),
         (1.0, 0.5, "walk_down"),
         (1.5, 0.5, "walk_down"),
         (2.0, 0.5, "walk_down"),
         (2.5, 0.5, "walk_down"),
         (3.0, 0.5, "walk_down"),
         (3.5, 0.5, "approach_next")],
    ],

    # ------------------------------------------------------------
    # Synth Bass 2 – ähnlich, aber etwas „luftiger“
    # ------------------------------------------------------------
    "Synth Bass 2": [
        # Pattern 1: Root auf 1 & 3, 8tel-Fills dazwischen
        [(0.0, 1.0, "root"),
         (1.0, 0.5, "walk_up"),
         (1.5, 0.5, "walk_up"),
         (2.0, 1.0, "root"),
         (3.0, 0.5, "walk_up"),
         (3.5, 0.5, "approach_next")],

        # Pattern 2: Root–Fifth–Root–Fifth
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "fifth"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "fifth")],

        # Pattern 3: Root–Octave-Lick
        [(0.0, 0.5, "root"),
         (0.5, 0.5, "octave"),
         (1.0, 0.5, "root"),
         (1.5, 0.5, "octave"),
         (2.0, 0.5, "fifth"),
         (2.5, 0.5, "root"),
         (3.0, 0.5, "root"),
         (3.5, 0.5, "approach_next")],

        # Pattern 4: „LoFi“-Root mit langer Note und kurzem Fill
        [(0.0, 3.0, "root"),
         (3.0, 0.5, "walk_up"),
         (3.5, 0.5, "approach_next")],

        # Pattern 5: Offbeat-Root mit Approaches
        [(0.5, 0.5, "root"),
         (1.5, 0.5, "root"),
         (2.5, 0.5, "root"),
         (3.0, 0.5, "walk_up"),
         (3.5, 0.5, "approach_next")],
    ],

    # ------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------
    "default": [
        # ähnlich wie Finger-Bass, aber generischer
        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "fifth"),
         (3.0, 1.0, "root")],

        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "root")],

        [(0.0, 1.0, "root"),
         (1.0, 1.0, "fifth"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "octave")],

        [(0.0, 0.5, "root"),
         (0.5, 0.5, "root"),
         (1.0, 0.5, "fifth"),
         (1.5, 0.5, "fifth"),
         (2.0, 1.0, "root"),
         (3.0, 1.0, "approach_next")],

        [(0.0, 1.0, "root"),
         (1.0, 1.0, "root"),
         (2.0, 0.5, "walk_up"),
         (2.5, 0.5, "walk_up"),
         (3.0, 1.0, "approach_next")],
    ],
}
