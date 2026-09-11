"""Clippy avatar: parses the pi0/clippy agent.json animation data and plays
frame sequences sliced from map.png."""

import json
from pathlib import Path

import pyglet

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAP_PNG = ASSETS / "clippy" / "map.png"
AGENT_JSON = ASSETS / "clippy" / "agent.json"


class Avatar:
    def __init__(self, scale: float = 3.0):
        self._texture = pyglet.image.load(str(MAP_PNG)).get_texture()
        data = json.loads(AGENT_JSON.read_text())
        self.frame_w, self.frame_h = data["framesize"]
        self.animations = data["animations"]
        self._region_cache = {}
        self.sprite = pyglet.sprite.Sprite(self._region(0, 0))
        self.sprite.scale = scale
        self.scale = scale
        self._frames = []
        self._durations = []
        self._frame_i = 0
        self._elapsed = 0.0
        self.loop = False
        self.finished = False
        self.play("RestPose")

    def _region(self, x, y):
        key = (x, y)
        if key not in self._region_cache:
            self._region_cache[key] = self._texture.get_region(
                x, y, self.frame_w, self.frame_h
            )
        return self._region_cache[key]

    def play(self, name: str) -> bool:
        anim = self.animations.get(name)
        if anim is None:
            return False
        frames = []
        durations = []
        for fr in anim["frames"]:
            for (x, y) in fr["images"]:
                frames.append(self._region(x, y))
                durations.append(fr["duration"] / 1000.0)
        self._frames = frames
        self._durations = durations
        self._frame_i = 0
        self._elapsed = 0.0
        self.loop = bool(anim.get("useExitBranching", False))
        self.finished = False
        self.sprite.image = frames[0]
        return True

    def update(self, dt: float):
        if not self._frames:
            return
        self._elapsed += dt
        while self._elapsed >= self._durations[self._frame_i]:
            self._elapsed -= self._durations[self._frame_i]
            if self._frame_i + 1 < len(self._frames):
                self._frame_i += 1
            elif self.loop:
                self._frame_i = 0
            else:
                self.finished = True
                break
        self.sprite.image = self._frames[self._frame_i]

    def draw(self):
        self.sprite.draw()