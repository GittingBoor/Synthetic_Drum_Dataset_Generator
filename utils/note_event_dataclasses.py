# utils/note_event_dataclasses.py
import sys
import importlib
from dataclasses import dataclass, field
from typing import Set, List, Optional

if sys.version_info >= (3, 8):
    typing_module = importlib.import_module("typing")
else:
    typing_module = importlib.import_module("typing_extensions")

TypedDict = typing_module.TypedDict


@dataclass
class Note:
    is_drum: bool
    program: int  # MIDI program number (0-127), 128 for drum in YourMT3 convention
    onset: float  # onset time in seconds
    offset: float  # offset time in seconds
    pitch: int  # MIDI note number (0-127)
    velocity: int  # (0-1) if binary velocity, otherwise (0-127)


@dataclass
class NoteEvent:
    is_drum: bool
    program: int  # [0, 127], 128 for drum but ignored in tokenizer
    time: Optional[float]  # absolute time. allow None for tie note events
    velocity: int  # 1 for onset, 0 for offset; drum typically has no offset
    pitch: int  # MIDI pitch
    activity: Optional[Set[int]] = field(default_factory=set)

    def equals_except(self, note_event, *excluded_attrs) -> bool:
        if not isinstance(note_event, NoteEvent):
            return False
        for attr, value in self.__dict__.items():
            if attr not in excluded_attrs and value != note_event.__dict__.get(attr):
                return False
        return True

    def equals_only(self, note_event, *included_attrs) -> bool:
        if not isinstance(note_event, NoteEvent):
            return False
        for attr in included_attrs:
            if self.__dict__.get(attr) != note_event.__dict__.get(attr):
                return False
        return True


class NoteEventListsBundle(TypedDict):
    note_events: List[List[NoteEvent]]
    tie_note_events: List[List[NoteEvent]]
    start_times: List[float]
