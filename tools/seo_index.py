#!/usr/bin/env python3
"""Rebuild search-index.json + sitemap.xml and add SEO meta to every indexable page.

Covers this site plus every public GitHub Pages project site and public repo
of ikonstas70. Existing hand-written search entries are kept as-is.

    python3 tools/seo_index.py            # rebuild + inject meta into local pages
    python3 tools/seo_index.py --meta DIR # only inject meta into another repo's HTML
"""
import html, json, os, re, subprocess, sys, urllib.request
from datetime import date

USER = "ikonstas70"
HOST = f"https://{USER}.github.io"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROBOTS_MAX = '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">'
SKIP_FILES = {"404.html"}
SKIP_REPOS = {f"{USER}.github.io"}


def disallowed():
    rules = []
    for line in open(os.path.join(ROOT, "robots.txt")):
        if line.lower().startswith("disallow:"):
            p = line.split(":", 1)[1].strip()
            if p:
                rules.append(p)
    return rules


def text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def meta(t, attr, name):
    m = re.search(rf'<meta\s+{attr}="{re.escape(name)}"\s+content="([^"]*)"', t, re.I) or \
        re.search(rf'<meta\s+content="([^"]*)"\s+{attr}="{re.escape(name)}"', t, re.I)
    return html.unescape(m.group(1)).strip() if m else ""


def first_para(t):
    body = t.split("<main", 1)[-1]
    for p in re.findall(r"<p(?![^>]*class=\"meta)[^>]*>(.*?)</p>", body, re.S | re.I):
        s = text(p)
        if len(s) > 60:
            return s if len(s) <= 200 else s[:197].rsplit(" ", 1)[0] + "…"
    return ""


def bylinish(s):
    return not s or (len(s) < 90 and ("·" in s or "Ioannis" in s))


def page_info(t):
    title = meta(t, "property", "og:title") or text((re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S | re.I) or [None, ""])[1]) \
        or text((re.search(r"<title>(.*?)</title>", t, re.S | re.I) or [None, ""])[1])
    desc = meta(t, "name", "description") or meta(t, "property", "og:description")
    if bylinish(desc):
        desc = first_para(t)
    tag = text((re.search(r'<span class="tag">(.*?)</span>', t, re.S) or [None, ""])[1])
    canon = (re.search(r'<link rel="canonical" href="([^"]+)"', t) or [None, ""])[1]
    return title, desc, tag, canon


def excluded(t):
    return bool(re.search(r'name="robots"[^>]*noindex', t, re.I) or 'http-equiv="refresh"' in t)


def inject_meta(path, desc):
    """Add a meta description and the max-preview robots tag where missing."""
    t = open(path, encoding="utf-8", errors="ignore").read()
    if excluded(t) or "<title>" not in t:
        return False
    orig = t
    add = []
    if not meta(t, "name", "description") and desc:
        add.append(f'<meta name="description" content="{html.escape(desc, quote=True)}">')
    if re.search(r'<meta name="robots"', t):
        t = re.sub(r'<meta name="robots" content="index, follow[^"]*">', ROBOTS_MAX, t)
    else:
        add.append(ROBOTS_MAX)
    if add:
        t = re.sub(r"(</title>)", r"\1\n" + "\n".join(add).replace("\\", r"\\"), t, count=1)
    if t != orig:
        open(path, "w", encoding="utf-8").write(t)
        return True
    return False


def git_date(repo, rel):
    out = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cs", "--", rel],
                         capture_output=True, text=True).stdout.strip()
    return out or date.today().isoformat()


def local_pages():
    rules = disallowed()
    pages = []
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "tools"]
        for f in files:
            if not f.endswith(".html") or f in SKIP_FILES or f.startswith("google"):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, ROOT)
            url = "/" + (rel[:-len("index.html")] if f == "index.html" else rel[:-5])
            if any(url.startswith(r) for r in rules):
                continue
            t = open(full, encoding="utf-8", errors="ignore").read()
            if excluded(t):
                continue
            title, desc, tag, canon = page_info(t)
            if canon.startswith(HOST):
                url = canon[len(HOST):] or "/"
            pages.append(dict(full=full, rel=rel, url=url, title=title, desc=desc, tag=tag,
                              lastmod=git_date(ROOT, rel)))
    local_pages.cache = pages
    return pages


def first_md_line(md):
    for line in md.splitlines():
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line).strip("#*➜ -")
        s = text(s.replace("**", ""))
        if len(s) > 40 and not s.startswith(("!", "<", "|")):
            return s[:200]
    return ""


def gh(path):
    return json.loads(subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True).stdout)


def github_items():
    """Public Pages project sites (each HTML page) and public repos without Pages."""
    repos = json.loads(subprocess.run(
        ["gh", "repo", "list", USER, "-L", "300", "--visibility", "public", "--json",
         "name,description,pushedAt,isFork"], capture_output=True, text=True, check=True).stdout)
    rules = disallowed()
    pages, entries = [], []
    for r in repos:
        name = r["name"]
        if name in SKIP_REPOS or r["isFork"] or any(f"/{name}/".startswith(x) for x in rules):
            continue
        try:
            gh(f"repos/{USER}/{name}/pages")
            has_pages = True
        except subprocess.CalledProcessError:
            has_pages = False
        repo_date = r["pushedAt"][:10]
        if not has_pages:
            if os.path.isdir(os.path.join(ROOT, name)):
                continue
            entries.append(dict(title=f"{name} (GitHub repository)", desc=r["description"] or name,
                                section="GitHub", tag="Repository", url=f"https://github.com/{USER}/{name}"))
            continue
        tree = gh(f"repos/{USER}/{name}/git/trees/HEAD?recursive=1")["tree"]
        files = [x["path"] for x in tree if x["path"].endswith(".html")]
        if any(p["url"] == f"/{name}/" for p in local_pages.cache):
            continue  # already served from this site's own folder
        if not files and any(x["path"] == "README.md" for x in tree):
            files = ["README.md"]
        for path in files:
            raw = urllib.request.urlopen(
                f"https://raw.githubusercontent.com/{USER}/{name}/HEAD/{path}").read().decode("utf-8", "ignore")
            if path.endswith(".md"):
                title, desc, url = r["description"] or name, first_md_line(raw), f"/{name}/"
            else:
                if excluded(raw):
                    continue
                title, desc, _, _ = page_info(raw)
                url = f"/{name}/" + ("" if path == "index.html" else
                                     path[:-len("index.html")] if path.endswith("/index.html") else path)
            pages.append(dict(url=url, lastmod=repo_date))
            entries.append(dict(title=title or name, desc=desc or (r["description"] or ""),
                                section="GitHub", tag=name, url=url))
    return pages, entries


def section_of(url):
    for prefix, name in (("/articles/", "Articles"), ("/awareness/", "Security Awareness"),
                         ("/data-science/", "Data Science"), ("/readings", "Readings")):
        if url.startswith(prefix):
            return name
    return "Page"


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--meta":
        n = 0
        for dirpath, dirs, files in os.walk(sys.argv[2]):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if f.endswith(".html") and f not in SKIP_FILES:
                    p = os.path.join(dirpath, f)
                    n += inject_meta(p, page_info(open(p, errors="ignore").read())[1])
        print(f"meta updated in {n} files")
        return

    idx_path = os.path.join(ROOT, "search-index.json")
    old = {e["url"]: e for e in json.load(open(idx_path)) if e.get("section") != "GitHub"}
    local = local_pages()
    index, seen = [], set()
    for p in local:
        if p["url"] in ("/search", "/404"):
            continue
        e = old.get(p["url"])
        if e and bylinish(e.get("desc")):
            e["desc"] = p["desc"]
        e = e or dict(title=p["title"], desc=p["desc"], section=section_of(p["url"]),
                                     tag=p["tag"] or section_of(p["url"]), url=p["url"])
        index.append(e)
        seen.add(p["url"])
    gh_pages, gh_entries = github_items()
    index += gh_entries
    index.sort(key=lambda e: e["title"].lower())
    json.dump(index, open(idx_path, "w"), ensure_ascii=False)

    changed = sum(inject_meta(p["full"], (old.get(p["url"]) or {}).get("desc") or p["desc"]) for p in local)

    urls = sorted({(p["url"], p["lastmod"]) for p in local + gh_pages}, key=lambda x: (x[0] != "/", x[0]))
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u, d in urls:
            f.write(f"  <url><loc>{html.escape(HOST + u)}</loc><lastmod>{d}</lastmod></url>\n")
        f.write("</urlset>\n")
    print(f"search index: {len(index)} entries ({len(gh_entries)} GitHub)")
    print(f"sitemap: {len(urls)} URLs")
    print(f"meta updated in {changed} local pages")


if __name__ == "__main__":
    main()
