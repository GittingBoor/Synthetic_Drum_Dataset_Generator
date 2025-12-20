from __future__ import annotations

import ctypes
import os
from ctypes.util import find_library
from typing import Optional
import pretty_midi
import soundfile as sf

_FS_NOOP_CB = None

def _load_fluidsynth_library() -> Optional[ctypes.CDLL]:
    candidates: list[str] = []

    # Conda: bevorzugt direkt aus dem Env laden
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        candidates.extend(
            [
                os.path.join(conda_prefix, "lib", "libfluidsynth.so.3"),
                os.path.join(conda_prefix, "lib", "libfluidsynth.so.2"),
                os.path.join(conda_prefix, "lib", "libfluidsynth.so"),
            ]
        )

    # Linux generische Namen
    candidates.extend(["libfluidsynth.so.3", "libfluidsynth.so.2", "libfluidsynth.so"])

    # Windows (falls du es auch dort weiter nutzen willst)
    candidates.extend(
        [
            "libfluidsynth-3.dll",
            "libfluidsynth-2.dll",
            "libfluidsynth.dll",
            "fluidsynth.dll",
        ]
    )

    # system lookup
    found = find_library("fluidsynth")
    if found:
        candidates.append(found)

    for name in candidates:
        try:
            return ctypes.CDLL(name)
        except OSError:
            continue

    return None


def _disable_fluidsynth_warnings() -> None:
    """Schaltet FluidSynth-Logs auf WARN/INFO/DBG stumm (plattformübergreifend)."""
    global _FS_NOOP_CB

    try:
        lib = _load_fluidsynth_library()
        if lib is None:
            return

        # log levels (fluidsynth)
        FLUID_WARN = 2
        FLUID_INFO = 3
        FLUID_DBG = 4

        # callback signature: void (*)(int level, const char* message, void* data)
        CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)

        def _noop(_level: int, _message: bytes, _data: ctypes.c_void_p) -> None:
            return

        _FS_NOOP_CB = CALLBACK(_noop)

        lib.fluid_set_log_function.argtypes = (ctypes.c_int, CALLBACK, ctypes.c_void_p)
        lib.fluid_set_log_function.restype = ctypes.c_void_p

        for level in (FLUID_WARN, FLUID_INFO, FLUID_DBG):
            lib.fluid_set_log_function(level, _FS_NOOP_CB, None)

    except Exception:
        return

class AudioRenderer:
    """Rendert MIDI-Dateien zu Audiodateien (z. B. WAV).

    Verantwortung:
        AudioRenderer konvertiert eine MIDI-Datei in eine Audiodatei (z. B. WAV),
        meist über Soundfonts oder eine externe Rendering-Engine.
        Er ist also die Brücke zwischen symbolischen Daten (MIDI) und dem Signal,
        das das Modell wirklich hören wird.
        Außerdem kann er verschiedene Mix-Varianten erzeugen (z. B. Drums lauter
        oder leiser), um das Training robuster zu machen.
    """

    def __init__(
            self,
            soundfont_path: str,
            output_sample_rate: int,
            render_backend: str,
    ) -> None:
        """Konstruktor für den AudioRenderer.

        Args:
            soundfont_path: Pfad zu einer Soundfont-Datei (z. B. GeneralUser.sf2).
            output_sample_rate: Samplerate der gerenderten Audiodateien
                (z. B. 16000 oder 44100).
            render_backend: Name des Rendering-Backends
                (z. B. "fluidsynth", wird aktuell nur als Info gespeichert).
        """
        self.soundfont_path = soundfont_path
        self.output_sample_rate = output_sample_rate
        self.render_backend = render_backend
        _disable_fluidsynth_warnings()

    def render_midi_to_wav(self, midi_path: str, output_wav_path: str) -> None:
        directory = os.path.dirname(output_wav_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        if not os.path.exists(self.soundfont_path):
            raise FileNotFoundError(
                f"Soundfont {self.soundfont_path!r} wurde nicht gefunden. "
                "Passe den Pfad in deiner Konfiguration an."
            )

        _disable_fluidsynth_warnings()

        pm = pretty_midi.PrettyMIDI(midi_path)

        audio = pm.fluidsynth(
            fs=self.output_sample_rate,
            sf2_path=self.soundfont_path,
        )

        # Enforce mono
        if hasattr(audio, "ndim") and audio.ndim == 2:
            audio = audio.mean(axis=1)

        sf.write(output_wav_path, audio, self.output_sample_rate)

