from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

import numpy as np
import random

WIDTH, HEIGHT = 800, 400
BAR_COUNT = 40
MAX_BAR_HEIGHT = HEIGHT - 50

class Particle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-10, 10)
        self.y = y
        self.size = random.randint(4, 8)
        self.life = 40
        self.speed_y = random.uniform(0.5, 1.5)

    def update(self):
        self.y += self.speed_y
        self.life -= 1

    def is_dead(self):
        return self.life <= 0

class VisualizerWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_data = None
        self.audio_pos = 0
        self.buffer_size = 2048
        self.particles = []
        self.sound = None

        self.load_audio("Bad Girl Season 1 Ending 1 HD.wav")  # Replace with your WAV file path

        Clock.schedule_interval(self.update_visualizer, 1 / 30)

    def load_audio(self, filepath):
        from scipy.io import wavfile
        rate, data = wavfile.read(filepath)
        if len(data.shape) > 1:
            data = data[:, 0]
        self.audio_data = data / np.max(np.abs(data))
        self.rate = rate

        self.sound = SoundLoader.load(filepath)
        if self.sound:
            self.sound.play()

    def update_visualizer(self, dt):
        self.canvas.clear()
        with self.canvas:
            if self.audio_data is None:
                return

            if self.audio_pos + self.buffer_size < len(self.audio_data):
                chunk = self.audio_data[self.audio_pos:self.audio_pos + self.buffer_size]
                self.audio_pos += self.buffer_size
            else:
                chunk = self.audio_data[self.audio_pos:]
                self.audio_pos = 0  # loop

            fft = np.abs(np.fft.fft(chunk))
            fft = fft[:self.buffer_size // 2]

            bins = np.array_split(fft, BAR_COUNT)
            spectrum = np.array([np.mean(bin) for bin in bins])
            max_val = np.max(spectrum)
            if max_val == 0:
                spectrum = np.zeros_like(spectrum)
            else:
                spectrum = spectrum / max_val

            bar_width = WIDTH / BAR_COUNT
            avg_volume = np.mean(spectrum)

            # Draw bars
            for i, magnitude in enumerate(spectrum):
                bar_height = magnitude * MAX_BAR_HEIGHT
                intensity = int(200 * (i / BAR_COUNT)) + 50
                color_val = min(255, intensity)
                Color(0, 0, color_val / 255)
                x = i * bar_width
                y = 0
                Rectangle(pos=(x, y), size=(bar_width * 0.8, bar_height))

            # Spawn particles based on volume
            if avg_volume > 0.1:
                for _ in range(int(avg_volume * 10)):
                    bar_index = random.randint(0, BAR_COUNT - 1)
                    x_pos = bar_index * bar_width + bar_width / 2
                    y_pos = 0
                    self.particles.append(Particle(x_pos, y_pos))

            # Update and draw particles
            alive_particles = []
            for p in self.particles:
                p.update()
                if not p.is_dead():
                    alive_particles.append(p)
                    Color(0, 0.6, 1, p.life / 40)
                    Ellipse(pos=(p.x, p.y), size=(p.size, p.size))
            self.particles = alive_particles


class BRSApp(App):
    def build(self):
        return VisualizerWidget(size=(WIDTH, HEIGHT))


if __name__ == "__main__":
    BRSApp().run()
