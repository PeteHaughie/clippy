"""Explosion playback for the floating Clippy.

Two paths for removing the green-screen:
  * live_key=True  -> the raw green PNG frames are keyed at render time by a
    GLSL fragment shader (showcase of pyglet's shader support).
  * live_key=False -> pre-baked transparent PNG frames made once with ffmpeg
    (safe path, no GPU requirement).
"""

from pathlib import Path

import pyglet
import pyglet.gl as gl
from pyglet.graphics.shader import Shader, ShaderProgram

ASSETS = Path(__file__).resolve().parent.parent / "assets"

_VERTEX_SRC = """#version 150 core
in vec2 a_position;
in vec2 a_tex_coords;
out vec2 v_tex_coords;
void main() {
    v_tex_coords = a_tex_coords;
    gl_Position = vec4(a_position, 0.0, 1.0);
}
"""

_FRAGMENT_SRC = """#version 150 core
uniform sampler2D u_texture;
uniform vec3 u_key_color;
uniform float u_similarity;
uniform float u_smoothness;
in vec2 v_tex_coords;
out vec4 out_color;
void main() {
    vec4 col = texture(u_texture, v_tex_coords);
    vec3 diff = abs(col.rgb - u_key_color);
    float dist = max(diff.r, max(diff.g, diff.b));
    float alpha = 1.0 - smoothstep(u_similarity, u_similarity + u_smoothness, dist);
    out_color = vec4(col.rgb, col.a * alpha);
}
"""

# Source gif chroma green: RGB(36, 252, 1)
KEY_COLOR = (0.141176, 0.988235, 0.003922)
SIMILARITY = 0.30
SMOOTHNESS = 0.15

FRAME_RATE = 10.0  # gif is 10 fps


class Explosion:
    def __init__(self, live_key: bool = True, scale: float = 3.0):
        self.scale = scale
        self.x = 0.0
        self.y = 0.0
        self.live_key = live_key
        self.playing = False
        self._frame_i = 0
        self._clock = 0.0
        base = "explosion-green" if live_key else "explosion"
        self._frames = [
            pyglet.image.load(str(p)).get_texture()
            for p in sorted((ASSETS / "clippy" / base).glob("frame-*.png"))
        ]
        self._program = None
        if live_key:
            self._program = ShaderProgram(
                Shader(_VERTEX_SRC, "vertex"), Shader(_FRAGMENT_SRC, "fragment")
            )
        self._sprite = None

    def trigger(self):
        self.playing = True
        self._frame_i = 0
        self._clock = 0.0

    @property
    def active(self) -> bool:
        return self.playing

    def update(self, dt: float):
        if not self.playing:
            return
        self._clock += dt
        while self._clock >= 1.0 / FRAME_RATE:
            self._clock -= 1.0 / FRAME_RATE
            self._frame_i += 1
            if self._frame_i >= len(self._frames):
                self.playing = False
                break

    def draw(self):
        if not self.playing or self._frame_i >= len(self._frames):
            return
        img = self._frames[self._frame_i]
        tw = img.width * self.scale
        th = img.height * self.scale
        if self._program is not None:
            self._render_keyed(img, tw, th)
        else:
            if self._sprite is None:
                self._sprite = pyglet.sprite.Sprite(img)
            self._sprite.scale = self.scale
            self._sprite.position = (self.x, self.y, 0)
            self._sprite.draw()

    def _render_keyed(self, img, tw, th):
        img.bind()
        with self._program:
            self._program["u_key_color"] = KEY_COLOR
            self._program["u_similarity"] = float(SIMILARITY)
            self._program["u_smoothness"] = float(SMOOTHNESS)
            ox, oy = self.x, self.y
            positions = (ox, oy, ox + tw, oy, ox + tw, oy + th, ox, oy + th)
            tex_coords = (0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0)
            vlist = self._program.vertex_list(
                4, gl.GL_TRIANGLE_FAN,
                a_position=("f", positions),
                a_tex_coords=("f", tex_coords),
            )
            vlist.draw(gl.GL_TRIANGLE_FAN)
            vlist.delete()