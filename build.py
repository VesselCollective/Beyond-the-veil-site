"""Build the Beyond the Veil site from content.json into dist/.

Every name, time, link and line of copy lives in content.json. Edit it, run
`python3 build.py`, and push. Netlify publishes dist/ as-is.
"""
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
C = json.loads((ROOT / "content.json").read_text())
e = html.escape
L = C["links"]
VERSION = "17"
GEM = '<span class="gem" aria-hidden="true"></span>'
BUY = "Buy tickets"


def buy(cls="btn btn-holo", label=BUY):
    return f'<a class="{cls}" href="{e(L["tickets"])}" target="_blank" rel="noopener">{label}</a>'


def ext(href, label, cls="btn btn-ghost"):
    return f'<a class="{cls}" href="{e(href)}" target="_blank" rel="noopener">{label}</a>'


def rule():
    return '<div class="rule" aria-hidden="true"><span></span></div>'


def heading(text, hid, kicker=""):
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    return f'{k}<h2 id="{hid}">{e(text)}</h2>{rule()}'


def joined(items, cls=""):
    parts = [f"<span>{e(x)}</span>" for x in items]
    return f'<p class="joined {cls}">' + f" {GEM} ".join(parts) + "</p>"


def head(title, description):
    url = C["meta"]["site_url"]
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="theme-color" content="#07080d">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Beyond the Veil">
<meta property="og:title" content="{e(C['hero']['title'])}: {e(C['hero']['subtitle'])}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{url}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{url}/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/img/touch-icon.png">
<link rel="preload" href="/img/hero.webp" as="image" type="image/webp">
<link rel="preload" href="/fonts/cinzel-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/jost-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={VERSION}">
</head>
"""


def calendar_links():
    ev = C["event"]
    start = ev["doors_utc"].replace("-", "").replace(":", "")
    end = ev["end_utc"].replace("-", "").replace(":", "")
    details = f"{C['hero']['subtitle']}. Arrival 7 to 8 PM, doors close at 8, opening ceremony 8:30. {C['meta']['site_url']}"
    g = ("https://calendar.google.com/calendar/render?action=TEMPLATE"
         f"&text={quote(C['hero']['title'])}&dates={start}/{end}"
         f"&details={quote(details)}&location={quote(ev['calendar_location'])}")
    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Beyond the Veil//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT", "UID:beyond-the-veil-2026@beyondtheveil-atx", f"DTSTAMP:{start}",
        f"DTSTART:{start}", f"DTEND:{end}", f"SUMMARY:{C['hero']['title']}",
        f"DESCRIPTION:{details.replace(',', chr(92) + ',')}", f"LOCATION:{ev['calendar_location'].replace(',', chr(92) + ',')}",
        f"URL:{C['meta']['site_url']}", "BEGIN:VALARM", "TRIGGER:-PT3H", "ACTION:DISPLAY",
        "DESCRIPTION:Beyond the Veil tonight. Doors close at 8 PM.", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", ""])
    return g, ics


NAV = [("#flow", "The Flow"), ("#music", "Music"), ("#costume", "Costume"), ("#tickets", "Tickets"),
       ("#vessel", "VESSEL"), ("#venue", "Venue"), ("#faq", "FAQ")]
GUIDE = ("/guide/", "Party Guide")


def nav(base="", solid=False):
    links = [(base + h, t) for h, t in NAV] + [GUIDE]
    inline = "".join(f'<a href="{h}"' + (' aria-current="page"' if base and h == GUIDE[0] else "") + f'>{t}</a>' for h, t in links)
    return f"""<header class="nav{' solid' if solid else ''}" id="nav">
  <a class="brand" href="{base or ''}#top" aria-label="Beyond the Veil, back to top">{GEM}<span>Beyond the Veil</span></a>
  <nav class="nav-links" aria-label="Sections">{inline}</nav>
  {buy("btn btn-holo btn-sm nav-cta")}
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="sr-only">Open menu</span><i></i><i></i></button>
</header>
<div class="menu" id="menu" hidden>
  <nav aria-label="Menu">{inline}<a href="{base}#nominate">Nominate</a></nav>
  {buy("btn btn-holo")}
</div>"""


def hero():
    h = C["hero"]
    facts = "".join(f'<div><dt>{e(f["k"])}</dt><dd>{e(f["v"])}</dd></div>' for f in h["facts"])
    rules = f" {GEM} ".join(f"<span>{e(r)}</span>" for r in h["rules"])
    return f"""<section class="hero" id="top" aria-label="Beyond the Veil">
  <div class="hero-bg" aria-hidden="true">
    <img src="/img/hero.webp" srcset="/img/hero-800.webp 800w, /img/hero.webp 1254w" sizes="(max-width: 700px) 800px, 1254px" alt="" width="1254" height="1254" fetchpriority="high">
  </div>
  <div class="hero-top">
    <p class="presenters"><span>{e(h['presenters'])}</span><span class="presents">{e(h['presents'])}</span></p>
    <h1>{e(h['title'])}</h1>
    <p class="subtitle">{e(h['subtitle'])}</p>
  </div>
  <div class="hero-window" aria-hidden="true"></div>
  <div class="hero-info">
    <p class="dates">{e(h['dates'])}</p>
    <p class="place"><strong>{e(h['venue'])}</strong> {GEM} {e(h['place'])}</p>
    <dl class="facts">{facts}</dl>
    <div class="actions">
      {buy("btn btn-holo btn-lg")}
      <a class="btn btn-ghost" href="#nominate">Nominate a guest</a>
    </div>
    <p class="rules-line">{rules}</p>
  </div>
</section>
<div class="countdown-band" aria-label="Time until the gate opens">
  <div class="countdown" role="timer">
    <div><b data-u="d">--</b><small>Days</small></div>
    <div><b data-u="h">--</b><small>Hours</small></div>
    <div><b data-u="m">--</b><small>Minutes</small></div>
    <div><b data-u="s">--</b><small>Seconds</small></div>
  </div>
  <p class="countdown-label">until the gate opens</p>
</div>"""


def faq_html(items):
    out = []
    for f in items:
        link = f' <a href="{e(f["href"])}">{e(f.get("link", "Read more"))}</a>' if f.get("href") else ""
        out.append(f'<details><summary>{e(f["q"])}</summary><p>{e(f["a"])}{link}</p></details>')
    return "\n".join(out)


def guide_page():
    g, ag, ins, vn = C["guide"], C["agreement"], C["inside"], C["venue"]
    agree = "".join(f'<li><strong>{e(i["k"])}</strong><span>{e(i["v"])}</span></li>' for i in ag["items"])
    inside = "".join(
        f'<li><h3>{e(i["k"])}</h3><p>{e(i["v"])}</p>' + (f'<p class="must">{e(i["strong"])}</p>' if i.get("strong") else "") + "</li>"
        for i in ins["items"])
    food = "".join(f'<li><strong>{e(f["k"])}</strong> {e(f["v"])}</li>' for f in ins["food"])
    vtimes = "".join(f'<div><dt>{e(x["k"])}</dt><dd>{e(x["v"])}</dd></div>' for x in vn["times"])
    parking = "".join(f"<p>{e(p)}</p>" for p in vn["parking"])
    rides = "".join(f"<p>{e(p)}</p>" for p in vn["rides"])
    return head(f"Party Guide · {C['hero']['title']}", g["intro"]) + f"""<body class="guide-page">
<a class="skip" href="#main">Skip to the guide</a>
<canvas class="veil" aria-hidden="true"></canvas>
<div class="veil-dim" aria-hidden="true"></div>
{nav("/", solid=True)}

<main id="main">
<section class="guide-intro" aria-labelledby="guide-h">
  <div class="wrap center">
    <p class="kicker">{e(g['kicker'])}</p>
    <h1 id="guide-h">{e(g['title'])}</h1>
    {rule()}
    <p class="lead">{e(g['intro'])}</p>
    <nav class="guide-toc" aria-label="In this guide"><a href="#agreement">Group Agreement</a><a href="#inside">Inside the Gates</a><a href="#arrival">Getting There</a><a href="#guide-faq">Questions</a></nav>
  </div>
</section>

<section id="agreement" class="agreement" aria-labelledby="agree-h">
  <div class="wrap">
    {heading(ag['title'], 'agree-h', 'Please read')}
    <p class="intro">{e(ag['intro'])}</p>
    <p>{e(ag['lead'])}</p>
    <ol class="agree">{agree}</ol>
    <p class="outro">{e(ag['outro'])}</p>
  </div>
</section>

<section id="inside" class="inside" aria-labelledby="inside-h">
  <div class="wrap">
    {heading(ins['title'], 'inside-h', 'House notes')}
    <ul class="inside-list">{inside}</ul>
    <h3 class="label">{e(ins['food_label'])}</h3>
    <ul class="points">{food}</ul>
  </div>
</section>

<section id="arrival" class="venue" aria-labelledby="arrival-h">
  <div class="wrap">
    {heading('Getting There', 'arrival-h', vn['name'])}
    <div class="address">
      <strong>{e(vn['name'])}</strong>
      <span>{e(vn['address'])}</span>
      {ext(L['map'], 'Open in Maps', 'btn btn-ghost btn-sm')}
    </div>
    <h3>{e(vn['start_label'])}</h3>
    <p>{e(vn['start'])}</p>
    <dl class="facts small">{vtimes}</dl>
    <h3>{e(vn['parking_label'])}</h3>
    {parking}
    <h3>{e(vn['rides_label'])}</h3>
    {rides}
    <p class="center">{ext(L['whatsapp'], 'Join the rideshare WhatsApp group', 'btn btn-holo')}</p>
  </div>
</section>

<section id="guide-faq" class="faq" aria-labelledby="gfaq-h">
  <div class="wrap">
    {heading('Questions', 'gfaq-h', 'House rules')}
    <div class="faq-list">
{faq_html(g['faq'])}
    </div>
    <p class="center ask">Anything else? Email <a href="mailto:{e(L['email'])}">{e(L['email'])}</a>.</p>
    <p class="center"><a class="btn btn-ghost" href="/">Back to the invitation</a></p>
  </div>
</section>
</main>

<footer>
  {rule()}
  <p>Questions: <a href="mailto:{e(L['email'])}">{e(L['email'])}</a></p>
  <p>{e(C['footer']['noshare'])}</p>
</footer>
<script src="/veil.js?v={VERSION}" defer></script>
<script src="/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def index_page():
    inv, mu, ag, co, t, ve, vn, ins, po = (C[k] for k in
        ("invitation", "music", "agreement", "costume", "tickets", "vessel", "venue", "inside", "plusones"))
    gcal, _ = calendar_links()

    def rich(t):
        import re
        t = e(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        return re.sub(r"_(.+?)_", r"<em>\1</em>", t)
    def para(i, p):
        if isinstance(p, dict):
            a, z = p["feature"]
            return f'<div class="feature" aria-label="{e(a)} {e(z)}"><div class="gemline" aria-hidden="true"><i></i></div><p class="feature-a">{"".join(f'<span>{e(x)}</span>' for x in a.replace(", and ", ",|and ").split("|"))}</p><p class="feature-b">{e(z)}</p><div class="gemline" aria-hidden="true"><i></i></div></div>'
        return f'<p{" class=\"cap\"" if i == 0 else ""}>{rich(p)}</p>'
    paras = "\n".join(para(i, p) for i, p in enumerate(inv["paragraphs"]))
    flow = "\n".join(
        f'<li class="{"key" if s.get("key") else ""}"><time>{e(s["time"])}</time>'
        f'<h3>{e(s["name"])}</h3><p>{e(s["text"])}</p></li>' for s in C["flow"])

    def portrait(name, photo=None, note="", role=""):
        if photo:
            pic = f'<img src="/img/artists/{e(photo)}" alt="" loading="lazy" decoding="async" width="600" height="750">'
        else:
            pic = f'<span class="mono" aria-hidden="true">{e(name[:1].upper())}</span>'
        role = f'<small class="role">{e(role)}</small>' if role else ""
        note = f'<small>{e(note)}</small>' if note else ""
        return (f'<li class="artist{"" if photo else " no-photo"}"><figure>{pic}</figure>'
                f'<span class="nm">{role}<b>{e(name)}</b>{note}</span></li>')

    stages = "\n".join(
        f'<div class="stage"><h3>{e(s["name"])}</h3>{rule()}<ul class="lineup">'
        + "".join(portrait(a["name"], a.get("photo"), a.get("note", "")) for a in s["artists"])
        + "</ul>" + (f'<p class="more">{e(s["more"])}</p>' if s.get("more") else "") + "</div>"
        for s in mu["stages"])
    cast_people = ([(mu["host_label"], mu["host"]), (mu["direction_label"], mu["direction"])]
                   + [(mu["featuring_label"], f) for f in mu["featuring"]])
    cast = "".join(portrait(p["name"], p.get("photo"), role=r) for r, p in cast_people)
    acts = "".join(
        f'<li>' + (f'<img class="act-logo" src="/img/{e(a["logo"])}" alt="{e(a["logo_alt"])}" width="{a["logo_w"]}" height="{a["logo_h"]}" loading="lazy">' if a.get("logo") else "") + f'<span class="act-name">{e(a["name"])}</span>'  + (f'<span class="act-by">{e(a["by"])}</span>' if a.get("by") else "") + "</li>"
        for a in mu["activations"])

    agree = "".join(f'<li><strong>{e(i["k"])}</strong><span>{e(i["v"])}</span></li>' for i in ag["items"])

    points = "".join(f'<li><strong>{e(p["k"])}</strong> {e(p["v"])}</li>' for p in co["points"])
    colors = "".join(f'<li><span class="sw sw-{e(c["swatch"])}"></span>{e(c["name"])}</li>' for c in co["colors"])
    words = f" {GEM} ".join(f"<span>{e(w)}</span>" for w in co["words"])
    etsy = "\n".join(
        f'<div class="etsy-group"><h4>{e(g["name"])}</h4><ul>'
        + "".join(f'<li><a href="{e(i["u"])}" target="_blank" rel="noopener">'
                  f'<span class="etsy-img"><img src="{e(i["img"].replace("il_1080xN.", "il_570xN.").replace("il_794xN.", "il_570xN."))}" data-full="{e(i["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer"></span>'
                  f'<span class="etsy-t">{e(i["t"])}</span><em>Shop on Etsy</em></a></li>' for i in g["items"])
        + "</ul></div>" for g in co["etsy_groups"])

    def shots(hidden):
        return "".join(
            f'<figure class="shot"{" aria-hidden=\"true\"" if hidden else ""}><img src="/img/{e(p["src"])}" alt="{"" if hidden else e(p["alt"])}" loading="lazy" width="{p["w"]}" height="{p["h"]}"></figure>'
            for p in C["community"]["photos"])
    gallery = shots(False) + shots(True)

    tiers = "\n".join(f'<li><span class="tier-n">{i + 1}</span>{e(x)}</li>' for i, x in enumerate(t["tiers"]))
    notes = "".join(f"<li>{e(n)}</li>" for n in t["notes"])
    stats = f" {GEM} ".join(f"<span>{e(s)}</span>" for s in ve["stats"])
    vparas = "".join(f"<p>{e(p)}</p>" for p in ve["paragraphs"])
    vtimes = "".join(f'<div><dt>{e(x["k"])}</dt><dd>{e(x["v"])}</dd></div>' for x in vn["times"])
    parking = "".join(f"<p>{e(p)}</p>" for p in vn["parking"])
    rides = "".join(f"<p>{e(p)}</p>" for p in vn["rides"])
    inside = "".join(
        f'<li><h3>{e(i["k"])}</h3><p>{e(i["v"])}</p>' + (f'<p class="must">{e(i["strong"])}</p>' if i.get("strong") else "") + "</li>"
        for i in ins["items"])
    food = "".join(f'<li><strong>{e(f["k"])}</strong> {e(f["v"])}</li>' for f in ins["food"])
    faq = faq_html(C["faq"])
    vid = L["video_id"]

    return head(C["meta"]["title"], C["meta"]["description"]) + f"""<body>
<a class="skip" href="#main">Skip to the invitation</a>
<canvas class="veil" aria-hidden="true"></canvas>
<div class="veil-dim" aria-hidden="true"></div>
{nav()}
{hero()}

<main id="main">
<section id="community" class="community" aria-labelledby="community-h">
  <div class="wrap">{heading(C['community']['title'], 'community-h', C['community']['kicker'])}<p class="lead">{e(C['community']['caption'])}</p></div>
  <div class="video">
    <button type="button" data-id="{e(vid)}" aria-label="Play the Halloween 2025 recap video">
      <img src="/img/recap-poster.webp" alt="" loading="lazy" width="1024" height="576">
      <span class="play"></span><span class="video-label">Watch the Halloween 2025 recap</span>
    </button>
  </div>
  <div class="marquee" aria-label="Photos from Halloween 2025"><div class="marquee-track">{gallery}</div></div>
  <p class="credit">{e(C['community']['credit'])}</p>
</section>

<section class="invitation" id="invitation" aria-labelledby="inv-h">
  <div class="hook">
    <p class="hook-head">{e(C['hook']['line'].split('. ', 1)[0])}.</p>
    {"".join(f'<p class="hook-line">{e(p)}</p>' for p in C['hook']['line'].split('. ', 1)[1].split(chr(10) + chr(10)))}
    <p class="hook-curated">{e(C['hook']['curated'])}</p>
    <p class="hook-sober"><strong>{e(C['hook']['alcohol_k'])}</strong> {e(C['hook']['alcohol_v'])}</p>
  </div>
  <div class="letter">
    <h2 id="inv-h" class="greeting">{e(inv['greeting'])}</h2>
    {paras}
    <p class="signoff">{e(inv['closing'])}<strong>{e(inv['signature'])}</strong></p>
  </div>
</section>

<section id="flow" aria-labelledby="flow-h">
  <div class="wrap">
    {heading('The Flow', 'flow-h', 'October 31 into November 1')}
    <ol class="flow">
{flow}
    </ol>
    <div class="cal">
      <a class="btn btn-ghost btn-sm" href="/beyond-the-veil.ics" download>Add to Apple or Outlook calendar</a>
      {ext(gcal, 'Add to Google Calendar', 'btn btn-ghost btn-sm')}
    </div>
  </div>
</section>

<section id="music" class="music" aria-labelledby="music-h">
  <div class="wrap wide">
    {heading('Music Performances', 'music-h', 'Two stages')}
    <p class="intro">{e(mu['intro'])}</p>
    <div class="stages">
{stages}
    </div>
    <p class="label cast-label">The cast</p>
    <ul class="cast lineup">{cast}</ul>
    <p class="label">{e(mu['activations_label'])}</p>
    <ul class="activations">{acts}</ul>
  </div>
</section>

<section id="costume" class="costume" aria-labelledby="costume-h">
  <div class="wrap">
    {heading(co['title'], 'costume-h', 'Your costume')}
    <p class="intro">{e(co['lead'])}</p>
    <ul class="points">{points}</ul>
  </div>
  <aside class="warning" aria-label="{e(co['warning_label'])}">
    <p class="warning-label">{e(co['warning_label'])}</p>
    <p class="warning-text">{e(co['warning'])}</p>
    <p class="warning-after">{e(co['warning_after'])}</p>
  </aside>
  <div class="wrap wide palette-words">
    <figure class="costume-board"><img src="/img/silver-veil.webp" alt="The Silver Veil moodboard: lunar, chrome and mystic tones with sheer organza, crystal and liquid metal" loading="lazy" width="480" height="600"></figure>
    <div>
      <h3 class="label">{e(co['colors_label'])}</h3>
      <ul class="colors">{colors}</ul>
    </div>
    <div>
      <h3 class="label">{e(co['words_label'])}</h3>
      <p class="words">{words}</p>
    </div>
  </div>
  <div class="wrap wide moodboard">
    <h3 class="label">{e(co['pinterest_label'])}</h3>
    <div class="pin-frame" id="pin-frame">
      <a class="pin-fallback" data-pin-do="embedBoard" data-pin-scale-height="380" data-pin-scale-width="110" href="{e(L['pinterest'])}">Open the mood board on Pinterest</a>
    </div>
    <p class="center">{ext(L['pinterest'], 'Open the full board on Pinterest', 'btn btn-ghost btn-sm')}</p>
  </div>
  <div class="wrap wide">
    <h3 class="label">{e(co['etsy_label'])}</h3>
    <div class="etsy">
{etsy}
    </div>
    <p class="center">{ext(L['etsy'], 'See every Etsy favorite', 'btn btn-ghost btn-sm')}</p>
  </div>
</section>

<section id="tickets" class="tickets" aria-labelledby="tickets-h">
  <div class="wrap">
    {heading('Tickets', 'tickets-h')}
    <div class="ticket">
      <div class="ticket-face">
        <p class="admit">Admit one</p>
        <p class="ticket-title">{e(C['hero']['title'])}</p>
        <p class="ticket-meta">{e(C['hero']['dates'])}<br>{e(C['hero']['venue'])}, {e(C['hero']['place'])}</p>
        <p class="lead">{e(t['lead'])}</p>
        <p class="center">{e(t['text'])}</p>
        <ol class="tiers">
{tiers}
        </ol>
      </div>
      <div class="ticket-stub">{buy("btn btn-holo btn-lg")}</div>
    </div>
    <ul class="ticket-notes">{notes}</ul>
  </div>
</section>

<section id="vessel" class="vessel" aria-labelledby="vessel-h">
  <div class="vessel-inner">
    <p class="label">{e(ve['label'])}</p>
    <img class="wordmark" src="/img/vessel-white.svg" alt="VESSEL" width="320" height="65" loading="lazy">
    <h2 id="vessel-h" class="spaced">{e(ve['spaced'])}</h2>
    <p class="stats">{stats}</p>
    <div class="vessel-grid">
      <img class="vessel-photo" src="/img/lovestack.webp" alt="The VESSEL LoveStack box with white and black organza pouches under an eclipse" loading="lazy" width="900" height="900">
      <div class="vessel-copy">
        {vparas}
        <p class="offer">{e(ve['offer'])}</p>
        {buy("btn btn-holo btn-lg", "Buy tickets + LoveStack")}
      </div>
    </div>
    <img class="vessel-chart" src="/img/lovestack-protocol.webp" alt="How to use LoveStack: LoveSupport doses 1 to 3 on days 1 and 2, then LoveRestore doses 4 to 6 with your first meal on days 3 to 5" loading="lazy" width="1200" height="1200">
  </div>
</section>

<section id="venue" class="venue" aria-labelledby="venue-h">
  <div class="wrap">
    {heading(vn['title'], 'venue-h', 'Getting there')}
    <p class="intro">{e(vn['text'])}</p>
  </div>
  <div class="venue-photos">{"".join(f'<figure><img src="/img/{e(p["src"])}" alt="{e(p["alt"])}" loading="lazy" width="1200" height="800"></figure>' for p in vn["photos"])}</div>
  <div class="wrap">
    <div class="address">
      <strong>{e(vn['name'])}</strong>
      <span>{e(vn['address'])}</span>
      {ext(L['map'], 'Open in Maps', 'btn btn-ghost btn-sm')}
    </div>
    <h3>{e(vn['start_label'])}</h3>
    <p>{e(vn['start'])}</p>
    <dl class="facts small">{vtimes}</dl>
    <h3>{e(vn['parking_label'])}</h3>
    {parking}
    <h3>{e(vn['rides_label'])}</h3>
    {rides}
    <p class="center">{ext(L['whatsapp'], 'Join the rideshare WhatsApp group', 'btn btn-holo')}</p>
  </div>
</section>

<section id="nominate" class="nominate" aria-labelledby="nominate-h">
  <div class="wrap center">
    {heading(po['title'], 'nominate-h')}
    <p>{e(po['text'])}</p>
    <p class="lead">{e(po['nominate'])}</p>
    {ext(L['nominate'], 'Nominate a guest')}
  </div>
</section>

<section id="faq" class="faq" aria-labelledby="faq-h">
  <div class="wrap">
    {heading('Questions', 'faq-h', 'Quick answers')}
    <div class="faq-list">
{faq}
    </div>
    <p class="center ask">Still wondering? Email <a href="mailto:{e(L['email'])}">{e(L['email'])}</a>.</p>
  </div>
</section>

<section class="closing" aria-label="Closing">
  <p class="closing-line">{e(C['closing']['line'])}</p>
  <p class="closing-call">{e(C['closing']['call'])}</p>
  {buy("btn btn-holo btn-lg")}
</section>
</main>

<footer>
  {rule()}
  <p>Questions: <a href="mailto:{e(L['email'])}">{e(L['email'])}</a></p>
  <p>{e(C['footer']['noshare'])}</p>
  <p class="fine">Michael Pullano &amp; Austin Dance Temple. <a href="/guide/">Party Guide</a></p>
</footer>

<div class="sticky" aria-hidden="true">{buy("btn btn-holo").replace('rel="noopener"', 'rel="noopener" tabindex="-1"')}</div>
<script src="/veil.js?v={VERSION}" defer></script>
<script src="/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#8e9298"/><stop offset="1" stop-color="#cfc6f2"/></linearGradient></defs><rect width="64" height="64" rx="14" fill="#07080d"/><rect x="20" y="20" width="24" height="24" transform="rotate(45 32 32)" fill="url(#g)"/></svg>"""


def touch_icon():
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (180, 180), (7, 8, 13))
    ImageDraw.Draw(im).polygon([(90, 46), (134, 90), (90, 134), (46, 90)], fill=(220, 222, 228))
    return im


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(SRC / "img", DIST / "img")
    shutil.copytree(SRC / "fonts", DIST / "fonts")
    for f in ("style.css", "main.js", "veil.js"):
        shutil.copy(SRC / f, DIST / f)
    (DIST / "index.html").write_text(index_page())
    (DIST / "guide").mkdir()
    (DIST / "guide" / "index.html").write_text(guide_page())
    _, ics = calendar_links()
    (DIST / "beyond-the-veil.ics").write_text(ics)
    (DIST / "favicon.svg").write_text(FAVICON)
    touch_icon().save(DIST / "img" / "touch-icon.png")
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (DIST / "_headers").write_text(
        "/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Content-Type-Options: nosniff\n"
        "/beyond-the-veil.ics\n  Content-Type: text/calendar; charset=utf-8\n"
        "/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n")
    print("Built", sum(1 for p in DIST.rglob("*") if p.is_file()), "files")


if __name__ == "__main__":
    main()
