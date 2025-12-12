from __future__ import annotations
from typing import Dict, Optional, List

from .song_specification import SongSpecification


class DatasetExample:
    """Repräsentiert ein einzelnes Beispiel im Datensatz.

    Verantwortung:
        DatasetExample repräsentiert ein einzelnes Beispiel im Datensatz,
        bestehend aus Audio, Labels und Metadaten.
        Damit hast du eine saubere Struktur, um jeden Clip im Dataset zu
        beschreiben.
        Diese Informationen können später in eine Index-Datei geschrieben werden,
        die deine Trainingspipeline nutzt.
    """

    def __init__(
        self,
        song_identifier: str,
        audio_path: str,
        label_path: str,
        midi_path: str,
        mix_variant: str,
        song_specification: SongSpecification,

        notes_npy_path: Optional[str] = None,
        note_events_npy_path: Optional[str] = None,
        n_frames: Optional[int] = None,
        program: Optional[List[int]] = None,
        is_drum: Optional[List[int]] = None,
    ) -> None:
        """Konstruktor für ein DatasetExample.

        Args:
            song_identifier: Bezeichner des Songs (z. B. "song_0001_pop_c_major").
            audio_path: Pfad zur zugehörigen Audiodatei.
            label_path: Pfad zur zugehörigen Label-Datei.
            midi_path: Pfad zur zugehörigen MIDI-Datei.
            mix_variant: Name der Mix-Variante (z. B. "drums_loud").
            song_specification: Ursprüngliche SongSpecification dieses Beispiels.
            notes_npy_path: Pfad zur notes-NumPy-Datei (YourMT3-kompatibel).
            note_events_npy_path: Pfad zur note_events-NumPy-Datei (YourMT3-kompatibel).
            n_frames: Anzahl Samples (Frames) der WAV-Datei bei 16 kHz.
            program: Liste der verwendeten Programme (GM 0-127, Drums=128).
            is_drum: Liste der Drum-Flags (0/1) passend zu program.
        """
        self.song_identifier = song_identifier
        self.audio_path = audio_path
        self.label_path = label_path
        self.midi_path = midi_path
        self.mix_variant = mix_variant
        self.song_specification = song_specification

        self.notes_npy_path = notes_npy_path
        self.note_events_npy_path = note_events_npy_path
        self.n_frames = n_frames
        self.program = program
        self.is_drum = is_drum

    def to_index_entry(self) -> Dict:
        """Erzeugt einen Dictionary-Eintrag für eine Index-Datei.

        Beschreibung:
            Erzeugt einen Dictionary-Eintrag mit allen nötigen Informationen
            (Pfaden, Metadaten), der in eine globale Index-Datei aufgenommen
            werden kann.

        Returns:
            Dictionary mit allen Informationen dieses DatasetExample.
        """
        spec = self.song_specification

        # Wir bauen hier bewusst ein eigenes Dict, statt spec.to_dict() aufzurufen,
        # damit das auch funktioniert, wenn z. B. band_configuration = None ist.
        song_spec_dict: Dict = {
            "song_identifier": getattr(spec, "song_identifier", None),
            "tempo_bpm": getattr(spec, "tempo_bpm", None),
            "time_signature": getattr(spec, "time_signature", None),
            "number_of_bars": getattr(spec, "number_of_bars", None),
            "key": getattr(spec, "key", None),
            "style": getattr(spec, "style", None),
            "random_seed": getattr(spec, "random_seed", None),
        }

        return {
            "song_identifier": self.song_identifier,
            "audio_path": self.audio_path,
            "label_path": self.label_path,
            "midi_path": self.midi_path,
            "mix_variant": self.mix_variant,

            "notes_npy_path": self.notes_npy_path,
            "note_events_npy_path": self.note_events_npy_path,
            "n_frames": self.n_frames,
            "program": self.program,
            "is_drum": self.is_drum,

            "song_specification": song_spec_dict,
        }
