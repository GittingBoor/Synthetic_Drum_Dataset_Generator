from __future__ import annotations

from typing import List
import os

import pretty_midi
import soundfile as sf


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
        self.soundfont_path: str = soundfont_path
        self.output_sample_rate: int = int(output_sample_rate)
        self.render_backend: str = render_backend

    def render_midi_to_wav(self, midi_path: str, output_wav_path: str) -> None:
        """Rendert eine einzelne MIDI-Datei in eine WAV-Datei.

        Beschreibung:
            Lädt die MIDI-Datei mit pretty_midi, rendert sie über fluidsynth
            mit der angegebenen Soundfont und speichert das Ergebnis als WAV.

        Args:
            midi_path: Pfad zur Eingabe-MIDI-Datei.
            output_wav_path: Pfad zur zu erzeugenden WAV-Datei.
        """
        # Ordner anlegen, falls nötig
        directory = os.path.dirname(output_wav_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Safety: existiert die Soundfont?
        if not os.path.exists(self.soundfont_path):
            raise FileNotFoundError(
                f"Soundfont {self.soundfont_path!r} wurde nicht gefunden. "
                "Passe den Pfad in deiner Konfiguration an."
            )

        # MIDI laden
        pm = pretty_midi.PrettyMIDI(midi_path)

        # Audio über fluidsynth rendern (mono oder stereo, returns numpy array)
        audio = pm.fluidsynth(
            fs=self.output_sample_rate,
            sf2_path=self.soundfont_path,
        )

        # WAV schreiben
        sf.write(output_wav_path, audio, self.output_sample_rate)

    def render_with_mix_variants(
        self,
        midi_path: str,
        output_prefix: str,
        drum_gain_db: List[float],
    ) -> List[str]:
        """Rendert mehrere Mix-Varianten eines Songs.

        Aktuelle einfache Implementierung:
            - Rendert für jeden Gain-Wert eine eigene Datei.
            - Die Gain-Werte werden noch NICHT wirklich im Mix angewandt
              (du bekommst identische Audios mit unterschiedlichen Dateinamen).
            - Später kannst du hier z. B. per separatem Drum-Bus o. Ä. arbeiten.

        Args:
            midi_path: Pfad zur Eingabe-MIDI-Datei.
            output_prefix: Präfix für die Ausgabedateien.
            drum_gain_db: Liste von Drum-Gain-Werten in dB.

        Returns:
            Liste der Pfade zu den erzeugten Audiodateien.
        """
        output_paths: List[str] = []

        for gain in drum_gain_db:
            gain_int = int(round(gain))
            if gain_int > 0:
                gain_tag = f"plus{gain_int}dB"
            elif gain_int < 0:
                gain_tag = f"minus{abs(gain_int)}dB"
            else:
                gain_tag = "0dB"

            output_wav_path = f"{output_prefix}_drums_{gain_tag}.wav"

            # TODO: Gain wirklich im Mix anwenden.
            # Aktuell: einfach normal rendern.
            self.render_midi_to_wav(midi_path=midi_path, output_wav_path=output_wav_path)
            output_paths.append(output_wav_path)

        return output_paths



