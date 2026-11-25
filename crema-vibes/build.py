#!/usr/bin/env python3
"""Crema Vibes — Bespoke Editorial Sans & Icon Font Builder.

Generates TrueType (TTF), OpenType (OTF), WOFF, and WOFF2 font files across
9 weights (UltraThin 100 to Dark 900) with proportional advance widths, smooth
cubic Bézier splines, exact horizontal diagonal terminals, seamless U/u bases,
refined lining figures (0–9), and embedded Crema Vibes icons (U+E001–U+E014).
"""
import math
from pathlib import Path
import numpy as np
from shapely.geometry import box, Polygon, Point, LineString
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.svgLib.path import SVGPath
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0

FAMILY = 'Crema Vibes'
OUT = Path(__file__).resolve().parent.parent
WEIGHTS = [
    (100, 'UltraThin'),
    (200, 'Thin'),
    (300, 'Light'),
    (400, 'Regular'),
    (500, 'Medium'),
    (600, 'SemiBold'),
    (700, 'Bold'),
    (800, 'ExtraBold'),
    (900, 'Dark'),
]

UPM = 1000
ASC = 800
DESC = -200
CAP = 700
XH = 500

ICONS = {
    'arrow-up': (0xE001, 'M512 768L256 384h192v-384h128v384h192z'),
    'menu': (0xE002, 'M128 704v-64h768v64h-768zM128 384v-64h768v64h-768zM128 64v-64h768v64h-768z'),
    'search': (0xE003, 'M652 96c-194 0-352 158-352 352s158 352 352 352 352-158 352-352-158-352-352-352zM652 736c-159 0-288-129-288-288s129-288 288-288 288 129 288 288-129 288-288 288zM906 80l-44-44-168 168 44 44z'),
    'trending-up': (0xE004, 'M128 640l256-256 192 192 320-320v192h-64v-96l-256 256-192-192-192 192zM832 192h128v128h-64v-64h-64z'),
    'chip': (0xE005, 'M320 192v512h384v-512h-384zM576 640h-128v-384h128v384zM256 384h-128v-64h128v-128h64v512h-64v-128h-128v-64h128zM640 128h64v128h128v64h-128v128h128v64h-128v128h-64zM384 0h64v128h-64zM512 0h64v128h-64zM384 768h64v128h-64zM512 768h64v128h-64zM896 384h128v64h-128zM896 512h128v64h-128zM0 384h128v64h-128zM0 512h128v64h-128z'),
    'document': (0xE006, 'M192 64v768h384v-256h256v-512h-640zM640 704l128-128h-128v128zM128 0h630l162 162v666q0 26-19 45t-45 19h-640q-26 0-45-19t-19-45v-768q0-26 19-45t45-19zM256 448h384v64h-384v-64zM256 576h384v64h-384v-64zM256 320h256v64h-256v-64z'),
    'target': (0xE007, 'M512 64c-247 0-448 201-448 448s201 448 448 448 448-201 448-448-201-448-448-448zM512 896c-212 0-384-172-384-384s172-384 384-384 384 172 384 384-172 384-384 384zM512 192c-177 0-320 143-320 320s143 320 320 320 320-143 320-320-143-320-320-320zM512 768c-141 0-256-115-256-256s115-256 256-256 256 115 256 256-115 256-256 256zM512 320c-106 0-192 86-192 192s86 192 192 192 192-86 192-192-86-192-192-192zM512 640c-71 0-128-57-128-128s57-128 128-128 128 57 128 128-57 128-128 128z'),
    'bar-chart': (0xE008, 'M128 128h128v512h-128v-512zM320 256h128v384h-128v-384zM512 64h128v576h-128v-576zM768 384h128v256h-128v-256z'),
    'layers': (0xE009, 'M512 128l-384 192 384 192 384-192-384-192zM512 416l-256-128 256-128 256 128-256 128zM128 512l384 192 384-192-64-32-320 160-320-160zM128 640l384 192 384-192-64-32-320 160-320-160z'),
    'chat-bubble': (0xE010, 'M832 384q0 80-40 149t-109 109-149 40q-72 0-135-34l-183 48 48-183q-34-63-34-135 0-80 40-149t109-109 149-40 149 40 109 109 40 149zM512 128c-177 0-320 143-320 320 0 64 19 124 52 176l-36 140 140-36c52 33 112 52 176 52 177 0 320-143 320-320s-143-320-320-320z'),
    'megaphone': (0xE011, 'M128 320v256l512 256v-768zM576 224v384l-384-192v-192zM832 416c53 0 96-43 96-96s-43-96-96-96v192zM704 576h-64v-320h64c0-141 115-256 256-256v64c-106 0-192 86-192 192v320z'),
    'linkedin': (0xE012, 'M256 704v-448h-128v448h128zM192 320c35 0 64 29 64 64s-29 64-64 64-64-29-64-64 29-64 64-64zM320 256h128v64c17-43 64-85 149-85 128 0 163 85 163 213v256h-128v-213c0-53-21-85-75-85-64 0-96 43-96 107v191h-128v-448z'),
    'whatsapp': (0xE013, 'M512 64c-247 0-448 201-448 448 0 88 26 171 71 241l-48 175 175-48c70 45 153 71 241 71 247 0 448-201 448-448s-201-448-448-448zM512 857c-78 0-152-24-214-65l-15-9-107 28 28-104-10-16c-44-62-68-136-68-214 0-202 164-366 366-366s366 164 366 366-164 366-366 366zM693 576c-10-5-61-30-71-33s-17-5-24 5c-7 10-28 33-34 40-6 7-12 8-23 3-10-5-44-16-84-51-31-27-52-61-58-71-6-10-1-16 4-21 5-5 10-12 16-18 5-6 7-10 10-17 3-7 2-13-1-18s-22-54-31-74c-8-19-16-16-23-17h-19c-7 0-17 2-26 12s-35 34-35 83 36 97 41 103c5 6 71 106 171 148 24 10 43 16 57 21 24 8 46 6 63 3 19-3 61-25 69-49 9-24 9-45 6-49s-10-7-19-11z'),
    'email': (0xE014, 'M128 192v512q0 26 19 45t45 19h640q26 0 45-19t19-45v-512q0-26-19-45t-45-19h-640q-26 0-45 19t-19 45zM192 192h640v64l-320 192-320-192v-64zM192 320l320 192 320-192v384h-640v-384z'),
}

EXTRA_CHARS = [
    ('\u2013', 'endash'),
    ('\u2014', 'emdash'),
    ('\u2022', 'bullet'),
    ('\u2018', 'quoteleft'),
    ('\u2019', 'quoteright'),
    ('\u201C', 'quotedblleft'),
    ('\u201D', 'quotedblright'),
]

# --- Geometry Helpers ---

def signed_area(pts):
    return sum(pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1] for i in range(len(pts) - 1))

def contour_to_pen(pen, coords, want_cw):
    pts = list(coords)
    if len(pts) < 3:
        return
    if (signed_area(pts) < 0) != want_cw:
        pts.reverse()
    pen.moveTo((round(pts[0][0]), round(pts[0][1])))
    for p in pts[1:-1]:
        pen.lineTo((round(p[0]), round(p[1])))
    pen.closePath()

def pen_from_geom(geom, is_cff=False):
    pen = T2CharStringPen(None, None) if is_cff else TTGlyphPen(None)
    geoms = getattr(geom, 'geoms', [geom])
    for item in geoms:
        if item.is_empty or item.geom_type != 'Polygon':
            continue
        contour_to_pen(pen, item.exterior.coords, not is_cff)
        for hole in item.interiors:
            contour_to_pen(pen, hole.coords, is_cff)
    return pen.getCharString() if is_cff else pen.glyph()

def bezier_cubic(p0, p1, p2, p3, n=32):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3

def make_ellipse(cx, cy, rx, ry, n=64):
    theta = np.linspace(0, 2 * np.pi, n)
    return Polygon([(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta])

def make_ring(cx, cy, rx, ry, stroke_x, stroke_y, n=64):
    theta = np.linspace(0, 2 * np.pi, n)
    outer = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta]
    rx_in = max(5, rx - stroke_x)
    ry_in = max(5, ry - stroke_y)
    inner = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta)]
    return Polygon(outer, [inner])

def make_arc_strip(cx, cy, rx, ry, a_rad, b_rad, stroke_x, stroke_y, n=48):
    theta = np.linspace(a_rad, b_rad, n)
    outer = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta]
    rx_in = max(5, rx - stroke_x)
    ry_in = max(5, ry - stroke_y)
    inner = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta)]
    return Polygon(outer + inner)

def make_bowl_right(x_stem, y_bot, y_top, width, stroke_x, stroke_y, n=48):
    """Smooth D-bowl extending rightward from x_stem with horizontal tangents (no V-notch)."""
    cy = (y_top + y_bot) * 0.5
    ry = (y_top - y_bot) * 0.5
    flat = min(50.0, width * 0.22)
    cx = x_stem + flat
    rx = max(20.0, width - flat)
    theta = np.linspace(-np.pi * 0.5, np.pi * 0.5, n)
    outer = [(x_stem, y_bot), (cx, y_bot)] + [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta[1:-1]] + [(cx, y_top), (x_stem, y_top)]
    outer_poly = Polygon(outer)
    rx_in = max(5.0, rx - stroke_x)
    ry_in = max(5.0, ry - stroke_y)
    inner = [(x_stem, y_top - stroke_y), (cx, y_top - stroke_y)] + [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta[1:-1])] + [(cx, y_bot + stroke_y), (x_stem, y_bot + stroke_y)]
    inner_poly = Polygon(inner)
    return outer_poly.difference(inner_poly)

def make_bowl_left(x_stem, y_bot, y_top, width, stroke_x, stroke_y, n=48):
    """Smooth D-bowl extending leftward from x_stem with horizontal tangents (no V-notch)."""
    cy = (y_top + y_bot) * 0.5
    ry = (y_top - y_bot) * 0.5
    flat = min(50.0, width * 0.22)
    cx = x_stem - flat
    rx = max(20.0, width - flat)
    theta = np.linspace(np.pi * 0.5, np.pi * 1.5, n)
    outer = [(x_stem, y_top), (cx, y_top)] + [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta[1:-1]] + [(cx, y_bot), (x_stem, y_bot)]
    outer_poly = Polygon(outer)
    rx_in = max(5.0, rx - stroke_x)
    ry_in = max(5.0, ry - stroke_y)
    inner = [(x_stem, y_bot + stroke_y), (cx, y_bot + stroke_y)] + [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta[1:-1])] + [(cx, y_top - stroke_y), (x_stem, y_top - stroke_y)]
    inner_poly = Polygon(inner)
    return outer_poly.difference(inner_poly)

def make_arch_solid(x_left_stem, x_right, y_base, y_top, stem, hair):
    """Seamless single-polygon lowercase shoulder arch fused to a left stem.

    Starts inside the left stem (x_left_stem) so unioning with the vertical stem
    is 100% solid with zero gaps or floating baseline artifacts.
    """
    y_join = y_top * 0.60
    x_mid = (x_left_stem + x_right) * 0.52
    rx = x_right - x_mid
    ry = y_top - y_join

    # Outer contour: from inside left stem -> up & over apex -> down right leg to y_base
    left_rise = [(x_left_stem, y_join - hair), (x_left_stem, y_join)]
    # Top-left quadrant from x_left_stem to x_mid
    t_l = np.linspace(np.pi, np.pi * 0.5, 24)
    rx_l = x_mid - x_left_stem
    arc_l = [(x_mid + rx_l * np.cos(t), y_join + ry * np.sin(t)) for t in t_l]
    # Top-right quadrant from x_mid to x_right
    t_r = np.linspace(np.pi * 0.5, 0, 24)
    arc_r = [(x_mid + rx * np.cos(t), y_join + ry * np.sin(t)) for t in t_r]
    right_leg = [(x_right, y_join), (x_right, y_base), (x_right - stem, y_base), (x_right - stem, y_join)]

    # Inner contour: back over apex to left stem
    rx_in_r = max(5, rx - stem)
    rx_in_l = max(5, rx_l - stem * 0.2)
    ry_in = max(5, ry - hair)
    arc_in_r = [(x_mid + rx_in_r * np.cos(t), y_join + ry_in * np.sin(t)) for t in np.linspace(0, np.pi * 0.5, 24)]
    arc_in_l = [(x_mid + rx_in_l * np.cos(t), y_join + ry_in * np.sin(t)) for t in np.linspace(np.pi * 0.5, np.pi, 24)]

    pts = left_rise + arc_l + arc_r[1:] + right_leg + arc_in_r[1:] + arc_in_l[1:]
    return Polygon(pts).buffer(0)

def make_s_shape(x, y, w, h, stem, hair):
    p0 = np.array([x + w - stem * 0.4, y + h - 105])
    p1 = np.array([x + w - stem * 0.4, y + h - hair * 0.5])
    p2 = np.array([x + stem * 0.3, y + h - hair * 0.5])
    p3 = np.array([x + stem * 0.3, y + h * 0.72])
    seg1 = bezier_cubic(p0, p1, p2, p3, 25)

    p4 = np.array([x + stem * 0.3, y + h * 0.58])
    p5 = np.array([x + w * 0.5, y + h * 0.50])
    seg2 = bezier_cubic(p3, p4, p5, p5, 20)

    p6 = np.array([x + w - stem * 0.3, y + h * 0.42])
    p7 = np.array([x + w - stem * 0.3, y + h * 0.28])
    seg3 = bezier_cubic(p5, p5, p6, p7, 20)

    p8 = np.array([x + w - stem * 0.3, y + hair * 0.5])
    p9 = np.array([x + stem * 0.4, y + hair * 0.5])
    p10 = np.array([x + stem * 0.4, y + 105])
    seg4 = bezier_cubic(p7, p8, p9, p10, 25)

    pts = np.vstack([seg1, seg2[1:], seg3[1:], seg4[1:]])
    s_poly = LineString(pts).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
    return s_poly.intersection(box(x - 50, y, x + w + 50, y + h))

def make_c_shape(cx, cy, rx, ry, stem, hair, start_deg=40, end_deg=320):
    rad0 = math.radians(start_deg)
    rad1 = math.radians(end_deg)
    theta = np.linspace(rad0, rad1, 60)
    outer = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta]
    rx_in = max(5, rx - stem)
    ry_in = max(5, ry - hair)
    inner = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta)]
    return Polygon(outer + inner)

def make_e_shape(x, y, w, h, stem, hair):
    """Crisp editorial lowercase e with open eye across all weights."""
    cx = x + w * 0.5
    cy = y + h * 0.50
    rx = w * 0.48
    ry = h * 0.50
    bar_h = min(48, hair * 0.72)
    rx_in = max(35, rx - stem)
    ry_in = max(35, ry - hair * 0.85)

    # Top closed eye (0 to 180 deg)
    theta_top = np.linspace(0, np.pi, 45)
    outer_top = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta_top]
    inner_top = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta_top)]
    top_eye = Polygon(outer_top + inner_top)

    # Horizontal crossbar
    bar = box(cx - rx, cy - bar_h * 0.5, cx + rx, cy + bar_h * 0.5)

    # Bottom curve (180 to 332 deg)
    theta_bot = np.linspace(np.pi, 2 * np.pi - math.radians(28), 50)
    outer_bot = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta_bot]
    inner_bot = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in reversed(theta_bot)]
    bot_curve = Polygon(outer_bot + inner_bot)

    return unary_union([top_eye, bar, bot_curve]).intersection(box(x - 20, y, x + w + 20, y + h))

def make_ampersand(w, stem, hair):
    # Clean, balanced editorial ampersand: generous upper loop + open lower bowl + crisp leg
    p_top_r = np.array([340, 495])
    p_top_t = np.array([250, CAP - hair * 0.5])
    p_top_l = np.array([150, 520])
    p_waist = np.array([220, 360])
    seg_top1 = bezier_cubic(np.array([340, 455]), np.array([355, CAP - hair * 0.5]), p_top_t, p_top_l, 24)
    seg_top2 = bezier_cubic(p_top_l, np.array([140, 430]), p_waist, p_waist, 18)

    # Bottom-left bowl curving down to baseline and up to right-mid
    p_bot_l = np.array([95, 175])
    p_bot_b = np.array([255, hair * 0.5])
    p_bot_r = np.array([w - 90, 210])
    seg_bot1 = bezier_cubic(p_waist, np.array([115, 295]), np.array([95, 245]), p_bot_l, 20)
    seg_bot2 = bezier_cubic(p_bot_l, np.array([95, hair * 0.5]), p_bot_b, np.array([395, hair * 0.5]), 24)
    seg_bot3 = bezier_cubic(np.array([395, hair * 0.5]), np.array([w - 110, 40]), p_bot_r, p_bot_r, 16)

    # Diagonal leg from upper-left waist down to bottom-right foot
    seg_leg = bezier_cubic(p_top_l, np.array([155, 420]), np.array([350, 170]), np.array([w - 75, 0]), 28)

    loop_pts = np.vstack([seg_top1, seg_top2[1:], seg_bot1[1:], seg_bot2[1:], seg_bot3[1:]])
    loop_poly = LineString(loop_pts).buffer(hair * 0.48, cap_style=2, join_style=1, resolution=32)
    leg_poly = LineString(seg_leg).buffer(hair * 0.50, cap_style=2, join_style=1, resolution=32)
    return unary_union([loop_poly, leg_poly]).intersection(box(0, 0, w, CAP))

# --- Precision Diagonals & Seamless U/V/W ---

def make_v_exact(lsb, rsb, y_top, stem):
    mid = (lsb + rsb) * 0.5
    dx = mid - lsb
    hyp = np.hypot(dx, y_top)
    stem_h = stem * (hyp / y_top)
    vertex_y = min(y_top - 10, stem * (hyp / dx))

    pts = [
        (lsb, y_top),
        (mid, 0),
        (rsb, y_top),
        (rsb - stem_h, y_top),
        (mid, vertex_y),
        (lsb + stem_h, y_top)
    ]
    return Polygon(pts)

def make_w_exact(lsb, rsb, y_top, stem, center_h_ratio=0.82):
    """W with horizontal top terminals, sharp valley vertices, and solid shared mid-apex."""
    mid = (lsb + rsb) * 0.5
    q1 = lsb + (mid - lsb) * 0.50
    q2 = mid + (rsb - mid) * 0.50
    h2 = y_top * center_h_ratio

    def sw(dx, dy):
        return stem * np.hypot(dx, dy) / dy if dy != 0 else stem

    s1 = sw(q1 - lsb, y_top)
    s2 = sw(mid - q1, h2)
    s3 = sw(q2 - mid, h2)
    s4 = sw(rsb - q2, y_top)

    left_leg  = Polygon([(lsb, y_top), (lsb + s1, y_top), (q1 + s1 * 0.5, 0), (q1 - s1 * 0.5, 0)])
    left_arm  = Polygon([(q1 - s2 * 0.5, 0), (q1 + s2 * 0.5, 0), (mid + s2 * 0.5, h2), (mid - s2 * 0.5, h2)])
    right_arm = Polygon([(mid - s3 * 0.5, h2), (mid + s3 * 0.5, h2), (q2 + s3 * 0.5, 0), (q2 - s3 * 0.5, 0)])
    right_leg = Polygon([(q2 - s4 * 0.5, 0), (q2 + s4 * 0.5, 0), (rsb, y_top), (rsb - s4, y_top)])

    pad = stem * 0.55
    pad_q1  = box(q1 - pad, 0, q1 + pad, pad)
    pad_q2  = box(q2 - pad, 0, q2 + pad, pad)
    pad_mid = box(mid - pad, h2 - pad, mid + pad, h2 + pad)

    w_shape = unary_union([left_leg, left_arm, right_arm, right_leg, pad_q1, pad_q2, pad_mid])
    return w_shape.intersection(box(lsb - 20, 0, rsb + 20, y_top))

def make_a_exact(lsb, rsb, CAP, stem, hair):
    mid = (lsb + rsb) * 0.5
    dx = mid - lsb
    hyp = np.hypot(dx, CAP)
    stem_h = stem * hyp / CAP
    poly1 = Polygon([(lsb, 0), (lsb + stem_h, 0), (mid + stem_h * 0.35, CAP), (mid - stem_h * 0.5, CAP)])
    poly2 = Polygon([(rsb, 0), (rsb - stem_h, 0), (mid - stem_h * 0.35, CAP), (mid + stem_h * 0.5, CAP)])
    crossbar = box(lsb + dx * 0.25, 220, rsb - dx * 0.25, 220 + hair)
    a_shape = unary_union([poly1, poly2, crossbar])
    return a_shape.intersection(box(lsb - 20, 0, rsb + 20, CAP))

def make_u_seamless(lsb, rsb, y_top, stem, hair, r_bot=220):
    cx = (lsb + rsb) * 0.5
    rx = (rsb - lsb) * 0.5
    cy = r_bot
    ry = r_bot

    outer_left = [(lsb, y_top), (lsb, cy)]
    theta_out = np.linspace(np.pi, 2 * np.pi, 50)
    outer_arc = [(cx + rx * np.cos(t), cy + ry * np.sin(t)) for t in theta_out]
    outer_right = [(rsb, cy), (rsb, y_top)]

    rx_in = max(10, rx - stem)
    ry_in = max(10, ry - hair)
    inner_right = [(rsb - stem, y_top), (rsb - stem, cy)]
    theta_in = np.linspace(2 * np.pi, np.pi, 50)
    inner_arc = [(cx + rx_in * np.cos(t), cy + ry_in * np.sin(t)) for t in theta_in]
    inner_left = [(lsb + stem, cy), (lsb + stem, y_top)]

    all_pts = outer_left + outer_arc[1:-1] + outer_right + inner_right + inner_arc[1:-1] + inner_left
    return Polygon(all_pts)

def make_lower_u_flush(lsb, rsb, XH, stem, hair, r_bot=185):
    """Lowercase u: smooth tangential bottom curve meeting a clean vertical right stem."""
    u_body = make_u_seamless(lsb, rsb, XH, stem, hair, r_bot=r_bot)
    right_stem = box(rsb - stem, 0, rsb, XH)
    return unary_union([u_body, right_stem])

def make_x_exact(lsb, rsb, y_top, stem):
    dx = rsb - lsb
    hyp = np.hypot(dx, y_top)
    stem_h = stem * hyp / y_top
    poly1 = Polygon([(lsb, y_top), (lsb + stem_h, y_top), (rsb, 0), (rsb - stem_h, 0)])
    poly2 = Polygon([(lsb, 0), (lsb + stem_h, 0), (rsb, y_top), (rsb - stem_h, y_top)])
    return unary_union([poly1, poly2]).intersection(box(lsb - 20, 0, rsb + 20, y_top))

def make_y_upper(lsb, rsb, CAP, stem):
    mid = (lsb + rsb) * 0.5
    dx = mid - lsb
    hyp = np.hypot(dx, CAP - 300)
    stem_h = stem * hyp / (CAP - 300)
    poly1 = Polygon([(lsb, CAP), (lsb + stem_h, CAP), (mid + stem * 0.5, 300), (mid - stem * 0.5, 300)])
    poly2 = Polygon([(rsb, CAP), (rsb - stem_h, CAP), (mid - stem * 0.5, 300), (mid + stem * 0.5, 300)])
    vert = box(mid - stem * 0.5, 0, mid + stem * 0.5, 300)
    return unary_union([poly1, poly2, vert]).intersection(box(lsb - 20, 0, rsb + 20, CAP))

def make_y_lower(lsb, rsb, XH, stem):
    mid = (lsb + rsb) * 0.5
    # Right diagonal runs straight from top-right to descender foot (-180)
    dx2 = rsb - (mid - 115)
    h2 = XH + 180
    hyp2 = np.hypot(dx2, h2)
    stem_h2 = stem * hyp2 / h2
    poly2 = Polygon([(rsb, XH), (rsb - stem_h2, XH), (mid - 115 - stem_h2, -180), (mid - 115, -180)])

    # Left diagonal meets the centerline of poly2 cleanly inside poly2 (zero bump)
    x_join = mid - 115 + (rsb - (mid - 115)) * (180 / h2)
    dx1 = x_join - lsb
    hyp1 = np.hypot(dx1, XH)
    stem_h1 = stem * hyp1 / XH
    poly1 = Polygon([(lsb, XH), (lsb + stem_h1, XH), (x_join + stem_h1 * 0.15, 0), (x_join - stem_h2 * 0.45, 0)])
    return unary_union([poly1, poly2]).intersection(box(lsb - 40, -180, rsb + 20, XH))

def shape_glyph(ch, weight):
    """Generates geometric outline and proportional advance width."""
    t = 22 + (weight - 100) * (158 / 800)
    stem = t
    hair = max(16, t * 0.88)
    forms = []

    def rect(x, y, w, h):
        forms.append(box(x, y, x + w, y + h))

    def line_poly(pts, width=stem):
        forms.append(LineString(pts).buffer(width * 0.5, cap_style=2, join_style=1, resolution=32))

    # Whitespace
    if ch == ' ':
        return None, 280

    # Punctuation & Typographical Symbols
    if ch == '.':
        rect(120, 0, stem, stem)
        return unary_union(forms), 240 + int(stem)
    elif ch == ',':
        rect(120, 0, stem, stem)
        p_tail = [(120 + stem, stem), (120 + stem * 0.8, -stem * 0.7), (120, -stem * 0.9)]
        line_poly(p_tail, stem * 0.6)
        return unary_union(forms), 240 + int(stem)
    elif ch == ':':
        rect(120, 0, stem, stem)
        rect(120, XH - stem, stem, stem)
        return unary_union(forms), 240 + int(stem)
    elif ch == ';':
        rect(120, XH - stem, stem, stem)
        rect(120, 0, stem, stem)
        p_tail = [(120 + stem, stem), (120 + stem * 0.8, -stem * 0.7), (120, -stem * 0.9)]
        line_poly(p_tail, stem * 0.6)
        return unary_union(forms), 240 + int(stem)
    elif ch == '!':
        rect(150 - stem * 0.5, 170, stem, CAP - 170)
        rect(150 - stem * 0.5, 0, stem, stem)
        return unary_union(forms), 300
    elif ch == '?':
        cx, cy, rx, ry = 250, 520, 190, 180
        hook = make_arc_strip(cx, cy, rx, ry, -math.pi * 0.3, math.pi, stem, hair)
        stem_drop = box(cx - stem * 0.5, 180, cx + stem * 0.5, cy - ry + hair)
        dot = box(cx - stem * 0.5, 0, cx + stem * 0.5, stem)
        forms.extend([hook, stem_drop, dot])
        return unary_union(forms), 500
    elif ch == '-':
        rect(80, XH * 0.5 - hair * 0.5, 340, hair)
        return unary_union(forms), 500
    elif ch in ('\u2013', '–'):
        rect(50, XH * 0.5 - hair * 0.5, 420, hair)
        return unary_union(forms), 520
    elif ch in ('\u2014', '—'):
        rect(40, XH * 0.5 - hair * 0.5, 620, hair)
        return unary_union(forms), 700
    elif ch in ('\u2022', '•'):
        forms.append(make_ellipse(220, XH * 0.5, stem * 0.75, stem * 0.75))
        return unary_union(forms), 440
    elif ch == '&':
        forms.append(make_ampersand(600, stem, hair))
        return unary_union(forms), 620
    elif ch == '_':
        rect(40, -140, 480, hair)
        return unary_union(forms), 560
    elif ch == '/':
        line_poly([(80, -60), (380, CAP + 20)], hair)
        return unary_union(forms), 460
    elif ch == '\\':
        line_poly([(80, CAP + 20), (380, -60)], hair)
        return unary_union(forms), 460
    elif ch == '(':
        forms.append(make_arc_strip(280, 260, 240, 460, math.pi * 0.55, math.pi * 1.45, stem, hair))
        return unary_union(forms), 340
    elif ch == ')':
        forms.append(make_arc_strip(60, 260, 240, 460, -math.pi * 0.45, math.pi * 0.45, stem, hair))
        return unary_union(forms), 340
    elif ch == '[':
        rect(100, -80, stem, CAP + 160)
        rect(100, CAP + 80 - hair, 160, hair)
        rect(100, -80, 160, hair)
        return unary_union(forms), 340
    elif ch == ']':
        rect(240 - stem, -80, stem, CAP + 160)
        rect(80, CAP + 80 - hair, 160, hair)
        rect(80, -80, 160, hair)
        return unary_union(forms), 340
    elif ch == '+':
        rect(70, 250 - hair * 0.5, 360, hair)
        rect(250 - hair * 0.5, 70, hair, 360)
        return unary_union(forms), 500
    elif ch == '=':
        rect(70, 310, 360, hair)
        rect(70, 190, 360, hair)
        return unary_union(forms), 500
    elif ch in ("'", '"', '\u2018', '\u2019', '\u201C', '\u201D'):
        rect(120, CAP - 180, stem * 0.8, 180)
        if ch in ('"', '\u201C', '\u201D'):
            rect(120 + stem * 1.4, CAP - 180, stem * 0.8, 180)
            return unary_union(forms), 240 + int(stem * 2.2)
        return unary_union(forms), 240 + int(stem)

    # Numerals 0-9 (Refined Editorial Lining Figures)
    if ch.isdigit():
        w = 560
        cx = w * 0.5
        if ch == '0':
            forms.append(make_ring(cx, CAP * 0.5, w * 0.44, CAP * 0.50, stem, hair))
        elif ch == '1':
            stem_x = (w - stem) * 0.5 + 20
            beak_w = 110
            beak_drop = 110
            beak_h = hair * 0.9
            poly_1 = Polygon([
                (stem_x, 0),
                (stem_x + stem, 0),
                (stem_x + stem, CAP),
                (stem_x, CAP),
                (stem_x - beak_w, CAP - beak_drop),
                (stem_x - beak_w, CAP - beak_drop - beak_h),
                (stem_x, CAP - beak_drop),
            ])
            forms.append(poly_1)
        elif ch == '2':
            # Smooth continuous Bezier top-arch + flowing diagonal neck into flat base
            p0 = np.array([95, CAP - 115])
            p1 = np.array([120, CAP - hair * 0.5])
            p2 = np.array([w - 95, CAP - hair * 0.5])
            p3 = np.array([w - 95, 505])
            p4 = np.array([w - 95, 360])
            p5 = np.array([155, 140])
            p6 = np.array([105, hair * 0.5])
            seg1 = bezier_cubic(p0, p1, p2, p3, 28)
            seg2 = bezier_cubic(p3, p4, p5, p6, 28)
            pts = np.vstack([seg1, seg2[1:]])
            curve = LineString(pts).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            base = box(70, 0, w - 70, hair)
            forms.extend([curve, base])
        elif ch == '3':
            # Continuous smooth 3 using cubic Bezier spine + solid bowls, zero waist gaps
            p0 = np.array([105, CAP - 115])
            p1 = np.array([130, CAP - hair * 0.5])
            p2 = np.array([w - 105, CAP - hair * 0.5])
            p3 = np.array([w - 105, 520])
            p4 = np.array([w - 105, 365])
            p5 = np.array([cx - 35, 360])
            seg_top = bezier_cubic(p0, p1, p2, p3, 25)
            seg_mid_t = bezier_cubic(p3, p4, p5, p5, 20)

            p6 = np.array([w - 95, 345])
            p7 = np.array([w - 95, 185])
            p8 = np.array([w - 95, hair * 0.5])
            p9 = np.array([105, hair * 0.5])
            p10 = np.array([95, 125])
            seg_mid_b = bezier_cubic(p5, p5, p6, p7, 20)
            seg_bot = bezier_cubic(p7, p8, p9, p10, 25)

            top_pts = np.vstack([seg_top, seg_mid_t[1:]])
            bot_pts = np.vstack([seg_mid_b, seg_bot[1:]])
            top_s = LineString(top_pts).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            bot_s = LineString(bot_pts).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            waist_cap = box(cx - 55, 360 - hair * 0.5, cx + 10, 360 + hair * 0.5)
            forms.extend([top_s, bot_s, waist_cap])
        elif ch == '4':
            stem_x = w - 150
            vert = box(stem_x - stem, 0, stem_x, CAP)
            dx = stem_x - 70
            hyp = np.hypot(dx, CAP - 200)
            stem_h = stem * hyp / (CAP - 200)
            diag = Polygon([
                (stem_x, CAP),
                (stem_x - stem_h, CAP),
                (70, 200),
                (70 + stem_h, 200)
            ])
            crossbar = box(60, 200, w - 60, 200 + hair)
            forms.extend([vert, diag, crossbar])
        elif ch == '5':
            # Continuous 5: top bar + vertical neck + smooth Bezier bottom bowl (zero shelf gap)
            lsb5 = 85
            top_bar = box(lsb5, CAP - hair, w - 95, CAP)
            neck = box(lsb5, 345, lsb5 + stem, CAP)
            p0 = np.array([lsb5 + stem * 0.5, 345 + hair * 0.5])
            p1 = np.array([cx + 40, 390])
            p2 = np.array([w - 80, 340])
            p3 = np.array([w - 80, 195])
            p4 = np.array([w - 80, hair * 0.5])
            p5 = np.array([cx, hair * 0.5])
            p6 = np.array([80 + hair * 0.5, hair * 0.5])
            p7 = np.array([80 + hair * 0.5, 130])
            seg1 = bezier_cubic(p0, p1, p2, p3, 25)
            seg2 = bezier_cubic(p3, p4, p5, p6, 25)
            seg3 = bezier_cubic(p6, np.array([80 + hair * 0.5, 65]), p7, p7, 15)
            pts = np.vstack([seg1, seg2[1:], seg3[1:]])
            bowl_s = LineString(pts).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            join_pad = box(lsb5, 345, lsb5 + stem + 15, 345 + hair)
            forms.extend([top_bar, neck, join_pad, bowl_s])
        elif ch == '6':
            bowl = make_ring(cx, 220, w * 0.44, 220, stem, hair)
            p0 = np.array([w - 90, CAP - hair * 0.5])
            p1 = np.array([cx - 20, CAP - hair * 0.5])
            p2 = np.array([cx - w * 0.44 + stem * 0.5, 440])
            p3 = np.array([cx - w * 0.44 + stem * 0.5, 220])
            seg = bezier_cubic(p0, p1, p2, p3, 35)
            spine = LineString(seg).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            forms.extend([bowl, spine])
        elif ch == '7':
            top_bar = box(70, CAP - hair, w - 70, CAP)
            diag = Polygon([
                (w - 70, CAP),
                (w - 70 - stem * 1.15, CAP),
                (170, 0),
                (170 + stem * 1.15, 0)
            ])
            forms.extend([top_bar, diag])
        elif ch == '8':
            top_loop = make_ring(cx, 515, w * 0.38, 185, stem, hair)
            bot_loop = make_ring(cx, 195, w * 0.45, 195, stem, hair)
            forms.extend([top_loop, bot_loop])
        elif ch == '9':
            bowl = make_ring(cx, CAP - 220, w * 0.44, 220, stem, hair)
            p0 = np.array([90, hair * 0.5])
            p1 = np.array([cx + 20, hair * 0.5])
            p2 = np.array([cx + w * 0.44 - stem * 0.5, CAP - 440])
            p3 = np.array([cx + w * 0.44 - stem * 0.5, CAP - 220])
            seg = bezier_cubic(p0, p1, p2, p3, 35)
            spine = LineString(seg).buffer(hair * 0.5, cap_style=2, join_style=1, resolution=32)
            forms.extend([bowl, spine])
        return unary_union(forms).intersection(box(0, 0, w, CAP)), w

    # Uppercase A-Z
    if ch.isupper():
        if ch == 'A':
            w = 640
            return make_a_exact(60, w - 60, CAP, stem, hair), w
        elif ch == 'B':
            w = 620
            lsb = 70
            rect(lsb, 0, stem, CAP)
            top_b = make_bowl_right(lsb + stem - 5, 340, CAP, 230, stem, hair)
            bot_b = make_bowl_right(lsb + stem - 5, 0, 360, 250, stem, hair)
            forms.extend([top_b, bot_b])
            return unary_union(forms), w
        elif ch == 'C':
            w = 640
            forms.append(make_c_shape(w * 0.5 + 10, CAP * 0.5, w * 0.44, CAP * 0.50, stem, hair, start_deg=40, end_deg=320))
            return unary_union(forms), w
        elif ch == 'D':
            w = 640
            lsb = 70
            rect(lsb, 0, stem, CAP)
            forms.append(make_bowl_right(lsb + stem - 5, 0, CAP, w - 70 - (lsb + stem - 5), stem, hair))
            return unary_union(forms), w
        elif ch == 'E':
            w = 540
            lsb = 70
            rect(lsb, 0, stem, CAP)
            rect(lsb, CAP - hair, w - 130, hair)
            rect(lsb, 340, w - 170, hair)
            rect(lsb, 0, w - 120, hair)
            return unary_union(forms), w
        elif ch == 'F':
            w = 520
            lsb = 70
            rect(lsb, 0, stem, CAP)
            rect(lsb, CAP - hair, w - 130, hair)
            rect(lsb, 330, w - 170, hair)
            return unary_union(forms), w
        elif ch == 'G':
            w = 660
            cx = w * 0.5 + 10
            forms.append(make_c_shape(cx, CAP * 0.5, w * 0.44, CAP * 0.50, stem, hair, start_deg=38, end_deg=328))
            rect(cx, 320, w - 60 - cx, hair)
            rect(w - 60 - stem, 0, stem, 320 + hair)
            return unary_union(forms), w
        elif ch == 'H':
            w = 660
            lsb = 70
            rect(lsb, 0, stem, CAP)
            rect(w - 70 - stem, 0, stem, CAP)
            rect(lsb, 340, w - 140, hair)
            return unary_union(forms), w
        elif ch == 'I':
            w = 280
            rect((w - stem) * 0.5, 0, stem, CAP)
            return unary_union(forms), w
        elif ch == 'J':
            w = 500
            rsb = w - 70
            rect(rsb - stem, 200, stem, CAP - 200)
            forms.append(make_arc_strip(rsb - 170, 200, 170, 200, -math.pi * 0.95, 0, stem, hair))
            return unary_union(forms), w
        elif ch == 'K':
            w = 600
            lsb = 70
            rect(lsb, 0, stem, CAP)
            dx1 = (w - 60) - (lsb + stem * 0.8)
            hyp1 = np.hypot(dx1, CAP - 290)
            s_h1 = stem * hyp1 / (CAP - 290)
            up_diag = Polygon([(lsb + stem * 0.7, 290), (lsb + stem * 0.7 + s_h1, 290), (w - 60, CAP), (w - 60 - s_h1, CAP)])
            dx2 = (w - 50) - (lsb + stem * 0.8)
            hyp2 = np.hypot(dx2, 360)
            s_h2 = stem * hyp2 / 360
            down_diag = Polygon([(lsb + stem * 0.7, 360), (lsb + stem * 0.7 + s_h2, 360), (w - 50, 0), (w - 50 - s_h2, 0)])
            forms.extend([up_diag, down_diag])
            return unary_union(forms).intersection(box(lsb - 20, 0, w + 20, CAP)), w
        elif ch == 'L':
            w = 500
            lsb = 70
            rect(lsb, 0, stem, CAP)
            rect(lsb, 0, w - 130, hair)
            return unary_union(forms), w
        elif ch == 'M':
            w = 780
            lsb = 70
            rsb = w - 70
            mid = w * 0.5
            rect(lsb, 0, stem, CAP)
            rect(rsb - stem, 0, stem, CAP)
            dx = mid - (lsb + stem * 0.5)
            hyp = np.hypot(dx, CAP - 120)
            sh = stem * hyp / (CAP - 120)
            left_d = Polygon([(lsb, CAP), (lsb + sh, CAP), (mid + sh * 0.5, 120), (mid - sh * 0.5, 120)])
            right_d = Polygon([(rsb, CAP), (rsb - sh, CAP), (mid - sh * 0.5, 120), (mid + sh * 0.5, 120)])
            forms.extend([left_d, right_d])
            return unary_union(forms).intersection(box(lsb - 20, 0, rsb + 20, CAP)), w
        elif ch == 'N':
            w = 680
            lsb = 70
            rsb = w - 70
            rect(lsb, 0, stem, CAP)
            rect(rsb - stem, 0, stem, CAP)
            dx = (rsb - stem) - lsb
            hyp = np.hypot(dx, CAP)
            sh = stem * hyp / CAP
            diag = Polygon([(lsb, CAP), (lsb + sh, CAP), (rsb, 0), (rsb - sh, 0)])
            forms.append(diag)
            return unary_union(forms).intersection(box(lsb - 20, 0, rsb + 20, CAP)), w
        elif ch == 'O':
            w = 680
            forms.append(make_ring(w * 0.5, CAP * 0.5, w * 0.44, CAP * 0.50, stem, hair))
            return unary_union(forms), w
        elif ch == 'P':
            w = 580
            lsb = 70
            rect(lsb, 0, stem, CAP)
            forms.append(make_bowl_right(lsb + stem - 5, 310, CAP, w - 70 - (lsb + stem - 5), stem, hair))
            return unary_union(forms), w
        elif ch == 'Q':
            w = 680
            forms.append(make_ring(w * 0.5, CAP * 0.5, w * 0.44, CAP * 0.50, stem, hair))
            dx = 220
            hyp = np.hypot(dx, 240)
            sh = stem * hyp / 240
            tail = Polygon([(380, 160), (380 + sh, 160), (600, -80), (600 - sh, -80)])
            forms.append(tail)
            return unary_union(forms), w
        elif ch == 'R':
            w = 600
            lsb = 70
            rect(lsb, 0, stem, CAP)
            bowl = make_bowl_right(lsb + stem - 5, 300, CAP, 230, stem, hair)
            dx = w - 70 - 270
            hyp = np.hypot(dx, 320)
            stem_h = stem * hyp / 320
            leg = Polygon([(270, 320), (w - 70, 0), (w - 70 - stem_h, 0), (270 - stem * 0.5, 320)])
            forms.extend([bowl, leg])
            return unary_union(forms).intersection(box(lsb - 20, 0, w, CAP)), w
        elif ch == 'S':
            w = 560
            forms.append(make_s_shape(50, 0, w - 100, CAP, stem, hair))
            return unary_union(forms), w
        elif ch == 'T':
            w = 580
            rect(40, CAP - hair, w - 80, hair)
            rect((w - stem) * 0.5, 0, stem, CAP)
            return unary_union(forms), w
        elif ch == 'U':
            w = 640
            return make_u_seamless(70, w - 70, CAP, stem, hair, 220), w
        elif ch == 'V':
            w = 620
            return make_v_exact(50, w - 50, CAP, stem), w
        elif ch == 'W':
            w = 860
            return make_w_exact(60, w - 60, CAP, stem), w
        elif ch == 'X':
            w = 600
            return make_x_exact(60, w - 60, CAP, stem), w
        elif ch == 'Y':
            w = 600
            return make_y_upper(60, w - 60, CAP, stem), w
        elif ch == 'Z':
            w = 580
            top_b = box(60, CAP - hair, w - 60, CAP)
            bot_b = box(60, 0, w - 60, hair)
            dx = w - 70 - 70
            hyp = np.hypot(dx, CAP)
            stem_h = stem * hyp / CAP
            diag = Polygon([(w - 70, CAP), (w - 70 - stem_h, CAP), (70, 0), (70 + stem_h, 0)])
            forms.extend([top_b, bot_b, diag])
            return unary_union(forms).intersection(box(40, 0, w - 40, CAP)), w

    # Lowercase a-z
    if ch.islower():
        if ch == 'a':
            w = 580
            rsb = w - 60
            x_stem = rsb - stem * 0.5
            rect(rsb - stem, 0, stem, XH)
            forms.append(make_bowl_left(x_stem, 0, XH, x_stem - 55, stem, hair))
            return unary_union(forms), w
        elif ch == 'b':
            w = 600
            lsb = 60
            x_stem = lsb + stem * 0.5
            rect(lsb, 0, stem, 720)
            forms.append(make_bowl_right(x_stem, 0, XH, (w - 55) - x_stem, stem, hair))
            return unary_union(forms), w
        elif ch == 'c':
            w = 520
            forms.append(make_c_shape(w * 0.5 + 10, XH * 0.5, w * 0.44, XH * 0.50, stem, hair, start_deg=35, end_deg=325))
            return unary_union(forms), w
        elif ch == 'd':
            w = 600
            rsb = w - 60
            x_stem = rsb - stem * 0.5
            rect(rsb - stem, 0, stem, 720)
            forms.append(make_bowl_left(x_stem, 0, XH, x_stem - 55, stem, hair))
            return unary_union(forms), w
        elif ch == 'e':
            w = 540
            forms.append(make_e_shape(50, 0, w - 100, XH, stem, hair))
            return unary_union(forms), w
        elif ch == 'f':
            # Graceful f: vertical stem rising into smooth top curve without piercing arch
            w = 360
            stem_x = 120
            y_join = 520
            rect(stem_x, 0, stem, y_join)
            arch_r = 115
            hook = make_arc_strip(stem_x + arch_r, y_join, arch_r, 190, 0, math.pi, stem, hair)
            cross = box(35, XH - hair, 315, XH)
            forms.extend([hook, cross])
            return unary_union(forms), w
        elif ch == 'g':
            w = 600
            rsb = w - 60
            x_stem = rsb - stem * 0.5
            rect(rsb - stem, -65, stem, XH + 65)
            bowl = make_bowl_left(x_stem, 0, XH, x_stem - 55, stem, hair)
            # Graceful J-hook descender curving down to -185 and sweeping left
            hook_rx = 185
            tail = make_arc_strip(rsb - hook_rx, -55, hook_rx, 130, -math.pi * 0.88, 0, stem, hair)
            forms.extend([bowl, tail])
            return unary_union(forms), w
        elif ch == 'h':
            w = 580
            lsb = 60
            rect(lsb, 0, stem, 720)
            forms.append(make_arch_solid(lsb + stem * 0.5, w - 70, 0, XH, stem, hair))
            return unary_union(forms), w
        elif ch == 'i':
            w = 240
            cx_i = w * 0.5
            rect(cx_i - stem * 0.5, 0, stem, XH)
            rect(cx_i - stem * 0.5, XH + 100, stem, stem)
            return unary_union(forms), w
        elif ch == 'j':
            w = 280
            rsb = w - 60
            rect(rsb - stem, -65, stem, XH + 65)
            rect(rsb - stem, XH + 100, stem, stem)
            hook_rx = 125
            tail = make_arc_strip(rsb - hook_rx, -55, hook_rx, 130, -math.pi * 0.85, 0, stem, hair)
            forms.append(tail)
            return unary_union(forms), w
        elif ch == 'k':
            w = 540
            lsb = 60
            rect(lsb, 0, stem, 720)
            dx1 = (w - 60) - (lsb + stem * 0.8)
            hyp1 = np.hypot(dx1, XH - 220)
            s_h1 = stem * hyp1 / (XH - 220)
            up_diag = Polygon([(lsb + stem * 0.7, 220), (lsb + stem * 0.7 + s_h1, 220), (w - 60, XH), (w - 60 - s_h1, XH)])
            dx2 = (w - 50) - (lsb + stem * 0.8)
            hyp2 = np.hypot(dx2, 270)
            s_h2 = stem * hyp2 / 270
            down_diag = Polygon([(lsb + stem * 0.7, 270), (lsb + stem * 0.7 + s_h2, 270), (w - 50, 0), (w - 50 - s_h2, 0)])
            forms.extend([up_diag, down_diag])
            return unary_union(forms).intersection(box(lsb - 20, 0, w + 20, 720)), w
        elif ch == 'l':
            w = 240
            rect((w - stem) * 0.5, 0, stem, 720)
            return unary_union(forms), w
        elif ch == 'm':
            w = 860
            lsb = 60
            rect(lsb, 0, stem, XH)
            mid_x = (w + lsb) * 0.5 - 10
            arch1 = make_arch_solid(lsb + stem * 0.5, mid_x, 0, XH, stem, hair)
            arch2 = make_arch_solid(mid_x - stem * 0.5, w - 60, 0, XH, stem, hair)
            forms.extend([arch1, arch2])
            return unary_union(forms), w
        elif ch == 'n':
            w = 580
            lsb = 60
            rect(lsb, 0, stem, XH)
            forms.append(make_arch_solid(lsb + stem * 0.5, w - 70, 0, XH, stem, hair))
            return unary_union(forms), w
        elif ch == 'o':
            w = 560
            forms.append(make_ring(w * 0.5, XH * 0.5, w * 0.44, XH * 0.50, stem, hair))
            return unary_union(forms), w
        elif ch == 'p':
            w = 600
            lsb = 60
            x_stem = lsb + stem * 0.5
            stem_p = box(lsb, -180, lsb + stem, XH)
            bowl_p = make_bowl_right(x_stem, 0, XH, (w - 55) - x_stem, stem, hair)
            forms.extend([stem_p, bowl_p])
            return unary_union(forms), w
        elif ch == 'q':
            w = 600
            rsb = w - 60
            x_stem = rsb - stem * 0.5
            stem_q = box(rsb - stem, -180, rsb, XH)
            bowl_q = make_bowl_left(x_stem, 0, XH, x_stem - 55, stem, hair)
            forms.extend([stem_q, bowl_q])
            return unary_union(forms), w
        elif ch == 'r':
            w = 370
            lsb = 60
            rect(lsb, 0, stem, XH)
            # Clean curved shoulder branch seamlessly joined to left stem
            y_join = XH * 0.62
            rx_r = w - 45 - (lsb + stem * 0.5)
            ry_r = XH - y_join
            t_r = np.linspace(np.pi, np.pi * 0.35, 32)
            cx_r = lsb + stem * 0.5 + rx_r * 0.9
            outer = [(lsb + stem * 0.5, y_join - hair)] + [(cx_r + rx_r * np.cos(t), y_join + ry_r * np.sin(t)) for t in t_r]
            inner = [(cx_r + max(5, rx_r - stem * 0.8) * np.cos(t), y_join + max(5, ry_r - hair) * np.sin(t)) for t in reversed(t_r)]
            forms.append(Polygon(outer + inner))
            return unary_union(forms).intersection(box(lsb - 10, 0, w, XH)), w
        elif ch == 's':
            w = 480
            forms.append(make_s_shape(40, 0, w - 80, XH, stem, hair))
            return unary_union(forms), w
        elif ch == 't':
            # Graceful lowercase t: vertical stem down to y_foot, curving cleanly RIGHT & UP into J-hook
            w = 360
            stem_x = 115
            y_foot = 135
            rect(stem_x, y_foot, stem, 525)
            hook_rx = 95
            hook = make_arc_strip(stem_x + hook_rx, y_foot, hook_rx, y_foot, math.pi, 2 * math.pi, stem, hair)
            cross = box(35, XH - hair, 295, XH)
            forms.extend([hook, cross])
            return unary_union(forms), w
        elif ch == 'u':
            w = 580
            return make_lower_u_flush(60, w - 60, XH, stem, hair, 180), w
        elif ch == 'v':
            w = 520
            return make_v_exact(50, w - 50, XH, stem), w
        elif ch == 'w':
            w = 760
            return make_w_exact(50, w - 50, XH, stem), w
        elif ch == 'x':
            w = 500
            return make_x_exact(50, w - 50, XH, stem), w
        elif ch == 'y':
            w = 520
            return make_y_lower(50, w - 50, XH, stem), w
        elif ch == 'z':
            w = 480
            lsb_z, rsb_z = 50, w - 50
            top_b = box(lsb_z, XH - hair, rsb_z, XH)
            bot_b = box(lsb_z, 0, rsb_z, hair)
            dx = rsb_z - lsb_z
            hyp = np.hypot(dx, XH)
            diag_h = hair * hyp / XH
            diag = Polygon([(rsb_z, XH), (rsb_z - diag_h, XH), (lsb_z, 0), (lsb_z + diag_h, 0)])
            forms.extend([top_b, bot_b, diag])
            return unary_union(forms).intersection(box(lsb_z, 0, rsb_z, XH)), w

    return None, 500


def build(weight, style):
    print(f"Building {FAMILY} {style} (weight {weight})...")
    chars = [chr(i) for i in range(32, 127)]
    for char, _ in EXTRA_CHARS:
        if char not in chars:
            chars.append(char)

    gs_ttf = {}
    gs_otf = {}
    met = {}
    cmap = {}

    for ch in chars:
        name = 'space' if ch == ' ' else f'uni{ord(ch):04X}'
        geom, adv = shape_glyph(ch, weight)
        if geom is None:
            gs_ttf[name] = TTGlyphPen(None).glyph()
            t2p = T2CharStringPen(adv, None)
            gs_otf[name] = t2p.getCharString()
        else:
            gs_ttf[name] = pen_from_geom(geom, is_cff=False)
            t2p = T2CharStringPen(adv, None)
            for item in getattr(geom, 'geoms', [geom]):
                if item.is_empty or item.geom_type != 'Polygon':
                    continue
                contour_to_pen(t2p, item.exterior.coords, False)
                for hole in item.interiors:
                    contour_to_pen(t2p, hole.coords, True)
            gs_otf[name] = t2p.getCharString()
        met[name] = (adv, 0)
        cmap[ord(ch)] = name

    # Embedded 14 Crema Vibes Icons (U+E001–U+E014)
    for icon_name, (code, svg_d) in ICONS.items():
        name = f'uni{code:04X}'
        svg_path = SVGPath.fromstring(f'<path d="{svg_d}"/>')

        tt_pen = TTGlyphPen(None)
        cu_pen = Cu2QuPen(tt_pen, max_err=1.0)
        svg_path.draw(cu_pen)
        gs_ttf[name] = tt_pen.glyph()

        t2_pen = T2CharStringPen(1024, None)
        svg_path.draw(t2_pen)
        gs_otf[name] = t2_pen.getCharString()

        met[name] = (1024, 0)
        cmap[code] = name

    # .notdef glyph
    p_tt = TTGlyphPen(None)
    contour_to_pen(p_tt, [(85, 0), (615, 0), (615, 700), (85, 700), (85, 0)], True)
    contour_to_pen(p_tt, [(155, 70), (545, 70), (545, 630), (155, 630), (155, 70)], False)
    gs_ttf['.notdef'] = p_tt.glyph()

    p_t2 = T2CharStringPen(700, None)
    contour_to_pen(p_t2, [(85, 0), (615, 0), (615, 700), (85, 700), (85, 0)], False)
    contour_to_pen(p_t2, [(155, 70), (545, 70), (545, 630), (155, 630), (155, 70)], True)
    gs_otf['.notdef'] = p_t2.getCharString()
    met['.notdef'] = (700, 0)

    glyph_order = ['.notdef'] + [cmap[ord(c)] for c in chars] + [f'uni{code:04X}' for _, (code, _) in ICONS.items()]
    ps = f'CremaVibes-{style}'
    name_tbl = {
        'familyName': FAMILY,
        'styleName': style,
        'uniqueFontIdentifier': f'Crema Vibes: {ps}',
        'fullName': f'{FAMILY} {style}',
        'psName': ps,
        'version': 'Version 2.600',
        'copyright': 'Copyright 2026 Crema Vibes. Original outlines.',
        'trademark': 'Crema Vibes',
    }

    adjust = round(22 + weight * 0.025)
    pairs = ['AV', 'AW', 'AY', 'AT', 'Ta', 'Te', 'To', 'Va', 'Ve', 'Vo', 'Wa', 'We', 'Wo', 'Ya', 'Yo', 'LT', 'FA', 'PA']
    kern_dict = {(cmap[ord(a)], cmap[ord(b)]): -adjust for a, b in pairs if ord(a) in cmap and ord(b) in cmap}

    # Build TTF + WOFF + WOFF2
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupGlyf(gs_ttf)
    fb.setupHorizontalMetrics(met)
    fb.setupHorizontalHeader(ascent=ASC, descent=DESC)
    fb.setupCharacterMap(cmap)
    fb.setupHead(unitsPerEm=UPM)
    fb.setupOS2(
        sTypoAscender=ASC, sTypoDescender=DESC,
        usWinAscent=ASC, usWinDescent=-DESC,
        usWeightClass=weight, fsSelection=0x40,
        sxHeight=XH, sCapHeight=CAP
    )
    fb.setupNameTable(name_tbl)
    fb.setupPost()
    fb.setupMaxp()

    k = newTable('kern')
    k.version = 0
    sub = KernTable_format_0()
    sub.version = 0
    sub.coverage = 1
    sub.format = 0
    sub.kernTable = kern_dict
    k.kernTables = [sub]
    fb.font['kern'] = k

    ttf = OUT / f'{ps}.ttf'
    fb.save(ttf)
    for flavor in ('woff', 'woff2'):
        f = TTFont(ttf)
        f.flavor = flavor
        f.save(OUT / f'{ps}.{flavor}')

    # Build OTF
    fb_otf = FontBuilder(UPM, isTTF=False)
    fb_otf.setupGlyphOrder(glyph_order)
    fb_otf.setupCFF(ps, {'FullName': name_tbl['fullName']}, gs_otf, {})
    fb_otf.setupHorizontalMetrics(met)
    fb_otf.setupHorizontalHeader(ascent=ASC, descent=DESC)
    fb_otf.setupCharacterMap(cmap)
    fb_otf.setupHead(unitsPerEm=UPM)
    fb_otf.setupOS2(
        sTypoAscender=ASC, sTypoDescender=DESC,
        usWinAscent=ASC, usWinDescent=-DESC,
        usWeightClass=weight, fsSelection=0x40,
        sxHeight=XH, sCapHeight=CAP
    )
    fb_otf.setupNameTable(name_tbl)
    fb_otf.setupPost()
    fb_otf.save(OUT / f'{ps}.otf')

    if style == 'Regular':
        for suffix in ('ttf', 'otf', 'woff', 'woff2'):
            (OUT / f'crema-vibes.{suffix}').write_bytes((OUT / f'{ps}.{suffix}').read_bytes())


if __name__ == '__main__':
    for weight, style in WEIGHTS:
        build(weight, style)
    print("✓ All 9 font weights (TTF, OTF, WOFF, WOFF2) built successfully.")
