#!/usr/bin/env python3
"""Build the Laguna Beach pool preview: the city's pool page, a page per nearby pool, the
printable list (computed live), and Pool Safety. Run: python3 build.py"""
import json, math, os, html

E = html.escape
V = json.load(open("views.json"))  # Pool Relay share tokens, see README
FEED = ",".join(V.values())
LBHS = (33.5421579, -117.7759374)  # Laguna Beach High School & Community Pool, from the city's map
CITY = "https://www.lagunabeachcity.net/government/departments/parks-recreation/pool"

def miles(a, b):
    R, r = 3958.8, math.pi / 180
    h = math.sin((b[0] - a[0]) * r / 2) ** 2 + math.cos(a[0] * r) * math.cos(b[0] * r) * math.sin((b[1] - a[1]) * r / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

# The city's list, in its own order, with what its pin says and what the operator actually publishes.
POOLS = [
  dict(n=1, slug="laguna-niguel", name="Laguna Niguel Aquatics Center", facility="Laguna Niguel Aquatics Center", area="Laguna Niguel",
       address="29751 Crown Valley Pkwy, Laguna Niguel, CA 92677", phone="(949) 425-5114", lat=33.5313975, lng=-117.7086446,
       operator="City of Laguna Niguel; lessons, water aerobics and adult swim by Premier Aquatics",
       url="https://www.cityoflagunaniguel.org/1827/Aquatics", view="lnac",
       water="25-yard lap pool, 13 lanes, with diving boards; a warm (87°) teaching pool",
       fees="$5 drop-in for adults 14–59, $4 for seniors and youth. 20-swim pass: $60 resident, $80 non-resident.",
       said="Weekdays: 6am-1pm & 7-8pm · Weekends: 9am-4pm · Swim lessons & water aerobics offered · $5 drop-in, $80/20 visits",
       real=["Weekends are two different swims: lap swim 9am–1pm, then rec swim 1–4pm with the diving boards open.",
             "Weekdays 4–7pm the lap pool belongs to the Dolphin Aquatics swim team; there is no public swim 1–4pm.",
             "Water aerobics (Mon/Wed 10am) and Adult Swim (Mon/Wed/Fri 11am–1pm, Sat 9–11am) aren't on the city's pool grid at all.",
             "$80 for 20 visits is the non-resident price, which is what a Laguna Beach swimmer pays; Laguna Niguel residents pay $60. Premier's site lists only $80.",
             "Closed Nov 26, Dec 12, Dec 24–25 and Dec 28–Jan 8 (maintenance). The city's holiday list gives no year."]),
  dict(n=2, slug="aliso-viejo", name="Aliso Viejo Aquatic Center", facility="Aliso Viejo Aquatic Center", area="Aliso Viejo",
       address="29 Santa Barbara Dr, Aliso Viejo, CA 92656", phone="(949) 425-2559", lat=33.600445, lng=-117.72586,
       operator="Premier Aquatics (Premier Swim Academy / SwimOC), under contract with the City of Aliso Viejo",
       url="https://premierswimacademy.com/aliso-viejo/", view="avac",
       water="25-meter lap pool (lane count not published), wading pool and splash pad; the rec pool is summer-only",
       fees="Day pass $6 resident / $8 non-resident adults. Annual $187 / $246.",
       said="Mon/Wed: 10am-3:30pm · Tue/Thu: 6:30am-3:30pm · Fri-Sun: 10am-5pm · Swim lessons, swim team & water aerobics offered · $8 drop-in, $246/year",
       real=["The 3:30pm times are when lap swim stops, not when the pool closes: it's open to 6pm Mon–Thu, with the lanes going to the Flying Fish swim team from 4pm.",
             "Most weekends it closes early for weddings, at 2–3:30pm instead of 5pm. Those times are only on a Google Calendar.",
             "Three sources give three lap-swim cutoffs: 3:30pm, 3:55pm, and swim team from 4pm.",
             "$8 and $246 are the non-resident prices (what a Laguna Beach swimmer pays); Aliso Viejo residents pay $6 and $187.",
             "The operator's page still shows last year's Thanksgiving dates and says the rec pool is \"closed until Spring 2026\"."]),
  dict(n=3, slug="montanoso", name="Montanoso Recreation Center", facility="Montanoso Recreation and Fitness Center", area="Mission Viejo",
       address="25800 Montanoso Dr, Mission Viejo, CA 92691", phone="(949) 859-4348", lat=33.587505, lng=-117.663139,
       operator="City of Mission Viejo", url="https://www.missionviejo.gov/aquatics", view="montanoso",
       water="25-yard pool, 6 lanes",
       fees="Day use $10 adults, $5 youth. Membership $30/month resident, $40 non-resident, plus a $50 initiation fee.",
       said="Weekdays: 5:30am-7:45pm · Saturdays: 7am-6:45pm · Sundays: 7am-4:45pm · Water aerobics offered · $10 drop-in, $40/month",
       real=["From noon to close, family rec swim shares the pool with lap swim. No page says how many lanes stay roped for laps.",
             "There is no water aerobics at Montanoso this fall. The city's only aqua classes moved from Sierra to the Marguerite complex.",
             "$40/month is the non-resident membership (Laguna Beach swimmers pay it), plus a $50 initiation fee the list leaves out.",
             "Holiday hours are published for the building, not the pool; the pool closes 15 minutes earlier."]),
  dict(n=4, slug="sierra", name="Sierra Recreation Center", facility="Sierra Recreation and Fitness Center", area="Mission Viejo",
       address="26887 Recodo Ln, Mission Viejo, CA 92691", phone="(949) 859-4348", lat=33.571677, lng=-117.659306,
       operator="City of Mission Viejo", url="https://www.missionviejo.gov/aquatics", view="sierra",
       water="25-yard pool, 8 lanes, diving board",
       fees="Same as Montanoso: day use $10 adults, $5 youth.",
       said="Weekdays: 5:30am-7:45pm · Saturdays: 7am-6:45pm · Sundays: 7am-4:45pm · Water aerobics offered · $10 drop-in, $40/month",
       real=["The pool has been closed since Sep 8 for replastering. The city gives only a tentative reopening \"by Thanksgiving weekend\".",
             "Mission Viejo's own pages disagree on the closure: Sep 8 on the Aquatics page, Sep 1–Nov 30 on the rentals page.",
             "The city's lap and rec swim table still lists Sierra's hours beside Montanoso's, with no dates."]),
  dict(n=5, slug="marian-bergeson", name="Marian Bergeson Aquatic Complex", facility="Marian Bergeson Aquatic Center", area="Newport Beach",
       address="2101 Eastbluff Dr, Newport Beach, CA 92660", phone="(949) 270-8100", lat=33.6343046, lng=-117.8772041,
       operator="City of Newport Beach, at Corona del Mar High School", url="https://www.newportbeachca.gov/government/departments/recreation-senior-services/aquatics", view="bergeson",
       water="One outdoor pool, 50 m × 8 lanes or 25 yd × 18 lanes (a directory's figures; the city publishes none)",
       fees="5 visits $16, 20 visits $55, annual $176 for adults (non-residents add $11 or $33).",
       said="Weekdays: 6-9pm · Weekends: 7am-12pm · Swim lessons offered · $16/5 visits, $209/year",
       real=["Weekends run 7am–2pm, not to noon.",
             "$209 is the non-resident annual price, which a Laguna Beach swimmer pays; Newport Beach residents pay $176.",
             "Swim lessons are summer-only; the city says Summer 2027 registration opens in March.",
             "The schedule is a PDF per month, and only September and October are posted. October's Saturdays say \"Limited Lanes\" without saying how many."]),
  dict(n=6, slug="woollett", name="Woollett Aquatics Center", facility="William Woollett Jr. Aquatics Center", area="Irvine",
       address="4601 Walnut Ave, Irvine, CA 92604", phone="(949) 724-6717", lat=33.701776, lng=-117.780588,
       operator="City of Irvine", url="https://www.cityofirvine.org/community-services/aquatics", view="woollett",
       water="Two 50-meter pools and a 10-lane teaching pool",
       fees="See the City of Irvine.",
       said="Weekdays: 6am-2pm & 6-8pm · Weekends 8-10am · Swim lessons & water aerobics offered · $5 drop-in, $525/year",
       real=["This schedule is the City of Irvine's own fall lane-by-lane allocation, already in Pool Relay, so lap swim shows exactly which lanes are public."]),
  dict(n=7, slug="san-clemente", name="San Clemente Aquatics Center", facility="San Clemente Aquatics Center", area="San Clemente",
       address="987 Avenida Vista Hermosa, San Clemente, CA 92673", phone="(949) 429-8797", lat=33.4598593, lng=-117.6056412,
       operator="City of San Clemente", url="https://www.sanclemente.gov/195/Aquatics", view="scac",
       water="50-meter competition pool (17 short-course lanes) and a 25-yard, 6-lane activity pool with slides",
       fees="$8 resident / $13 non-resident adults. Monthly $83 / $132; annual $400 / $732.",
       said="Mon/Wed/Fri: 5:30am-3pm & 4:30-8pm · Tue/Thu: 5:30am-12pm & 4:30-8pm · Saturday: 9am-4pm · Swim lessons & water aerobics offered · $13 drop-in, $132/month, $732/year",
       real=["Mon/Wed/Fri lap swim runs 5:30am–8pm with no midday break; the break is only Tue/Thu, noon to 4:30pm, for staffing.",
             "San Clemente's own three listings disagree on Friday (8pm or 6pm) and Sunday (closed, or noon–4pm).",
             "On weekday evenings the swim team and water polo club take most lanes; the allocation sheet leaves lanes 1–2 and 11–12 public.",
             "The lane sheet is labeled \"SUMMER 2026\" but is the Aug 17–31 fall sheet, and nothing newer is posted.",
             "Thanksgiving: the same page says closed Nov 26–27 in one place and Nov 27–28 in another."]),
  dict(n=8, slug="ole-hanson", name="Ole Hanson Beach Club", facility="Ole Hanson Beach Club", area="San Clemente",
       address="105 W Avenida Pico, San Clemente, CA 92672", phone="(949) 388-2131", lat=33.431577, lng=-117.6314574,
       operator="City of San Clemente", url="https://www.sanclemente.gov/195/Aquatics", view="ohbc",
       water="25-yard, 6-lane pool and a teaching pool, above the beach",
       fees="Same passes as the Aquatics Center: $8 resident / $13 non-resident adults.",
       said="Mon-Thu: 4:30-6:30pm · Tue/Thu: 8am-12pm · Sunday: 12-4pm · Swim lessons offered · $13 drop-in, $132/month, $732/year",
       real=["There is no Mon–Thu 4:30–6:30pm lap swim on any San Clemente page. Lap swim is Tue/Thu 8am–noon.",
             "Sundays noon–4pm are junior lap swim (ages 8–14) and rec swim in the teaching pool, not adult laps.",
             "Closed for winter maintenance from Nov 22 to Dec 6; the city's own page gives the start as both Nov 21 and Nov 22."]),
]
for p in POOLS:
    p["mi"] = miles(LBHS, (p["lat"], p["lng"]))
    p["href"] = f"pools/{p['slug']}.html"

def js_pools(prefix=""):
    return json.dumps([dict(slug=p["slug"], name=p["name"], area=p["area"], kind="yearRound", address=p["address"], phone=p["phone"],
                            lat=p["lat"], lng=p["lng"], photo=None, facility=p["facility"], href=prefix + p["href"]) for p in POOLS], indent=0)

MENU = [("top", "Recreation", "#"), ("", "Parks and Recreation", "#"), ("", "Activity Guide", "#"), ("", "Recreation Classes", "#"),
        ("pool", "Pool", "index.html"), ("sub find", "Where to swim now", "index.html#find"), ("sub week", "Nearby pools this week", "nearby-pools.html"),
        ("sub safety", "Pool Safety", "pool-safety.html"), ("", "Special Events & Programs", "#"), ("", "Centennial Celebration", "#"),
        ("", "Parks, Permits, and Facility Rentals", "#"), ("", "Senior Services", "#")]

def page(path, title, here, crumbs, body, aside, scripts="", wide=""):
    up = "../" if "/" in path else ""
    cls = lambda c: ("top" if "top" in c.split() else "sub" if "sub" in c.split() else "") + (" here" if here and here in c.split() else "")
    menu = "".join(f'<a class="{cls(c)}" href="{up + h if not h.startswith("#") else h}">{E(t)}</a>' for c, t, h in MENU)
    doc = f"""<!doctype html>
<!-- UNOFFICIAL PREVIEW. Not a City of Laguna Beach website. A mock-up of {CITY}
     with the nearby pools on one live Pool Relay schedule. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{E(title)} | Laguna Beach preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=PT+Sans:wght@400;700&family=PT+Sans+Narrow:wght@700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}style.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
</head>
<body>
<div class="preview-note"><b>Unofficial preview.</b> Not a City of Laguna Beach page &mdash; a mock-up of
  <a href="{CITY}" target="_blank" rel="noopener noreferrer">the city's pool page</a> with the nearby pools on one live schedule.</div>
<div class="util"><div class="in"><span>Report Urgent Safety Issues</span><span>Transparency Portal</span><span>Staff Directory</span><span class="btn">SERVICES</span></div></div>
<header class="site"><div class="hdr">
  <a class="brand" href="{up}index.html"><img src="https://www.lagunabeachcity.net/Project/Contents/Main/_gfx/cmn/logo2023.png" alt="City of Laguna Beach" onerror="this.parentNode.classList.add('noimg')"><span class="wm"><small>CITY OF</small><b>LAGUNA BEACH</b></span></a>
  <nav class="nav" aria-label="Main"><span>LIVE HERE</span><span>DO BUSINESS HERE</span><span>VISIT HERE</span><span>OUR BEACHES</span><span>OUR INITIATIVES</span><span class="on">GOVERNMENT</span></nav>
</div></header>
<div class="wrap"><div class="cols">
  <nav class="menu" aria-label="Recreation">{menu}</nav>
  <main class="sheet">
    <div class="main">
      <div class="crumbs">{crumbs}</div>
      <h1>{E(title)}</h1>
{body}
    </div>
    <aside class="aside">{aside}</aside>
    <div class="wide">{wide}</div>
  </main>
</div></div>
<footer class="site"><div class="in">
  <div><h4>CONTACT US</h4><p>City of Laguna Beach<br>505 Forest Avenue<br>Laguna Beach, CA 92651<br>Phone 949-497-3311</p></div>
  <div><h4>CITY HALL HOURS</h4><p>Monday – Thursday<br>7:30 a.m. to 5:30 p.m.<br>Alternate Fridays<br>7:30 a.m. to 4:30 p.m.</p></div>
  <div><h4>ABOUT THIS PREVIEW</h4><p>Built to demonstrate embedded <a href="https://www.poolrelay.com" target="_blank" rel="noopener">Pool Relay</a> schedules.
    Not operated by or affiliated with the City of Laguna Beach or any pool listed. Schedules read from each operator's own site on October 22, 2026.</p></div>
</div></footer>
<script>window.POOLS = {js_pools(up)};</script>
{scripts}
</body>
</html>
"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    open(path, "w").write(doc)

LEAFLET = '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>'
CONTACT = """<h3>Contact Us</h3><div class="b"><p><b>Laguna Beach HS &amp; Community Pool</b><br>(949) 497-0780</p>
<p>communitypool@lagunabeachcity.net</p><p class="muted">The pool is closed for reconstruction. The pools below are run by their own cities; call them for their hours.</p></div>"""

# ── The pool page ────────────────────────────────────────────────────────────
cards = "".join(f"""<li class="card"><h3><span class="n">{p['n']}</span><a href="{p['href']}">{E(p['name'])}</a></h3>
  <p>{E(p['area'])} · <b>{p['mi']:.1f} mi</b> from the LBHS pool</p>
  <p>{E(p['water'])}</p>
  <p class="said"><b>The city's list says:</b> {E(p['said'])}{'' if p['slug'] == 'woollett' else f"<br><b>Not quite:</b> {E(p['real'][0])}"}</p></li>""" for p in POOLS)
index_body = f"""
      <div class="alert"><b>The pool is closed for reconstruction.</b> Work began in June 2026 and is planned to finish in
        about May 2027. Until then, these eight pools in neighboring cities are open for lap swim, lessons and water fitness.</div>
      <p class="lede">Where can I swim today? This board answers from each pool's own schedule: who's open right now, for what,
        on how many lanes, until when, and how far from the Laguna Beach pool.</p>
      <div id="find"></div>
      <div id="finder" class="finder" data-view="{FEED}" data-center="[33.56,-117.73]" data-zoom="10"
        data-origin="[{LBHS[0]},{LBHS[1]}]" data-origin-label="from the LBHS pool" data-origin-name="Laguna Beach High School &amp; Community Pool (closed)"></div>
      <p class="muted" style="font-size:14px">Live from each operator's posted schedule. Lane assignments are our estimate where a pool doesn't publish them.
        Hours change: check a pool's page before you drive. <a href="nearby-pools.html">This week, pool by pool</a> (printable).</p>

      <h2>The nearby pools</h2>
      <ul class="cards">{cards}</ul>

      <h2>Pool Modernization Project</h2>
      <p>The Laguna Beach Unified School District's aging pool, which also serves as the city's only pool, reached the end of its
        30-year lifespan. The new aquatic facility will have 16 swim lanes, new restrooms and changing areas for the community and the
        school district, shaded seating, and rooftop solar water heating. The district has a <a href="https://www.lbusd.org/departments/facilities/capital-improvement-projects" target="_blank" rel="noopener">project page with a live construction camera</a>.</p>
      <div class="facts">
        <div><dt>Construction began</dt><dd>June 8, 2026</dd></div>
        <div><dt>Planned to finish</dt><dd>About May 2027</dd></div>
        <div><dt>New pool</dt><dd>16 lanes</dd></div>
      </div>

      <div class="replaces">
        <h2>What this replaces</h2>
        <ul>
          <li><b>A map of pins copied once.</b> The city's map and printable PDF copy each pool's hours from one moment. By October,
            several were already wrong. Sierra has been closed since September 8. Newport Beach's weekends run to 2pm, not noon. Ole Hanson
            has no Mon–Thu evening lap swim. Montanoso offers no water aerobics this fall. Aliso Viejo's "3:30pm" is when lap swim stops,
            not when the pool closes.</li>
          <li><b>Eight sites, six operators, eight formats.</b> Getting the real hours means a monthly PDF (Newport Beach), Canva images
            (Aliso Viejo, Laguna Niguel), a Google Calendar of wedding closures (Aliso Viejo), lane sheets saved as pictures and labeled
            "Summer" (San Clemente), a swim-team handbook (Laguna Niguel) and FlippingBook brochures.</li>
          <li><b>Prices without saying whose.</b> Four pins quote a non-resident price with no label. That is the right price for a
            Laguna Beach swimmer, who is a non-resident at every one of these pools. But nothing says so, and each operator's own page
            leads with its resident price. Montanoso's $40/month also leaves out a $50 initiation fee.</li>
          <li><b>"Scheduled to begin on June 8, and is planned to last 12 months."</b> The city's page gives no year and still reads as
            future tense. The school district says construction began in June 2026 and ends in May 2027. Its own timeline also still
            says the pool would be under construction "from March to August 2026".</li>
          <li><b>One schedule instead.</b> When each pool's schedule is entered once, this page, the printable list and every pool's
            calendar update together. A pool that closes says so here the same day.</li>
        </ul>
      </div>"""
head, tail = index_body.split('      <div id="find"></div>', 1)
page("index.html", "Laguna Beach High School & Community Pool", "find",
     'Government &rsaquo; Departments &rsaquo; Recreation &rsaquo; Pool', head, CONTACT, LEAFLET + '\n<script src="finder.js"></script>', wide='<div id="find"></div>' + tail)

# ── Each nearby pool ─────────────────────────────────────────────────────────
for p in POOLS:
    real = "".join(f"<li>{E(x)}</li>" for x in p["real"])
    body = f"""
      <a class="back" href="../index.html#find">&larr; Where to swim while the Laguna Beach pool is closed</a>
      <p class="lede">{E(p['area'])} · {E(p['address'])} · <b>{p['mi']:.1f} miles</b> from the Laguna Beach pool</p>
      <div class="today"><div id="today" data-view="{FEED}" data-pool="{p['slug']}"><p class="muted">Loading today's schedule…</p></div></div>
      <div class="facts">
        <div><dt>Run by</dt><dd style="font-size:15px">{E(p['operator'])}</dd></div>
        <div><dt>Phone</dt><dd>{E(p['phone'])}</dd></div>
        <div><dt>The water</dt><dd style="font-size:15px">{E(p['water'])}</dd></div>
        <div><dt>Fees</dt><dd style="font-size:15px">{E(p['fees'])}</dd></div>
      </div>
      <!--WIDE-->
      <h2>Lane by lane</h2>
      <div class="frame"><iframe src="https://www.poolrelay.com/embed/{V[p['view']]}" height="760" title="{E(p['name'])}, by lane" loading="lazy"></iframe></div>
      <div class="finding"><b>The city's list says:</b> {E(p['said'])}
        <ul>{real}</ul>
        <p style="margin:6px 0 0">Source: <a href="{E(p['url'])}" target="_blank" rel="noopener">{E(p['url'].split('//')[1].split('/')[0])}</a>, read October 22, 2026.</p></div>"""
    head, tail = body.split("<!--WIDE-->")
    page(f"pools/{p['slug']}.html", p["name"], None,
         '<a href="../index.html">Pool</a> &rsaquo; Nearby pools', head, CONTACT, '<script src="../finder.js"></script>', wide=tail)

# ── The printable list, computed ─────────────────────────────────────────────
page("nearby-pools.html", "Nearby Pools: This Week", "week", '<a href="index.html">Pool</a> &rsaquo; Nearby pools',
     f"""
      <p class="lede">The city's printable list, rebuilt from each pool's live schedule for the next seven days. Print it from your browser.</p>
      """, CONTACT, '<script src="finder.js"></script>', wide=f"""<div id="week" data-view="{FEED}"><p class="muted">Loading every pool's week…</p></div>""")

# ── Pool Safety ──────────────────────────────────────────────────────────────
SAFETY = f"""
      <p>Whether you swim at a public pool or in your own backyard pool, staying safe in a pool takes common sense: learn to swim;
        supervise children in a pool closely; never swim alone; and know what to do in an emergency.</p>
      <p>Our staff are well trained in emergency response, and attend frequent trainings to refresh their skills.</p>
      <h2>Sign your child up for swim lessons</h2>
      <p>Laguna Beach's summer Learn-to-Swim program returns with the new pool. Until then, these nearby pools teach lessons this
        fall. Here is who has a class today and this week:</p>
      <!--WIDE--><div id="finder" class="finder" data-view="{FEED}" data-kind="learn" data-day="today" data-center="[33.56,-117.73]" data-zoom="10"
        data-origin="[{LBHS[0]},{LBHS[1]}]" data-origin-label="from the LBHS pool" data-origin-name="Laguna Beach High School &amp; Community Pool (closed)"></div>
      <h2>Home pool safety</h2>
      <p>Follow the International Swimming Hall of Fame's water safety tips, or read about home swimming pool safety. Swimmers of
        all ages can learn from the Red Cross's safety tips, and mark International Water Safety Day, May 15, on the calendar.</p>"""
head, tail = SAFETY.split("<!--WIDE-->")
page("pool-safety.html", "Pool Safety", "safety", '<a href="index.html">Pool</a> &rsaquo; Pool Safety', head, CONTACT,
     LEAFLET + '\n<script src="finder.js"></script>', wide=tail)
print("built", 3 + len(POOLS), "pages")
