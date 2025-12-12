# python inspect_npy.py

from __future__ import annotations

import numpy as np

PATH = r"data\synthetic_drums_dataset_test_1\notes\0001_C-major_pop-straight_Inst8_BPM120_Seed1235_notes.npy"
# oder note_events:
# PATH = r"data/synthetic_drums_yourmt3_16k/note_events/<DEIN_FILE>_note_events.npy"

obj = np.load(PATH, allow_pickle=True)

print("type:", type(obj))
print("shape:", getattr(obj, "shape", None))
print("dtype:", getattr(obj, "dtype", None))

data = obj.item()  # weil wir ein dict gespeichert haben
print("keys:", list(data.keys()))

# Beispiel: Notes anzeigen (die ersten 5)
if "notes" in data:
    notes = data["notes"]
    print("notes count:", len(notes))
    for n in notes[:5]:
        print(n)

# Beispiel: NoteEvents anzeigen (die ersten 10)
if "note_events" in data:
    ne = data["note_events"]
    # je nach Format: Liste oder verschachtelt
    if isinstance(ne, list) and len(ne) > 0 and isinstance(ne[0], list):
        flat = ne[0]
    else:
        flat = ne
    print("note_events count:", len(flat))
    for e in flat[:10]:
        print(e)
