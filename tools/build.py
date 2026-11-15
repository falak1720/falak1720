"""Build every animated SVG used in Falak's GitHub profile README.

Usage:  python tools/build.py
Writes light + dark variants of each piece into ../assets/.
"""
import math
import os
import random
import re

from svgkit import THEMES, Font, Svg, discrete_typing, write

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
ICONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)


def bg(svg, t, rx=20, grad_id="bg"):
    svg.gdef(f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{t["bg1"]}"/><stop offset="1" stop-color="{t["bg2"]}"/></linearGradient>')
    svg.add(f'<rect width="{svg.w}" height="{svg.h}" rx="{rx}" fill="url(#{grad_id})"/>')


def stars(svg, t, n, box, seed, rmax=1.6, cls="tw"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(0.5, rmax)
        d, dur = rnd.uniform(0, 5), rnd.uniform(2.5, 6)
        out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
                   f'style="animation-delay:-{d:.2f}s;animation-duration:{dur:.2f}s"/>')
    svg.add(f'<g fill="{t["star"]}">' + "".join(out) + "</g>")
    svg.css(f".{cls}{{animation:twinkle 4s ease-in-out infinite}}"
            "@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:.9}}")


def icon_path(slug):
    s = open(os.path.join(ICONS, f"{slug}.svg"), encoding="utf-8").read()
    return re.search(r'<path d="([^"]+)"', s).group(1)


# ---------------------------------------------------------------------------
# 1. Header: "Falak" means sky — a night sky whose stars form a scatter plot.
# ---------------------------------------------------------------------------
def header(mode):
    t = THEMES[mode]
    W, H = 1200, 380
    s = Svg(W, H, "Falak — Psychology and Behavioral Data Science. Falak means sky in Urdu.")
    bg(s, t, rx=22)
    # soft glow behind the constellation
    s.gdef(f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t["acc2"]}" stop-opacity=".28"/>'
           f'<stop offset="1" stop-color="{t["acc2"]}" stop-opacity="0"/></radialGradient>')
    s.gdef(f'<clipPath id="hclip"><rect width="{W}" height="{H}" rx="22"/></clipPath>')
    s.add(f'<g clip-path="url(#hclip)"><ellipse cx="930" cy="190" rx="300" ry="190" fill="url(#glow)" class="breathe"/></g>')
    s.css(".breathe{animation:breathe 8s ease-in-out infinite;transform-origin:930px 190px}"
          "@keyframes breathe{0%,100%{opacity:.7;transform:scale(1)}50%{opacity:1;transform:scale(1.06)}}")
    stars(s, t, 90, (10, 10, W - 10, H - 10), seed=3)

    # shooting stars
    s.gdef(f'<linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["star"]}" stop-opacity="0"/>'
           f'<stop offset="1" stop-color="{t["star"]}" stop-opacity=".95"/></linearGradient>')
    s.add('<g class="shoot s1"><rect x="0" y="-1" width="120" height="2" rx="1" fill="url(#trail)"/></g>'
          '<g class="shoot s2"><rect x="0" y="-1" width="90" height="1.6" rx="1" fill="url(#trail)"/></g>')
    s.css(".shoot{opacity:0}"
          ".s1{animation:shoot1 11s linear infinite 2.5s}"
          ".s2{animation:shoot2 11s linear infinite 8s}"
          "@keyframes shoot1{0%{opacity:0;transform:translate(420px,30px) rotate(18deg)}2%{opacity:1}"
          "9%{opacity:0;transform:translate(760px,140px) rotate(18deg)}100%{opacity:0;transform:translate(760px,140px) rotate(18deg)}}"
          "@keyframes shoot2{0%{opacity:0;transform:translate(820px,20px) rotate(24deg)}2%{opacity:1}"
          "8%{opacity:0;transform:translate(1080px,135px) rotate(24deg)}100%{opacity:0;transform:translate(1080px,135px) rotate(24deg)}}")

    # --- constellation scatter plot (loops every 14s) ---
    rnd = random.Random(11)
    pts = []
    for i in range(16):
        x = 740 + i * 27 + rnd.uniform(-8, 8)
        y = 300 - (x - 740) * 0.47 + rnd.gauss(0, 20)
        pts.append((x, y))
    order = sorted(range(len(pts)), key=lambda i: pts[i][0])
    cyc = 14.0

    def pct(sec):
        return f"{sec / cyc * 100:.2f}%"

    # axis ticks (faint)
    s.add(f'<g stroke="{t["line"]}" stroke-width="1" class="axes">'
          f'<line x1="720" y1="330" x2="1160" y2="330"/><line x1="720" y1="330" x2="720" y2="70"/>'
          + "".join(f'<line x1="{720 + k * 88}" y1="330" x2="{720 + k * 88}" y2="336"/>' for k in range(6))
          + "</g>")
    # constellation edges between neighbouring stars, drawn after points appear
    edges = []
    for a, b in zip(order, order[1:]):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        L = math.hypot(x2 - x1, y2 - y1)
        edges.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" pathLength="1" class="edge"/>')
    s.add(f'<g stroke="{t["acc"]}" stroke-width="1.1" stroke-opacity=".55" class="edges">' + "".join(edges) + "</g>")
    s.css(".edge{stroke-dasharray:1;stroke-dashoffset:1;animation:edge 14s ease infinite}"
          f"@keyframes edge{{0%,{pct(2.4)}{{stroke-dashoffset:1;opacity:1}}{pct(4.4)}{{stroke-dashoffset:0}}"
          f"{pct(12.2)}{{stroke-dashoffset:0;opacity:1}}{pct(13.4)},100%{{stroke-dashoffset:0;opacity:0}}}}")
    # points
    dots = []
    for rank, i in enumerate(order):
        x, y = pts[i]
        dots.append(f'<g transform="translate({x:.1f} {y:.1f})"><g class="pt" style="animation-delay:{rank * 0.11:.2f}s">'
                    f'<circle r="7" fill="{t["acc2"]}" opacity=".18"/><circle r="3.4" fill="{t["star"]}"/>'
                    f'<path d="M0 -8 L1 -1 L8 0 L1 1 L0 8 L-1 1 L-8 0 L-1 -1Z" fill="{t["star"]}" opacity=".55" class="spark"/></g></g>')
    s.add("".join(dots))
    s.css(".pt{animation:pt 14s cubic-bezier(.22,1,.36,1) infinite;opacity:0}"
          f"@keyframes pt{{0%{{opacity:0;transform:scale(0)}}{pct(0.6)}{{opacity:1;transform:scale(1.35)}}{pct(1.0)}{{transform:scale(1)}}"
          f"{pct(12.2)}{{opacity:1;transform:scale(1)}}{pct(13.4)},100%{{opacity:0;transform:scale(.6)}}}}"
          ".spark{animation:spark 3s ease-in-out infinite}@keyframes spark{0%,100%{opacity:.15}50%{opacity:.8}}")
    # regression line + label
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    b = sum((x - mx) * (y - my) for x, y in pts) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    lx1, lx2 = 728, 1160
    s.add(f'<line x1="{lx1}" y1="{a + b * lx1:.1f}" x2="{lx2}" y2="{a + b * lx2:.1f}" stroke="{t["warm"]}" stroke-width="3.2" '
          f'stroke-linecap="round" pathLength="1" class="reg"/>')
    s.css(".reg{stroke-dasharray:1;stroke-dashoffset:1;animation:reg 14s cubic-bezier(.65,0,.35,1) infinite}"
          f"@keyframes reg{{0%,{pct(4.6)}{{stroke-dashoffset:1;opacity:1}}{pct(6.4)}{{stroke-dashoffset:0}}"
          f"{pct(12.2)}{{stroke-dashoffset:0;opacity:1}}{pct(13.4)},100%{{stroke-dashoffset:0;opacity:0}}}}")
    lab, _, _ = s.text("ρ = .63   social skills × extraversion", 1160, 362, 13, "mono", t["muted"], anchor="end", cls="rlab")
    s.add(lab)
    s.css(".rlab{opacity:0;animation:rlab 14s ease infinite}"
          f"@keyframes rlab{{0%,{pct(6.2)}{{opacity:0}}{pct(7.0)},{pct(12.2)}{{opacity:1}}{pct(13.4)},100%{{opacity:0}}}}")

    # --- left: identity ---
    g, _, _ = s.text("PSYCHOLOGY  ×  BEHAVIORAL DATA SCIENCE", 66, 92, 14, "mono", t["acc"], tracking=0.16,
                     per_char=lambda i, ch: f' class="ey" style="animation-delay:{0.02 * i:.2f}s"')
    s.add(g)
    s.css(".ey{opacity:0;animation:fadein .5s ease forwards}@keyframes fadein{to{opacity:1}}")
    name, nw, _ = s.text("Falak", 60, 210, 132, "display", t["ink"],
                         per_char=lambda i, ch: f' class="nm" style="animation-delay:{0.35 + 0.09 * i:.2f}s"')
    s.add(name)
    s.css(".nm{opacity:0;animation:rise 1s cubic-bezier(.22,1,.36,1) forwards}"
          "@keyframes rise{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}")
    # a little star dotting the name
    s.add(f'<g transform="translate({66 + nw + 14:.0f} 112)"><g class="nstar">'
          f'<path d="M0 -13 L3 -3 L13 0 L3 3 L0 13 L-3 3 L-13 0 L-3 -3Z" fill="{t["warm"]}"/></g></g>')
    s.css(".nstar{opacity:0;animation:nstar 1s cubic-bezier(.22,1,.36,1) 1.1s forwards, spin 12s linear 2.1s infinite}"
          "@keyframes nstar{from{opacity:0;transform:scale(0) rotate(-90deg)}to{opacity:1;transform:scale(1) rotate(0)}}"
          "@keyframes spin{to{transform:rotate(360deg)}}")
    # Urdu: فلک (presentation forms in visual left-to-right order)
    urdu, uw, _ = s.text("ﮏﻠﻓ", 68, 262, 34, "arabic", t["warm"], cls="sub1")
    s.add(urdu)
    meaning, _, _ = s.text("—  Urdu for “sky”", 68 + uw + 14, 256, 15, "mono", t["muted"], cls="sub1")
    s.add(meaning)
    l1, _, _ = s.text("M.S. Data Science in Human Behavior  ·  UW–Madison", 68, 304, 20, "sans", t["soft"], cls="sub2")
    l2, _, _ = s.text("B.S. Psychology, Highest Honors  ·  Michigan State  ·  NASA HERA mission control", 68, 334, 15, "sans", t["muted"], cls="sub3")
    s.add(l1); s.add(l2)
    s.css(".sub1,.sub2,.sub3{opacity:0;animation:up .9s cubic-bezier(.22,1,.36,1) forwards}"
          ".sub1{animation-delay:1.1s}.sub2{animation-delay:1.35s}.sub3{animation-delay:1.55s}"
          "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}")
    return s


# ---------------------------------------------------------------------------
# 2. Typing tagline (self-hosted, matches the rest of the set)
# ---------------------------------------------------------------------------
def typing(mode):
    t = THEMES[mode]
    W, H = 900, 54
    s = Svg(W, H, "Turning human behavior into evidence. Survey design to SPSS, R and Python to Quarto. "
                  "Former mission control for a NASA Mars analog. Open to research and data roles.")
    lines = [
        "turning human behavior into evidence",
        "survey design → SPSS / R / Python → Quarto",
        "ex mission control · NASA HERA Mars analog",
        "open to research & behavioral-data roles",
    ]
    slot, size = 5.5, 21
    cyc = slot * len(lines)
    f = Font.get("mono")
    for li, txt in enumerate(lines):
        full = "› " + txt
        w = f.width(full, size)
        x0 = (W - w) / 2 - 8
        cid = f"c{li}"
        g, _, xs = s.text(full, x0, 35, size, "mono", t["acc"], attrs=f' clip-path="url(#{cid})"')
        n = len(full)
        start = li * slot + 0.25
        vals, kt = discrete_typing(n, xs, x0, start, 0.045, slot - 0.25 - n * 0.045 - n * 0.018 - 0.2, 0.018, cyc)
        s.gdef(f'<clipPath id="{cid}"><rect x="{x0 - 1:.1f}" y="0" width="0" height="{H}">'
               f'<animate attributeName="width" values="{vals}" keyTimes="{kt}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>'
               f'</rect></clipPath>')
        s.add(g)
        # caret follows the clip edge
        cx_vals = ";".join(f"{x0 + float(v):.1f}" for v in vals.split(";"))
        on0, on1 = li * slot / cyc, (li + 1) * slot / cyc
        s.add(f'<rect y="13" width="10" height="26" rx="1.5" fill="{t["warm"]}" class="caret" opacity="0">'
              f'<animate attributeName="x" values="{cx_vals}" keyTimes="{kt}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{on0:.4f};{on1:.4f}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>'
              f'</rect>')
    s.css(".caret{animation:blink 1s steps(1) infinite}@keyframes blink{50%{fill-opacity:0}}")
    return s


# ---------------------------------------------------------------------------
# 3. R console card that types out who she is
# ---------------------------------------------------------------------------
def console(mode):
    t = THEMES[mode]
    W, H = 900, 452
    s = Svg(W, H, "R console introducing Falak: M.S. Data Science in Human Behavior at UW–Madison; B.S. Psychology, "
                  "Highest Honors, Michigan State; research in social media and confidence, multiteam systems, auditory timing, "
                  "student wellbeing; toolkit R, Python, SPSS, Quarto, Qualtrics; speaks Hindi, Urdu, English.")
    s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    s.add(f'<path d="M1 17 a16 16 0 0 1 16 -16 H{W - 17} a16 16 0 0 1 16 16 V44 H1Z" fill="{t["panel2"]}"/>'
          f'<line x1="1" y1="44" x2="{W - 1}" y2="44" stroke="{t["line"]}"/>')
    for i, c in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
        s.add(f'<circle cx="{26 + i * 20}" cy="23" r="6" fill="{c}"/>')
    tt, _, _ = s.text("falak.R  —  R Console", W / 2, 28, 13, "mono", t["muted"], anchor="middle")
    s.add(tt)

    P, N, S, F, K, O = t["muted"], t["acc"], t["ok"], t["warm"], t["soft"], t["ink"]
    L = [
        [("> ", P), ("falak", N), (" <- ", K), ("list", F), ("(", K)],
        [("+   ", P), ("now", N), ("      = ", K), ('"M.S. Data Science in Human Behavior, UW–Madison"', S), (",", K)],
        [("+   ", P), ("before", N), ("   = ", K), ('"B.S. Psychology, Highest Honors, Michigan State"', S), (",", K)],
        [("+   ", P), ("research", N), (" = ", K), ("c", F), ("(", K), ('"social media & confidence"', S), (", ", K), ('"multiteam systems"', S), (",", K)],
        [("+                ", P), ('"auditory timing"', S), (", ", K), ('"student wellbeing"', S), ("),", K)],
        [("+   ", P), ("toolkit", N), ("  = ", K), ("c", F), ("(", K), ('"R"', S), (", ", K), ('"Python"', S), (", ", K), ('"SPSS"', S), (", ", K), ('"Quarto"', S), ("),", K)],
        [("+   ", P), ("speaks", N), ("   = ", K), ("c", F), ("(", K), ('"Hindi"', S), (", ", K), ('"Urdu"', S), (", ", K), ('"English"', S), (")", K)],
        [("+ ", P), (")", K)],
        [("> ", P), ("cor.test", F), ("(", K), ("curiosity", N), (", ", K), ("rigor", N), (", ", K), ("method", N), (" = ", K), ('"spearman"', S), (")$", K), ("estimate", N)],
        [("      rho", O)],
        [("     0.99 ", O), ("  # n.s. is not an option", P)],
    ]
    output = {9, 10}
    size, lh, x0, y0 = 15.5, 31, 28, 82
    f = Font.get("mono")
    per = 0.028
    t_cursor = 0.6
    cyc = 26.0
    for li, segs in enumerate(L):
        y = y0 + li * lh
        full = "".join(x for x, _ in segs)
        xs_all = [x0]
        for ch in full:
            xs_all.append(xs_all[-1] + f.advance(ch) * size / f.upm)
        cid = f"l{li}"
        parts = []
        cx = x0
        for txt, col in segs:
            g, w, _ = s.text(txt, cx, y, size, "mono", col)
            parts.append(g)
            cx += w
        s.add(f'<g clip-path="url(#{cid})">' + "".join(parts) + "</g>")
        n = len(full)
        if li in output:
            spc = 0.0005
            t_cursor += 0.25
        else:
            spc = per
        vl, tl = ["0", "0"], ["0", f"{t_cursor / cyc:.4f}"]
        tt_ = t_cursor
        for i in range(1, n + 1):
            tt_ += spc
            vl.append(f"{xs_all[i] - x0 + 2:.1f}"); tl.append(f"{tt_ / cyc:.4f}")
        vl.append("0"); tl.append(f"{(cyc - 0.6) / cyc:.4f}")
        s.gdef(f'<clipPath id="{cid}"><rect x="{x0 - 2}" y="{y - lh + 6}" width="0" height="{lh}">'
               f'<animate attributeName="width" values="{";".join(vl)}" keyTimes="{";".join(tl)}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>'
               f'</rect></clipPath>')
        t_cursor += n * spc + (0.35 if li in (0, 7, 8) else 0.12)
    # final prompt with blinking cursor
    yf = y0 + len(L) * lh
    pr, pw, _ = s.text("> ", x0, yf, size, "mono", P, cls="fin")
    s.add(pr)
    s.add(f'<rect x="{x0 + pw + 2:.1f}" y="{yf - 15}" width="9" height="19" fill="{t["warm"]}" class="fin cur"/>')
    on = t_cursor / cyc * 100
    s.css(f".fin{{opacity:0;animation:fin {cyc}s steps(1) infinite}}"
          f"@keyframes fin{{0%{{opacity:0}}{on:.2f}%{{opacity:1}}{(cyc - 0.6) / cyc * 100:.2f}%{{opacity:0}}}}"
          ".cur{animation:fin 26s steps(1) infinite, blink2 1s steps(1) infinite}"
          "@keyframes blink2{50%{fill-opacity:0}}")
    return s


# ---------------------------------------------------------------------------
# 4. Research cards
# ---------------------------------------------------------------------------
def card_frame(s, t, tag, title):
    s.add(f'<rect x="1" y="1" width="{s.w - 2}" height="{s.h - 2}" rx="16" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    g, _, _ = s.text(tag, 22, 32, 11.5, "mono", t["acc"], tracking=0.1)
    s.add(g)
    g, _, _ = s.text(title, 22, s.h - 22, 19, "serif", t["ink"])
    s.add(g)


def card_social(mode):
    t = THEMES[mode]
    s = Svg(420, 270, "Animated card: social media and real-life confidence study, 211 participants")
    card_frame(s, t, "FEATURED STUDY · N = 211", "Social media & real-life confidence")
    # phone
    px, py, pw, ph = 38, 50, 104, 168
    s.gdef(f'<clipPath id="scr"><rect x="{px + 7}" y="{py + 16}" width="{pw - 14}" height="{ph - 30}" rx="6"/></clipPath>')
    s.add(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="16" fill="{t["panel2"]}" stroke="{t["muted"]}" stroke-width="1.5"/>'
          f'<rect x="{px + pw / 2 - 14}" y="{py + 6}" width="28" height="4" rx="2" fill="{t["muted"]}"/>')
    posts = []
    cols = [t["acc"], t["warm"], t["pink"], t["ok"], t["yellow"]]
    for k in range(10):
        yy = py + 22 + k * 46
        c = cols[k % 5]
        posts.append(f'<g transform="translate({px + 12} {yy})"><rect width="80" height="40" rx="6" fill="{t["panel"]}"/>'
                     f'<circle cx="10" cy="10" r="5" fill="{c}"/><rect x="20" y="7" width="40" height="5" rx="2.5" fill="{t["line"]}"/>'
                     f'<rect x="6" y="20" width="68" height="14" rx="3" fill="{c}" opacity=".35"/></g>')
    s.add(f'<g clip-path="url(#scr)"><g class="feed">' + "".join(posts) + "</g></g>")
    s.css(".feed{animation:feed 7s linear infinite}@keyframes feed{to{transform:translateY(-230px)}}")
    # floating hearts
    heart = "M0 3 C0 -1 -6 -1 -6 3 C-6 6 0 9 0 11 C0 9 6 6 6 3 C6 -1 0 -1 0 3Z"
    for k, (hx, d) in enumerate([(128, 0), (118, 1.3), (134, 2.6)]):
        s.add(f'<g transform="translate({hx} 150)"><path d="{heart}" fill="{t["pink"]}" class="hrt" style="animation-delay:{d}s"/></g>')
    s.css(".hrt{opacity:0;animation:hrt 3.9s ease-out infinite}"
          "@keyframes hrt{0%{opacity:0;transform:translate(0,0) scale(.6)}15%{opacity:1}100%{opacity:0;transform:translate(22px,-90px) scale(1.2)}}")
    # bar chart: most-used platforms
    bars = [("IG", 93.3), ("TT", 84.6), ("SC", 83.2), ("YT", 72.2), ("FB", 34.1)]
    bx, base, bh = 190, 196, 120
    for k, (lab, v) in enumerate(bars):
        x = bx + k * 40
        h = bh * v / 100
        col = t["warm"] if k == 0 else t["acc"]
        s.add(f'<rect x="{x}" y="{base - bh}" width="24" height="{bh}" rx="4" fill="{t["line"]}" opacity=".35"/>')
        s.add(f'<g transform="translate({x} {base})"><rect class="bar" x="0" y="{-h:.1f}" width="24" height="{h:.1f}" rx="4" fill="{col}" '
              f'style="animation-delay:{k * 0.12:.2f}s;transform-origin:0 0"/></g>')
        g, _, _ = s.text(lab, x + 12, base + 17, 11, "mono", t["muted"], anchor="middle")
        s.add(g)
        g, _, _ = s.text(f"{v:.0f}", x + 12, base - h - 7, 11, "monob", t["soft"], anchor="middle", cls="bv",
                         attrs=f' style="animation-delay:{0.6 + k * 0.12:.2f}s"')
        s.add(g)
    s.css(".bar{animation:grow 7s cubic-bezier(.22,1,.36,1) infinite}"
          "@keyframes grow{0%{transform:scaleY(0)}18%,85%{transform:scaleY(1)}95%,100%{transform:scaleY(0)}}"
          ".bv{opacity:0;animation:bv 7s ease infinite}@keyframes bv{0%,12%{opacity:0}20%,82%{opacity:1}90%,100%{opacity:0}}")
    g, _, _ = s.text("% using each platform", 190, 62, 11, "mono", t["muted"])
    s.add(g)
    return s


def card_nasa(mode):
    t = THEMES[mode]
    s = Svg(420, 270, "Animated card: NASA HERA Mars analog and Project FUSION, mission control")
    card_frame(s, t, "NASA #80NSSC23K1124 · MISSION CONTROL", "NASA HERA · Project FUSION")
    stars(s, t, 40, (10, 44, 410, 225), seed=21, rmax=1.3, cls="tw2")
    cx, cy, r = 150, 140, 58
    s.gdef('<radialGradient id="mars" cx=".35" cy=".35" r=".75"><stop offset="0" stop-color="#f2a27a"/>'
           '<stop offset=".6" stop-color="#c8562e"/><stop offset="1" stop-color="#6e2412"/></radialGradient>'
           f'<clipPath id="planet"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    # orbit (back half)
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="104" ry="28" fill="none" stroke="{t["muted"]}" stroke-opacity=".45" stroke-dasharray="3 5" transform="rotate(-14 {cx} {cy})"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#mars)"/>')
    craters = []
    rnd = random.Random(5)
    P = 130
    base_craters = [(rnd.uniform(0, P), rnd.uniform(cy - 50, cy + 50), rnd.uniform(3, 9)) for _ in range(8)]
    for rep in (0, 1):
        for x, y, rr in base_craters:
            craters.append(f'<circle cx="{cx - r + x + rep * P:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="#5a1d0e" opacity=".35"/>')
    s.add(f'<g clip-path="url(#planet)"><g class="spinp">' + "".join(craters) + "</g></g>")
    s.css(".spinp{animation:spinp 16s linear infinite}@keyframes spinp{from{transform:translateX(0)}to{transform:translateX(-130px)}}")
    # terminator shading
    s.add(f'<circle cx="{cx + 18}" cy="{cy + 10}" r="{r}" fill="#000" opacity=".22" clip-path="url(#planet)"/>')
    # orbiting habitat along a rotated ellipse
    s.add(f'<g transform="rotate(-14 {cx} {cy})"><g>'
          f'<g><rect x="-7" y="-4" width="14" height="8" rx="3" fill="{t["ink"]}"/><rect x="-16" y="-2" width="7" height="4" fill="{t["acc"]}"/>'
          f'<rect x="9" y="-2" width="7" height="4" fill="{t["acc"]}"/>'
          f'<animateMotion dur="9s" repeatCount="indefinite" path="M{cx + 104} {cy} A104 28 0 1 1 {cx - 104} {cy} A104 28 0 1 1 {cx + 104} {cy}"/></g></g></g>')
    # front half of orbit over planet
    s.add(f'<path d="M{cx - 104} {cy} A104 28 0 0 0 {cx + 104} {cy}" fill="none" stroke="{t["muted"]}" stroke-opacity=".6" stroke-dasharray="3 5" transform="rotate(-14 {cx} {cy})"/>')
    # mission control console
    mx, my = 262, 64
    s.add(f'<rect x="{mx}" y="{my}" width="138" height="128" rx="10" fill="{t["panel2"]}" stroke="{t["line"]}"/>')
    g, _, _ = s.text("HERA · MCC", mx + 12, my + 22, 11, "monob", t["soft"], tracking=0.08); s.add(g)
    for k, (lab, col, d) in enumerate([("COMMS", t["ok"], 0), ("CREW", t["ok"], .4), ("BUDGET", t["yellow"], .8), ("SIM", t["warm"], 1.2)]):
        yy = my + 44 + k * 20
        s.add(f'<circle cx="{mx + 16}" cy="{yy - 4}" r="4" fill="{col}" class="led" style="animation-delay:{d}s"/>')
        g, _, _ = s.text(lab, mx + 28, yy, 11, "mono", t["muted"]); s.add(g)
        s.add(f'<rect x="{mx + 84}" y="{yy - 8}" width="40" height="6" rx="3" fill="{t["line"]}"/>'
              f'<rect x="{mx + 84}" y="{yy - 8}" width="40" height="6" rx="3" fill="{col}" class="meter" style="animation-delay:-{d * 2}s;transform-origin:{mx + 84}px 0"/>')
    s.css(".led{animation:led 1.6s ease-in-out infinite}@keyframes led{0%,100%{opacity:.35}50%{opacity:1}}"
          ".meter{animation:meter 3s ease-in-out infinite}@keyframes meter{0%,100%{transform:scaleX(.3)}50%{transform:scaleX(.95)}}")
    # comm signal arcs from console to planet
    for k in range(3):
        s.add(f'<path d="M{mx - 6} {my + 60} q-14 -14 0 -28" transform="translate({-k * 0} 0)" fill="none" stroke="{t["acc"]}" stroke-width="2" '
              f'stroke-linecap="round" class="sig" style="animation-delay:{k * 0.45:.2f}s"/>')
    s.css(".sig{opacity:0;animation:sig 1.35s ease-out infinite}"
          "@keyframes sig{0%{opacity:0;transform:translateX(0)}30%{opacity:1}100%{opacity:0;transform:translateX(-40px)}}")
    return s


def card_tones(mode):
    t = THEMES[mode]
    s = Svg(420, 270, "Animated card: when do two tones become two, an auditory timing perception study")
    card_frame(s, t, "TAP LAB · TIMING, ATTENTION & PERCEPTION", "When do two tones become two?")
    base = 134
    s.add(f'<line x1="22" y1="{base}" x2="398" y2="{base}" stroke="{t["line"]}" stroke-width="1"/>')

    def burst(cx, amp, col, cls):
        pts = []
        for i in range(0, 121):
            x = -30 + i * 0.5
            env = math.exp(-((x) / 13) ** 2)
            y = -amp * env * math.sin(x * 1.25)
            pts.append(f"{x:.1f},{y:.1f}")
        return (f'<g transform="translate({cx} {base})"><g class="{cls}"><polyline points="{" ".join(pts)}" fill="none" '
                f'stroke="{col}" stroke-width="2.4" stroke-linejoin="round"/></g></g>')

    s.add(burst(150, 46, t["acc"], "tA"))
    s.add(burst(270, 46, t["warm"], "tB"))
    # tone B slides toward A and back; A pulses
    s.css(".tB{animation:slide 8s cubic-bezier(.65,0,.35,1) infinite}"
          "@keyframes slide{0%,10%{transform:translateX(0)}45%,60%{transform:translateX(-104px)}95%,100%{transform:translateX(0)}}"
          ".tA{animation:pulse 1s ease-in-out infinite;transform-origin:0 0}"
          ".tB polyline{animation:pulse 1s ease-in-out infinite .5s;transform-origin:0 0}"
          "@keyframes pulse{0%,100%{transform:scaleY(.85)}50%{transform:scaleY(1.05)}}")
    # Δt dimension line between peaks (shrinks with the slide)
    s.add(f'<g transform="translate(150 196)"><g class="dt">'
          f'<line x1="0" y1="0" x2="120" y2="0" stroke="{t["muted"]}" stroke-width="1.4"/>'
          f'<line x1="0" y1="-6" x2="0" y2="6" stroke="{t["muted"]}" stroke-width="1.4"/>'
          f'<line x1="120" y1="-6" x2="120" y2="6" stroke="{t["muted"]}" stroke-width="1.4" class="dtR"/></g></g>')
    s.css(".dt line:first-child{animation:dtw 8s cubic-bezier(.65,0,.35,1) infinite;transform-origin:0 0}"
          "@keyframes dtw{0%,10%{transform:scaleX(1)}45%,60%{transform:scaleX(.133)}95%,100%{transform:scaleX(1)}}"
          ".dtR{animation:slide 8s cubic-bezier(.65,0,.35,1) infinite}")
    g, _, _ = s.text("Δt", 200, 216, 13, "monob", t["soft"], anchor="middle"); s.add(g)
    two, _, _ = s.text("“two tones”", 398, 70, 14, "mono", t["acc"], anchor="end", cls="lab2"); s.add(two)
    one, _, _ = s.text("“one tone?”", 398, 70, 14, "mono", t["warm"], anchor="end", cls="lab1"); s.add(one)
    s.css(".lab2{animation:l2 8s ease infinite}.lab1{opacity:0;animation:l1 8s ease infinite}"
          "@keyframes l2{0%,30%{opacity:1}38%,72%{opacity:0}80%,100%{opacity:1}}"
          "@keyframes l1{0%,32%{opacity:0}40%,70%{opacity:1}78%,100%{opacity:0}}")
    # little listener icon (head with sound arcs)
    s.add(f'<g transform="translate(46 84)" fill="none" stroke="{t["muted"]}" stroke-width="1.6" stroke-linecap="round">'
          f'<path d="M0 0 a10 10 0 1 1 6 9 v6 h-6"/><path d="M14 -4 q5 4 0 8" class="arc1"/><path d="M19 -8 q9 8 0 16" class="arc2"/></g>')
    s.css(".arc1,.arc2{animation:led 1.2s ease-in-out infinite}.arc2{animation-delay:.3s}"
          "@keyframes led{0%,100%{opacity:.25}50%{opacity:1}}")
    return s


# ---------------------------------------------------------------------------
# 5. Research pipeline with a travelling pulse
# ---------------------------------------------------------------------------
def pipeline(mode):
    t = THEMES[mode]
    W, H = 1000, 262
    s = Svg(W, H, "Research workflow: question, design, collect, analyze, report, and back to new questions")
    steps = [("Question", "what about people?"), ("Design", "validated scales · Qualtrics"), ("Collect", "SONA · lab sessions"),
             ("Analyze", "SPSS · R · Python"), ("Report", "Quarto · reproducible")]
    xs = [100 + i * 200 for i in range(5)]
    y = 92
    cyc = 7.5
    s.add(f'<path d="M{xs[0]} {y} H{xs[-1]}" stroke="{t["line"]}" stroke-width="2.5"/>')
    s.add(f'<path d="M{xs[-1] + 60} {y + 96} C{xs[-1] + 60} {y + 148}, {xs[0] - 60} {y + 148}, {xs[0] - 60} {y + 96}" fill="none" stroke="{t["line"]}" '
          f'stroke-width="1.6" stroke-dasharray="4 6" class="ret"/>')
    s.css(".ret{animation:dash 1.4s linear infinite}@keyframes dash{to{stroke-dashoffset:-20}}")
    s.add(f'<rect x="{W / 2 - 70}" y="{y + 124}" width="140" height="24" rx="12" fill="{t["bg1"] if mode == "dark" else t["panel"]}"/>')
    g, _, _ = s.text("new questions", W / 2, y + 140, 12, "mono", t["muted"], anchor="middle"); s.add(g)
    # progress fill along the main line
    s.add(f'<path d="M{xs[0]} {y} H{xs[-1]}" stroke="{t["acc"]}" stroke-width="2.5" pathLength="1" class="fill"/>')
    s.css(f".fill{{stroke-dasharray:1;stroke-dashoffset:1;animation:fill {cyc}s linear infinite}}"
          "@keyframes fill{0%{stroke-dashoffset:1}70%{stroke-dashoffset:0}88%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}")
    icons = {
        "Question": f'<path d="M-6 -6 a6 6 0 1 1 6 6 v4" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><circle cx="0" cy="10" r="1.8" fill="currentColor"/>',
        "Design": '<rect x="-9" y="-10" width="18" height="20" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M-5 -4h10M-5 1h10M-5 6h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        "Collect": '<circle cx="-5" cy="-3" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="6" cy="-3" r="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M-12 10 q7 -9 14 0 M0 10 q7 -9 14 0" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
        "Analyze": '<path d="M-10 10 V-10 M-10 10 H10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="-5" cy="4" r="1.8" fill="currentColor"/><circle cx="0" cy="-1" r="1.8" fill="currentColor"/><circle cx="5" cy="1" r="1.8" fill="currentColor"/><circle cx="8" cy="-6" r="1.8" fill="currentColor"/><path d="M-8 6 L9 -8" stroke="currentColor" stroke-width="1.6"/>',
        "Report": '<path d="M-8 -11 h11 l6 6 v16 h-17z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M-4 0 h8 M-4 5 h8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
    }
    for i, ((name, sub), x) in enumerate(zip(steps, xs)):
        arrive = i * 0.7 * cyc / 4 if i else 0.0
        a_pct = arrive / cyc * 100
        s.add(f'<g transform="translate({x} {y})">'
              f'<circle r="34" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>'
              f'<circle r="34" fill="none" stroke="{t["acc"]}" stroke-width="2.5" class="ring r{i}"/>'
              f'<circle r="34" fill="none" stroke="{t["acc"]}" stroke-width="2" class="ping p{i}"/>'
              f'<g style="color:{t["ink"]}">{icons[name]}</g></g>')
        s.css(f".r{i}{{opacity:0;animation:r{i} {cyc}s ease infinite}}"
              f"@keyframes r{i}{{0%,{max(a_pct - 0.1, 0):.2f}%{{opacity:0}}{a_pct + 1:.2f}%,88%{{opacity:1}}100%{{opacity:0}}}}"
              f".p{i}{{opacity:0;animation:p{i} {cyc}s ease-out infinite;transform-origin:0 0}}"
              f"@keyframes p{i}{{0%,{max(a_pct - 0.1, 0):.2f}%{{opacity:0;transform:scale(1)}}{a_pct + 0.5:.2f}%{{opacity:.9;transform:scale(1)}}"
              f"{a_pct + 12:.2f}%{{opacity:0;transform:scale(1.7)}}100%{{opacity:0}}}}")
        g, _, _ = s.text(name, x, y + 60, 17, "sansb", t["ink"], anchor="middle"); s.add(g)
        g, _, _ = s.text(sub, x, y + 80, 11.5, "mono", t["muted"], anchor="middle"); s.add(g)
    # travelling comet
    s.gdef(f'<radialGradient id="comet"><stop offset="0" stop-color="{t["warm"]}"/><stop offset="1" stop-color="{t["warm"]}" stop-opacity="0"/></radialGradient>')
    s.add(f'<g><circle r="13" fill="url(#comet)"/><circle r="4.5" fill="{t["warm"]}"/>'
          f'<animateMotion dur="{cyc}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.7;1" calcMode="linear" path="M{xs[0]} {y} H{xs[-1]}"/>'
          f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.7;.74;1" dur="{cyc}s" repeatCount="indefinite"/></g>')
    return s


# ---------------------------------------------------------------------------
# 6. Toolkit orbit
# ---------------------------------------------------------------------------
def toolkit(mode):
    t = THEMES[mode]
    W, H = 1000, 470
    s = Svg(W, H, "Toolkit: R, Python, Quarto, SPSS, Git, GitHub, Jupyter, pandas, LaTeX, Qualtrics")
    cx, cy = W / 2, H / 2
    stars(s, t, 50, (20, 20, W - 20, H - 20), seed=9, rmax=1.2, cls="tw3")
    for r, op in [(112, .7), (186, .5)]:
        s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["line"]}" stroke-width="1.4" stroke-dasharray="2 7" opacity="{op}"/>')
    # core
    s.gdef(f'<radialGradient id="core"><stop offset="0" stop-color="{t["acc2"]}" stop-opacity=".5"/><stop offset="1" stop-color="{t["acc2"]}" stop-opacity="0"/></radialGradient>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="78" fill="url(#core)" class="breathe2"/>')
    s.css(f".breathe2{{animation:br2 5s ease-in-out infinite;transform-origin:{cx}px {cy}px}}@keyframes br2{{50%{{transform:scale(1.15)}}}}")
    s.add(f'<circle cx="{cx}" cy="{cy}" r="46" fill="{t["panel"]}" stroke="{t["acc"]}" stroke-width="1.6"/>')
    g, _, _ = s.text("toolkit", cx, cy - 2, 13, "monob", t["acc"], anchor="middle"); s.add(g)
    g, _, _ = s.text("psych × data", cx, cy + 16, 10.5, "mono", t["muted"], anchor="middle"); s.add(g)

    dark = mode == "dark"
    tools_inner = [("r", "#276DC3", "R"), ("python", "#3776AB", "Python"), ("quarto", "#39729E", "Quarto"), (None, "#052FAD", "IBM")]
    tools_outer = [("git", "#F03C2E", "Git"), ("github", "#ffffff" if dark else "#181717", "GitHub"), ("jupyter", "#F37626", "Jupyter"),
                   ("pandas", "#e70488" if dark else "#150458", "pandas"), ("latex", "#47b3b3" if dark else "#008080", "LaTeX"),
                   ("qualtrics", "#00B4EF", "Qualtrics")]

    def chip(slug, col, label):
        inner = (f'<g transform="translate(-14 -20) scale(1.1667)"><path d="{icon_path(slug)}" fill="{col}"/></g>' if slug
                 else s.text("SPSS", 0, -2, 14, "monob", "#4d74e6" if dark else col, anchor="middle")[0])
        lab, _, _ = s.text(label, 0, 22, 10.5, "mono", t["muted"], anchor="middle")
        return (f'<circle r="34" fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="1.4"/>' + inner + lab)

    for ring, (tools, r, dur, cls) in enumerate([(tools_inner, 112, 36, "o1"), (tools_outer, 186, 60, "o2")]):
        items = []
        for k, (slug, col, label) in enumerate(tools):
            ang = 2 * math.pi * k / len(tools) - math.pi / 2 + ring * 0.4
            x, y = r * math.cos(ang), r * math.sin(ang)
            items.append(f'<g transform="translate({x:.1f} {y:.1f})"><g class="{cls}c">{chip(slug, col, label)}</g></g>')
        s.add(f'<g transform="translate({cx} {cy})"><g class="{cls}">' + "".join(items) + "</g></g>")
        sign = 1 if ring == 0 else -1
        s.css(f".{cls}{{animation:{cls} {dur}s linear infinite}}@keyframes {cls}{{to{{transform:rotate({sign * 360}deg)}}}}"
              f".{cls}c{{animation:{cls}c {dur}s linear infinite}}@keyframes {cls}c{{to{{transform:rotate({-sign * 360}deg)}}}}")
    return s


# ---------------------------------------------------------------------------
# 7. Count-up stats
# ---------------------------------------------------------------------------
def stats(mode):
    t = THEMES[mode]
    W, H = 1000, 160
    s = Svg(W, H, "By the numbers: 3.9 GPA, 211 survey participants, 50+ audio recordings coded, "
                  "35+ articles reviewed, 5 research roles, 3 languages")
    items = [(3.9, "{:.1f}", "", "GPA · Highest Honors"), (211, "{:.0f}", "", "survey participants"),
             (50, "{:.0f}", "+", "recordings coded"), (35, "{:.0f}", "+", "articles reviewed"),
             (5, "{:.0f}", "", "research roles"), (3, "{:.0f}", "", "languages")]
    cyc, frames, count_t = 12.0, 16, 1.6
    tw = (W - 5 * 14) / 6
    for k, (val, fmt, suf, label) in enumerate(items):
        x = k * (tw + 14)
        s.add(f'<rect x="{x + 1:.1f}" y="1" width="{tw - 2:.1f}" height="{H - 2}" rx="14" fill="{t["panel"]}" stroke="{t["line"]}"/>')
        cxm = x + tw / 2
        delay = k * 0.15
        for fi in range(frames + 1):
            p = fi / frames
            eased = 1 - (1 - p) ** 3
            v = val * eased
            txt = fmt.format(v) + (suf if fi == frames else "")
            t0 = delay + count_t * fi / frames
            t1 = delay + count_t * (fi + 1) / frames if fi < frames else cyc - 0.4
            g, _, _ = s.text(txt, cxm, 82, 46, "serif", t["ink"] if fi == frames else t["soft"], anchor="middle", attrs=' opacity="0"')
            g = g.replace(' opacity="0">', f' opacity="0"><animate attributeName="opacity" values="0;1;0" '
                          f'keyTimes="0;{t0 / cyc:.4f};{t1 / cyc:.4f}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>', 1)
            s.add(g)
        g, _, _ = s.text(label, cxm, 116, 12.5, "sans", t["muted"], anchor="middle"); s.add(g)
        s.add(f'<rect x="{x + 22:.1f}" y="134" width="{tw - 44:.1f}" height="4" rx="2" fill="{t["line"]}"/>')
        s.add(f'<rect x="{x + 22:.1f}" y="134" width="{tw - 44:.1f}" height="4" rx="2" fill="{t["warm"] if k == 0 else t["acc"]}" '
              f'class="sb" style="transform-origin:{x + 22:.1f}px 0;animation-delay:{delay:.2f}s"/>')
    s.css(f".sb{{animation:sb {cyc}s cubic-bezier(.22,1,.36,1) infinite}}"
          f"@keyframes sb{{0%{{transform:scaleX(0)}}{count_t / cyc * 100:.1f}%,95%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}")
    return s


# ---------------------------------------------------------------------------
# 8. Stroop effect mini-experiment
# ---------------------------------------------------------------------------
def stroop(mode):
    t = THEMES[mode]
    W, H = 1000, 250
    s = Svg(W, H, "Stroop effect demo: color words shown in mismatched ink colors. Name the ink color, not the word.")
    s.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t["panel"]}" stroke="{t["line"]}"/>')
    g, _, _ = s.text("TRY IT  ·  SAY THE INK COLOR, NOT THE WORD", 34, 44, 12.5, "monob", t["acc"], tracking=0.12); s.add(g)
    ink = {"red": "#e5484d", "blue": "#3e7bfa", "green": "#2fa86b", "yellow": "#e0a800", "purple": "#9b5de5"}
    seq = [("RED", "blue"), ("GREEN", "purple"), ("BLUE", "yellow"), ("YELLOW", "red"), ("PURPLE", "green"), ("BLUE", "red")]
    per = 1.6
    cyc = per * len(seq)
    cx, cy = 300, 158
    for k, (word, col) in enumerate(seq):
        t0, t1 = k * per / cyc, (k + 1) * per / cyc
        g, _, _ = s.text(word, cx, cy, 78, "sansb", ink[col], anchor="middle", attrs=' opacity="0"')
        anim = (f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{t0:.4f};{t1:.4f}" dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/>')
        s.add(g.replace(' opacity="0">', f' opacity="0">{anim}', 1))
    # per-trial timer bar
    s.add(f'<rect x="{cx - 160}" y="196" width="320" height="5" rx="2.5" fill="{t["line"]}"/>'
          f'<rect x="{cx - 160}" y="196" width="320" height="5" rx="2.5" fill="{t["warm"]}" class="timer" style="transform-origin:{cx - 160}px 0"/>')
    s.css(f".timer{{animation:timer {per}s linear infinite}}@keyframes timer{{from{{transform:scaleX(1)}}to{{transform:scaleX(0)}}}}")
    # trial dots
    for k in range(len(seq)):
        s.add(f'<circle cx="{cx - 50 + k * 20}" cy="222" r="4" fill="{t["line"]}"/>')
    s.add(f'<circle cy="222" r="4" fill="{t["acc"]}"><animate attributeName="cx" values="{";".join(str(cx - 50 + k * 20) for k in range(len(seq)))}" '
          f'dur="{cyc}s" calcMode="discrete" repeatCount="indefinite"/></circle>')
    # explainer on the right
    s.add(f'<line x1="610" y1="70" x2="610" y2="210" stroke="{t["line"]}"/>')
    g, _, _ = s.text("Felt that tiny delay?", 646, 100, 24, "serif", t["ink"]); s.add(g)
    for i, ln in enumerate(["That’s the Stroop effect (Stroop, 1935).",
                            "Reading is so automatic that the word",
                            "interferes with naming the ink. It’s one",
                            "of the most replicated findings in psychology."]):
        g, _, _ = s.text(ln, 646, 134 + i * 22, 14.5, "sans", t["muted"]); s.add(g)
    return s


# ---------------------------------------------------------------------------
# 9. Footer: brain-wave sweep
# ---------------------------------------------------------------------------
def footer(mode):
    t = THEMES[mode]
    W, H = 1200, 170
    s = Svg(W, H, "Thanks for stopping by. Let's build better evidence about people.")
    bg(s, t, rx=22, grad_id="fbg")
    stars(s, t, 40, (10, 10, W - 10, H - 10), seed=31, rmax=1.3, cls="tw4")
    # EEG-like path
    rnd = random.Random(4)
    pts = []
    x = 0
    while x <= W:
        burst = 1.0 if (x % 400) < 70 else 0.35
        y = 62 + math.sin(x * 0.09) * 6 * burst + rnd.gauss(0, 5 * burst)
        pts.append(f"{x:.0f},{y:.1f}")
        x += 6
    d = "M" + " L".join(pts)
    s.add(f'<path d="{d}" fill="none" stroke="{t["line"]}" stroke-width="1.6"/>')
    s.gdef(f'<linearGradient id="eegg" x1="0" x2="1"><stop offset="0" stop-color="{t["acc"]}" stop-opacity="0"/>'
           f'<stop offset=".85" stop-color="{t["acc"]}"/><stop offset="1" stop-color="{t["warm"]}"/></linearGradient>')
    s.add(f'<path d="{d}" fill="none" stroke="{t["acc"]}" stroke-width="2.2" stroke-linecap="round" pathLength="100" class="eeg"/>')
    s.css(".eeg{stroke-dasharray:14 86;animation:eeg 5s linear infinite}@keyframes eeg{from{stroke-dashoffset:14}to{stroke-dashoffset:-86}}")
    g, _, _ = s.text("thanks for stopping by", W / 2, 122, 30, "display", t["ink"], anchor="middle"); s.add(g)
    g, _, _ = s.text("let’s build better evidence about people", W / 2, 150, 13, "mono", t["muted"], anchor="middle", tracking=0.06); s.add(g)
    return s


PIECES = {
    "header": header, "typing": typing, "console": console, "card-social": card_social, "card-nasa": card_nasa,
    "card-tones": card_tones, "pipeline": pipeline, "toolkit": toolkit, "stats": stats, "stroop": stroop, "footer": footer,
}

if __name__ == "__main__":
    import sys
    only = sys.argv[1:] or list(PIECES)
    for name in only:
        for mode in ("light", "dark"):
            size = write(os.path.join(OUT, f"{name}-{mode}.svg"), PIECES[name](mode))
            print(f"{name}-{mode}.svg  {size / 1024:.1f} KB")
