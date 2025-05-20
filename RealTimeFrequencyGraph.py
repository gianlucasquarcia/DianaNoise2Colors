import colorsys
import sys

import numpy as np
import pyqtgraph as pg
import sounddevice as sd
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from scipy.fftpack import fft

UPDATE_RATE_MS = 30  # Aggiorna ogni 30 ms


class RealTimeFrequencyGraph(QWidget):
    def __init__(self, show_wave: bool = False):
        super().__init__()
        self.setWindowTitle("Grafico Frequenze in Tempo Reale")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Grafico
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground("black")
        self.plot_widget.setLabel("left", "Ampiezza")
        self.plot_widget.setLabel("bottom", "Frequenza (Hz)")
        self.plot = pg.ScatterPlotItem()
        self.plot_widget.addItem(self.plot)

        # Parametri audio
        self.sample_rate = 48000  # Hz
        self.chunk_size = 1024

        # Stream audio
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
        )
        self.stream.start()

        # Dati iniziali
        self.audio_data = np.zeros(self.chunk_size)

        # Timer per aggiornare il grafico
        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_plot_with_wave if show_wave else self.update_plot_with_spot
        )
        self.timer.start(UPDATE_RATE_MS)  # Aggiorna ogni 30 ms

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data = indata[:, 0]

    def update_plot_with_spot(self):
        # Calcola la FFT
        fft_data = fft(self.audio_data)
        freqs = np.fft.fftfreq(len(fft_data), 1 / self.sample_rate)
        magnitude = np.abs(fft_data[: len(fft_data) // 2])
        freqs = freqs[: len(freqs) // 2]

        # Crea una mappa di colori
        color_map = pg.ColorMap(
            pos=np.linspace(0, 1, 3),
            color=[(0, 0, 255), (0, 255, 0), (255, 0, 0)],  # Blu -> Verde -> Rosso
        )
        colors = color_map.map(magnitude / np.max(magnitude), mode="qcolor")

        # Aggiorna il grafico
        spots = [
            {"pos": (freq, mag), "brush": color}
            for freq, mag, color in zip(freqs, magnitude, colors)
        ]
        self.plot.setData(spots)

    def update_plot_with_wave(self):
        # Dividi l'audio in segmenti
        chunked_audio = np.array_split(
            self.audio_data, len(self.audio_data) // self.chunk_size
        )
        colors = []

        for chunk in chunked_audio:
            # Calcola la frequenza dominante
            fft_data = fft(chunk)
            freqs = np.fft.fftfreq(len(fft_data), 1 / self.sample_rate)
            magnitude = np.abs(fft_data[: len(fft_data) // 2])
            freqs = freqs[: len(freqs) // 2]
            dominant_freq = freqs[np.argmax(magnitude)]

            # Mappa la frequenza a un colore
            colors.append(self.frequency_to_color(dominant_freq))

        # Disegna l'onda colorata
        self.plot_widget.clear()
        x_vals = np.linspace(0, len(self.audio_data), len(self.audio_data))
        for i, chunk in enumerate(chunked_audio):
            start_idx = i * self.chunk_size
            end_idx = start_idx + len(chunk)
            color = (
                pg.mkColor(colors[i])
                if i < len(colors)
                else pg.mkColor((255, 255, 255))
            )
            self.plot_widget.plot(
                x_vals[start_idx:end_idx],
                self.audio_data[start_idx:end_idx],
                pen=pg.mkPen(color, width=2),
            )

    @staticmethod
    def frequency_to_color(freq):
        # Mappa la frequenza su un gradiente di colori (rosso -> viola)
        freq = np.clip(freq, 50, 5000)
        min_freq, max_freq = 50, 5000
        normalized = (freq - min_freq) / (max_freq - min_freq)
        hue = 300 * normalized  # 0 -> rosso, 300 -> viola
        r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 1.0, 1.0)
        return int(r * 255), int(g * 255), int(b * 255)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    wave_option = True if sys.argv[1:] and sys.argv[1] == "--wave" else False

    window = RealTimeFrequencyGraph(show_wave=wave_option)
    window.show()
    sys.exit(app.exec_())
