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


# ---------------------------------------------------------------------------
# Test-Helfer und Testfunktionen für AudioRenderer
# ---------------------------------------------------------------------------

def _create_noop_renderer() -> AudioRenderer:
    """Erzeugt einen AudioRenderer mit 'noop'-Backend für Tests."""
    print("\n[SETUP] Erzeuge AudioRenderer mit Backend='noop' für Tests …")
    renderer = AudioRenderer(
        soundfont_path="dummy.sf2",
        output_sample_rate=16000,
        render_backend="noop",
    )
    print(
        f"[SETUP] AudioRenderer(soundfont_path={renderer.soundfont_path!r}, "
        f"output_sample_rate={renderer.output_sample_rate}, "
        f"render_backend={renderer.render_backend!r})"
    )
    return renderer


def test_render_midi_to_wav_creates_file() -> None:
    """Testet, ob render_midi_to_wav eine Datei erzeugt (noop-Backend)."""
    print("[TEST] test_render_midi_to_wav_creates_file gestartet …")
    renderer = _create_noop_renderer()

    midi_path = "dummy_input.mid"
    output_wav_path = "test_output_single.wav"

    # Dummy-MIDI-Datei anlegen (Inhalt ist egal, da noop-Backend nur die Datei erstellt)
    with open(midi_path, "wb") as f:
        f.write(b"dummy midi content")

    # falls schon vorhanden, löschen
    if os.path.exists(output_wav_path):
        os.remove(output_wav_path)

    renderer.render_midi_to_wav(midi_path=midi_path, output_wav_path=output_wav_path)

    print(f"  - Existiert {output_wav_path}: {os.path.exists(output_wav_path)}")
    assert os.path.exists(output_wav_path), "WAV-Datei wurde nicht erzeugt."

    size = os.path.getsize(output_wav_path)
    print(f"  - Dateigröße von {output_wav_path}: {size} Bytes")
    # Bei noop ist eine leere Datei ok, wichtig ist: sie existiert.

    # Aufräumen
    os.remove(midi_path)
    os.remove(output_wav_path)

    print("[TEST] test_render_midi_to_wav_creates_file erfolgreich abgeschlossen.\n")


def test_render_midi_to_wav_unsupported_backend_raises() -> None:
    """Testet, ob ein nicht unterstütztes Backend einen NotImplementedError wirft."""
    print("[TEST] test_render_midi_to_wav_unsupported_backend_raises gestartet …")
    renderer = AudioRenderer(
        soundfont_path="dummy.sf2",
        output_sample_rate=16000,
        render_backend="fluidsynth",  # aktuell nicht implementiert
    )

    midi_path = "dummy_input.mid"
    output_wav_path = "test_output_unsupported_backend.wav"

    with open(midi_path, "wb") as f:
        f.write(b"dummy midi content")

    try:
        renderer.render_midi_to_wav(midi_path=midi_path, output_wav_path=output_wav_path)
    except NotImplementedError as e:
        print(f"  - Erwarteter Fehler gefangen: {e}")
    else:
        # Wenn kein Fehler geworfen wird, ist das ein Testfehler
        raise AssertionError(
            "Es wurde kein NotImplementedError für ein nicht unterstütztes Backend geworfen."
        )
    finally:
        if os.path.exists(midi_path):
            os.remove(midi_path)
        if os.path.exists(output_wav_path):
            os.remove(output_wav_path)

    print("[TEST] test_render_midi_to_wav_unsupported_backend_raises erfolgreich abgeschlossen.\n")


def test_render_with_mix_variants_creates_multiple_files() -> None:
    """Testet, ob render_with_mix_variants mehrere Dateien mit korrekten Namen erzeugt."""
    print("[TEST] test_render_with_mix_variants_creates_multiple_files gestartet …")
    renderer = _create_noop_renderer()

    midi_path = "dummy_input.mid"
    with open(midi_path, "wb") as f:
        f.write(b"dummy midi content")

    output_prefix = "test_mix"
    gains = [6.0, 0.0, -6.0]

    # Vorher evtl. vorhandene Dateien löschen
    expected_paths = [
        f"{output_prefix}_drums_plus6dB.wav",
        f"{output_prefix}_drums_0dB.wav",
        f"{output_prefix}_drums_minus6dB.wav",
    ]
    for p in expected_paths:
        if os.path.exists(p):
            os.remove(p)

    result_paths = renderer.render_with_mix_variants(
        midi_path=midi_path,
        output_prefix=output_prefix,
        drum_gain_db=gains,
    )

    print(f"  - Erwartete Pfade: {expected_paths}")
    print(f"  - Zurückgegebene Pfade: {result_paths}")

    assert result_paths == expected_paths, "Die zurückgegebenen Pfade stimmen nicht mit den erwarteten überein."

    for p in result_paths:
        print(f"  - Existiert {p}: {os.path.exists(p)}")
        assert os.path.exists(p), f"Datei {p} wurde nicht erzeugt."

    # Aufräumen
    os.remove(midi_path)
    for p in result_paths:
        os.remove(p)

    print("[TEST] test_render_with_mix_variants_creates_multiple_files erfolgreich abgeschlossen.\n")


def run_all_audio_renderer_tests() -> None:
    """Führt alle Tests für AudioRenderer aus und gibt eine Zusammenfassung aus."""
    print("============================================================")
    print("Starte AudioRenderer-Test-Suite …")
    print("============================================================\n")

    tests = [
        test_render_midi_to_wav_creates_file,
        test_render_midi_to_wav_unsupported_backend_raises,
        test_render_with_mix_variants_creates_multiple_files,
    ]

    for test_func in tests:
        print(f"[RUN] {test_func.__name__} wird ausgeführt …")
        test_func()

    print("============================================================")
    print("Alle AudioRenderer-Tests wurden erfolgreich ausgeführt.")
    print("============================================================")


if __name__ == "__main__":
    run_all_audio_renderer_tests()
