"""Build the Beyond the Veil site from content.json into dist/.

Every name, time, link and line of copy lives in content.json. Edit it, run
`python3 build.py`, and redeploy.
"""
import html
import json
import shutil
from pathlib import Path

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
L = dict(C["links"], map=P["map"], whatsapp=P["whatsapp"])
C["guide"]["address"] = P["address"]
VERSION = "6"


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
<meta name="theme-color" content="#0b0c13">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(C['hero']['title'])}: {e(C['hero']['subtitle'])}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{url}/img/og.jpg">
<meta property="og:url" content="{url}/">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect x='9' y='9' width='14' height='14' transform='rotate(45 16 16)' fill='%23e7e9e7'/%3E%3C/svg%3E">
<link rel="preload" href="/fonts/cinzel-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/cormorant-garamond-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={VERSION}">
{extra}
</head>
"""


def rule():
    return '<div class="rule" aria-hidden="true"><span></span></div>'


def names(items, cls="names"):
    sep = '<span class="sep" aria-hidden="true">&#9670;</span>'
    parts = [f"<span>{e(n)}</span>" for n in items]
    return f'<p class="{cls}">' + " ".join(p + "&nbsp;" + sep for p in parts[:-1]) + " " + parts[-1] + "</p>"


def index_page():
    h, inv, cr, co, t = C["hero"], C["invitation"], C["credits"], C["costume"], C["tickets"]
    flow = "\n".join(
        f'<li class="{"key" if s["name"] == "The Crossing" else ""}"><time>{e(s["time"])}</time>'
        f'<h3>{e(s["name"])}</h3><p>{e(s["text"])}</p></li>'
        for s in C["flow"]
    )
    palette = "\n".join(
        f'<li><span class="chip{" metal" if p["name"] == "Liquid Silver" else ""}" style="background:{p["hex"]}"></span>{e(p["name"])}</li>'
        for p in co["palette"]
    )
    tiers = "\n".join(f"<li>{e(x)}</li>" for x in t["tiers"])
    addons = "\n".join(f'<div><h3>{e(a["name"])}</h3><p>{e(a["text"])}</p></div>' for a in t["addons"])
    details = "\n".join(f'<div><dt>{e(d["name"])}</dt><dd>{e(d["text"])}</dd></div>' for d in C["details"])
    paras = "\n".join(f"<p>{e(p)}</p>" for p in inv["paragraphs"])
    vid = L["video_id"]

    return head(C["meta"]["title"], C["meta"]["description"]) + f"""<body>
<div class="veil-intro" aria-hidden="true"><div class="panel left"></div><div class="panel right"></div></div>

<header class="hero">
  <div class="hero-art"><picture><source media="(max-width: 640px)" srcset="/img/hand-m.webp"><img src="/img/hand.webp" alt="A hand reaching through a sheer veil" width="1121" height="278" fetchpriority="high"></picture></div>
  <p class="presenters">{e(h['presenters'])}</p>
  <h1>{e(h['title'])}</h1>
  <p class="subtitle">{e(h['subtitle'])}</p>
  {rule()}
  <p class="dates">{e(h['dates'])}</p>
  <p class="place">{e(h['location'])} &nbsp;&#8226;&nbsp; {e(h['venue'])}</p>
  <p class="arrival">{e(h['arrival'])}</p>
  <div class="actions">
    <a class="btn btn-holo" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a>
    <a class="btn btn-ghost" href="{e(L['nominate'])}" target="_blank" rel="noopener">Nominate a guest</a>
  </div>
</header>

<main>
<section class="invitation organza" aria-labelledby="inv-h">
  <div class="wrap">
    <h2 id="inv-h" class="sr-only">The invitation</h2>
    <p class="greeting">{e(inv['greeting'])}</p>
    {paras}
    <p class="signoff">{e(inv['closing'])}<strong>{e(inv['signature'])}</strong></p>
  </div>
</section>

<section id="flow" aria-labelledby="flow-h">
  <div class="wrap">
    <h2 id="flow-h">The Flow</h2>
    {rule()}
    <ol class="flow">
{flow}
    </ol>
  </div>
  <figure class="photo-wide"><img src="/img/grounds.webp" alt="A guest in a glowing crown looks out over the estate grounds at night" loading="lazy" width="1024" height="1533"></figure>
</section>

<section id="night" class="credits" aria-labelledby="night-h">
  <div class="wrap">
    <h2 id="night-h">The Night</h2>
    {rule()}
    <p class="credit-label">{e(cr['direction_label'])}</p>
    <p class="names">{e(cr['direction'])}</p>
    <p class="credit-label">{e(cr['music_label'])}</p>
    {names(cr['music'])}
    <p class="credit-label">{e(cr['featuring_label'])}</p>
    {names(cr['featuring'])}
    <p class="credit-label">{e(cr['activations_label'])}</p>
    {names(cr['activations'], 'names small')}
  </div>
  <div class="pair">
    <img src="/img/dancefloor.webp" alt="Guests in horned masks under violet lasers on the dance floor" loading="lazy" width="1024" height="1533">
    <img src="/img/fire-fans.webp" alt="A fire performer spinning flaming fans" loading="lazy" width="1024" height="1533">
  </div>
</section>

<section id="costume" class="organza" aria-labelledby="costume-h">
  <div class="wrap">
    <h2 id="costume-h">The Costume</h2>
    {rule()}
    <p class="lead">{e(co['lead'])}</p>
    <p>{e(co['text'])}</p>
    <ul class="palette" aria-label="The Silver Veil palette">
{palette}
    </ul>
    <div class="inspo">
      <a href="{e(L['pinterest'])}" target="_blank" rel="noopener"><strong>The moodboard</strong><span>{e(co['pinterest_text'])} On Pinterest.</span></a>
      <a href="{e(L['etsy'])}" target="_blank" rel="noopener"><strong>Costume picks</strong><span>{e(co['etsy_text'])} On Etsy.</span></a>
    </div>
    <p>{e(co['layers'])}</p>
  </div>
  <figure><img src="/img/angels.webp" alt="Three guests from 2025 in holographic silver, white wings and eye halos" loading="lazy" width="1400" height="1400"></figure>
  <figure class="moodboard"><img src="/img/silver-veil.webp" alt="The Silver Veil moodboard: lunar, chrome and mystic tones with sheer organza, crystal and liquid metal" loading="lazy" width="480" height="600"></figure>
</section>

<section id="community" aria-labelledby="community-h">
  <div class="wrap"><h2 id="community-h">The Community</h2>{rule()}</div>
  <div class="video">
    <button type="button" data-id="{e(vid)}" aria-label="Play the Halloween 2025 recap">
      <img src="https://i.ytimg.com/vi/{e(vid)}/hqdefault.jpg" alt="" loading="lazy">
      <span class="play"></span>
    </button>
  </div>
  <p class="center" style="color:var(--slate-soft);font-style:italic;font-size:.9em;margin-top:.8rem">{e(C['community']['caption'])}</p>
  <figure><img src="/img/fire-circle.webp" alt="A fire performer above a circle of guests, one kneeling in the center" loading="lazy" width="1024" height="1533" style="max-width:34rem;margin:0 auto"><figcaption>Photos from Halloween 2025 by Last Weekend.</figcaption></figure>
</section>

<section id="tickets" class="organza" aria-labelledby="tickets-h">
  <div class="wrap">
    <h2 id="tickets-h">Tickets</h2>
    {rule()}
    <p class="lead">{e(t['lead'])}</p>
    <p class="center">{e(t['text'])}</p>
    <ol class="tiers">
{tiers}
    </ol>
    <div class="center"><a class="btn btn-holo" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a></div>
    <div class="addons">
{addons}
    </div>
    <p class="after">{e(t['after'])}</p>
  </div>
</section>

<section id="details" aria-labelledby="details-h">
  <div class="wrap">
    <h2 id="details-h">The Details</h2>
    {rule()}
    <dl class="details">
{details}
    </dl>
  </div>
</section>

<section id="nominate" class="organza" aria-labelledby="nominate-h">
  <div class="wrap center">
    <h2 id="nominate-h">Nominate a Guest</h2>
    {rule()}
    <p class="lead">{e(C['nominate']['lead'])}</p>
    <p>{e(C['nominate']['text'])}</p>
    <a class="btn btn-ghost" href="{e(L['nominate'])}" target="_blank" rel="noopener">Nominate a guest</a>
  </div>
</section>

<section class="partner" aria-label="Partner">
  <p class="label">{e(C['partner']['label'])}</p>
  <p class="wordmark">{e(C['partner']['name'])}</p>
</section>

<section class="closing"><p>{e(C['closing'])}</p></section>
</main>

<footer>
  <p>{e(C['footer']['questions'])} <a href="mailto:{e(L['email'])}">{e(L['email'])}</a></p>
  <p>{e(C['footer']['noshare'])}</p>
  <p><a href="/guide/">{e(C['footer']['guide_link'])}</a></p>
</footer>

<div class="sticky"><a class="btn btn-holo" href="{e(L['tickets'])}" target="_blank" rel="noopener">Secure your place</a></div>
<script src="/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def guide_page():
    g = C["guide"]
    secs = "\n".join(
        f'<h3>{e(s["name"])}</h3><ul>' + "".join(f"<li>{e(i)}</li>" for i in s["items"]) + "</ul>"
        for s in g["sections"]
    )
    inner = f"""<h2>The Guide</h2>
    {rule()}
    <p class="lead">{e(g['intro'])}</p>
    <div class="address">
      <strong>{e(g['address_name'])}</strong>
      {e(g['address'])}<br>
      <a href="{e(L['map'])}" target="_blank" rel="noopener">Open in Maps</a>
    </div>
    <div class="actions" style="margin-bottom:2.5rem">
      <a class="btn btn-holo" href="{e(L['whatsapp'])}" target="_blank" rel="noopener">Join the rideshare group</a>
    </div>
    {secs}
    <h3>Questions</h3>
    <p>Email <a href="mailto:{e(L['email'])}">{e(L['email'])}</a>. Please don't text the producers directly.</p>
    <p class="center" style="margin-top:2.5rem"><a href="/">Back to the invitation</a></p>"""
    payload = encrypt(inner, gate_code())
    return head("Ticket holders · Beyond the Veil", "Ticket-holder entry") + f"""<body>
<main>
<section class="gate" id="gate">
  <div>
    <h2>Cross the Veil</h2>
    {rule()}
    <p>Enter the code from your Partiful invite to open the ticket-holder guide.</p>
    <form id="gate-form">
      <label class="sr-only" for="code">Gate code</label>
      <input id="code" name="code" autocomplete="off" autocapitalize="characters" spellcheck="false" required autofocus>
      <p class="error" role="alert" id="gate-error" hidden>That isn't the code. Check your Partiful invite and try again.</p>
      <button class="btn btn-holo" type="submit">Open the guide</button>
    </form>
    <p style="margin-top:2rem"><a href="/">Back to the invitation</a></p>
  </div>
</section>
<section class="guide" id="guide" hidden><div class="wrap" id="guide-body"></div></section>
</main>
<script>window.__VEIL__ = {json.dumps(payload)};</script>
<script src="/gate.js?v={VERSION}" defer></script>
</body>
</html>
"""


def gate_code():
    """The gate code comes from the GATE_CODE environment variable or a local,
    never-published .gatecode file, so it is not stored in the site's source."""
    import os
    code = os.environ.get("GATE_CODE") or (ROOT / ".gatecode").read_text().strip()
    return "".join(ch for ch in code.upper() if ch.isalnum())


def encrypt(plaintext, code):
    """AES-256-GCM with a key derived from the code (PBKDF2-SHA256, 310k rounds).
    The page holds only ciphertext; the browser decrypts it with the right code."""
    import base64, os
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=310000).derive(code.encode())
    ct = AESGCM(key).encrypt(iv, plaintext.encode(), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"salt": b(salt), "iv": b(iv), "ct": b(ct), "iter": 310000}


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "guide").mkdir(parents=True)
    shutil.copytree(SRC / "img", DIST / "img")
    shutil.copytree(SRC / "fonts", DIST / "fonts")
    shutil.copy(SRC / "style.css", DIST / "style.css")
    shutil.copy(SRC / "main.js", DIST / "main.js")
    shutil.copy(SRC / "gate.js", DIST / "gate.js")
    (DIST / "index.html").write_text(index_page())
    (DIST / "guide" / "index.html").write_text(guide_page())
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    (DIST / "_headers").write_text(
        "/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Content-Type-Options: nosniff\n"
    )
    print("Built", sorted(str(p.relative_to(DIST)) for p in DIST.rglob("*") if p.is_file()))


if __name__ == "__main__":
    main()
