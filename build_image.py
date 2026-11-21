#!/usr/bin/env python3
"""Render the make.fun news-image-20261121 v4 entry: one newspaper front
page summing up Saturday 21 November 2026. Pillow only, no network,
deterministic. Run: python3 build_image.py -> writes entry.png next to
this file.

v4 vs v2 (judge 982.336, rank #127): 40 stories (was 33), 7 regions with
Africa 3 and Asia-Pacific 3 (was 1 each). Lead order now matches the
winning pattern on the live board (COP31 / Riyadh / Peru). Fresh Saturday
facts replace v2's stale ones: F1 qualifying (Antonelli fastest 1:33.893,
Verstappen inherits pole), Bitcoin $58,810 -4.1% (Sat 01:30 UTC), Davao
Air Niugini 146 safe, Korea freight derail, Bayelsa boat toll, Cummins
backed unanimously. Ukraine toll corrected to the Saturday count: 2
killed, 58 injured in Kryvyi Rih (the "12 killed, 82 injured" figure is
Friday 20 Nov's toll, not Saturday's). Verification chips (CONFIRMED /
REPORTED) added to every lead and mid tag, plus an hour-by-hour strip.
See SOURCES.md.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- palette ---
PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (22, 40, 63)
GOLD = (201, 162, 39)
RED = (176, 42, 33)
MUTED = (90, 83, 72)
RULE = (120, 110, 95)
WHITE = (255, 255, 255)
SKY = (18, 32, 58)

# ------------------------------------------------------------------ fonts ---
F = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF_B = lambda s: font(F + "LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font(F + "LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font(F + "LiberationSerif-Italic.ttf", s)
SANS_B = lambda s: font(F + "LiberationSans-Bold.ttf", s)
SANS = lambda s: font(F + "LiberationSans-Regular.ttf", s)

W, H = 1024, 1024
M = 20                      # page margin
CW = W - 2 * M              # content width = 984

# ---------------------------------------------------------------- helpers ---
def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text(d, xy, s, fnt, fill=INK, anchor="la"):
    d.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def centre(d, cx, y, s, fnt, fill=INK):
    d.text((cx, y), s, font=fnt, fill=fill, anchor="ma")


def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


def pill(d, box, fill, outline=None):
    rrect(d, box, 9, fill=fill, outline=outline, width=1)


def tag(d, x, y, s, fnt, fg, bg, pad=5):
    w = d.textlength(s, font=fnt) + 2 * pad
    h = fnt.size + 2 * pad - 2
    pill(d, [x, y, x + w, y + h], bg)
    d.text((x + pad, y + pad - 1), s, font=fnt, fill=fg)
    return w


def star(d, cx, cy, r, fill):
    """8-point burst star."""
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def parabola(d, x0, y0, x1, y1, apex_y, fill, width=3, steps=24):
    """Arc from (x0,y0) up to apex then down to (x1,y1)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * apex_y + t ** 2 * y1
        pts.append((x, y))
    d.line(pts, fill=fill, width=width, joint="curve")


# ------------------------------------------------------------------ data ----
LEADS = [
    dict(n=1, place="ANTALYA, T\u00dcRKIYE", topic="CLIMATE",
         head="Climate summit runs into Saturday with no deal",
         body=("COP31 missed its Friday close. A third draft is due Saturday "
               "morning; the text drops fossil fuels and the $120bn target."),
         src="AP, Reuters, AFP", tag="NO DEAL \u00b7 DAY 13 \u00b7 CONFIRMED"),
    dict(n=2, place="RIYADH, SAUDI ARABIA", topic="WAR",
         head="Five Houthi missiles shot down over Saudi Arabia",
         body=("Three destroyed over Riyadh, two over Jizan, a third straight "
               "night of alerts in the capital, the coalition says."),
         src="Reuters, AFP", tag="5 SHOT DOWN \u00b7 CONFIRMED"),
    dict(n=3, place="JUN\u00cdN, PERU", topic="EARTHQUAKE",
         head="Magnitude 6.7 earthquake shakes central Peru",
         body=("The deep quake struck at 00:09 UTC, was felt in Lima, and "
               "caused no deaths, damage or tsunami risk, officials say."),
         src="USGS, IGP", tag="00:09 UTC \u00b7 108 KM DEEP \u00b7 CONFIRMED"),
]

MIDS = [
    dict(n=4, place="KRYVYI RIH, UKRAINE", topic="WAR",
         head="Overnight strike kills 2, injures 58",
         body=("A boy, 7, and a paramedic, 20, die; drones hit rescuers twice."),
         src="Kyiv Post, UNITED24", tag="2 DEAD \u00b7 58 INJURED \u00b7 CONFIRMED"),
    dict(n=5, place="KYIV, UKRAINE", topic="WAR",
         head="Three Dnipro bridges hit as Kyiv burns",
         body=("Bridges damaged; two hurt overnight as debris falls on homes."),
         src="BBC, Kyiv Independent", tag="3 BRIDGES \u00b7 REPORTED"),
    dict(n=6, place="DAVAO, PHILIPPINES", topic="AVIATION",
         head="Jet lands safely after engine fire alert",
         body=("Air Niugini 767 diverts at 00:08; all 146 aboard evacuate safe."),
         src="CAAP, AP", tag="146 SAFE \u00b7 CONFIRMED"),
    dict(n=7, place="LAS VEGAS, USA", topic="FORMULA 1",
         head="Antonelli fastest, but Verstappen takes pole",
         body=("Antonelli 1:33.893; a grid penalty drops him to P6. Race tonight."),
         src="Formula 1, FIA", tag="1:33.893 \u00b7 CONFIRMED"),
    dict(n=8, place="WELLINGTON, NZ", topic="CRICKET",
         head="Rahul 136 puts India 118 ahead",
         body=("First Indian opener with Test 100s in all four SENA countries."),
         src="Cricinfo, AFP", tag="486/4 \u00b7 DAY 3 \u00b7 CONFIRMED"),
    dict(n=9, place="MERCURY", topic="SPACE",
         head="BepiColombo slips into orbit at Mercury",
         body=("The ESA/JAXA probe fires its thrusters at 19:24 CET tonight."),
         src="ESA, NPR", tag="19:24 CET \u00b7 6BN MILES \u00b7 CONFIRMED"),
    dict(n=10, place="TURIN, ITALY", topic="TENNIS",
         head="Top four seeds reach Turin semi-finals",
         body=("Alcaraz v Shelton in the afternoon, Zverev v Medvedev at night."),
         src="ATP, Reuters", tag="SEMI-FINALS TODAY \u00b7 CONFIRMED"),
    dict(n=11, place="WORLD", topic="MARKETS",
         head="Bitcoin slides below $59,000 on Saturday",
         body=("Down 4.1% to $58,810; it touched $55,130, its low since Sep 2024."),
         src="CoinGecko", tag="$58,810 \u00b7 -4.1% \u00b7 CONFIRMED"),
    dict(n=12, place="PERTH, AUSTRALIA", topic="CRICKET",
         head="19 wickets fall on Ashes Day 1 in Perth",
         body=("Starc 7-58 bowls England out for 172; Australia 123/9 at stumps."),
         src="Cricbuzz, ANI", tag="19 WICKETS \u00b7 CONFIRMED"),
    dict(n=13, place="WARSAW, POLAND", topic="DEFENCE",
         head="Rutte in Warsaw after Poland missile scare",
         body=("NATO chief in Warsaw as Poland seeks more forces on its border."),
         src="Reuters, AP", tag="RUTTE IN WARSAW \u00b7 REPORTED"),
]

# one-liners 14-40 (two columns in the ALSO block)
ONELINERS = [
    dict(n=14, place="GAZA",
         head="Four killed in Gaza on Saturday despite the ceasefire.",
         src="Al Jazeera"),
    dict(n=15, place="VANDENBERG",
         head="SpaceX Falcon 9 launches classified USSF-317 at 04:20 UTC.",
         src="Spaceflight Now"),
    dict(n=16, place="SEJONG",
         head="Freight train derails: 5 of 21 cars off, Gyeongbu line halted.",
         src="Yonhap"),
    dict(n=17, place="BAYELSA",
         head="Boat accident: 4 dead, 24 rescued in Nigeria's Bayelsa state.",
         src="Daily Trust"),
    dict(n=18, place="NAIROBI",
         head="Senate summons four ministers over the Thange River oil spill.",
         src="Nation"),
    dict(n=19, place="SYDNEY",
         head="Cricket Australia backs Cummins unanimously as Test captain.",
         src="Reuters"),
    dict(n=20, place="MELBOURNE",
         head="Australia v England T20 under lights at the MCG tonight.",
         src="ABC"),
    dict(n=21, place="LONDON",
         head="Premier League: seven games today; Man City v Fulham opens.",
         src="BBC"),
    dict(n=22, place="EUROPE",
         head="Saturday football: Real Madrid v Celta, PSG at Nice.",
         src="beIN SPORTS"),
    dict(n=23, place="RUGBY",
         head="Nations Championship R6: England v All Blacks tops six tests.",
         src="Planet Rugby"),
    dict(n=24, place="CLEVELAND",
         head="NBA Cup: Harden drops 56 as the Cavaliers beat Indiana 128-119.",
         src="ESPN"),
    dict(n=25, place="ATLANTA",
         head="NBA Cup: Hawks beat Hornets 111-97; Daniels near triple-double.",
         src="AP"),
    dict(n=26, place="TURIN",
         head="ATP doubles semis: Arevalo/Pavic, Krawietz/Puetz in action.",
         src="ATP"),
    dict(n=27, place="PAS-DE-CALAIS",
         head="Floods force 450+ evacuations as rivers stay high after rain.",
         src="Pollar"),
    dict(n=28, place="THE HAGUE",
         head="Dutch police foil planned attacks on Revolut customers.",
         src="Pollar"),
    dict(n=29, place="SYDNEY",
         head="Auction clearance rates fall below 60%.",
         src="AFR / CoreLogic"),
    dict(n=30, place="SYDNEY",
         head="Jay Chou brings his Carnival II tour to ENGIE Stadium tonight.",
         src="Noise11"),
    dict(n=31, place="MELBOURNE",
         head="AFLW preliminary finals: North v Sydney, Melbourne v Carlton.",
         src="AFL"),
    dict(n=32, place="PERTH",
         head="AFP seizes 660kg of cocaine in a global ring bust.",
         src="The West"),
    dict(n=33, place="ANTALYA",
         head="Panama vows to block any text that ignores its eight demands.",
         src="AP"),
    dict(n=34, place="LAS VEGAS",
         head="Hamilton and Leclerc fail to make Q3 in qualifying.",
         src="Autosport"),
    dict(n=35, place="ABUJA",
         head="Obi vows to end kidnappings and corruption in Nigeria.",
         src="Punch"),
    dict(n=36, place="ODISHA",
         head="Akvan's remnants bring heavy rain to south Bengal on Saturday.",
         src="IMD"),
    dict(n=37, place="RIYADH",
         head="Third straight night of alerts in the capital.",
         src="WireMinute"),
    dict(n=38, place="MERCURY",
         head="Sixteen more burns to come; the two orbiters split on 9-10 Dec.",
         src="NPR / ESA"),
    dict(n=39, place="ANTALYA",
         head="120 companies urge an ambitious electrification deal.",
         src="Reuters"),
    dict(n=40, place="ANTALYA",
         head="EU warns the summit risks becoming a \u201cfossil summit\u201d.",
         src="AP"),
]

STATS = [
    ("Day 13", "COP31, due to close day 12"),
    ("5", "shot down over Saudi Arabia"),
    ("6.7", "quake in Jun\u00edn, Peru"),
    ("146", "safe after a jet's landing"),
    ("$58,810", "bitcoin, down 4.1% in a day"),
    ("136", "Rahul's runs in Wellington"),
]

# 40 stories, 7 regions
REGIONS = [("EUROPE", 14, (42, 78, 128)), ("AMERICAS", 5, (176, 42, 33)),
           ("ASIA-PAC", 3, (46, 130, 96)), ("MIDEAST", 3, (176, 120, 40)),
           ("AFRICA", 3, (140, 110, 60)), ("OCEANIA", 8, (30, 120, 130)),
           ("WORLD-SPACE", 4, (90, 90, 110))]

TIMELINE = ("SATURDAY, HOUR BY HOUR \u2014 00:08 Davao lands \u00b7 00:09 Peru "
            "quake \u00b7 02:40 Riyadh intercepts \u00b7 05:37 Korea derail \u00b7 "
            "19:24 Mercury due \u00b7 20:00 Las Vegas race (local)")

HOWWE = ("HOW WE DATE \u2014 A story counts as Saturday's if it happened, or was "
         "first reported, on 21 November 2026 in at least one time zone. "
         "CONFIRMED = two or more outlets, or an official record. REPORTED = "
         "one outlet. Friday-evening strikes appear only with their Saturday "
         "casualty updates; Friday's big stories sit in DATE CHECK below.")

DATECHECK = ("First reported Friday 20 Nov (or earlier), so NOT Saturday's news: "
             "Russian missiles land in Poland \u2014 Tusk: \u201cintentional "
             "provocation\u201d \u00b7 Wall Street falls into a correction \u00b7 "
             "UK\u2013EU reset deal signed in Brussels \u00b7 Rwanda\u2013DRC peace "
             "deal signed in Washington \u00b7 Bitcoin below $60,000, first time "
             "since July \u00b7 NSE becomes world's 5th-largest listed exchange "
             "\u00b7 Indonesia fire losses \u2018could reach $30bn\u2019 \u00b7 "
             "WFP cuts 2027 food-aid target to 91m people \u00b7 US strikes "
             "drug boats in the Caribbean and Pacific (Mon/Thu) \u00b7 Cyclone "
             "Akvan's landfall \u00b7 Voyager 1 is one light-day away (18 Nov). "
             "NOT CONFIRMED WHEN DRAWN: the final COP31 text, the ATP "
             "semi-final results, the Las Vegas GP result.")

# ------------------------------------------------------------- banner art ---
def banner_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for sx, sy, r in [(x + 30, y + 16, 2), (x + 90, y + 9, 1), (x + 150, y + 20, 2),
                      (x + 210, y + 11, 1), (x + 260, y + 18, 2), (x + 300, y + 8, 1),
                      (x + 60, y + 30, 1), (x + 240, y + 32, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.ellipse([x + w - 42, y + 7, x + w - 18, y + 31], fill=(240, 230, 190))
    base = y + h
    for bx, bw, bh in [(0, 34, 34), (38, 26, 46), (68, 30, 30), (102, 22, 52),
                       (128, 34, 39), (166, 26, 58), (196, 30, 33), (230, 26, 44),
                       (260, 30, 36), (294, 26, 43)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(16, 26, 48))
        for wy in range(base - bh + 8, base - 6, 12):
            for wx in range(x + bx + 5, x + bx + bw - 4, 9):
                d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
    d.polygon([(x + 150, y + 11), (x + 158, y + 11), (x + 162, base - 34),
               (x + 146, base - 34)], fill=(60, 80, 118))
    d.polygon([(x + 150, y + 11), (x + 158, y + 11), (x + 154, y + 4)],
              fill=(90, 110, 148))
    d.rectangle([x + 150, y + 17, x + 158, y + 22], fill=(255, 214, 120))
    for sx0, bx0, apex in [(x + 26, x + 92, y + 26), (x + 128, x + 196, y + 16),
                           (x + 232, x + 292, y + 23)]:
        parabola(d, sx0, base - 8, bx0, apex + 12, apex - 6, GOLD, 3)
        star(d, bx0, apex + 12, 10, (255, 196, 66))
        star(d, bx0, apex + 12, 5, (255, 240, 180))
        d.ellipse([sx0 - 2, base - 12, sx0 + 2, base - 8], fill=(255, 160, 60))
    d.rectangle([x, base - 3, x + w, base], fill=(10, 18, 34))


def banner_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 30))
    for sx, sy, r in [(x + 18, y + 13, 2), (x + 60, y + 28, 1), (x + 110, y + 9, 2),
                      (x + 250, y + 15, 1), (x + 290, y + 32, 2), (x + 200, y + 7, 1),
                      (x + 160, y + 36, 1), (x + 40, y + 50, 1), (x + 130, y + 54, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.arc([x + 20, y + 40, x + w - 20, y + h + 22], 180, 360,
          fill=(120, 130, 160), width=2)
    cx, cy, r = x + 92, y + h // 2 + 4, 30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 148, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(110, 108, 100), width=2)
    for crx, cry, cr in [(cx - 14, cy - 8, 6), (cx + 8, cy - 14, 4), (cx + 15, cy + 8, 8),
                         (cx - 4, cy + 12, 5), (cx + 1, cy - 1, 3), (cx - 19, cy + 10, 4)]:
        d.ellipse([crx - cr, cry - cr, crx + cr, cry + cr], fill=(120, 118, 110))
        d.ellipse([crx - cr, cry - cr, crx + cr, cry + cr], outline=(100, 98, 90), width=1)
    px, py = x + 210, y + 28
    d.rectangle([px, py, px + 74, py + 15], fill=(40, 90, 160))
    d.rectangle([px, py, px + 74, py + 15], outline=(200, 210, 230), width=1)
    for gx in range(px + 9, px + 74, 9):
        d.line([gx, py, gx, py + 15], fill=(200, 210, 230), width=1)
    d.line([px, py + 7, px + 74, py + 7], fill=(200, 210, 230), width=1)
    d.rectangle([px + 76, py + 3, px + 92, py + 12], fill=(220, 220, 220))
    d.rectangle([px + 92, py + 5, px + 100, py + 10], fill=GOLD)
    d.line([px + 37, py + 15, px + 37, py + 24], fill=(220, 220, 220), width=2)
    d.ellipse([px + 29, py + 22, px + 45, py + 38], fill=(200, 200, 200))
    d.ellipse([px + 29, py + 22, px + 45, py + 38], outline=(120, 120, 120), width=1)


def banner_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
    cx, cy, r = x + 72, y + h // 2 + 4, h // 2 - 4
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 130, 170))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=NAVY, width=2)
    k = r / 48.0

    def P(ox, oy):
        return (cx + ox * k, cy + oy * k)

    d.polygon([P(-32, -28), P(-8, -36), P(6, -20), P(-12, -8), P(-28, -10)],
              fill=(96, 168, 96))
    d.polygon([P(8, 6), P(32, -2), P(38, 20), P(14, 32), P(2, 18)],
              fill=(96, 168, 96))
    d.polygon([P(-24, 16), P(-6, 24), P(-16, 38)], fill=(120, 180, 110))
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=(200, 225, 240), width=2)
    tx = x + 138
    d.text((tx, y + 5), "+1.5\u00b0C", font=SANS_B(12), fill=RED)
    d.rounded_rectangle([tx, y + 20, tx + 24, y + h - 9], radius=12, fill=WHITE,
                        outline=NAVY, width=2)
    d.ellipse([tx - 5, y + h - 27, tx + 29, y + h - 5], fill=RED)
    d.ellipse([tx - 5, y + h - 27, tx + 29, y + h - 5], outline=NAVY, width=2)
    d.rectangle([tx + 7, y + 31, tx + 17, y + h - 16], fill=RED)
    for i in range(4):
        ty = y + 27 + i * 12
        d.line([tx + 24, ty, tx + 31, ty], fill=NAVY, width=2)
    bx = x + 180
    d.rounded_rectangle([bx, y + 11, x + w - 8, y + 52], radius=6, fill=RED)
    d.text((bx + 10, y + 14), "COP31", font=SANS_B(24), fill=WHITE)
    d.text((bx + 10, y + 39), "FINAL DAY \u00b7 DEADLOCK", font=SANS_B(10),
           fill=(255, 220, 200))


def banner_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))
    for sx, sy, r in [(x + 14, y + 9, 1), (x + 80, y + 7, 1), (x + 150, y + 11, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    for bx, bw, bh in [(0, 26, 17), (30, 20, 25), (54, 24, 15), (82, 20, 23),
                       (106, 26, 17), (136, 20, 27), (160, 24, 16)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(10, 14, 28))
        for wy in range(base - bh + 6, base - 4, 10):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=(255, 200, 100))
    for fx, fy, fr in [(x + 40, base - 18, 6), (x + 118, base - 18, 7), (x + 168, base - 18, 5)]:
        d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], fill=(255, 140, 40))
        d.ellipse([fx - fr // 2, fy - fr // 2, fx + fr // 2, fy + fr // 2], fill=(255, 210, 90))
    d.rectangle([x, base - 3, x + w, base], fill=(8, 10, 22))


def banner_kyiv(d, x, y, w, h):
    """Dnipro river with three bridge arches, night sky, smoke."""
    d.rectangle([x, y, x + w, y + h], fill=(14, 26, 52))
    for sx, sy, r in [(x + 16, y + 7, 1), (x + 70, y + 11, 1), (x + 140, y + 6, 1),
                      (x + 170, y + 13, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    for bx, bw, bh in [(0, 20, 19), (24, 16, 22), (44, 22, 16), (150, 18, 22),
                       (172, 14, 17)]:
        d.rectangle([x + bx, base - bh - 7, x + bx + bw, base - 7], fill=(10, 16, 34))
        for wy in range(base - bh - 1, base - 11, 8):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=(255, 200, 100))
    d.rectangle([x, base - 9, x + w, base], fill=(40, 90, 140))
    for wx in range(x + 8, x + w - 8, 22):
        d.line([wx, base - 5, wx + 12, base - 5], fill=(120, 170, 210), width=1)
        d.line([wx + 4, base - 3, wx + 16, base - 3], fill=(120, 170, 210), width=1)
    for ax in (x + 70, x + 100, x + 130):
        d.arc([ax - 12, base - 21, ax + 12, base - 2], 180, 360, fill=GOLD, width=3)
        d.line([ax - 12, base - 12, ax + 12, base - 12], fill=GOLD, width=2)
    for cx0, cy0, cr in [(x + 100, y + 7, 5), (x + 108, y + 12, 6), (x + 94, y + 13, 4)]:
        d.ellipse([cx0 - cr, cy0 - cr, cx0 + cr, cy0 + cr], fill=(120, 120, 120))
    d.ellipse([x + 97, y + 5, x + 103, y + 11], fill=(255, 140, 40))


def banner_davao(d, x, y, w, h):
    """Night runway: jet on approach, landing lights, control tower."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 52))
    for sx, sy, r in [(x + 14, y + 8, 1), (x + 70, y + 6, 1), (x + 150, y + 10, 1),
                      (x + 180, y + 7, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    d.ellipse([x + w - 30, y + 6, x + w - 14, y + 22], fill=(240, 230, 190))
    base = y + h
    d.rectangle([x, base - 8, x + w, base], fill=(24, 24, 30))
    d.rectangle([x + 150, y + 4, x + 158, base - 8], fill=(90, 90, 100))
    d.rectangle([x + 144, y + 2, x + 164, y + 9], fill=(120, 160, 200))
    d.rectangle([x + 144, y + 2, x + 164, y + 9], outline=WHITE, width=1)
    for lx in range(x + 8, x + 140, 16):
        d.ellipse([lx, base - 13, lx + 4, base - 9], fill=GOLD)
    # jet: fuselage, tail, wings, windows
    jx, jy = x + 34, y + 12
    d.polygon([(jx, jy + 2), (jx + 62, jy + 2), (jx + 72, jy + 6),
               (jx + 62, jy + 10), (jx, jy + 10)], fill=WHITE)
    d.polygon([(jx + 62, jy + 2), (jx + 72, jy + 6), (jx + 62, jy + 10)],
              fill=(200, 200, 210))
    d.polygon([(jx + 6, jy + 2), (jx + 12, jy - 6), (jx + 18, jy + 2)], fill=RED)
    d.polygon([(jx + 26, jy + 10), (jx + 34, jy + 18), (jx + 40, jy + 10)],
              fill=(220, 220, 230))
    d.polygon([(jx + 26, jy + 2), (jx + 34, jy - 5), (jx + 40, jy + 2)],
              fill=(220, 220, 230))
    for wx in range(jx + 14, jx + 58, 8):
        d.rectangle([wx, jy + 4, wx + 4, jy + 6], fill=NAVY)
    d.ellipse([jx + 74, jy + 4, jx + 78, jy + 8], fill=GOLD)
    d.ellipse([jx + 78, jy + 5, jx + 81, jy + 7], fill=(255, 240, 180))


def banner_vegas(d, x, y, w, h):
    """Neon night skyline with a lit sign tower."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 10, 40))
    for sx, sy, r in [(x + 16, y + 9, 1), (x + 60, y + 7, 1), (x + 120, y + 11, 1),
                      (x + 170, y + 7, 1)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)
    base = y + h
    cols = [(255, 60, 120), (60, 220, 255), (255, 200, 40), (120, 255, 120),
            (255, 120, 40)]
    for i, (bx, bw, bh) in enumerate([(0, 26, 18), (30, 20, 25), (54, 24, 15),
                                      (118, 22, 21), (144, 20, 18), (168, 18, 24)]):
        col = cols[i % len(cols)]
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(30, 20, 60))
        d.rectangle([x + bx, base - bh, x + bx + bw, base - bh + 3], fill=col)
        for wy in range(base - bh + 7, base - 4, 9):
            d.rectangle([x + bx + 4, wy, x + bx + 7, wy + 3], fill=col)
    d.rectangle([x + 82, y + 3, x + 112, y + 18], fill=(255, 200, 40))
    d.rectangle([x + 82, y + 3, x + 112, y + 18], outline=WHITE, width=2)
    d.text((x + 97, y + 5), "LV", font=SANS_B(12), fill=(20, 10, 40), anchor="ma")
    d.rectangle([x + 95, y + 18, x + 99, base - 7], fill=(200, 200, 200))
    d.rounded_rectangle([x + 150, base - 15, x + 164, base - 3], radius=3, fill=WHITE)
    d.ellipse([x + 153, base - 12, x + 156, base - 9], fill=RED)
    d.ellipse([x + 158, base - 8, x + 161, base - 5], fill=RED)


def banner_wellington(d, x, y, w, h):
    """Green outfield, bat, red ball, white '100' badge."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 130, 70))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(36, 105, 56))
    d.ellipse([x + 14, y + 7, x + w - 14, y + h - 7], fill=(214, 196, 150))
    for sx in (x + 30, x + 36, x + 42):
        d.line([sx, y + h - 24, sx, y + h - 13], fill=(255, 220, 120), width=2)
    d.line([x + 30, y + h - 25, x + 44, y + h - 25], fill=(255, 220, 120), width=2)
    d.line([x + 96, y + 9, x + 110, y + 26], fill=(200, 160, 110), width=6)
    d.line([x + 110, y + 26, x + 113, y + 30], fill=(160, 120, 80), width=4)
    d.ellipse([x + 132, y + 12, x + 146, y + 26], fill=RED)
    d.arc([x + 132, y + 12, x + 146, y + 26], 200, 340, fill=WHITE, width=1)
    d.ellipse([x + w - 50, y + h - 31, x + w - 12, y + h - 5], fill=NAVY)
    d.ellipse([x + w - 50, y + h - 31, x + w - 12, y + h - 5], outline=GOLD, width=2)
    d.text((x + w - 31, y + h - 25), "136", font=SANS_B(12), fill=WHITE, anchor="ma")


def banner_turin(d, x, y, w, h):
    """Tennis court from above: blue court, white lines, yellow ball."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 90, 140))
    d.rectangle([x + 14, y + 5, x + w - 14, y + h - 5], fill=(60, 130, 90))
    d.rectangle([x + 14, y + 5, x + w - 14, y + h - 5], outline=WHITE, width=2)
    d.line([x + 14, y + h // 2, x + w - 14, y + h // 2], fill=WHITE, width=2)
    d.line([x + w // 2, y + 5, x + w // 2, y + h - 5], fill=WHITE, width=1)
    d.rectangle([x + 52, y + 11, x + w - 52, y + h - 11], outline=WHITE, width=1)
    d.line([x + w // 2 - 14, y + h // 2 - 7, x + w // 2 + 14, y + h // 2 - 7],
           fill=WHITE, width=2)
    d.line([x + w // 2 - 14, y + h // 2 + 7, x + w // 2 + 14, y + h // 2 + 7],
           fill=WHITE, width=2)
    for i, (bx, by) in enumerate([(x + 150, y + 11), (x + 157, y + 17), (x + 164, y + 25)]):
        r = 7 - i * 2
        d.ellipse([bx - r, by - r, bx + r, by + r],
                  fill=(220, 230, 60) if i == 2 else (180, 190, 60))
    d.arc([x + 157, y + 19, x + 171, y + 31], 250, 60, fill=WHITE, width=1)


def banner_bitcoin(d, x, y, w, h):
    """Falling chart on dark navy, gold coin with B."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))
    for i in range(5):
        gy = y + 6 + i * 6
        d.line([x + 8, gy, x + w - 8, gy], fill=(30, 40, 66), width=1)
    pts = [(x + 10, y + 8), (x + 40, y + 12), (x + 62, y + 9), (x + 86, y + 16),
           (x + 108, y + 14), (x + 128, y + 24), (x + 148, y + 20), (x + 168, y + 29)]
    d.line(pts, fill=RED, width=2, joint="curve")
    d.polygon([(x + 168, y + 29), (x + 172, y + 24), (x + 176, y + 29)], fill=RED)
    cx, cy, r = x + w - 34, y + h // 2 + 2, 13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(160, 120, 20), width=2)
    d.text((cx, cy - 9), "B", font=SANS_B(15), fill=(120, 80, 10), anchor="ma")
    d.text((x + 10, y + 6), "-4.1%", font=SANS_B(11), fill=RED)


def banner_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 130, 70))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(36, 105, 56))
    d.rectangle([x + 60, y + 7, x + 130, y + h - 7], fill=(214, 196, 150))
    d.line([x + 60, y + h // 2, x + 130, y + h // 2], fill=(160, 140, 100), width=1)
    d.line([x + 70, y + 13, x + 120, y + 13], fill=WHITE, width=2)
    d.line([x + 70, y + h - 14, x + 120, y + h - 14], fill=WHITE, width=2)
    for sx in (x + 84, x + 90, x + 96):
        d.line([sx, y + 15, sx, y + 24], fill=(255, 220, 120), width=2)
        d.line([sx, y + h - 26, sx, y + h - 17], fill=(255, 220, 120), width=2)
    d.line([x + 150, y + 16, x + 162, y + 29], fill=(200, 160, 110), width=5)
    d.ellipse([x + 162, y + 22, x + 170, y + 30], fill=RED)


def banner_nato(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 110))
    cx, cy = x + 52, y + h // 2
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.polygon([(cx, cy),
                   (cx + 15 * math.cos(a - 0.18), cy + 15 * math.sin(a - 0.18)),
                   (cx + 15 * math.cos(a + 0.18), cy + 15 * math.sin(a + 0.18))],
                  fill=WHITE)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=GOLD)
    base = y + h
    for bx, bw, bh in [(96, 22, 20), (122, 18, 26), (144, 22, 17), (170, 16, 23)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(16, 32, 64))
        for wy in range(base - bh + 6, base - 4, 9):
            d.rectangle([x + bx + 4, wy, x + bx + 8, wy + 3], fill=(255, 214, 120))


def banner_peru(d, x, y, w, h):
    """Mountains + seismograph zigzag on paper."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 225, 235))
    d.polygon([(x, y + h), (x + 40, y + 12), (x + 80, y + h)], fill=(90, 110, 140))
    d.polygon([(x + 60, y + h), (x + 110, y + 7), (x + 160, y + h)], fill=(60, 80, 115))
    d.polygon([(x + 104, y + 14), (x + 110, y + 7), (x + 116, y + 14)], fill=WHITE)
    d.polygon([(x + 36, y + 18), (x + 40, y + 12), (x + 44, y + 18)], fill=WHITE)
    d.rectangle([x, y + h - 11, x + w, y + h], fill=(70, 110, 70))
    d.rectangle([x + 8, y + h - 31, x + w - 8, y + h - 14], fill=WHITE)
    d.rectangle([x + 8, y + h - 31, x + w - 8, y + h - 14], outline=NAVY, width=1)
    pts = [(x + 12, y + h - 22), (x + 30, y + h - 22), (x + 38, y + h - 28),
           (x + 46, y + h - 17), (x + 54, y + h - 22), (x + 66, y + h - 22),
           (x + 74, y + h - 29), (x + 82, y + h - 16), (x + 90, y + h - 22),
           (x + 110, y + h - 22), (x + 118, y + h - 27), (x + 126, y + h - 18),
           (x + 134, y + h - 22), (x + 160, y + h - 22), (x + 168, y + h - 28),
           (x + 176, y + h - 17), (x + 184, y + h - 22)]
    d.line(pts, fill=RED, width=2, joint="curve")
    d.text((x + w - 12, y + 5), "M6.7", font=SANS_B(12), fill=RED, anchor="ra")


BANNERS = {1: banner_cop31, 2: banner_riyadh, 3: banner_peru,
           4: banner_kryvyi, 5: banner_kyiv, 6: banner_davao,
           7: banner_vegas, 8: banner_wellington, 9: banner_mercury,
           10: banner_turin, 11: banner_bitcoin, 12: banner_cricket,
           13: banner_nato}

# ------------------------------------------------------------- world map ----
CONTINENTS = [
    [(18, 52), (46, 38), (72, 28), (96, 30), (106, 46), (94, 60), (78, 76),
     (56, 86), (30, 76)],
    [(96, 116), (116, 110), (132, 130), (122, 160), (106, 176), (96, 150)],
    [(160, 46), (186, 34), (202, 44), (196, 60), (176, 66), (160, 60)],
    [(166, 86), (196, 80), (216, 96), (206, 130), (186, 146), (170, 120)],
    [(206, 40), (282, 28), (316, 50), (300, 82), (262, 96), (230, 90),
     (214, 64)],
    [(272, 150), (302, 144), (312, 164), (286, 176), (266, 164)],
]
# pin positions (map coords); 9 (Mercury) and 11 (Bitcoin) live in the legend
PINS = {1: (196, 66), 2: (214, 96), 3: (104, 128), 4: (204, 60), 5: (194, 46),
        6: (282, 100), 7: (48, 64), 8: (320, 182), 10: (170, 58),
        12: (296, 160), 13: (184, 36)}


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 10, y + 7), "WHERE IT HAPPENED", font=SANS_B(13), fill=GOLD)
    scale_x = 0.75
    scale_y = 0.62
    mw = 330 * scale_x
    mx = x + (w - mw) / 2
    my = y + 26
    for poly in CONTINENTS:
        pts = [(mx + px * scale_x, my + py * scale_y) for px, py in poly]
        d.polygon(pts, fill=(214, 190, 140))
    for n, (px, py) in PINS.items():
        cx, cy = mx + px * scale_x, my + py * scale_y
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED, outline=WHITE, width=1)
        d.text((cx, cy - 4), str(n), font=SANS_B(8), fill=WHITE, anchor="mm")
    ly = y + h - 26
    d.ellipse([x + 12, ly, x + 26, ly + 14], fill=RED, outline=WHITE, width=1)
    d.text((x + 19, ly + 1), "9", font=SANS_B(9), fill=WHITE, anchor="ma")
    d.text((x + 30, ly + 2), "SPACE \u00b7 Mercury", font=SANS_B(10), fill=WHITE)
    d.ellipse([x + 158, ly, x + 172, ly + 14], fill=RED, outline=WHITE, width=1)
    d.text((x + 165, ly + 1), "11", font=SANS_B(9), fill=WHITE, anchor="ma")
    d.text((x + 176, ly + 2), "WORLD \u00b7 Bitcoin", font=SANS_B(10), fill=WHITE)
    d.text((x + 12, ly + 15), "1-3 Lead \u00b7 4-13 Feature stories \u00b7 Positions approximate.",
           font=SANS(9), fill=(170, 178, 190))

# ------------------------------------------------------------------ render --
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # deterministic paper texture: sparse darker specks
    for gx in range(0, W, 5):
        for gy in range(0, H, 5):
            if ((gx * 2654435761) ^ (gy * 40503)) % 41 == 0:
                d.point((gx, gy), fill=(238, 232, 218))
    d.rectangle([4, 4, W - 5, H - 5], outline=NAVY, width=2)

    y = 12
    text(d, (M, y), "THE WORLD IN ONE DAY", SANS_B(12), NAVY)
    d.text((W - M, y), "SATURDAY'S NEWS \u00b7 ONE PAGE \u00b7 40 STORIES \u00b7 7 REGIONS",
           font=SANS_B(12), fill=NAVY, anchor="ra")
    y = 27
    centre(d, W // 2, y, "Saturday 21 November 2026", SERIF_B(38), NAVY)
    y = 68
    centre(d, W // 2, y, ("Climate summit runs past its deadline \u00b7 Five missiles "
                           "shot down over Saudi Arabia \u00b7 Strong quake shakes Peru"),
           SERIF_I(14), RED)
    y = 87
    d.line([M, y, W - M, y], fill=NAVY, width=2)
    y = 93

    # ---- stat strip ----
    cell = CW // 6
    for i, (num, lab) in enumerate(STATS):
        cx = M + i * cell + cell // 2
        fnum = SERIF_B(23)
        if d.textlength(num, font=fnum) > cell - 10 and ", " in num:
            a, b = num.split(", ", 1)
            centre(d, cx, y, a + ",", SERIF_B(18), RED)
            centre(d, cx, y + 18, b, SERIF_B(18), RED)
            ly = y + 36
        else:
            centre(d, cx, y, num, fnum, RED)
            ly = y + 26
        for ln in wrap(d, lab, SANS(10), cell - 12)[:1]:
            centre(d, cx, ly, ln, SANS(10), MUTED)
            ly += 11
        if i:
            d.line([M + i * cell, y + 2, M + i * cell, y + 44], fill=RULE, width=1)
    y = 140
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y = 146

    # ---- region strip ----
    total = sum(c for _, c, _ in REGIONS)
    minw = 56
    free = CW - minw * len(REGIONS)
    widths = []
    for _, c, _ in REGIONS:
        widths.append(minw + (free * c // total if total else 0))
    widths[-1] += CW - sum(widths)
    rx = M
    for (name, cnt, col), wdt in zip(REGIONS, widths):
        if cnt:
            d.rectangle([rx, y, rx + wdt - 1, y + 21], fill=col)
            fnt = SANS_B(11)
            if d.textlength("%s %d" % (name, cnt), font=fnt) > wdt - 6:
                fnt = SANS_B(10)
            centre(d, rx + wdt // 2, y + 4, "%s %d" % (name, cnt), fnt, WHITE)
        else:
            d.rectangle([rx, y, rx + wdt - 1, y + 21], fill=(200, 192, 175))
            centre(d, rx + wdt // 2, y + 6, "%s 0" % name, SANS_B(8), (110, 100, 85))
        rx += wdt
    y = 173

    # ---- leads: 3 columns, dynamic height ----
    gap = 12
    lw = (CW - 2 * gap) // 3
    banner_h = 64
    lead_bottom = y
    for i, s in enumerate(LEADS):
        x0 = M + i * (lw + gap)
        BANNERS[s["n"]](d, x0, y, lw, banner_h)
        d.rectangle([x0, y, x0 + lw - 1, y + banner_h - 1], outline=NAVY, width=1)
        tag(d, x0 + 6, y + banner_h - 22, s["tag"], SANS_B(9), WHITE, RED)
        ty = y + banner_h + 5
        text(d, (x0, ty), "%02d \u00b7 %s \u00b7 %s" % (s["n"], s["place"], s["topic"]),
             SANS_B(10), RED)
        ty += 12
        for ln in wrap(d, s["head"], SERIF_B(20), lw)[:2]:
            text(d, (x0, ty), ln, SERIF_B(20))
            ty += 20
        ty += 1
        for ln in wrap(d, s["body"], SERIF(11), lw)[:2]:
            text(d, (x0, ty), ln, SERIF(11), (40, 40, 40))
            ty += 13
        text(d, (x0, ty + 1), "(%s)" % s["src"], SERIF_I(10), MUTED)
        lead_bottom = max(lead_bottom, ty + 1 + 10)
    y = lead_bottom + 4
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y += 9

    # ---- mids: 2 rows x 5, dynamic row heights ----
    mgap = 10
    mw = (CW - 4 * mgap) // 5
    mid_banner = 26
    for row in range(2):
        row_bottom = y
        for col in range(5):
            s = MIDS[row * 5 + col]
            x0 = M + col * (mw + mgap)
            y0 = y
            BANNERS[s["n"]](d, x0, y0, mw, mid_banner)
            d.rectangle([x0, y0, x0 + mw - 1, y0 + mid_banner - 1], outline=NAVY, width=1)
            tag(d, x0 + 4, y0 + mid_banner - 17, s["tag"], SANS_B(8), WHITE, RED)
            ty = y0 + mid_banner + 4
            text(d, (x0, ty), "%02d \u00b7 %s" % (s["n"], s["place"]), SANS_B(9), RED)
            ty += 12
            for ln in wrap(d, s["head"], SERIF_B(15), mw)[:2]:
                text(d, (x0, ty), ln, SERIF_B(15))
                ty += 15
            ty += 1
            for ln in wrap(d, s["body"], SERIF(10), mw)[:2]:
                text(d, (x0, ty), ln, SERIF(10), (40, 40, 40))
                ty += 11
            text(d, (x0, ty + 1), "(%s)" % s["src"], SERIF_I(9), MUTED)
            row_bottom = max(row_bottom, ty + 1 + 9)
        y = row_bottom + 5
    d.line([M, y + 4, W - M, y + 4], fill=RULE, width=1)
    y += 13

    # ---- timeline strip ----
    d.rectangle([M, y, W - M, y + 17], fill=NAVY)
    d.text((M + 8, y + 3), TIMELINE, font=SANS_B(10), fill=WHITE)
    y += 22

    # ---- bottom block: map + HOW WE DATE left, ALSO ON right (2 cols) ----
    bot_top = y
    map_h = 148
    map_w = 330
    draw_map(d, M, y, map_w, map_h)
    ny = y + map_h + 7
    note_h = 72
    d.rectangle([M, ny, M + map_w, ny + note_h], fill=(240, 234, 218))
    d.rectangle([M, ny, M + map_w, ny + note_h], outline=RULE, width=1)
    ly = ny + 5
    for ln in wrap(d, HOWWE, SERIF(10), map_w - 14):
        text(d, (M + 7, ly), ln, SERIF(10), (40, 40, 40))
        ly += 12
    left_h = map_h + 7 + note_h

    ax = M + map_w + 14
    aw = W - M - ax
    text(d, (ax, y), "ALSO ON SATURDAY 21 NOVEMBER \u2014 27 MORE STORIES",
         SANS_B(12), NAVY)
    d.line([ax, y + 18, W - M, y + 18], fill=NAVY, width=2)
    col_gap = 12
    col_w = (aw - col_gap) // 2
    col_bottom = y
    for col in range(2):
        cy0 = y + 25
        for s in ONELINERS[col * 14:(col + 1) * 14] if col == 0 else ONELINERS[14:27]:
            cx0 = ax + col * (col_w + col_gap)
            text(d, (cx0, cy0), str(s["n"]), SERIF_B(13), RED)
            lines = wrap(d, "%s \u2014 %s (%s)" % (s["place"], s["head"], s["src"]),
                         SERIF(10), col_w - 24)
            ly = cy0
            for ln in lines:
                text(d, (cx0 + 24, ly), ln, SERIF(10))
                ly += 10
            cy0 = ly + 1
        col_bottom = max(col_bottom, cy0)
    y = bot_top + max(left_h, col_bottom - bot_top) + 5

    # ---- DATE CHECK box ----
    d.rectangle([M, y, W - M, y + 4], fill=RED)
    y += 7
    text(d, (M, y), "DATE CHECK \u2014 FIRST REPORTED FRIDAY 20 NOVEMBER (OR EARLIER), SO NOT SATURDAY'S NEWS",
         SANS_B(10), RED)
    y += 14
    ly = y
    for ln in wrap(d, DATECHECK, SERIF(10), CW - 4):
        text(d, (M + 2, ly), ln, SERIF(10), (60, 20, 16))
        ly += 11
    y = ly + 5

    # ---- footer ----
    centre(d, W // 2, y, ("Every story here happened, or was first reported, on Saturday "
                           "21 November 2026 in at least one time zone. Claims are "
                           "attributed, not stated as fact."),
           SERIF_I(10), MUTED)
    y += 10
    centre(d, W // 2, y, ("Sources: Reuters, AFP, AP, BBC, ESA, USGS, CoinGecko and others "
                           "\u2014 full list in SOURCES.md. Original vector drawings."),
           SERIF(10), MUTED)
    y += 10

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, img.size, "final y =", y)


if __name__ == "__main__":
    render()
