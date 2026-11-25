from PIL import Image, ImageDraw, ImageFont

# 1. Render 'The new font' on royal blue background
img1 = Image.new('RGB', (1200, 600), (16, 24, 138))
d1 = ImageDraw.Draw(img1)
for style, y in [('CremaVibes-Light.ttf', 110), ('CremaVibes-Regular.ttf', 250), ('CremaVibes-Bold.ttf', 390)]:
    f = ImageFont.truetype(style, 88)
    d1.text((100, y), 'The new font', font=f, fill=(255, 255, 255))
img1.save('specimen_the_new_font.png')

# 2. Render full editorial specimens (Regular & Bold)
for style, out_name in [('CremaVibes-Regular.ttf', 'specimen_regular.png'), ('CremaVibes-Bold.ttf', 'specimen_bold.png')]:
    img = Image.new('RGB', (1600, 960), (252, 251, 249))
    d = ImageDraw.Draw(img)
    f_title = ImageFont.truetype(style, 58)
    f_alpha = ImageFont.truetype(style, 46)
    f_body  = ImageFont.truetype(style, 32)
    f_tag   = ImageFont.truetype(style, 54)

    d.text((60, 45), 'Crema Vibes \u2014 Bespoke Editorial Sans', font=f_title, fill=(25, 28, 36))
    d.line([(60, 130), (1540, 130)], fill=(220, 222, 230), width=2)

    d.text((60, 165), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', font=f_alpha, fill=(25, 28, 36))
    d.text((60, 240), 'abcdefghijklmnopqrstuvwxyz', font=f_alpha, fill=(25, 28, 36))
    d.text((60, 315), '0123456789  !? . , : ; - / ( ) + = \' \" &', font=f_alpha, fill=(25, 28, 36))
    d.line([(60, 405), (1540, 405)], fill=(220, 222, 230), width=2)

    d.text((60, 445), 'The quick brown fox jumps over the lazy dog.', font=f_body, fill=(40, 44, 54))
    d.text((60, 505), 'Sphinx of black quartz, judge my vow.', font=f_body, fill=(40, 44, 54))
    d.text((60, 565), 'Pack my box with five dozen liquor jugs.', font=f_body, fill=(40, 44, 54))
    d.text((60, 625), 'How razorback-jumping frogs can level six piqued gymnasts!', font=f_body, fill=(40, 44, 54))
    d.text((60, 685), 'The new font \u2014 Uu Vv Ww 0123456789 (2026)', font=f_body, fill=(40, 44, 54))
    d.line([(60, 765), (1540, 765)], fill=(220, 222, 230), width=2)

    d.text((60, 815), 'Modernity, Precision & Warmth', font=f_tag, fill=(235, 92, 32))
    img.save(out_name)

# 3. Render 14 Crema Vibes Icons sheet (rendered_glyphs.png)
icons = [
    (0xE001, 'arrow-up'), (0xE002, 'menu'), (0xE003, 'search'), (0xE004, 'trending'),
    (0xE005, 'chip'), (0xE006, 'document'), (0xE007, 'target'), (0xE008, 'bar-chart'),
    (0xE009, 'layers'), (0xE010, 'chat'), (0xE011, 'megaphone'), (0xE012, 'linkedin'),
    (0xE013, 'whatsapp'), (0xE014, 'email'),
]
img_ic = Image.new('RGB', (1480, 320), (14, 24, 42))
dic = ImageDraw.Draw(img_ic)
f_icon = ImageFont.truetype('crema-vibes.ttf', 52)
f_lbl = ImageFont.truetype('CremaVibes-Regular.ttf', 16)
for idx, (cp, lbl) in enumerate(icons):
    col = idx % 7
    row = idx // 7
    x = 50 + col * 205
    y = 40 + row * 140
    dic.text((x + 35, y), chr(cp), font=f_icon, fill=(242, 101, 34))
    dic.text((x + 25, y + 72), lbl, font=f_lbl, fill=(225, 232, 244))
img_ic.save('rendered_glyphs.png')

print('All specimens & rendered_glyphs.png saved!')
