# Beyond the Veil: invite and party guide

The event site for Beyond the Veil (Oct 31 to Nov 1, 2026), presented by Michael Pullano and Austin Dance Temple. Hosted on Netlify as `beyondtheveil-atx`; every push to `main` deploys.

## How it works

- `content.json` holds every name, time, link and line of copy. Change content there, nowhere else.
- `build.py` turns `content.json` and `src/` into the finished site in `dist/`.
- `dist/` is committed and is exactly what Netlify publishes. Netlify runs no build step.
- The old `/guide/` address redirects to the venue section of the main page.

## Updating the site

```sh
python3 build.py
git add -A && git commit -m "Update copy" && git push
```

Performer photos go in `src/img/artists/`; add `"photo": "file.webp"` to that artist in `content.json`.
