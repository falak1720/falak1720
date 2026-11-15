"""Small toolkit for building self-contained animated SVGs for a GitHub README.

All text is converted to vector outlines (via fontTools) so it renders identically
on GitHub regardless of installed fonts or Content-Security-Policy. Glyphs are
defined once per SVG in <defs> and reused with <use>, keeping files small.
"""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILES = {
    "display": "fraunces-italic.ttf",
    "serif": "fraunces-medium.ttf",
    "mono": "mono.ttf",
    "monob": "mono-bold.ttf",
    "sans": "inter.ttf",
    "sansb": "inter-semibold.ttf",
    "arabic": "arabic.ttf",
}

THEMES = {
    "dark": dict(
        bg1="#070d1a", bg2="#122142", panel="#0f1a2e", panel2="#152440", line="#24365a",
        ink="#eef2f9", soft="#c6d1e3", muted="#8e9bb3", acc="#8fb6ee", acc2="#6c9be0",
        warm="#f0a77e", ok="#6fd3a3", star="#ffffff", pink="#f28fb0", yellow="#f5d06f",
    ),
    "light": dict(
        bg1="#fbf8f3", bg2="#ece4d7", panel="#fffdf9", panel2="#f3eee6", line="#ddd4c6",
        ink="#14213d", soft="#2c3a57", muted="#5d6679", acc="#2f5d9e", acc2="#4a7cc4",
        warm="#c0602f", ok="#23845a", star="#2f5d9e", pink="#c2416f", yellow="#b98a10",
    ),
}


class Font:
    _cache = {}

    def __init__(self, key):
        self.key = key
        self.tt = TTFont(os.path.join(HERE, "fonts", FONT_FILES[key]))
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.upm = self.tt["head"].unitsPerEm
        self.hmtx = self.tt["hmtx"]

    @classmethod
    def get(cls, key):
        if key not in cls._cache:
            cls._cache[key] = Font(key)
        return cls._cache[key]

    def glyph(self, ch):
        name = self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))
        return name

    def advance(self, ch):
        return self.hmtx[self.glyph(ch)][0]

    def path(self, name):
        pen = SVGPathPen(self.gs)
        self.gs[name].draw(pen)
        return pen.getCommands()

    def width(self, text, size, tracking=0.0):
        return sum(self.advance(c) for c in text) * size / self.upm + tracking * size * max(len(text) - 1, 0)


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.defs = []
        self.style = []
        self.body = []
        self._glyphs = {}

    def add(self, s):
        self.body.append(s)

    def css(self, s):
        self.style.append(s)

    def gdef(self, s):
        self.defs.append(s)

    def _gid(self, font, name):
        key = (font.key, name)
        if key not in self._glyphs:
            gid = f"g{len(self._glyphs)}"
            d = font.path(name)
            self._glyphs[key] = gid
            # Glyph outlines are y-up; flip them once here.
            self.defs.append(f'<path id="{gid}" d="{d}" transform="scale(1,-1)"/>')
        return self._glyphs[key]

    def text(self, s, x, y, size, font="sans", fill="#000", anchor="start", tracking=0.0,
             cls="", attrs="", per_char=None):
        """Render text as reused glyph outlines. Returns (svg, width, char_xs).

        per_char: optional callable(i, ch) -> extra attribute string for each glyph,
        used for staggered character animations.
        """
        f = Font.get(font)
        w = f.width(s, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        k = size / f.upm
        out, cx, xs = [], x, []
        for i, ch in enumerate(s):
            xs.append(cx)
            name = f.glyph(ch)
            if ch != " ":
                gid = self._gid(f, name)
                use = f'<use href="#{gid}" transform="translate({cx:.2f} {y:.2f}) scale({k:.5f})"/>'
                if per_char:
                    out.append(f'<g{per_char(i, ch)}>{use}</g>')
                else:
                    out.append(use)
            cx += f.advance(ch) * k + tracking * size
        xs.append(cx)
        c = f' class="{cls}"' if cls else ""
        return f'<g fill="{fill}"{c}{attrs}>' + "".join(out) + "</g>", w, xs

    def render(self):
        style = "\n".join(self.style)
        reduce = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}}")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{self.label}">'
            f"<title>{self.label}</title>"
            f"<defs>{''.join(self.defs)}</defs>"
            f"<style>{style}\n{reduce}</style>"
            + "\n".join(self.body)
            + "</svg>"
        )


def discrete_typing(n_chars, char_xs, x0, start, per_char, hold, erase_per_char, cycle):
    """SMIL values/keyTimes for a clip-rect width that types n chars, holds, then erases.

    Times are in seconds within a cycle of length `cycle`. Returns (values, keyTimes).
    """
    vals, times = ["0"], ["0"]
    t = start
    times.append(f"{t / cycle:.4f}"); vals.append("0")
    for i in range(1, n_chars + 1):
        t += per_char
        times.append(f"{t / cycle:.4f}"); vals.append(f"{char_xs[i] - x0 + 2:.1f}")
    t += hold
    if erase_per_char:
        for i in range(n_chars - 1, -1, -1):
            t += erase_per_char
            times.append(f"{min(t / cycle, 1):.4f}"); vals.append(f"{char_xs[i] - x0 + 2 if i else 0:.1f}")
    if float(times[-1]) < 1:
        times.append("1"); vals.append(vals[-1])
    return ";".join(vals), ";".join(times)


def write(path, svg):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg.render())
    return os.path.getsize(path)
