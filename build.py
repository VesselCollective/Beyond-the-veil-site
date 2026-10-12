"""Build the Beyond the Veil site from content.json into dist/.

Every name, time, link and line of copy lives in content.json. Edit it, run
`python3 build.py`, and push. Netlify publishes dist/ as-is.
"""
import html
import json
import os
import shutil
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
C = json.loads((ROOT / "content.json").read_text())
# Ticket-holder details (address, map link, WhatsApp) live in private.json, which is
# git-ignored. They are only ever written into the site encrypted, inside /guide/.
_PRIV = ROOT / "private.json"
if not _PRIV.exists():
    raise SystemExit("private.json is missing. It holds the address and WhatsApp link and is kept out of git.")
P = json.loads(_PRIV.read_text())
e = html.escape
L = C["links"]
VERSION = "10"
DIAMOND = '<span class="gem" aria-hidden="true"></span>'


def ext(href, label, cls="btn btn-ghost"):
    return f'<a class="{cls}" href="{e(href)}" target="_blank" rel="noopener">{label}</a>'


def rule():
    return '<div class="rule" aria-hidden="true"><span></span></div>'


def joined(items, cls=""):
    """Names joined with the flyer's diamond, each name kept on one line."""
    parts = [f"<span>{e(x)}</span>" for x in items]
    return f'<p class="joined {cls}">' + f" {DIAMOND} ".join(parts) + "</p>"


def head(title, description, extra=""):
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
<link rel="preload" href="/fonts/cinzel-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/cormorant-garamond-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={VERSION}">
{extra}
</head>
"""


def calendar_links():
    ev = C["event"]
    start = ev["doors_utc"].replace("-", "").replace(":", "")
    end = ev["end_utc"].replace("-", "").replace(":", "")
    details = f"{C['hero']['subtitle']}. Doors 7 PM, opening ceremony 8:30 PM. {C['meta']['site_url']}"
    g = ("https://calendar.google.com/calendar/render?action=TEMPLATE"
         f"&text={quote(C['hero']['title'])}&dates={start}/{end}"
         f"&details={quote(details)}&location={quote(ev['calendar_location'])}")
    ics = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Beyond the Veil//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT", "UID:beyond-the-veil-2026@beyondtheveil-atx", f"DTSTAMP:{start}",
        f"DTSTART:{start}", f"DTEND:{end}", f"SUMMARY:{C['hero']['title']}",
        f"DESCRIPTION:{details}", f"LOCATION:{ev['calendar_location'].replace(',', chr(92) + ',')}",
        f"URL:{C['meta']['site_url']}", "BEGIN:VALARM", "TRIGGER:-PT3H", "ACTION:DISPLAY",
        "DESCRIPTION:Beyond the Veil tonight. Doors close at 8 PM.", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", ""])
    return g, ics


def nav():
    links = [("#flow", "The Flow"), ("#lineup", "Lineup"), ("#costume", "Costume"), ("#tickets", "Tickets"), ("#faq", "FAQ")]
    inline = "".join(f'<a href="{h}">{t}</a>' for h, t in links)
    return f"""<header class="nav" id="nav">
  <a class="brand" href="#top" aria-label="Beyond the Veil, back to top">{DIAMOND}<span>Beyond the Veil</span></a>
  <nav class="nav-links" aria-label="Sections">{inline}</nav>
  <a class="btn btn-holo btn-sm nav-cta" href="{e(L['tickets'])}" target="_blank" rel="noopener">Tickets</a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="sr-only">Open menu</span><i></i><i></i></button>
</header>
<div class="menu" id="menu" hidden>
  <nav aria-label="Menu">{inline}<a href="#nominate">Nominate</a></nav>
</div>"""


def index_page():
    h, inv, lu, co, t, pa = C["hero"], C["invitation"], C["lineup"], C["costume"], C["tickets"], C["partner"]
    gcal, _ = calendar_links()

    flow = "\n".join(
        f'<li class="{"key" if s.get("key") else ""}"><time>{e(s["time"])}</time>'
        f'<h3>{e(s["name"])}</h3><p>{e(s["text"])}</p></li>' for s in C["flow"])

    def artist(a):
        note = f'<small>{e(a["note"])}</small>' if a.get("note") else ""
        if a.get("photo"):
            return (f'<li class="artist has-photo"><img src="/img/artists/{e(a["photo"])}" alt="{e(a["name"])}" loading="lazy">'
                    f'<span>{e(a["name"])}{note}</span></li>')
        return f'<li class="artist"><span>{e(a["name"])}{note}</span></li>'

    stages = "\n".join(
        f'<div class="stage"><h3>{e(s["name"])}</h3>{rule()}<ul>' + "".join(artist(a) for a in s["artists"]) + "</ul></div>"
        for s in lu["stages"])

    photos = C["community"]["photos"]
    gallery = "\n".join(
        f'<figure class="shot shot-{i}"><img src="/img/{e(p["src"])}" alt="{e(p["alt"])}" loading="lazy" width="{p["w"]}" height="{p["h"]}"></figure>'
        for i, p in enumerate(photos))

    palette = "\n".join(
        f'<li><span class="chip{" metal" if p.get("metal") else ""}" style="--c:{p["hex"]}"></span>{e(p["name"])}</li>'
        for p in co["palette"])
    materials = "".join(f"<li>{e(m)}</li>" for m in co["materials"])
    tiers = "\n".join(f'<li><span class="tier-n">{i + 1}</span>{e(x)}</li>' for i, x in enumerate(t["tiers"]))
    notes = "".join(f"<li>{e(n)}</li>" for n in t["notes"])
    rules = "\n".join(f'<li><strong>{e(r["name"])}</strong><span>{e(r["text"])}</span></li>' for r in C["rules"])
    faq = "\n".join(
        f'<details><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in C["faq"])
    paras = "\n".join(f"<p>{e(p)}</p>" for p in inv["paragraphs"])
    times = f" {DIAMOND} ".join(f"<span>{e(x)}</span>" for x in h["times"])
    vid = L["video_id"]

    return head(C["meta"]["title"], C["meta"]["description"]) + f"""<body>
<a class="skip" href="#main">Skip to the invitation</a>
{nav()}

<canvas class="veil" aria-hidden="true"></canvas>
<div class="veil-dim" aria-hidden="true"></div>
<section class="hero" id="top" aria-label="Beyond the Veil">
  <div class="hero-inner">
    <img class="hand" src="/img/hand.webp" alt="" width="810" height="277" fetchpriority="high">
    <p class="presenters">{e(h['presenters'])}</p>
    <h1>{e(h['title'])}</h1>
    <p class="subtitle">{e(h['subtitle'])}</p>
    {rule()}
    <p class="dates">{e(h['dates'])}</p>
    <p class="place">{e(h['location'])} {DIAMOND} {e(h['venue'])}</p>
    <p class="times">{times}</p>
    <p class="tagline">{e(h['tagline'])}</p>
    <div class="actions">
      <a class="btn btn-holo" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a>
      <a class="btn btn-ghost" href="#nominate">Nominate a guest</a>
    </div>
    <div class="countdown" role="timer" aria-label="Time until doors open">
      <div><b data-u="d">--</b><small>Days</small></div>
      <div><b data-u="h">--</b><small>Hours</small></div>
      <div><b data-u="m">--</b><small>Minutes</small></div>
      <div><b data-u="s">--</b><small>Seconds</small></div>
    </div>
    <p class="countdown-label">until the gate opens</p>
  </div>
</section>

<main id="main">
<section class="invitation" id="invitation" aria-labelledby="inv-h">
  <div class="letter">
    <h2 id="inv-h" class="sr-only">The invitation</h2>
    <p class="greeting">{e(inv['greeting'])}</p>
    {paras}
    <p class="signoff">{e(inv['closing'])}<strong>{e(inv['signature'])}</strong></p>
  </div>
</section>

<section class="statement" aria-label="What this night is">
  <blockquote>{e(C['statement'])}</blockquote>
</section>

<section id="flow" aria-labelledby="flow-h">
  <div class="wrap">
    <h2 id="flow-h">The Flow</h2>
    {rule()}
    <ol class="flow">
{flow}
    </ol>
    <div class="cal">
      <a class="btn btn-ghost btn-sm" href="/beyond-the-veil.ics" download>Add to Apple or Outlook calendar</a>
      <a class="btn btn-ghost btn-sm" href="{e(gcal)}" target="_blank" rel="noopener">Add to Google Calendar</a>
    </div>
  </div>
</section>

<section id="lineup" class="lineup" aria-labelledby="lineup-h">
  <div class="wrap wide">
    <h2 id="lineup-h">The Lineup</h2>
    {rule()}
    <p class="label">{e(lu['direction_label'])}</p>
    <p class="headliner">{e(lu['direction'])}</p>
    <p class="label">Music performances</p>
    <div class="stages">
{stages}
    </div>
    <p class="label">{e(lu['featuring_label'])}</p>
    {joined(lu['featuring'], 'featuring')}
    <p class="label">{e(lu['activations_label'])}</p>
    {joined(lu['activations'], 'small')}
  </div>
</section>

<section id="community" class="community" aria-labelledby="community-h">
  <div class="wrap"><h2 id="community-h">The Community</h2>{rule()}<p class="lead">{e(C['community']['caption'])}</p></div>
  <div class="gallery">
{gallery}
  </div>
  <div class="video">
    <button type="button" data-id="{e(vid)}" aria-label="Play the Halloween 2025 recap video">
      <img src="/img/recap-poster.webp" alt="" loading="lazy" width="1024" height="576">
      <span class="play"></span><span class="video-label">Watch the 2025 recap</span>
    </button>
  </div>
  <p class="credit">{e(C['community']['credit'])}</p>
</section>

<section id="costume" class="costume" aria-labelledby="costume-h">
  <div class="wrap">
    <h2 id="costume-h">The Costume</h2>
    {rule()}
    <p class="lead">{e(co['lead'])}</p>
    <p>{e(co['text'])}</p>
  </div>
  <div class="costume-grid">
    <figure class="board"><img src="/img/silver-veil.webp" alt="The Silver Veil moodboard: lunar, chrome and mystic tones with sheer organza, crystal and liquid metal" loading="lazy" width="480" height="600"></figure>
    <div class="costume-side">
      <h3>The palette</h3>
      <ul class="palette" aria-label="The Silver Veil palette">
{palette}
      </ul>
      <h3>Materials that belong here</h3>
      <ul class="materials">{materials}</ul>
      <div class="inspo">
        <a href="{e(L['pinterest'])}" target="_blank" rel="noopener"><strong>The moodboard</strong><span>{e(co['pinterest_text'])}</span><em>Open on Pinterest</em></a>
        <a href="{e(L['etsy'])}" target="_blank" rel="noopener"><strong>Costume picks</strong><span>{e(co['etsy_text'])}</span><em>Shop on Etsy</em></a>
      </div>
    </div>
  </div>
  <div class="wrap"><p class="aside">{e(co['layers'])}</p></div>
</section>

<section id="tickets" class="tickets" aria-labelledby="tickets-h">
  <div class="wrap">
    <h2 id="tickets-h">Tickets</h2>
    {rule()}
    <div class="ticket">
      <div class="ticket-face">
        <p class="admit">Admit one</p>
        <p class="ticket-title">{e(C['hero']['title'])}</p>
        <p class="ticket-meta">{e(C['hero']['dates'])}<br>{e(C['hero']['location'])}</p>
        <p class="lead">{e(t['lead'])}</p>
        <p class="center">{e(t['text'])}</p>
        <ol class="tiers">
{tiers}
        </ol>
      </div>
      <div class="ticket-stub">
        <a class="btn btn-holo btn-lg" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a>
      </div>
    </div>
    <ul class="ticket-notes">{notes}</ul>
    <p class="after">{e(t['after'])}</p>
    <div class="addon"><h3>{e(t['parking']['name'])}</h3><p>{e(t['parking']['text'])}</p></div>
  </div>
</section>

<section class="partner" aria-labelledby="partner-h">
  <div class="partner-grid">
    <img class="partner-photo" src="/img/lovestack.webp" alt="The VESSEL LoveStack box with white and black organza pouches under an eclipse" loading="lazy" width="900" height="900">
    <div class="partner-copy">
      <p class="label">{e(pa['label'])}</p>
      <img class="wordmark" src="/img/vessel-white.svg" alt="VESSEL" width="300" height="61" loading="lazy">
      <h2 id="partner-h">{e(pa['product'])}</h2>
      <p>{e(pa['text'])}</p>
    </div>
  </div>
</section>

<section id="faq" class="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <h2 id="faq-h">Before You Cross</h2>
    {rule()}
    <ul class="rules">
{rules}
    </ul>
    <div class="faq-list">
{faq}
    </div>
    <p class="center ask">Still wondering? Email <a href="mailto:{e(L['email'])}">{e(L['email'])}</a>. Please don't text the producers directly.</p>
  </div>
</section>

<section id="nominate" class="nominate" aria-labelledby="nominate-h">
  <div class="wrap center">
    <h2 id="nominate-h">Nominate a Guest</h2>
    {rule()}
    <p class="lead">{e(C['nominate']['lead'])}</p>
    <p>{e(C['nominate']['text'])}</p>
    {ext(L['nominate'], 'Nominate a guest')}
  </div>
</section>

<section class="closing" aria-label="Closing">
  <p class="closing-line">{e(C['closing']['line'])}</p>
  <p class="closing-call">{e(C['closing']['call'])}</p>
  <a class="btn btn-holo btn-lg" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a>
</section>
</main>

<footer>
  {rule()}
  <p>Questions: <a href="mailto:{e(L['email'])}">{e(L['email'])}</a></p>
  <p>{e(C['footer']['noshare'])}</p>
  <p><a href="/guide/">{e(C['footer']['guide_link'])}</a></p>
  <p class="fine">Michael Pullano and Austin Dance Temple. {e(C['community']['credit'])}</p>
</footer>

<div class="sticky" aria-hidden="true"><a class="btn btn-holo" href="{e(L['tickets'])}" target="_blank" rel="noopener" tabindex="-1">Secure your place</a></div>
<script src="/veil.js?v={VERSION}" defer></script>
<script src="/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def guide_page():
    g = C["guide"]
    secs = "\n".join(
        f'<h3>{e(s["name"])}</h3><ul>' + "".join(f"<li>{e(i)}</li>" for i in s["items"]) + "</ul>"
        for s in g["sections"])
    inner = f"""<h2>The Guide</h2>
    {rule()}
    <p class="lead">{e(g['intro'])}</p>
    <div class="address">
      <strong>{e(P['address_name'])}</strong>
      {e(P['address'])}<br>
      <a href="{e(P['map'])}" target="_blank" rel="noopener">Open in Maps</a>
    </div>
    <div class="actions" style="margin-bottom:2.5rem">
      <a class="btn btn-holo" href="{e(P['whatsapp'])}" target="_blank" rel="noopener">Join the rideshare group</a>
    </div>
    {secs}
    <h3>Questions</h3>
    <p>Email <a href="mailto:{e(L['email'])}">{e(L['email'])}</a>. Please don't text the producers directly.</p>
    <p class="center" style="margin-top:2.5rem"><a href="/">Back to the invitation</a></p>"""
    payload = encrypt(inner, gate_code())
    return head("Ticket holders · Beyond the Veil", "Ticket-holder entry") + f"""<body class="guide-page">
<canvas class="veil veil-fixed" aria-hidden="true"></canvas>
<main>
<section class="gate" id="gate">
  <div class="gate-card">
    {DIAMOND}
    <h2>Cross the Veil</h2>
    {rule()}
    <p>Enter the code from your Partiful invite to open the ticket-holder guide.</p>
    <form id="gate-form">
      <label class="sr-only" for="code">Gate code</label>
      <input id="code" name="code" autocomplete="off" autocapitalize="characters" spellcheck="false" required autofocus placeholder="Code">
      <p class="error" role="alert" id="gate-error" hidden>That isn't the code. Check your Partiful invite and try again.</p>
      <button class="btn btn-holo" type="submit">Open the guide</button>
    </form>
    <p class="back"><a href="/">Back to the invitation</a></p>
  </div>
</section>
<section class="guide" id="guide" hidden><div class="wrap" id="guide-body"></div></section>
</main>
<script>window.__VEIL__ = {json.dumps(payload)};</script>
<script src="/veil.js?v={VERSION}" defer></script>
<script src="/gate.js?v={VERSION}" defer></script>
</body>
</html>
"""


def gate_code():
    """The gate code comes from the GATE_CODE environment variable or a local,
    never-published .gatecode file, so it is not stored in the site's source."""
    code = os.environ.get("GATE_CODE") or (ROOT / ".gatecode").read_text().strip()
    return "".join(ch for ch in code.upper() if ch.isalnum())


def encrypt(plaintext, code):
    """AES-256-GCM with a key derived from the code (PBKDF2-SHA256, 310k rounds).
    The page holds only ciphertext; the browser decrypts it with the right code."""
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=310000).derive(code.encode())
    ct = AESGCM(key).encrypt(iv, plaintext.encode(), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"salt": b(salt), "iv": b(iv), "ct": b(ct), "iter": 310000}


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#8e9298"/><stop offset="1" stop-color="#cfc6f2"/></linearGradient></defs><rect width="64" height="64" rx="14" fill="#07080d"/><rect x="20" y="20" width="24" height="24" transform="rotate(45 32 32)" fill="url(#g)"/></svg>"""


def touch_icon():
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (180, 180), (7, 8, 13))
    d = ImageDraw.Draw(im)
    d.polygon([(90, 46), (134, 90), (90, 134), (46, 90)], fill=(220, 222, 228))
    return im


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "guide").mkdir(parents=True)
    shutil.copytree(SRC / "img", DIST / "img")
    shutil.copytree(SRC / "fonts", DIST / "fonts")
    for f in ("style.css", "main.js", "gate.js", "veil.js"):
        shutil.copy(SRC / f, DIST / f)
    (DIST / "index.html").write_text(index_page())
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
