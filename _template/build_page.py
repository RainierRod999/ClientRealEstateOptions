#!/usr/bin/env python3
"""Mycasa client options page builder.
Usage: python3 build_page.py <template-base.html> <client.json> <out.html>
"""
import re, sys, json, urllib.parse
tpl_path, cfg_path, out_path = sys.argv[1:4]
src = open(tpl_path, encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
cfg = json.load(open(cfg_path, encoding='utf-8'))
CLIENT = cfg['client']; WA = cfg.get('whatsapp', '16463424105'); CITY = cfg['city']
SUB = cfg.get('subtitle', CITY.upper() + ' · RIVIERA MAYA · MÉXICO')
FOOT = cfg.get('footer_location', CITY.upper() + ' · QUINTANA ROO · MÉXICO')
props = cfg['properties']
for p in props:
    if isinstance(p.get('photos'), list): p['photos'] = ','.join(p['photos'])
    p.setdefault('levels', None); p.setdefault('note', ''); p.setdefault('type', 'PROPERTY')
    p.setdefault('badge_en', ''); p.setdefault('badge_es', p.get('badge_en', ''))
    p.setdefault('short', p['plain']); p.setdefault('name', p['plain'])
WA_SVG = re.search(r'(<svg xmlns.*?</svg>)', src, re.S).group(1)

def money(n): return f"${n:,.0f}"
def k(n): return f"${n/1e6:.1f}M" if n >= 1e6 else f"${n/1e3:.0f}k"

cards = []
for i, p in enumerate(props, 1):
    ids = p['photos'].split(',')
    slides = "\n".join(
        f'          <div class="carousel-slide"><img src="https://lh3.googleusercontent.com/d/{pid}=w1600" alt="{p["plain"]} photo {j+1}" referrerpolicy="no-referrer" {"" if j==0 else "loading=\"lazy\""} onerror="dropSlide(this)"></div>'
        for j, pid in enumerate(ids))
    dots = "".join(f'<div class="carousel-dot{" active" if j==0 else ""}" onclick="goToSlide(\'carousel-{i}\',{j})"></div>' for j in range(len(ids)))
    stats = ([(p['m2'], "M² TOTAL", "M² TOTAL")] if p.get('m2') else []) + [(p['bed'], "BEDROOMS", "RECÁMARAS"), (p['bath'], "BATHROOMS", "BAÑOS")]
    if p['levels']: stats.append((p['levels'], "LEVELS", "NIVELES"))
    stats_html = "".join(f'<div class="prop-stat"><span class="prop-stat-num">{v}</span><span class="prop-stat-label" data-en="{en}" data-es="{es}">{en}</span></div>' for v, en, es in stats)
    feats = "".join(f"<li>{f}</li>" for f in p['features'])
    inquire = "https://wa.me/%s?text=%s" % (WA, urllib.parse.quote_plus(f"Hi Rainier, I'm interested in {p['plain']}. Can we talk?"))
    cards.append(f'''
  <div class="property-card{" even" if i%2==0 else ""}" data-prop-id="prop-{i}" data-prop-name="{p['plain']}" data-prop-price="{money(p['price'])}">
    <div class="prop-image" style="padding:0;">
      {f'<span class="prop-badge" data-en="{p["badge_en"]}" data-es="{p["badge_es"]}">{p["badge_en"]}</span>' if p['badge_en'] else ''}
      <div class="carousel" id="carousel-{i}">
        <div class="carousel-track" id="track-{i}">
{slides}
        </div>
        <button class="carousel-btn prev" onclick="moveCarousel('carousel-{i}', -1)" aria-label="Previous photo">&#8592;</button>
        <button class="carousel-btn next" onclick="moveCarousel('carousel-{i}', 1)" aria-label="Next photo">&#8594;</button>
        <div class="carousel-dots" id="dots-{i}">{dots}</div>
        <div class="carousel-count" id="count-{i}">1 / {len(ids)}</div>
      </div>
    </div>
    <div class="prop-text">
      <p class="prop-number">{i:02d} · {p['type']}</p>
      <h3 class="prop-name">{p['name']}</h3>
      <p class="prop-location">{p['zone'].upper()} · {p['city'].upper()}</p>
      <div class="prop-stats">{stats_html}</div>
      <div class="prop-divider"></div>
      <ul class="prop-features">{feats}</ul>
      <div class="prop-price-block">
        <p class="prop-price-current">USD {money(p['price'])}</p>
        <p class="prop-price-note">{p['note']}</p>
      </div>
      <div class="prop-buttons">
        <a href="https://drive.google.com/drive/folders/{p['folder']}" target="_blank" class="btn" data-en="PHOTOS —" data-es="FOTOS —">PHOTOS —</a>
        <button class="btn save-btn" onclick="toggleSave(this)" data-en="☆ SAVE" data-es="☆ GUARDAR">☆ SAVE</button>
        <a href="{inquire}" target="_blank" class="btn" data-en="INQUIRE —" data-es="CONSULTAR —">INQUIRE —</a>
      </div>
      <a href="https://wa.me/{WA}" target="_blank" class="like-btn" onclick="likeThis(this)">
        {WA_SVG.replace('width="18" height="18"', 'width="16" height="16"')}
        <span data-en="I LIKE THIS ONE" data-es="ME GUSTA ESTA">I LIKE THIS ONE</span>
      </a>
      <p class="like-hint" data-en="Opens WhatsApp with a message to Rainier — just tap Send" data-es="Abre WhatsApp con un mensaje para Rainier — solo toca Enviar">Opens WhatsApp with a message to Rainier — just tap Send</p>
    </div>
  </div>''')

# fix "PENTHOUSE" label for villa

beds = [p['bed'] for p in props]; m2 = [p.get('m2') for p in props]; pr = [p['price'] for p in props]
rows = "".join(f"<tr><td>{p['short']}</td><td>{p['zone'].split(' · ')[0]}</td><td>{p['bed']}</td><td>{p['bath']}</td><td>{p.get('m2') or '—'}</td><td>{money(p['price'])}</td></tr>" for p in props)

extra_css = """
  .prop-badge { z-index: 12; }
  .carousel { position: absolute; inset: 0; min-height: 0; }
  .prop-image { min-height: 460px; }
  .like-btn { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 16px; background: var(--gold); color: var(--btn-hover-text); border: 1px solid var(--gold); padding: 14px 26px; font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; text-decoration: none; font-weight: 500; transition: opacity 0.2s, transform 0.2s; }
  .like-btn:hover { opacity: 0.88; }
  .like-btn.sent { background: transparent; color: var(--gold); }
  .like-hint { font-size: 0.68rem; color: var(--text-muted); margin-top: 8px; text-align: center; letter-spacing: 0.02em; }
  @media (max-width: 768px) { .prop-image { min-height: 300px; } }
"""

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Your Property Options in {CITY} — Mycasa Real Estate</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,400;1,500&family=Playfair+Display:ital,wght@0,400;1,400;1,600&display=swap" rel="stylesheet">
<style>{style}{extra_css}</style>
</head>
<body>

<button id="fav-counter" onclick="showFavorites()"></button>

<div id="main-view">
<button id="lang-toggle" onclick="toggleLang()"><span id="lang-label">ES</span></button>

<div id="hero">
  <div class="hero-bg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div class="hero-line"></div>
    <p class="hero-brand">Mycasa Real Estate</p>
    <h1 class="hero-title" data-en="Your Property Options<br>in {CITY}" data-es="Tus Opciones de Propiedades<br>en {CITY}">Your Property Options<br>in {CITY}</h1>
    <p class="hero-subtitle">{SUB}</p>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><span class="hero-stat-number">{len(props)}</span><span class="hero-stat-label" data-en="PROPERTIES" data-es="PROPIEDADES">PROPERTIES</span></div>
    <div class="hero-stat"><span class="hero-stat-number">{min(beds)}–{max(beds)}</span><span class="hero-stat-label" data-en="BEDROOMS" data-es="RECÁMARAS">BEDROOMS</span></div>
    {f'<div class="hero-stat"><span class="hero-stat-number">{min(m2)}–{max(m2)}</span><span class="hero-stat-label" data-en="M² TOTAL" data-es="M² TOTAL">M² TOTAL</span></div>' if all(m2) else ''}
    <div class="hero-stat"><span class="hero-stat-number">{k(min(pr))}–{k(max(pr))}</span><span class="hero-stat-label" data-en="PRICE RANGE" data-es="RANGO DE PRECIO">PRICE RANGE</span></div>
  </div>
  <div class="scroll-indicator">&#8964;</div>
</div>

<section id="properties">
  <span class="section-label" data-en="CURATED FOR YOU" data-es="SELECCIONADO PARA TI">CURATED FOR YOU</span>
  <h2 class="section-heading" data-en="Properties selected for {CLIENT}" data-es="Propiedades seleccionadas para {CLIENT}">Properties selected for {CLIENT}</h2>
{"".join(cards)}
</section>

<div id="table-section">
  <div>
    <span class="section-label" data-en="OVERVIEW" data-es="RESUMEN">OVERVIEW</span>
    <h2 class="section-heading" data-en="Property Comparison" data-es="Comparativa de propiedades">Property Comparison</h2>
    <div class="table-wrap">
      <table>
        <thead><tr>
          <th data-en="PROPERTY" data-es="PROPIEDAD">PROPERTY</th>
          <th data-en="ZONE" data-es="ZONA">ZONE</th>
          <th data-en="BED" data-es="RÉC">BED</th>
          <th data-en="BATH" data-es="BAÑOS">BATH</th>
          <th>M²</th>
          <th data-en="PRICE USD" data-es="PRECIO USD">PRICE USD</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</div>

<div id="cta">
  <p class="cta-brand">Mycasa Real Estate</p>
  <h2 class="cta-heading" data-en="Did any catch your eye?" data-es="¿Alguna te llamó la atención?">Did any catch your eye?</h2>
  <p class="cta-sub" data-en="Schedule a visit or request more information" data-es="Coordina una visita o solicita más información">Schedule a visit or request more information</p>
  <a href="https://wa.me/{WA}?text={urllib.parse.quote_plus("Hi Rainier, it's " + CLIENT + ". I saw the " + CITY + " properties. Can we schedule a visit?")}" target="_blank" class="cta-btn">
    {WA_SVG}
    <span data-en="SCHEDULE A VISIT" data-es="AGENDAR VISITA">SCHEDULE A VISIT</span>
  </a>
  <p class="cta-address">{FOOT} &nbsp;·&nbsp; +1 646 342 4105</p>
</div>
'''

script = re.search(r'<script>(.*?)</script>', src, re.S).group(1)
script = re.sub(r"mycasa_saved_\w+", "mycasa_saved_" + cfg.get("slug", CLIENT.lower()), script)
script = script.replace("let currentLang = 'en';", "var currentLang = 'en';")
# localStorage safety
script = script.replace("localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));", "try { localStorage.setItem(STORAGE_KEY, JSON.stringify(arr)); } catch(e) {}")
script += r'''
  // ── CAROUSEL: drop photos that fail to load (e.g. a video in the folder) ──
  function dropSlide(img) {
    const slide = img.closest('.carousel-slide');
    const carousel = img.closest('.carousel');
    if (!slide || !carousel) return;
    const num = carousel.id.split('-')[1];
    const idx = [...slide.parentNode.children].indexOf(slide);
    slide.remove();
    const dots = document.querySelectorAll('#dots-' + num + ' .carousel-dot');
    if (dots[idx]) dots[idx].remove();
    document.querySelectorAll('#dots-' + num + ' .carousel-dot').forEach((d, i) => d.setAttribute('onclick', "goToSlide('carousel-" + num + "'," + i + ")"));
    carouselState[carousel.id] = 0;
    updateCarousel(carousel.id, carousel.querySelectorAll('.carousel-slide').length);
  }

  // ── "I LIKE THIS ONE" → WhatsApp to Rainier ──
  const CLIENT_NAME = '__CLIENT__';
  const WA_NUMBER = '__WA__';
  function likeThis(a) {
    const card = a.closest('.property-card');
    const now = new Date();
    let cancun = '', local = '';
    try {
      cancun = now.toLocaleString('en-US', { timeZone: 'America/Cancun', weekday: 'short', month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
      local = now.toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });
    } catch (e) { cancun = now.toString(); }
    const msg =
      '👍 I LIKE THIS ONE!\n\n' +
      'Client: ' + CLIENT_NAME + '\n' +
      'Property: ' + card.dataset.propName + ' (USD ' + card.dataset.propPrice + ')\n' +
      'Clicked: ' + cancun + ' (Cancún time)' + (local ? '\nClient local time: ' + local : '') + '\n\n' +
      'Sent from my __CITY__ options page';
    a.href = 'https://wa.me/' + WA_NUMBER + '?text=' + encodeURIComponent(msg);
    a.classList.add('sent');
  }
'''

script = script.replace('__CLIENT__', CLIENT.replace("'", "\\'")).replace('__WA__', WA).replace('__CITY__', CITY)
fav = re.search(r'(<!-- ═+\s*FAVORITES VIEW.*?</div>\s*</div>\s*)</body>', src, re.S).group(1)
fav = re.sub(r"(for|para) [A-Z][\w ]*?(?=[\"<\n])", lambda m: m.group(1) + " " + CLIENT, fav)
fav = re.sub(r"YOUR SHORTLIST · [^<]*", "YOUR SHORTLIST · " + CITY.upper() + " · RIVIERA MAYA", fav)
fav = fav.replace('<div id="hero" style="height:55vh;min-height:340px;">', '<div id="fav-hero" style="position:relative;height:55vh;min-height:340px;display:flex;align-items:center;justify-content:center;overflow:hidden;">')

out = page + "\n<script>" + script + "</script>\n</div><!-- /main-view -->\n\n" + fav + "</body>\n</html>\n"
open(out_path, 'w', encoding='utf-8').write(out)
print(len(out))
