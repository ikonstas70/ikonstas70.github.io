#!/usr/bin/env python3
"""Builds the Portfolio section (/portfolio/*) and /license from page bodies in tools/portfolio/*.html.

Each body file starts with a JSON front-matter line:
  <!--{"slug": "...", "title": "...", "desc": "...", "tag": "...", "image": "..."}-->
Run: python3 tools/build_portfolio.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'tools' / 'portfolio'
SITE = 'https://ikonstas70.github.io'
SHARE = '/portfolio/share.jpg'   # 1200x630 social preview used by every page
BANNER = '''    <img src="/portfolio/banner.jpg" width="1400" height="280" loading="eager" alt="Close-up of an integrated circuit beside source code" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px;margin:0 0 22px">
'''

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<link rel="canonical" href="{url}">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Konstas Engineering Notes</title>
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta name="description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
{og_image}<meta name="twitter:card" content="{card}">
<link rel="stylesheet" href="/style.css">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-BZK50T0JFT"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","G-BZK50T0JFT");</script>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<div class="wrap">
  <header class="site">
    <img src="/ioannis-portrait.jpg" alt="Ioannis Konstas" style="float:left;width:72px;height:72px;object-fit:cover;border-radius:50%;border:1px solid hsl(43 45% 56% / .85);box-shadow:0 0 0 4px hsl(43 45% 56% / .12), 0 3px 14px rgb(0 0 0 / .5);margin:0 18px 6px 0;">
    <a class="brand" href="/">Konstas<em>.</em>Engineering Notes</a>
    <div class="tagline">Networking &middot; Cybersecurity &middot; Infrastructure</div>
    <div style="clear:both;"></div>
    <div class="rule"></div>
    <nav class="top">
      <a href="/">Articles</a>
      <a href="/portfolio/">Portfolio</a>
      <a href="/awareness/">Security Awareness</a>
      <a href="/data-science/">Data Science</a>
      <a href="/readings">Readings</a>
      <a href="/index-az">Index</a>
      <a href="/search">Search</a>
      <a href="/articles/sentinel-platform">SENTINEL</a>
      <a href="/stack">Stack</a>
      <a href="/about">About</a>
    </nav>
  </header>

  <main>
'''

FOOT = '''  </main>

  <footer class="site">
    <p>&copy; 2026 Ioannis Alexander Konstas. All rights reserved. Code samples are released under the <a href="/license">MIT License</a>. &middot; <a href="https://github.com/ikonstas70">github.com/ikonstas70</a></p>
  </footer>
</div>
</body>
</html>
'''


def build():
    pages = []
    for f in sorted(SRC.glob('*.html')):
        raw = f.read_text()
        m = re.match(r'<!--(\{.*?\})-->\n', raw, re.S)
        meta, body = json.loads(m.group(1)), raw[m.end():]
        slug = meta['slug']
        url = f"{SITE}/{slug}" if slug else SITE + '/'
        img = SHARE
        ld = {"@context": "https://schema.org", "@type": meta.get('type', 'TechArticle'), "headline": meta['title'],
              "author": {"@type": "Person", "name": "Ioannis Alexander Konstas", "alternateName": "Ioannis Konstas", "url": f"{SITE}/about"},
              "datePublished": "2026-11-02", "license": "https://opensource.org/licenses/MIT", "copyrightHolder": "Ioannis Alexander Konstas"}
        if img: ld["image"] = SITE + img
        html = HEAD.format(url=url, title=meta['title'], desc=meta['desc'], card='summary_large_image' if img else 'summary',
                           og_image=f'<meta property="og:image" content="{SITE}{img}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n' if img else '',
                           ld=json.dumps(ld, ensure_ascii=False)) + (BANNER if meta.get('banner', True) else '') + body + FOOT
        out = ROOT / (slug + '.html' if not slug.endswith('/') else slug + 'index.html')
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        pages.append((slug, meta))
        print('built', out.relative_to(ROOT))
    return pages


if __name__ == '__main__':
    build()
