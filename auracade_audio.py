from __future__ import annotations

import math
from array import array

import pygame


ARCADE_TRACK = {
    "beat": 0.18,
    "melody": [
        261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 329.63,
        349.23, 392.00, 440.00, 587.33, 440.00, 392.00, 349.23, 329.63,
        329.63, 392.00, 440.00, 523.25, 440.00, 392.00, 349.23, 329.63,
        293.66, 329.63, 392.00, 440.00, 392.00, 329.63, 293.66, 261.63,
    ],
    "bass": [
        130.81, 130.81, 130.81, 130.81, 98.00, 98.00, 98.00, 98.00,
        174.61, 174.61, 174.61, 174.61, 130.81, 130.81, 130.81, 130.81,
        164.81, 164.81, 164.81, 164.81, 123.47, 123.47, 123.47, 123.47,
        146.83, 146.83, 146.83, 146.83, 130.81, 130.81, 98.00, 98.00,
    ],
}

FANTASY_TRACK = {
    "step": 0.22,
    "lead": [
        392.00, 440.00, 523.25, 659.25,
        587.33, 523.25, 440.00, 392.00,
        440.00, 493.88, 587.33, 698.46,
        659.25, 587.33, 523.25, 440.00,
        392.00, 440.00, 523.25, 587.33,
        659.25, 587.33, 523.25, 440.00,
        349.23, 392.00, 440.00, 523.25,
        493.88, 440.00, 392.00, 349.23,
    ],
    "pads": [
        (196.00, 293.66, 392.00),
        (196.00, 293.66, 392.00),
        (220.00, 329.63, 440.00),
        (220.00, 329.63, 440.00),
        (174.61, 261.63, 349.23),
        (174.61, 261.63, 349.23),
        (196.00, 293.66, 392.00),
        (196.00, 293.66, 392.00),
    ],
    "bass": [98.00, 98.00, 110.00, 110.00, 87.31, 87.31, 98.00, 98.00],
}


def build_arcade_track() -> pygame.mixer.Sound:
    sample_rate = 22050
    beat = float(ARCADE_TRACK["beat"])
    melody = ARCADE_TRACK["melody"]
    bass = ARCADE_TRACK["bass"]
    frames = array("h")

    for note_index, freq in enumerate(melody):
        bass_freq = bass[note_index % len(bass)]
        total = int(sample_rate * beat)
        for i in range(total):
            t = i / sample_rate
            env = 1.0 - (i / total)
            square = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            tri = (2 / math.pi) * math.asin(math.sin(2 * math.pi * (freq / 2) * t))
            low = math.sin(2 * math.pi * bass_freq * t)
            pulse = 1.0 if math.sin(2 * math.pi * (freq * 2) * t) > 0.35 else -0.65
            value = (square * 0.36 + tri * 0.22 + pulse * 0.14 + low * 0.28) * env
            sample = max(-32768, min(32767, int(value * 13000)))
            frames.append(sample)
            frames.append(sample)

    return pygame.mixer.Sound(buffer=frames.tobytes())


def build_fantasy_track() -> pygame.mixer.Sound:
    sample_rate = 22050
    step = float(FANTASY_TRACK["step"])
    lead = FANTASY_TRACK["lead"]
    pads = FANTASY_TRACK["pads"]
    bass = FANTASY_TRACK["bass"]
    frames = array("h")

    for note_index, freq in enumerate(lead):
        chord = pads[(note_index // 4) % len(pads)]
        bass_freq = bass[(note_index // 4) % len(bass)]
        total = int(sample_rate * step)
        for i in range(total):
            t = i / sample_rate
            env = 1.0 - (i / total) * 0.82
            lead_voice = math.sin(2 * math.pi * freq * t)
            octave = math.sin(2 * math.pi * (freq * 0.5) * t) * 0.32
            shimmer = math.sin(2 * math.pi * (freq * 2.0) * t) * 0.18
            pad = sum(math.sin(2 * math.pi * tone * t) for tone in chord) / len(chord)
            low = math.sin(2 * math.pi * bass_freq * t)
            value = (lead_voice * 0.34 + octave * 0.14 + shimmer * 0.08 + pad * 0.24 + low * 0.26) * env
            sample = max(-32768, min(32767, int(value * 11800)))
            frames.append(sample)
            frames.append(sample)

    return pygame.mixer.Sound(buffer=frames.tobytes())

class LauncherMusic:
    def __init__(self) -> None:
        self.soundtracks: list[pygame.mixer.Sound] = []
        self.channel: pygame.mixer.Channel | None = None
        self.enabled = False
        self.suspended = False
        self.active_track_index = 0
        self.next_track_switch = 0.0

        self._init_mixer_and_tracks()

    def _init_mixer_and_tracks(self) -> None:
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        except pygame.error:
            return

        self.soundtracks = [build_fantasy_track()]
        self.channel = pygame.mixer.Channel(0)
        self.enabled = True
        self._start_next_track()

    @property
    def available(self) -> bool:
        return bool(self.soundtracks and self.channel is not None)

    def _start_next_track(self) -> None:
        if not self.available or not self.enabled or self.suspended:
            return
        assert self.channel is not None
        track = self.soundtracks[self.active_track_index]
        self.channel.set_volume(0.24)
        self.channel.play(track)
        self.next_track_switch = pygame.time.get_ticks() / 1000.0 + track.get_length()
        self.active_track_index = (self.active_track_index + 1) % len(self.soundtracks)

    def tick(self) -> None:
        if not self.available or not self.enabled or self.suspended:
            return
        if pygame.time.get_ticks() / 1000.0 >= self.next_track_switch:
            self._start_next_track()

    def toggle(self) -> str:
        if not self.available:
            return "Audio launcher non disponibile su questo sistema."
        self.enabled = not self.enabled
        assert self.channel is not None
        if not self.enabled:
            self.channel.stop()
            return "Musiche launcher disattivate"
        if not self.suspended:
            self._start_next_track()
        return "Musiche launcher attive"

    def suspend_for_game(self) -> None:
        if not self.available:
            return
        self.suspended = True
        assert self.channel is not None
        self.channel.stop()
        pygame.mixer.quit()

    def resume_after_game(self) -> None:
        self.suspended = False
        self.channel = None
        self.soundtracks = []
        self._init_mixer_and_tracks()
        if not self.available:
            return
        if self.enabled:
            self._start_next_track()

    def shutdown(self) -> None:
        if self.channel is not None:
            self.channel.stop()