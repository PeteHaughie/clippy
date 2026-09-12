"""Clippy avatar: parses the pi0/clippy agent.json animation data and plays
frame sequences sliced from map.png.

Mood *decisions* are a graph-declared state machine (:class:`MoodSM`,
phase 2): continuous/oneshot/interrupt rules decide which mood may run.
Playback (animation selection, wrapping, the idle-pool rotation) is the
projection and stays here.

* continuous moods (thinking/working/listening) hold and wrap to frame 0 when
  the animation list finishes;
* one-shot moods (greeting/celebrate/…) play once then auto-return to idle,
  settling on RestPose before the idle pool rotation kicks in after a delay.

Idle rotation is opt-in (``idle.rotate`` in the config, default off): with it
disabled Clippy simply holds the ``RestPose`` settle pose between contextual
moods, so he only animates when the chat (or a key) actually triggers a mood.
"""

import json
from pathlib import Path

import pyglet

from .moods import Moods
from .statemachine import StateMachine

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAP_PNG = ASSETS / "clippy" / "map.png"
AGENT_JSON = ASSETS / "clippy" / "agent.json"


def _mood_allow(moods: Moods, sm: StateMachine, mood: str) -> bool:
    """MoodSM guard: may ``mood`` replace the current mood?

    A one-shot mood is dropped while a continuous mood runs unless it is
    marked interrupt-ok (e.g. alert); anything else may interrupt.
    """
    cur = sm.current
    if cur == mood:
        return False  # caller's no-op path
    continuous = moods.is_continuous(mood)
    interrupt = moods.can_interrupt(mood)
    if (
        cur in moods.moods
        and cur != "idle"
        and moods.is_continuous(cur)
        and not continuous
        and not interrupt
    ):
        return False
    return True


def build_mood_sm(moods: Moods) -> StateMachine:
    """The avatar's mood machine: states = moods, edges = express/oneshot_done."""
    states = {name: {} for name in moods.moods}
    states.setdefault("idle", {})
    return StateMachine(
        {
            "initial": "idle",
            "states": states,
            "transitions": [
                {"src": "*", "trigger": "express", "guard": "mood_allow", "to": lambda sm, mood: mood},
                {"src": "*", "trigger": "oneshot_done", "guard": "not_idle", "to": "idle"},
            ],
        },
        guards={
            "mood_allow": lambda sm, mood: _mood_allow(moods, sm, mood),
            "not_idle": lambda sm: sm.current != "idle",
        },
    )


class Avatar:
    def __init__(self, scale: float = 3.0, moods: Moods | None = None):
        self.moods = moods or Moods()
        self.mood_sm = build_mood_sm(self.moods)
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

        # Idle rotation state (playback projection).
        self._idle_mode = False
        self._idle_elapsed = 0.0
        self._idle_rotating = False
        self._idle_rot_elapsed = 0.0
        self._idle_last = None

        self._play(self.moods.idle["settle"], wrap=False)

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
        return self.mood_sm.current

    def express(self, mood: str, hint: str | None = None) -> bool:
        """Drive the avatar into a semantic mood. Returns False if ignored.

        The interruption rules live in the MoodSM's ``mood_allow`` guard; the
        resolved animation is the projection of the (allowed) request.
        """
        if self.mood_sm.current == mood:
            return True  # already there
        if not self.mood_sm.fire("express", mood):
            return False  # one-shot dropped while a continuous mood runs
        name = self.moods.resolve(mood, hint)
        continuous = self.moods.is_continuous(mood)
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
        self.mood_sm.fire("oneshot_done")
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
        if self.mood_sm.current != "idle":
            self._settle_idle()

    def _update_idle(self, dt: float):
        if not self._idle_mode:
            return
        cfg = self.moods.idle
        # Idle rotation is opt-in (idle.rotate). Off by default: Clippy holds
        # the RestPose settle pose so he only animates when a mood is actually
        # triggered (chat, key, controller).
        if not cfg.get("rotate", False):
            return
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