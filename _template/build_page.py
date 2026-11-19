#!/usr/bin/env python3
"""Mycasa client options page builder.
Usage: python3 build_page.py <template.html> <client.json> <out.html>
Templates: _template/mycasa-one-sheet.html (brand-guide design, default)
           _template/rainier-one-sheet.html (original design)
A template may override parts of the page with <!-- SLOT:name -->...<!-- /SLOT:name -->
blocks: head, hero-brand, cta-brand. Missing slots fall back to the original markup.
"""
import re, sys, json, urllib.parse
tpl_path, cfg_path, out_path = sys.argv[1:4]
import os
# Old instructions pointed at template-base.html; it is now Mycasa One Sheet by default.
if os.path.basename(tpl_path) == 'template-base.html' and not os.path.exists(tpl_path):
    tpl_path = os.path.join(os.path.dirname(tpl_path), 'mycasa-one-sheet.html')
src = open(tpl_path, encoding='utf-8').read()
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
style = re.sub(r'#lang-toggle(:hover)?(?=\s*[,{])', lambda m: m.group(0) + ', #print-btn' + (m.group(1) or ''), style)
cfg = json.load(open(cfg_path, encoding='utf-8'))
SITE_URL = 'https://clientrealestateoptions.rainierrod.workers.dev/'
CLIENT = cfg['client']; WA = cfg.get('whatsapp', '16463424105'); CITY = cfg['city']
SUB = cfg.get('subtitle', CITY.upper() + ' · RIVIERA MAYA · MÉXICO')
FOOT = cfg.get('footer_location', CITY.upper() + ' · QUINTANA ROO · MÉXICO')
props = cfg['properties']
for p in props:
    if isinstance(p.get('photos'), list): p['photos'] = ','.join(p['photos'])
    p.setdefault('levels', None); p.setdefault('note', ''); p.setdefault('type', 'PROPERTY')
    p.setdefault('badge_en', ''); p.setdefault('badge_es', p.get('badge_en', ''))
    p.setdefault('short', p['plain']); p.setdefault('name', p['plain'])
    # 'added' = date the property was put on the page (YYYY-MM-DD) -> shown as "Added MM/DD/YY"
    # 'new'   = true for properties added after the page was first sent -> orange NEW flag
    p['added_fmt'] = ''
    if p.get('added'):
        y, mo, d = str(p['added']).split('-')[:3]; p['added_fmt'] = f"{int(mo):02d}/{int(d):02d}/{y[-2:]}"
def slot(name, default):
    m = re.search(r'<!-- SLOT:%s -->(.*?)<!-- /SLOT:%s -->' % (name, name), src, re.S)
    return m.group(1).strip() if m else default
FONTS = re.search(r'<link href="https://fonts\.googleapis\.com/css2[^"]*" rel="stylesheet">', src).group(0)
HEAD_EXTRA = slot('head', '')
HERO_BRAND = slot('hero-brand', '<div class="hero-line"></div>\n    <p class="hero-brand">Mycasa Real Estate</p>')
CTA_BRAND = slot('cta-brand', '<p class="cta-brand">Mycasa Real Estate</p>')
WA_SVG = re.search(r'(<svg xmlns.*?</svg>)', src, re.S).group(1)

def money(n): return f"${n:,.0f}"
def k(n): return f"${n/1e6:.1f}M" if n >= 1e6 else f"${n/1e3:.0f}k"

cards = []
for i, p in enumerate(props, 1):
    ids = p['photos'].split(',')
    slides = "\n".join(
        f'          <div class="carousel-slide"><img src="{pid if ('/' in pid or '.' in pid) else 'https://lh3.googleusercontent.com/d/'+pid+'=w1600'}" alt="{p["plain"]} photo {j+1}" referrerpolicy="no-referrer" {"" if j==0 else "loading=\"lazy\""} onerror="dropSlide(this)"></div>'
        for j, pid in enumerate(ids))
    dots = "".join(f'<div class="carousel-dot{" active" if j==0 else ""}" onclick="goToSlide(\'carousel-{i}\',{j})"></div>' for j in range(len(ids)))
    stats = ([(p['m2'], "M² TOTAL", "M² TOTAL")] if p.get('m2') else []) + [(p['bed'], "BEDROOMS", "RECÁMARAS")] + ([(p['bath'], "BATHROOMS", "BAÑOS")] if p.get('bath') else [])
    if p['levels']: stats.append((p['levels'], "LEVELS", "NIVELES"))
    stats_html = "".join(f'<div class="prop-stat"><span class="prop-stat-num">{v}</span><span class="prop-stat-label" data-en="{en}" data-es="{es}">{en}</span></div>' for v, en, es in stats)
    feats = "".join(f"<li>{f}</li>" for f in p['features'])
    like_static = "https://wa.me/%s?text=%s" % (WA, urllib.parse.quote(f"👍 I LIKE THIS ONE!\n\nClient: {CLIENT}\nProperty: {p['plain']} (USD {money(p['price'])})\n\nSent from my {CITY} options page"))
    inquire = "https://wa.me/%s?text=%s" % (WA, urllib.parse.quote_plus(f"Hi Rainier, I'm interested in {p['plain']}. Can we talk?"))
    cards.append(f'''
  <div class="property-card{" even" if i%2==0 else ""}{" print-break" if i%3==0 and i<len(props) else ""}" data-prop-id="prop-{i}" data-prop-name="{p['plain']}" data-prop-price="{money(p['price'])}">
    <div class="prop-image" style="padding:0;">
      {f'<span class="prop-badge" data-en="{p["badge_en"]}" data-es="{p["badge_es"]}">{p["badge_en"]}</span>' if p['badge_en'] else ''}
      {'<span class="new-flag" data-en="NEW" data-es="NUEVA">NEW</span>' if p.get('new') else ''}
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
        <p class="prop-price-current">{(f'<span style="font-size:0.45em;letter-spacing:0.14em;display:block;margin-bottom:6px;" data-en="{p["price_prefix"]}" data-es="{p.get("price_prefix_es", p["price_prefix"])}">{p["price_prefix"]}</span>') if p.get('price_prefix') else ''}USD {money(p['price'])}</p>
        <p class="prop-price-note">{p['note']}</p>
      </div>
      <div class="prop-buttons">
        {(f'<a href="{p["folder"] if p["folder"].startswith("http") else "https://drive.google.com/drive/folders/"+p["folder"]}" target="_blank" class="btn" data-en="PHOTOS —" data-es="FOTOS —">PHOTOS —</a>') if p.get('folder') else ''}
        <button class="btn save-btn" onclick="toggleSave(this)" data-en="☆ SAVE" data-es="☆ GUARDAR">☆ SAVE</button>
        <a href="{inquire}" target="_blank" class="btn" data-en="INQUIRE —" data-es="CONSULTAR —">INQUIRE —</a>
      </div>
      {f'<a href="{p["brochure"] if p["brochure"].startswith("http") else "https://drive.google.com/file/d/"+p["brochure"]+"/view"}" target="_blank" class="btn" style="display:block;text-align:center;margin-top:14px;" data-en="{p.get("brochure_label", "VIEW BROCHURE —")}" data-es="{p.get("brochure_label_es", "VER FOLLETO —")}">{p.get("brochure_label", "VIEW BROCHURE —")}</a>' if p.get('brochure') else ''}
      {f'<a href="{p["video"] if p["video"].startswith("http") else "https://drive.google.com/file/d/"+p["video"]+"/view"}" target="_blank" class="btn video-btn" style="display:block;text-align:center;margin-top:14px;" data-en="▶ WATCH TOUR VIDEO" data-es="▶ VER VIDEO TOUR">▶ WATCH TOUR VIDEO</a>' if p.get('video') else ''}
      <a href="{like_static}" target="_blank" class="like-btn" onclick="likeThis(this)">
        {WA_SVG.replace('width="18" height="18"', 'width="16" height="16"')}
        <span data-en="I LIKE THIS ONE" data-es="ME GUSTA ESTA">I LIKE THIS ONE</span>
      </a>
      <p class="like-hint" data-en="Opens WhatsApp with a message to Rainier — just tap Send" data-es="Abre WhatsApp con un mensaje para Rainier — solo toca Enviar">Opens WhatsApp with a message to Rainier — just tap Send</p>
      {(f'<p class="added-line">' + ('<span class="added-new" data-en="NEW" data-es="NUEVA">NEW</span>' if p.get('new') else '') + f'<span data-en="Added {p["added_fmt"]}" data-es="Agregada {p["added_fmt"]}">Added {p["added_fmt"]}</span></p>') if p['added_fmt'] else ''}
    </div>
  </div>''')

# fix "PENTHOUSE" label for villa

SHOW_BATH = any(p.get('bath') for p in props)
beds = [p['bed'] for p in props]; m2 = [p.get('m2') for p in props]; pr = [p['price'] for p in props]
rows = "".join(f"<tr><td>{p['short']}</td><td>{p['zone'].split(' · ')[0]}</td><td>{p['bed']}</td>{f"<td>{p['bath']}</td>" if SHOW_BATH else ''}<td>{p.get('m2') or '—'}</td><td>{money(p['price'])}</td></tr>" for p in props)

extra_css = """
  .prop-badge { z-index: 12; }
  .carousel { position: absolute; inset: 0; min-height: 0; }
  .prop-image { min-height: 460px; }
  .like-btn { display: flex; align-items: center; justify-content: center; gap: 10px; margin-top: 16px; background: var(--gold); color: var(--btn-hover-text); border: 1px solid var(--gold); padding: 14px 26px; font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; text-decoration: none; font-weight: 500; transition: opacity 0.2s, transform 0.2s; }
  .like-btn:hover { opacity: 0.88; }
  .like-btn.sent { background: transparent; color: var(--gold); }
  .like-hint { font-size: 0.68rem; color: var(--text-muted); margin-top: 8px; text-align: center; letter-spacing: 0.02em; }
  @media (max-width: 768px) { .prop-image { min-height: 300px; } }
  #print-btn { right: 86px !important; left: auto !important; }
  .new-flag { position: absolute; top: 18px; right: 18px; z-index: 12; background: #F89D23; color: #fff; font-size: 0.66rem; font-weight: 800; letter-spacing: 0.18em; padding: 7px 14px; border-radius: 999px; box-shadow: 0 2px 10px rgba(17,32,63,0.25); }
  .added-line { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 12px; font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #6E7E95; }
  .added-new { background: #F89D23; color: #fff; font-weight: 800; letter-spacing: 0.16em; font-size: 0.6rem; padding: 3px 9px; border-radius: 999px; }
  .print-only { display: none; }

  /* ── PRINT / SAVE AS PDF: cover page, 3 properties per page, then comparison + contact ── */
  @page { size: letter; margin: 0.35in; }
  @media print {
    * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    body { font-size: 9pt; }
    #lang-toggle, #print-btn, #fav-counter, #fav-view, .scroll-indicator,
    .carousel-btn, .carousel-dots, .carousel-count, .save-btn, .like-hint,
    #properties > .section-label, #properties > .section-heading { display: none !important; }
    .print-only { display: block !important; }
    #hero { height: 10.25in !important; min-height: 0 !important; break-after: page; page-break-after: always; }
    #properties { padding: 0 !important; margin: 0 !important; max-width: none !important; }
    .property-card, .property-card.even {
      flex-direction: row !important; height: 3.3in; min-height: 0 !important; margin: 0 0 0.12in 0 !important;
      box-shadow: none !important; transform: none !important; break-inside: avoid; page-break-inside: avoid; }
    .property-card.print-break { break-after: page; page-break-after: always; margin-bottom: 0 !important; }
    .prop-image { flex: 0 0 42% !important; min-height: 0 !important; height: 100%; }
    .carousel { position: absolute !important; inset: 0; min-height: 0 !important; height: 100% !important; }
    .carousel-track { transform: none !important; transition: none !important; height: 100%; }
    .carousel-slide { display: none; height: 100%; }
    .carousel-slide:first-child { display: block; }
    .new-flag { font-size: 6.5pt !important; padding: 3px 8px !important; top: 10px !important; right: 10px !important; }
    .added-line { font-size: 6pt !important; margin-top: 4px !important; gap: 5px !important; }
    .added-new { font-size: 5.5pt !important; padding: 1px 6px !important; }
    .prop-badge { font-size: 6.5pt !important; padding: 3px 8px !important; top: 10px !important; left: 10px !important; }
    .prop-text { flex: 1 1 58% !important; padding: 0.16in 0.24in !important; justify-content: center; overflow: hidden; }
    .prop-number { font-size: 6.5pt !important; margin: 0 0 2px !important; }
    .prop-name { font-size: 14pt !important; line-height: 1.12 !important; margin: 0 0 2px !important; }
    .prop-location { font-size: 6.5pt !important; margin: 0 0 6px !important; }
    .prop-stats { gap: 14px !important; margin: 0 0 4px !important; }
    .prop-stat-num { font-size: 12pt !important; }
    .prop-stat-label { font-size: 5.5pt !important; }
    .prop-divider { margin: 4px 0 !important; }
    .prop-features { margin: 0 0 4px !important; padding-left: 12px; }
    .prop-features li { font-size: 7pt !important; line-height: 1.3 !important; margin: 0 !important; padding: 0 0 0 10px !important; }
    .prop-features li::before { margin-top: 3px !important; }
    .prop-price-block { margin: 2px 0 0 !important; padding: 4px 0 0 !important; }
    .prop-price-current { font-size: 13pt !important; margin: 0 !important; }
    .prop-price-current span { font-size: 6pt !important; margin-bottom: 1px !important; }
    .prop-price-note { font-size: 6.5pt !important; line-height: 1.3 !important; margin: 1px 0 0 !important; }
    .prop-buttons { margin-top: 5px !important; gap: 6px !important; }
    .prop-text .btn, .prop-buttons .btn { padding: 4px 10px !important; font-size: 6.5pt !important; margin-top: 5px !important; }
    .prop-buttons .btn { margin-top: 0 !important; }
    .prop-text .like-btn, .like-btn { padding: 6px 14px !important; margin-top: 6px !important; font-size: 7pt !important; }
    .like-btn svg { width: 11px; height: 11px; }
    #table-section { break-before: page; page-break-before: always; padding: 0.3in 0 0.2in !important; }
    #cta { padding: 0.35in 0.3in !important; break-inside: avoid; }
    .print-note { font-size: 7pt; text-align: center; margin: 0.12in 0 0; opacity: 0.75; }
  }
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
{FONTS}{("\n" + HEAD_EXTRA) if HEAD_EXTRA else ""}
<style>{style}{extra_css}</style>
</head>
<body>

<button id="fav-counter" onclick="showFavorites()"></button>

<div id="main-view">
<button id="lang-toggle" onclick="toggleLang()"><span id="lang-label">ES</span></button>
<button id="print-btn" onclick="printPdf()" data-en="PDF ↓" data-es="PDF ↓" title="Print / Save as PDF">PDF ↓</button>

<div id="hero">
  <div class="hero-bg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    {HERO_BRAND}
    <h1 class="hero-title" data-en="Your Property Options<br>in {CITY}" data-es="Tus Opciones de Propiedades<br>en {CITY}">Your Property Options<br>in {CITY}</h1>
    <p class="hero-subtitle">{SUB}</p>
  </div>
  <div class="hero-stats">
    <div class="hero-stat"><span class="hero-stat-number">{len(props)}</span><span class="hero-stat-label" data-en="PROPERTIES" data-es="PROPIEDADES">PROPERTIES</span></div>
    <div class="hero-stat"><span class="hero-stat-number">{min(beds) if min(beds)==max(beds) else f'{min(beds)}–{max(beds)}'}</span><span class="hero-stat-label" data-en="BEDROOMS" data-es="RECÁMARAS">BEDROOMS</span></div>
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
          {'<th data-en="BATH" data-es="BAÑOS">BATH</th>' if SHOW_BATH else ''}
          <th>M²</th>
          <th data-en="PRICE USD" data-es="PRECIO USD">PRICE USD</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  </div>
</div>

<div id="cta">
  {CTA_BRAND}
  <h2 class="cta-heading" data-en="Did any catch your eye?" data-es="¿Alguna te llamó la atención?">Did any catch your eye?</h2>
  <p class="cta-sub" data-en="Schedule a visit or request more information" data-es="Coordina una visita o solicita más información">Schedule a visit or request more information</p>
  <a href="https://wa.me/{WA}?text={urllib.parse.quote_plus("Hi Rainier, it's " + CLIENT + ". I saw the " + CITY + " properties. Can we schedule a visit?")}" target="_blank" class="cta-btn">
    {WA_SVG}
    <span data-en="SCHEDULE A VISIT" data-es="AGENDAR VISITA">SCHEDULE A VISIT</span>
  </a>
  <p class="cta-address">{FOOT} &nbsp;·&nbsp; +1 646 342 4105</p>
  <p class="print-only print-note">Tap any button in this PDF — PHOTOS, INQUIRE, I LIKE THIS ONE — to open it. Live page: {SITE_URL}{cfg.get('slug', CLIENT.lower())}/</p>
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

  // ── PRINT / SAVE AS PDF (3 properties per page via print CSS) ──
  function printPdf() {
    document.querySelectorAll('img[loading="lazy"]').forEach(function (im) { im.loading = 'eager'; });
    document.querySelectorAll('.carousel').forEach(function (c) { try { carouselState[c.id] = 0; updateCarousel(c.id, c.querySelectorAll('.carousel-slide').length); } catch (e) {} });
    var t = document.title;
    document.title = 'Mycasa Property Options - ' + CLIENT_NAME + ' - __CITY__';
    setTimeout(function () { window.print(); document.title = t; }, 300);
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
