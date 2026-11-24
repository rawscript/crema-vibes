#!/usr/bin/env python3
"""Crema Vibes — bespoke editorial sans builder.

All outlines begin as original calligraphic skeletons, then are unioned before
being written to TrueType.  This avoids overlapping-contour artefacts and
keeps joins solid at every weight.
"""
from math import cos, sin, pi
from pathlib import Path
from shapely.geometry import LineString, Polygon, Point, box
from shapely.affinity import scale
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0

FAMILY='Crema Vibes'; OUT=Path(__file__).resolve().parent.parent
WEIGHTS=[(100,'UltraThin'),(200,'Thin'),(300,'Light'),(400,'Regular'),(500,'Medium'),(600,'SemiBold'),(700,'Bold'),(800,'ExtraBold'),(900,'Dark')]
UPM,ASC,DESC=1000,800,-250
# Design guides: baseline 0; flat x-height 500; cap height 710; ascender 730;
# descender -220. Rounded forms intentionally overshoot their flat alignments.
XH, X_OVER, CAP, CAP_OVER, DESCENDER = 500, 12, 710, 16, -220

def pts_arc(cx,cy,rx,ry,a,b,n=24):
    return [(cx+rx*cos(a*pi/180+(b-a)*pi/180*i/n),cy+ry*sin(a*pi/180+(b-a)*pi/180*i/n)) for i in range(n+1)]
def signed(q): return sum(q[i][0]*q[i+1][1]-q[i+1][0]*q[i][1] for i in range(len(q)-1))
def contour(p,q,want_clockwise):
    q=list(q)
    if (signed(q)<0)!=want_clockwise: q.reverse()
    p.moveTo(q[0])
    for z in q[1:]: p.lineTo(z)
    p.closePath()
def pen_from_geom(g):
    p=TTGlyphPen(None)
    for item in getattr(g,'geoms',[g]):
        if item.is_empty or item.geom_type!='Polygon': continue
        contour(p,item.exterior.coords,True)
        for hole in item.interiors: contour(p,hole.coords,False)
    return p.glyph()

def shape(ch,weight):
    # A restrained editorial colour: clean stems, slightly finer cross-strokes,
    # and no bulbous endpoints.  Weight grows steadily from 100 to 900.
    t=18+weight*.10; stem=t; hair=t*.90; forms=[]
    def line(q,z=stem): forms.append(LineString(q).buffer(z/2,cap_style=2,join_style=1,resolution=24))
    def arc(cx,cy,rx,ry,a,b,z=hair): line(pts_arc(cx,cy,rx,ry,a,b,48),z)
    def loop(cx,cy,rx,ry,z=hair): line(pts_arc(cx,cy,rx,ry,0,360,72),z)
    def dot(x,y,z=stem): forms.append(Point(x,y).buffer(z/2,resolution=24))
    def oval(cx,cy,rx,ry): return scale(Point(cx,cy).buffer(1,resolution=48),rx,ry)
    def bowl(cx,cy,rx,ry,z=stem):
        return oval(cx,cy,rx,ry).difference(oval(cx,cy,rx-z,ry-z))
    def arch(l,r,b,top,z=stem):
        """Closed, lightly flared lowercase shoulder with an open counter."""
        mid=(l+r)/2; outer=[(l,b),(l,top-120)]+pts_arc(mid,top-120,(r-l)/2,120,180,0,36)+[(r,b)]
        inner=[(l+z,b+1),(l+z,top-120)]+pts_arc(mid,top-120,(r-l)/2-z,120-z,180,0,36)+[(r-z,b+1)]
        return Polygon(outer,[inner])
    L,R,B,T=120,580,0,CAP
    if ch==' ': return None,280
    if ch=='.': dot(350,55,hair); return unary_union(forms),350
    if ch==',': line([(350,70),(325,-70)],hair); return unary_union(forms),350
    if ch=='-': line([(185,300),(515,300)],hair); return unary_union(forms),700
    if ch=='/': line([(145,-40),(585,760)],hair); return unary_union(forms),700
    if ch=='!': line([(350,160),(350,720)],stem); dot(350,55,hair); return unary_union(forms),700
    if ch=='?': arc(350,520,205,180,-20,200,hair); line([(545,500),(350,275)],hair); dot(350,55,hair); return unary_union(forms),700
    if ch.isdigit():
        if ch=='0': loop(350,360,205,340)
        elif ch=='1': line([(275,610),(350,700),(350,0)],stem); line([(225,0),(485,0)],hair)
        elif ch=='2': arc(335,535,210,175,-10,190,hair); line([(535,500),(150,0)],stem); line([(145,0),(565,0)],hair)
        elif ch=='3': arc(315,535,195,175,-85,105,hair); arc(315,180,205,180,-105,100,hair)
        elif ch=='4': line([(485,0),(485,720)],stem); line([(155,280),(485,720)],stem); line([(145,280),(585,280)],hair)
        elif ch=='5': line([(560,720),(180,720),(180,390),(475,390)],stem); arc(355,180,200,190,-10,205,hair)
        elif ch=='6': arc(365,185,205,185,-15,345,hair); line([(175,190),(230,690)],stem); arc(355,535,190,165,0,230,hair)
        elif ch=='7': line([(145,720),(580,720),(250,0)],stem)
        elif ch=='8': loop(350,535,185,170); loop(350,180,200,180)
        else: loop(340,535,200,185); line([(530,515),(445,0)],stem); arc(330,175,190,170,-80,115,hair)
    elif ch.isupper():
        if ch=='A': line([(110,0),(350,720),(590,0)],stem); line([(205,285),(495,285)],hair)
        elif ch=='B': line([(130,0),(130,720)],stem); arc(310,540,220,180,-90,90,hair); arc(310,180,225,180,-90,90,hair)
        elif ch=='C': arc(380,360,245,340,42,318,hair)
        elif ch=='D': line([(130,0),(130,720)],stem); arc(250,360,300,350,-90,90,hair)
        elif ch=='E': line([(130,0),(130,720)],stem); line([(130,720),(570,720)],hair); line([(130,360),(485,360)],hair); line([(130,0),(570,0)],hair)
        elif ch=='F': line([(130,0),(130,720)],stem); line([(130,720),(570,720)],hair); line([(130,360),(480,360)],hair)
        elif ch=='G': arc(380,360,245,340,40,320,hair); line([(385,300),(590,300),(590,50)],stem)
        elif ch=='H': line([(130,0),(130,720)],stem); line([(570,0),(570,720)],stem); line([(130,365),(570,365)],hair)
        elif ch=='I': line([(230,720),(470,720)],hair); line([(350,720),(350,0)],stem); line([(230,0),(470,0)],hair)
        elif ch=='J': line([(210,720),(560,720),(560,180)],stem); arc(350,180,210,180,-10,190,hair)
        elif ch=='K': line([(130,0),(130,720)],stem); line([(570,720),(130,355),(585,0)],stem)
        elif ch=='L': line([(130,720),(130,0),(570,0)],stem)
        elif ch=='M': line([(115,0),(115,720),(350,335),(585,720),(585,0)],stem)
        elif ch=='N': line([(130,0),(130,720),(570,0),(570,720)],stem)
        elif ch=='O': loop(350,360,235,340)
        elif ch=='P': line([(130,0),(130,720)],stem); arc(315,545,235,175,-90,90,hair)
        elif ch=='Q': loop(340,370,230,340); line([(415,175),(610,-55)],stem)
        elif ch=='R': line([(130,0),(130,720)],stem); arc(315,545,235,175,-90,90,hair); line([(330,365),(590,0)],stem)
        elif ch=='S': line([(540,630),(450,715),(265,700),(150,590),(185,430),(500,305),(545,170),(430,0),(230,25),(135,105)],hair)
        elif ch=='T': line([(120,720),(580,720)],hair); line([(350,720),(350,0)],stem)
        elif ch=='U': line([(130,720),(130,205)],stem); arc(350,205,220,205,180,360,hair); line([(570,205),(570,720)],stem)
        elif ch=='V': line([(110,720),(350,0),(590,720)],stem)
        elif ch=='W': line([(100,720),(235,0),(350,380),(465,0),(600,720)],stem)
        elif ch=='X': line([(120,720),(580,0)],stem); line([(580,720),(120,0)],stem)
        elif ch=='Y': line([(110,720),(350,365),(590,720)],stem); line([(350,365),(350,0)],stem)
        elif ch=='Z': line([(130,720),(575,720),(130,0),(575,0)],stem)
    elif ch.islower():
        # The lowercase carries the editorial character: open bowls, tall x-height,
        # and decisive but restrained diagonal exits.
        if ch=='a': forms.append(bowl(330,250,185,262)); line([(515,XH),(515,0)],stem)
        elif ch=='b': line([(135,0),(135,730)],stem); forms.append(bowl(365,250,200,262))
        elif ch=='c': forms.append(bowl(365,250,205,262).difference(box(365,40,650,460)))
        elif ch=='d': forms.append(bowl(335,250,200,262)); line([(565,0),(565,730)],stem)
        elif ch=='e': forms.append(bowl(350,250,205,262).difference(box(350,275,650,470))); line([(145,270),(525,270)],hair)
        elif ch=='f': arc(385,570,150,150,15,205,hair); line([(300,0),(300,700)],stem); line([(155,375),(490,375)],hair)
        elif ch=='g': forms.append(bowl(340,250,200,262)); line([(540,XH),(540,DESCENDER)],stem); arc(365,-95,175,125,-25,205,hair)
        elif ch=='h': line([(135,0),(135,730)],stem); forms.append(arch(135,565,0,XH))
        elif ch=='i': line([(350,0),(350,505)],stem); dot(350,650,hair)
        elif ch=='j': line([(350,-125),(350,505)],stem); dot(350,650,hair); arc(245,-110,105,100,10,190,hair)
        elif ch=='k': line([(135,0),(135,730)],stem); line([(555,XH),(140,250),(565,0)],stem)
        elif ch=='l': line([(350,0),(350,730)],stem)
        elif ch=='m': forms.append(arch(95,365,0,XH)); forms.append(arch(355,625,0,XH))
        elif ch=='n': forms.append(arch(135,565,0,XH))
        elif ch=='o': forms.append(bowl(350,250,205,262))
        elif ch=='p': line([(135,DESCENDER),(135,XH)],stem); forms.append(bowl(365,250,200,262))
        elif ch=='q': forms.append(bowl(335,250,200,262)); line([(565,XH),(565,DESCENDER)],stem)
        elif ch=='r': line([(135,0),(135,XH)],stem); forms.append(arch(135,520,220,440))
        elif ch=='s': line([(515,420),(420,500),(245,480),(155,375),(205,265),(475,190),(535,95),(430,0),(245,20),(155,95)],hair)
        elif ch=='t': line([(350,0),(350,675)],stem); line([(170,375),(535,375)],hair); arc(440,95,95,95,-10,180,hair)
        elif ch=='u': line([(135,505),(135,185)],stem); arc(350,185,215,185,180,360,hair); line([(565,505),(565,0)],stem)
        elif ch=='v': line([(120,505),(350,0),(580,505)],stem)
        elif ch=='w': line([(95,505),(225,0),(350,275),(475,0),(605,505)],stem)
        elif ch=='x': line([(125,505),(575,0)],stem); line([(575,505),(125,0)],stem)
        elif ch=='y': line([(125,505),(350,0),(575,505)],stem); line([(350,0),(235,-220)],stem)
        elif ch=='z': line([(135,505),(565,505),(135,0),(565,0)],hair)
    return unary_union(forms),700

def build(weight,style):
    chars=''.join(chr(i) for i in range(32,127)); gs={}; met={}; cmap={}
    for ch in chars:
        name='space' if ch==' ' else f'uni{ord(ch):04X}'; geom,adv=shape(ch,weight); gs[name]=TTGlyphPen(None).glyph() if geom is None else pen_from_geom(geom); met[name]=(adv,0); cmap[ord(ch)]=name
    p=TTGlyphPen(None); contour(p,[(85,0),(615,0),(615,720),(85,720),(85,0)],True); contour(p,[(155,70),(545,70),(545,650),(155,650),(155,70)],False); gs['.notdef']=p.glyph(); met['.notdef']=(700,0)
    fb=FontBuilder(UPM,isTTF=True); fb.setupGlyphOrder(['.notdef']+[cmap[ord(c)] for c in chars]); fb.setupGlyf(gs); fb.setupHorizontalMetrics(met); fb.setupHorizontalHeader(ascent=ASC,descent=DESC); fb.setupCharacterMap(cmap); fb.setupHead(unitsPerEm=UPM); fb.setupOS2(sTypoAscender=ASC,sTypoDescender=DESC,usWinAscent=ASC,usWinDescent=-DESC,usWeightClass=weight,fsSelection=0x40,sxHeight=XH,sCapHeight=CAP)
    ps='CremaVibes-'+style; fb.setupNameTable({'familyName':FAMILY,'styleName':style,'uniqueFontIdentifier':'Crema Vibes: '+ps,'fullName':FAMILY+' '+style,'psName':ps,'version':'Version 2.100','copyright':'Copyright 2026 Crema Vibes. Original outlines.','trademark':'Crema Vibes'}); fb.setupPost(); fb.setupMaxp()
    # Kern the most visible Latin display pairs.  The values are in font units
    # and become slightly stronger in heavier masters to preserve white-space.
    k=newTable('kern'); k.version=0; sub=KernTable_format_0(); sub.version=0; sub.coverage=1; sub.format=0
    adjust=round(22+weight*.025); pairs=['AV','AW','AY','AT','Ta','Te','To','Va','Ve','Vo','Wa','We','Wo','Ya','Yo','LT','FA','PA']
    sub.kernTable={(cmap[ord(a)],cmap[ord(b)]):-adjust for a,b in pairs}; k.kernTables=[sub]; fb.font['kern']=k
    ttf=OUT/(ps+'.ttf'); fb.save(ttf)
    for flavor in ('woff','woff2'):
        f=TTFont(ttf); f.flavor=flavor; f.save(OUT/(ps+'.'+flavor))
    if style=='Regular':
        for suffix in ('ttf','woff','woff2'): (OUT/f'crema-vibes.{suffix}').write_bytes((OUT/f'{ps}.{suffix}').read_bytes())

if __name__=='__main__':
    for weight,style in WEIGHTS: build(weight,style)
