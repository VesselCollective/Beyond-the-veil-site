# Beyond the Veil: invite and party guide

The private event site for Beyond the Veil (Oct 31 to Nov 1, 2026), presented by Michael Pullano and Austin Dance Temple. Hosted on Netlify as `beyondtheveil-atx`.

## How it works

- `content.json` holds every name, time, link and line of copy. Change content there, nowhere else.
- `build.py` turns `content.json` and `src/` into the finished site in `dist/`.
- `dist/` is committed and is exactly what Netlify publishes. Netlify runs no build step.
- `private.json` (git-ignored) holds the address, map link and WhatsApp link. A copy is kept in the Claude Project "Event Production".
- `/guide/` is the ticket-holder guide. Its content is encrypted (AES-256-GCM, key derived with PBKDF2) and opens only with the gate code, which guests get from the Partiful invite. The code is never stored in this repo.

## Updating the site

```sh
pip install cryptography
GATE_CODE=<the code> python3 build.py   # or keep the code in a local, git-ignored .gatecode file
git add -A && git commit -m "Update copy" && git push
```

Netlify deploys every push to `main`.
