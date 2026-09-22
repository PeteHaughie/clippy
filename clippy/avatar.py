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
import os
from pathlib import Path

import pyglet
from pyglet.graphics.shader import Shader, ShaderProgram

from .moods import Moods
from .statemachine import StateMachine

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MAP_PNG = ASSETS / "clippy" / "map.png"
AGENT_JSON = ASSETS / "clippy" / "agent.json"

#: The sprite sheet's background is magenta (255, 0, 255). It's alpha-0, but
#: linear filtering bleeds its RGB into the anti-aliased edges, leaving a purple
#: fringe. Chromakey the same way the explosion does (key by colour distance) so
#: those edge pixels go transparent.
KEY_COLOR = (1.0, 0.0, 1.0)
SIMILARITY = 0.30
SMOOTHNESS = 0.15

#: Fragment shader for the avatar sprite — pyglet's sprite vertex shader with a
#: chromakey pass (mirrors clippy/explosion.py).
_AVATAR_FRAGMENT_SRC = """#version 150 core
in vec4 vertex_colors;
in vec3 texture_coords;
out vec4 final_colors;
uniform sampler2D sprite_texture;
uniform vec3 u_key_color;
uniform float u_similarity;
uniform float u_smoothness;
void main()
{
    vec4 col = texture(sprite_texture, texture_coords.xy);
    vec3 diff = abs(col.rgb - u_key_color);
    float dist = max(diff.r, max(diff.g, diff.b));
    float key = smoothstep(u_similarity, u_similarity + u_smoothness, dist);
    final_colors = vec4(col.rgb, col.a * key) * vertex_colors;
}
"""


def frame_size(source: Path = AGENT_JSON) -> tuple[int, int]:
    """Read the sprite sheet's frame size without touching GL.

    The window must be sized from agent.json *before* any GL object
    (texture/sprite/shader) is created, because those need a current
    OpenGL context — and the context only exists once the pyglet Window
    has been constructed."""
    data = json.loads(Path(source).read_text())
    return tuple(data["framesize"])


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
    def __init__(self, scale: float = 1.5, moods: Moods | None = None):
        self.moods = moods or Moods()
        self.mood_sm = build_mood_sm(self.moods)
        self._texture = pyglet.image.load(str(MAP_PNG)).get_texture()
        data = json.loads(AGENT_JSON.read_text())
        self.frame_w, self.frame_h = data["framesize"]
        self.animations = data["animations"]
        self._region_cache = {}
        # Chromakey program (pyglet's sprite vertex shader + key fragment).
        self._key_program = ShaderProgram(
            Shader(pyglet.sprite.vertex_source, "vertex"),
            Shader(_AVATAR_FRAGMENT_SRC, "fragment"),
        )
        with self._key_program:
            self._key_program["u_key_color"] = KEY_COLOR
            self._key_program["u_similarity"] = SIMILARITY
            self._key_program["u_smoothness"] = SMOOTHNESS
        self.sprite = pyglet.sprite.Sprite(
            self._region(0, 0), program=self._key_program
        )
        self.sprite.scale = scale
        self.scale = scale
        self._frames = []
        self._durations = []
        self._frame_i = 0
        self._elapsed = 0.0
        self._wrap = False
        self._oneshot = False

        # Idle rotation state (playback projection). Starts ON: the avatar's initial
        # mood is "idle", so idle rotation should run from the very first frame
        # (a freshly started Prime sits idle before any brain turn).
        self._idle_mode = True
        self._idle_elapsed = 0.0
        self._idle_rotating = False
        self._idle_rot_elapsed = 0.0
        self._idle_last = None
        #: A specific idle-pool animation pinned by /mood idle <name>: plays on
        #: loop until any other mood is expressed (rotation is paused while set).
        self._idle_pinned: str | None = None
        #: A directly-played non-idle animation (play_animation) that should
        #: settle back to idle when it finishes.
        self._direct_oneshot = False

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

    def express(self, mood: str, hint: str | None = None, force: bool = False) -> bool:
        """Drive the avatar into a semantic mood. Returns False if ignored.

        The interruption rules live in the MoodSM's ``mood_allow`` guard; the
        resolved animation is the projection of the (allowed) request. Pass
        ``force=True`` (user-driven commands) to bypass the guard so any mood
        can be shown even while a continuous mood is running.
        """
        if self.mood_sm.current == mood:
            # Already in this mood. A fresh avatar starts with current == "idle"
            # yet _idle_mode is still False, so idle rotation would never start
            # unless we initialise it here (also makes /mood idle idempotent).
            if mood == "idle" and not self._idle_mode:
                self._idle_mode = True
                self._idle_rotating = False
                self._idle_elapsed = 0.0
                self._idle_rot_elapsed = 0.0
                self._idle_pinned = None
                self._play(self.moods.idle["settle"], wrap=False)
            return True  # already there
        if not self.mood_sm.fire("express", mood, force=force):
            return False  # one-shot dropped while a continuous mood runs
        name = self.moods.resolve(mood, hint)
        continuous = self.moods.is_continuous(mood)
        self._idle_mode = continuous and mood == "idle"
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        self._idle_pinned = None  # any new mood releases a pinned idle animation
        if self._idle_mode:
            self._play(self.moods.idle["settle"], wrap=False)
        else:
            self._play(name, wrap=continuous)
        return True

    def play_idle_animation(self, name: str) -> bool:
        """Pin a specific idle-pool animation, looping until a mood is called.

        Used by ``/mood idle <animation>`` so the user can pick exactly which
        idle animation plays (rotation is paused while pinned). Returns False
        for an unknown animation name.
        """
        if name not in self.animations:
            return False
        self._idle_mode = True
        self._idle_pinned = name
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        self._direct_oneshot = False
        self._play(name, wrap=True)
        return True

    def play_animation(self, name: str) -> bool:
        """Play any animation from the catalog directly (``/mood <name>``).

        Idle-pool animations loop (pinned, like ``/mood idle <name>``); any
        other animation plays once and then settles back to idle rotation.
        Returns False for an unknown animation name.
        """
        if name not in self.animations:
            return False
        pool = set(self.moods.idle["pool"])
        if name in pool:
            return self.play_idle_animation(name)
        self._idle_mode = False
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        self._idle_pinned = None
        self._direct_oneshot = True
        self._play(name, wrap=False)
        return True

    def _settle_idle(self):
        self.mood_sm.fire("oneshot_done")
        self._idle_mode = True
        self._idle_rotating = False
        self._idle_elapsed = 0.0
        self._idle_rot_elapsed = 0.0
        self._idle_pinned = None
        self._direct_oneshot = False
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
        if self.mood_sm.current != "idle" or self._direct_oneshot:
            self._settle_idle()

    def _update_idle(self, dt: float):
        if not self._idle_mode:
            return
        if self._idle_pinned:
            return  # keep playing the pinned idle animation
        cfg = self.moods.idle
        # Idle rotation is opt-in (idle.rotate). When on, the avatar loops
        # through the idle pool from initial_delay_sec until a mood is called.
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