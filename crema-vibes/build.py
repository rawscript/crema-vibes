#!/usr/bin/env python3
"""
Crema Vibes Icon Font Builder
Creates TTF and OTF font files from SVG path data
Requires: fonttools (pip install fonttools)
"""

import os
import re
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

FONT_FAMILY = "Crema Vibes"
FONT_NAME = "crema-vibes"
VERSION = "1.0.0"
UNITS_PER_EM = 1024

ICONS = {
    'arrow-up': ('E001', 'M512 768L256 384h192v-384h128v384h192z'),
    'menu': ('E002', 'M128 704v-64h768v64h-768zM128 384v-64h768v64h-768zM128 64v-64h768v64h-768z'),
    'search': ('E003', 'M652 96c-194 0-352 158-352 352s158 352 352 352 352-158 352-352-158-352-352-352zM652 736c-159 0-288-129-288-288s129-288 288-288 288 129 288 288-129 288-288 288zM906 80l-44-44-168 168 44 44z'),
    'trending-up': ('E004', 'M128 640l256-256 192 192 320-320v192h-64v-96l-256 256-192-192-192 192zM832 192h128v128h-64v-64h-64z'),
    'chip': ('E005', 'M320 192v512h384v-512h-384zM576 640h-128v-384h128v384zM256 384h-128v-64h128v-128h64v512h-64v-128h-128v-64h128zM640 128h64v128h128v64h-128v128h128v64h-128v128h-64zM384 0h64v128h-64zM512 0h64v128h-64zM384 768h64v128h-64zM512 768h64v128h-64zM896 384h128v64h-128zM896 512h128v64h-128zM0 384h128v64h-128zM0 512h128v64h-128z'),
    'document': ('E006', 'M192 64v768h384v-256h256v-512h-640zM640 704l128-128h-128v128zM128 0h630l162 162v666q0 26-19 45t-45 19h-640q-26 0-45-19t-19-45v-768q0-26 19-45t45-19zM256 448h384v64h-384v-64zM256 576h384v64h-384v-64zM256 320h256v64h-256v-64z'),
    'target': ('E007', 'M512 64c-247 0-448 201-448 448s201 448 448 448 448-201 448-448-201-448-448-448zM512 896c-212 0-384-172-384-384s172-384 384-384 384 172 384 384-172 384-384 384zM512 192c-177 0-320 143-320 320s143 320 320 320 320-143 320-320-143-320-320-320zM512 768c-141 0-256-115-256-256s115-256 256-256 256 115 256 256-115 256-256 256zM512 320c-106 0-192 86-192 192s86 192 192 192 192-86 192-192-86-192-192-192zM512 640c-71 0-128-57-128-128s57-128 128-128 128 57 128 128-57 128-128 128z'),
    'bar-chart': ('E008', 'M128 128h128v512h-128v-512zM320 256h128v384h-128v-384zM512 64h128v576h-128v-576zM768 384h128v256h-128v-256z'),
    'layers': ('E009', 'M512 128l-384 192 384 192 384-192-384-192zM512 416l-256-128 256-128 256 128-256 128zM128 512l384 192 384-192-64-32-320 160-320-160zM128 640l384 192 384-192-64-32-320 160-320-160z'),
    'chat-bubble': ('E010', 'M832 384q0 80-40 149t-109 109-149 40q-72 0-135-34l-183 48 48-183q-34-63-34-135 0-80 40-149t109-109 149-40 149 40 109 109 40 149zM512 128c-177 0-320 143-320 320 0 64 19 124 52 176l-36 140 140-36c52 33 112 52 176 52 177 0 320-143 320-320s-143-320-320-320z'),
    'megaphone': ('E011', 'M128 320v256l512 256v-768zM576 224v384l-384-192v-192zM832 416c53 0 96-43 96-96s-43-96-96-96v192zM704 576h-64v-320h64c0-141 115-256 256-256v64c-106 0-192 86-192 192v320z'),
    'linkedin': ('E012', 'M256 704v-448h-128v448h128zM192 320c35 0 64 29 64 64s-29 64-64 64-64-29-64-64 29-64 64-64zM320 256h128v64c17-43 64-85 149-85 128 0 163 85 163 213v256h-128v-213c0-53-21-85-75-85-64 0-96 43-96 107v191h-128v-448z'),
    'whatsapp': ('E013', 'M512 64c-247 0-448 201-448 448 0 88 26 171 71 241l-48 175 175-48c70 45 153 71 241 71 247 0 448-201 448-448s-201-448-448-448zM512 857c-78 0-152-24-214-65l-15-9-107 28 28-104-10-16c-44-62-68-136-68-214 0-202 164-366 366-366s366 164 366 366-164 366-366 366zM693 576c-10-5-61-30-71-33s-17-5-24 5c-7 10-28 33-34 40-6 7-12 8-23 3-10-5-44-16-84-51-31-27-52-61-58-71-6-10-1-16 4-21 5-5 10-12 16-18 5-6 7-10 10-17 3-7 2-13-1-18s-22-54-31-74c-8-19-16-16-23-17h-19c-7 0-17 2-26 12s-35 34-35 83 36 97 41 103c5 6 71 106 171 148 24 10 43 16 57 21 24 8 46 6 63 3 19-3 61-25 69-49 9-24 9-45 6-49s-10-7-19-11z'),
    'email': ('E014', 'M128 192v512q0 26 19 45t45 19h640q26 0 45-19t19-45v-512q0-26-19-45t-45-19h-640q-26 0-45 19t-19 45zM192 192h640v64l-320 192-320-192v-64zM192 320l320 192 320-192v384h-640v-384z'),
}


def parse_svg_path_to_pen(path_d, pen):
    """Parse SVG path data and draw it to a pen, converting cubic to quadratic."""
    tokens = re.findall(r'([MmZzLlHhVvCcSsQqTtAa])|([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)', path_d)
    
    commands = []
    values = []
    for cmd, val in tokens:
        if cmd:
            commands.append(cmd)
            values.append([])
        else:
            values[-1].append(float(val))
    
    x, y = 0, 0
    cx, cy = 0, 0
    start_x, start_y = 0, 0
    
    i = 0
    for cmd in commands:
        vals = values[i]
        i += 1
        
        if cmd == 'M':
            x, y = vals[0], vals[1]
            start_x, start_y = x, y
            pen.moveTo((x, y))
            for j in range(2, len(vals), 2):
                x, y = vals[j], vals[j+1]
                pen.lineTo((x, y))
        elif cmd == 'm':
            x, y = x + vals[0], y + vals[1]
            start_x, start_y = x, y
            pen.moveTo((x, y))
            for j in range(2, len(vals), 2):
                x, y = x + vals[j], y + vals[j+1]
                pen.lineTo((x, y))
        elif cmd == 'L':
            for j in range(0, len(vals), 2):
                x, y = vals[j], vals[j+1]
                pen.lineTo((x, y))
        elif cmd == 'l':
            for j in range(0, len(vals), 2):
                x, y = x + vals[j], y + vals[j+1]
                pen.lineTo((x, y))
        elif cmd == 'H':
            for v in vals:
                x = v
                pen.lineTo((x, y))
        elif cmd == 'h':
            for v in vals:
                x = x + v
                pen.lineTo((x, y))
        elif cmd == 'V':
            for v in vals:
                y = v
                pen.lineTo((x, y))
        elif cmd == 'v':
            for v in vals:
                y = y + v
                pen.lineTo((x, y))
        elif cmd == 'C':
            for j in range(0, len(vals), 6):
                x1, y1 = vals[j], vals[j+1]
                x2, y2 = vals[j+2], vals[j+3]
                x3, y3 = vals[j+4], vals[j+5]
                cx_val = (x1 + x2) / 2
                cy_val = (y1 + y2) / 2
                pen.qCurveTo((cx_val, cy_val), (x3, y3))
                cx, cy = x2, y2
                x, y = x3, y3
        elif cmd == 'c':
            for j in range(0, len(vals), 6):
                x1, y1 = x + vals[j], y + vals[j+1]
                x2, y2 = x + vals[j+2], y + vals[j+3]
                x3, y3 = x + vals[j+4], y + vals[j+5]
                cx_val = (x1 + x2) / 2
                cy_val = (y1 + y2) / 2
                pen.qCurveTo((cx_val, cy_val), (x3, y3))
                cx, cy = x2, y2
                x, y = x3, y3
        elif cmd == 'S':
            for j in range(0, len(vals), 4):
                x1, y1 = 2*x - cx, 2*y - cy
                x2, y2 = vals[j], vals[j+1]
                x3, y3 = vals[j+2], vals[j+3]
                cx_val = (x1 + x2) / 2
                cy_val = (y1 + y2) / 2
                pen.qCurveTo((cx_val, cy_val), (x3, y3))
                cx, cy = x2, y2
                x, y = x3, y3
        elif cmd == 's':
            for j in range(0, len(vals), 4):
                x1, y1 = 2*x - cx, 2*y - cy
                x2, y2 = x + vals[j], y + vals[j+1]
                x3, y3 = x + vals[j+2], y + vals[j+3]
                cx_val = (x1 + x2) / 2
                cy_val = (y1 + y2) / 2
                pen.qCurveTo((cx_val, cy_val), (x3, y3))
                cx, cy = x2, y2
                x, y = x3, y3
        elif cmd == 'Q':
            for j in range(0, len(vals), 4):
                qx, qy = vals[j], vals[j+1]
                x, y = vals[j+2], vals[j+3]
                pen.qCurveTo((qx, qy), (x, y))
        elif cmd == 'q':
            for j in range(0, len(vals), 4):
                qx, qy = x + vals[j], y + vals[j+1]
                x, y = x + vals[j+2], y + vals[j+3]
                pen.qCurveTo((qx, qy), (x, y))
        elif cmd == 'Z' or cmd == 'z':
            pen.closePath()
            x, y = start_x, start_y


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Building {FONT_FAMILY} v{VERSION}")
    print(f"Icons: {len(ICONS)}")
    print("-" * 40)
    
    # Create a new font
    from fontTools.fontBuilder import FontBuilder
    fb = FontBuilder(UNITS_PER_EM, isTTF=True)
    
    # Set up font info
    fb.setupHead(unitsPerEm=UNITS_PER_EM)
    fb.setupNameTable({
        "familyName": FONT_FAMILY,
        "styleName": "Regular",
        "uniqueFontIdentifier": f"{FONT_FAMILY.replace(' ', '')}-Regular",
        "fullName": f"{FONT_FAMILY} Regular",
        "version": VERSION,
        "psName": FONT_FAMILY.replace(" ", ""),
        "copyright": "Copyright 2026 Konsalta Hub",
        "trademark": FONT_FAMILY,
    })
    
    # Create glyphs
    glyphs = {}
    metrics = {}  # (width, lsb) tuples
    
    # .notdef glyph
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((0, 896))
    pen.lineTo((1024, 896))
    pen.lineTo((1024, 0))
    pen.closePath()
    glyphs['.notdef'] = pen.glyph()
    metrics['.notdef'] = (1024, 0)  # (advance width, left side bearing)
    
    # Icon glyphs
    for name, (code, path_d) in ICONS.items():
        try:
            pen = TTGlyphPen(None)
            parse_svg_path_to_pen(path_d, pen)
            glyphs[name] = pen.glyph()
            metrics[name] = (1024, 0)
        except Exception as e:
            print(f"  Warning: Failed to create glyph '{name}': {e}")
            pen = TTGlyphPen(None)
            pen.moveTo((0, 0))
            pen.lineTo((512, 896))
            pen.lineTo((1024, 0))
            pen.closePath()
            glyphs[name] = pen.glyph()
            metrics[name] = (1024, 0)
    
    # Setup glyph order
    glyph_order = ['.notdef'] + list(ICONS.keys())
    
    # Create char codes mapping
    char_map = {int(code, 16): name for name, (code, _) in ICONS.items()}
    
    # Setup glyph order first
    fb.setupGlyphOrder(glyph_order)
    
    # Setup the glyphs and metrics
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    
    # Setup character map before OS/2
    fb.setupCharacterMap(char_map)
    
    # Now setup OS/2 and Post
    fb.setupOS2()
    fb.setupPost()
    
    # Build and save
    font = fb.font
    
    ttf_path = os.path.join(script_dir, f"{FONT_NAME}.ttf")
    font.save(ttf_path)
    print(f"✓ TTF saved: {ttf_path}")
    
    otf_path = os.path.join(script_dir, f"{FONT_NAME}.otf")
    font.save(otf_path)
    print(f"✓ OTF saved: {otf_path}")
    
    print("-" * 40)
    print("Build complete!")
    print("\nTo create WOFF/WOFF2:")
    print("  pip install brotli")
    print(f"  fonttools ttLib.woff2 compress {ttf_path}")


if __name__ == "__main__":
    main()
