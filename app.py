import time

import numpy as np
import sounddevice as sd
from rich import print


def get_audio_amplitude(duration=0.5, sample_rate=44100):
    try:
        recording = sd.rec(
            int(sample_rate * duration),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        return np.mean(np.abs(recording))
    except Exception:
        return 0


def amplitude_to_color(amplitude):
    """Maps audio amplitude to different RGB channels based on ranges."""
    scaled_amplitude = amplitude * 100  # Adjust scaling as needed

    if scaled_amplitude < 0.3:
        red = int(scaled_amplitude / 0.3 * 255)
        return red, 0, 0
    elif scaled_amplitude < 0.6:
        green = int((scaled_amplitude - 0.3) / 0.3 * 255)
        return 0, green, 0
    else:
        blue = int((scaled_amplitude - 0.6) / 0.4 * 255)
        return 0, 0, blue


def rgb_to_hex(rgb):
    """Converts an RGB tuple (0-255) to a hexadecimal color code.

    Args:
      rgb: A tuple of three integers (Red, Green, Blue), each in the range 0-255.

    Returns:
      A string representing the hexadecimal color code (e.g., "#206496").
    """
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def print_colored_hex_rich(hex_color, text):
    if hex_color != "#000000":
        print(f"[{hex_color}]{text}[/{hex_color}]")


def print_ascii_art(file_path, hex_color):  # pragma: no cover
    with open(file_path, "r") as f:
        for line in f:
            print_colored_hex_rich(hex_color=hex_color, text=line)


if __name__ == "__main__":
    print("Starting audio recording and color association...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            amp = get_audio_amplitude()
            color = amplitude_to_color(amp)
            print_ascii_art("ascii_arts/welcome", hex_color=rgb_to_hex(color))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"An error occurred: {e}")
