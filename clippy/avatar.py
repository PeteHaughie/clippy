"""Clippy avatar: parses the pi0/clippy agent.json animation data and plays
frame sequences sliced from map.png.

Adds a semantic mood layer on top of the raw animation names. Moods are
resolved via :class:`clippy.moods.Moods`:

* continuous moods (thinking/working/listening) hold and wrap to frame 0 when
  the animation list finishes;
* one-shot moods (greeting/celebrate/…) play once then auto-return to idle,
  settling on RestPose before the idle pool rotation kicks in after a delay.
"""

import json
from pathlib import Path

import pyglet

from .moods import Moods

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAP_PNG = ASSETS / "clippy" / "map.png"
AGENT_JSON = ASSETS / "clippy" / "agent.json"


class Avatar:
    def __init__(self, scale: float = 3.0, moods: Moods | None = None):
        self.moods = moods or Moods()
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
        self._wrap = False
        self._oneshot = False

        # Idle rotation state.
        self._idle_mode = False
        self._idle_elapsed = 0.0
        self._idle_rotating = False
        self._idle_rot_elapsed = 0.0
        self._idle_last = None

        # Current mood; set by the first express() call below.
        self._mood = None

        self.express("idle")

    # ------------------------------------------------------------------ region

    def _region(self, x, y):
        key = (x, y)
        if key not in self._region_cache:
            self._region_cache[key] = self._texture.get_region(
                x, y, self.frame_w, self.frame_h
            )
        return self._region_cache[key]

    # ------------------------------------------------------------- mood layer

    @property
    def current_mood(self) -> str:
        return self._mood

    def express(self, mood: str, hint: str | None = None) -> bool:
        """Drive the avatar into a semantic mood. Returns False if ignored.

        Interruption rules: a running continuous mood is replaced only by
        another continuous mood; one-shot moods may interrupt anything only when
        marked interrupt-ok (e.g. alert), otherwise they are dropped.
        """
        name = self.moods.resolve(mood, hint)
        continuous = self.moods.is_continuous(mood)
        interrupt = self.moods.can_interrupt(mood)

        if self._mood == mood:
            return True  # already there

        if (self._mood in self.moods.moods
                and self._mood not in ("idle",)
                and self.moods.is_continuous(self._mood)
                and not continuous
                and not interrupt):
            return False  # one-shot dropped while a continuous mood runs

        self._mood = mood
        self._idle_mode = continuous and mood == "idle"
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        if self._idle_mode:
            self._play(self.moods.idle["settle"], wrap=False)
        else:
            self._play(name, wrap=continuous)
        return True

    def _settle_idle(self):
        self._mood = "idle"
        self._idle_mode = True
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        self._play(self.moods.idle["settle"], wrap=False)

    def _next_idle_animation(self) -> str:
        import random

        pool = self.moods.idle["pool"]
        candidates = [a for a in pool if a != self._idle_last] or pool
        chosen = random.choice(candidates)
        self._idle_last = chosen
        return chosen

    # ------------------------------------------------------------ playback

    def _play(self, name: str, wrap: bool = False):
        anim = self.animations[name]
        frames = []
        durations = []
        last_region = self._region(0, 0)
        for fr in anim["frames"]:
            if fr.get("images"):
                last_region = self._region(*fr["images"][0])
            frames.append(last_region)
            durations.append(max(fr["duration"] / 1000.0, 0.01))
        self._frames = frames
        self._durations = durations
        self._frame_i = 0
        self._elapsed = 0.0
        self._wrap = wrap
        self._oneshot = not wrap
        self.sprite.image = frames[0]

    def update(self, dt: float):
        if not self._frames:
            return
        if self._idle_mode:
            self._update_idle(dt)
        self._elapsed += dt
        changed = False
        while self._elapsed >= self._durations[self._frame_i]:
            self._elapsed -= self._durations[self._frame_i]
            if self._frame_i + 1 < len(self._frames):
                self._frame_i += 1
            elif self._wrap:
                self._frame_i = 0
            else:
                self._oneshot_done()
                changed = True
                break
        if not changed:
            self.sprite.image = self._frames[self._frame_i]

    def _oneshot_done(self):
        if self._mood != "idle":
            self._settle_idle()

    def _update_idle(self, dt: float):
        if not self._idle_mode:
            return
        cfg = self.moods.idle
        if not self._idle_rotating:
            self._idle_elapsed += dt
            if self._idle_elapsed >= cfg["initial_delay_sec"]:
                self._idle_rotating = True
                self._idle_rot_elapsed = 0.0
                self._play(self._next_idle_animation(), wrap=True)
        else:
            self._idle_rot_elapsed += dt
            if self._idle_rot_elapsed >= cfg["rotate_interval_sec"]:
                self._idle_rot_elapsed = 0.0
                self._play(self._next_idle_animation(), wrap=True)

    def draw(self):
        self.sprite.draw()