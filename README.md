# Mycasa client options pages

Each client page lives at `public/<slug>/index.html` and is served by Cloudflare Workers (static assets) at `https://clientrealestateoptions.<account>.workers.dev/<slug>/`.

- `_template/build_page.py` + `_template/template-base.html` — page builder
- `clients/<slug>.json` — per-client config

Build: `python3 _template/build_page.py _template/template-base.html clients/<slug>.json public/<slug>/index.html`
