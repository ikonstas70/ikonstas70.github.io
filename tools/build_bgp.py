#!/usr/bin/env python3
"""Builds the BGP series pages under /bgp/ from the parts below, using bgp/index.html's head, header and footer.
    python3 tools/build_bgp.py
Chapter 1 is published in five short parts (bgp/ch01-*.html) with previous/next navigation.
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://ikonstas70.github.io'
TEMPLATE = (ROOT / 'bgp/index.html').read_text()
SERIES = "Special Topics in BGP"
CH = "Chapter 1: One Login, the Whole Internet"

def table(head, rows, num=()):
    th = ''.join(f'<th>{h}</th>' for h in head)
    trs = ''.join('<tr>' + ''.join(f'<td{" style=\"text-align:right\"" if i in num else ""}>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def callout(text, kind='gold'):
    color = {'gold': 'var(--accent)', 'warn': 'hsl(36 70% 58%)'}[kind]
    return (f'<div style="border:1px solid hsl(43 45% 56% / .30);border-left:3px solid {color};background:hsl(0 0% 6%);'
            f'border-radius:6px;padding:12px 16px;margin:18px 0">{text}</div>')

PARTS = [
 ('ch01-1-the-session', 'The Session', 'Log in to a public route collector that holds the routing tables of more than twenty of the world\'s largest networks.', f'''
<blockquote>Most engineers configure BGP. Few ever look at the Internet through it. In this chapter we log in to a router that holds the routing table of more than twenty of the world's largest networks at once, read a single command's output line by line, and see how much it tells us: about the Internet, about the networks that run it, and about our own exposure.</blockquote>

<h2>The question</h2>
<p>How big is the Internet's routing table right now? How fast does it change? Which carriers filter what? And what can anyone, attacker or defender, learn about a network without ever touching it?</p>
<p>One free, public login answers all of it.</p>

<h2>Route Views</h2>
<p><strong>Route Views</strong> is a project of the University of Oregon. Its routers peer with networks around the world and collect their full routing tables, purely so engineers and researchers can see the Internet from many vantage points. It is public by design, and it is intended exactly for this.</p>

<figure style="margin:22px 0">
<video controls playsinline preload="metadata" poster="/bgp/ch01/poster.jpg" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px;background:#000">
  <source src="/bgp/ch01/route-views-session.mp4" type="video/mp4">
</video>
<figcaption style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">The whole session in 19 seconds: login, then <code>show ip bgp summary</code>.</figcaption>
</figure>

<h2>Log in yourself</h2>
<pre><code>$ telnet route-views.routeviews.org
Username: rviews
route-views&gt; show ip bgp summary</code></pre>
<p>That is the entire setup. No account, no VPN, no API key.</p>

<figure style="margin:22px 0"><img src="/bgp/ch01/bgp-summary.jpg" alt="Output of show ip bgp summary on route-views" loading="lazy" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px">
<figcaption style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">The output we read in the next four parts.</figcaption></figure>
'''),
 ('ch01-2-the-header', 'The Header', 'Eleven lines that give the size of the Internet, its rate of change, its security posture and the cost of carrying it.', f'''
<p>The first block of <code>show ip bgp summary</code> describes the router and its BGP table. Every line carries meaning.</p>
{table(['Line', 'Value', 'What it tells you'], [
 ['<code>BGP router identifier 128.223.51.103, local AS number 6447</code>', 'AS 6447', 'Route Views\' own autonomous system. A <strong>collector</strong>: it receives routes and announces none.'],
 ['<code>BGP table version is 1142409165</code>', '<strong>1.14 billion</strong>', 'Increments on every best-path change since the process started. This is the Internet\'s <strong>churn</strong>, and it never stops.'],
 ['<code>Path RPKI states: 6502331 valid, 13437858 not found, 17810 invalid</code>', '32.6% / 67.3% / 0.09%', 'Origin validation of every <strong>path</strong> (the three numbers add up exactly to the path count). A third of paths are cryptographically proven, two thirds have no ROA, and <strong>17,810 contradict a published ROA</strong>: leaks, hijacks or mistakes, visible because a collector does not filter.'],
 ['<code>916896 network entries</code>', '<strong>916,896</strong>', 'Unique IPv4 prefixes: the size of the global IPv4 table from this vantage point.'],
 ['<code>19957999 path entries</code>', '≈ <strong>21.8 per prefix</strong>', 'One copy of each prefix per full-table peer.'],
 ['<code>3265932/154547 BGP path/bestpath attribute entries</code>', '3.27 M / 155 k', 'Unique attribute sets. Twenty million paths share only 3.3 million sets, about six paths each. That sharing is why a full table fits in memory.'],
 ['<code>3013798 BGP AS-PATH entries</code>', '<strong>3.0 million</strong>', 'Distinct routes through the Internet\'s graph.'],
 ['<code>174831 BGP community entries</code>', '174,831', 'Distinct community sets: the policy tags networks attach to routes.'],
 ['<code>BGP using 3610266520 total bytes of memory</code>', '<strong>3.61 GB</strong>', 'Path entries 2.39 GB, attributes 0.81 GB. About 3.9 KB per prefix at 22 views: why full-table routers are sized the way they are.'],
 ['<code>BGP activity … 868168614/845632564 paths</code>', '<strong>868 million</strong>', 'Path entries created and freed since start: the true workload of a full-table router.'],
])}
{callout('<strong>Takeaway.</strong> In eleven lines you have the size of the Internet, its rate of change, its security posture and the hardware cost of carrying it.')}
'''),
 ('ch01-3-the-neighbors', 'The Neighbors', 'Who feeds the collector: 22 full tables from five continents, and the partial feeds that tell their own story.', f'''
<p>Below the header, each line is one BGP session. The columns that matter:</p>
{table(['Column', 'Meaning'], [
 ['<code>AS</code>', 'The neighbor\'s autonomous system'],
 ['<code>MsgRcvd</code> / <code>MsgSent</code>', 'BGP messages received and sent on this session'],
 ['<code>TblVer</code>', 'The table version this neighbor has been brought up to'],
 ['<code>InQ</code> / <code>OutQ</code>', 'Messages waiting to be processed or sent (backlog)'],
 ['<code>Up/Down</code>', 'How long the session has been in its current state'],
 ['<code>State/PfxRcd</code>', 'A number means Established, with that many prefixes; a word means not established'],
])}
<h2>Full tables</h2>
<p>27 sessions are Established, and <strong>22 deliver a full table</strong> of more than 840,000 prefixes. Operator names are from public registry data.</p>
{table(['Neighbor', 'AS', 'Network', 'Prefixes', 'Up'], [
 ['64.71.137.241', '6939', 'Hurricane Electric', '869,346', '34w3d'],
 ['4.68.4.46', '3356', 'Lumen (Level 3)', '845,477', '5d13h'],
 ['12.0.1.63', '7018', 'AT&amp;T', '846,376', '5d13h'],
 ['137.39.3.55', '701', 'Verizon', '847,301', '5d13h'],
 ['208.51.134.254', '3549', 'Lumen (ex-Global Crossing)', '846,350', '5d13h'],
 ['89.149.178.10', '3257', 'GTT', '846,817', '39w3d'],
 ['217.192.89.50', '3303', 'Swisscom', '876,786', '35w5d'],
 ['202.232.0.2', '2497', 'IIJ, Japan', '860,369', '24w2d'],
 ['203.62.252.83', '1221', 'Telstra, Australia', '856,424', '4w6d'],
 ['154.11.12.212', '852', 'TELUS, Canada', '848,162', '6w3d'],
 ['193.0.0.56', '3333', 'RIPE NCC', '862,740', '5w6d'],
 ['132.198.255.253', '1351', 'University of Vermont', '880,273', '25w4d'],
 ['209.124.176.223', '101', 'University of Washington', '850,407', '4w5d'],
], num=(3,))}
<h2>Partial feeds</h2>
<p>Networks that send only part of the table are just as informative: they show what each one chooses to export.</p>
{table(['Neighbor', 'AS', 'Prefixes', 'Reading'], [
 ['144.228.241.130', '1239 (Sprint)', '63,381', 'Customer routes only'],
 ['198.32.252.33', '20080 (AMPATH, Miami)', '19,714', 'Research and education, Latin America'],
 ['208.74.64.40', '19214', '350,114', 'Partial view'],
 ['203.181.248.168', '7660 (APAN, Japan)', '710,120', 'Near-full research view'],
 ['202.93.8.242', '24441', '4,505', 'Regional routes'],
], num=(2,))}
'''),
 ('ch01-4-what-the-numbers-reveal', 'What the Numbers Reveal', 'Five readings an experienced engineer takes from the neighbor table, and the sessions that are down.', f'''
<h2>1. This is a collector, and the counters prove it</h2>
<p>Hurricane Electric sent <strong>95.3 million</strong> messages in 34 weeks; the collector sent back 381,931. Over 241 days that is one message about every 55 seconds: keepalives and nothing else.</p>
<h2>2. Churn has a fingerprint per network</h2>
<p>Divide <code>MsgRcvd</code> by uptime:</p>
{table(['Peer', 'Updates per day', 'Per second'], [['Hurricane Electric (6939)', '≈ 395,000', '≈ 4.6'], ['Coloclue (8283)', '≈ 777,000', '≈ 9.0'], ['GTT (3257)', '≈ 314,000', '≈ 3.6']], num=(1, 2))}
<h2>3. Correlated events are visible</h2>
<p>AS 3356, 7018, 701 and 3549 have all been up for exactly <strong>5d13h</strong>. Four of the largest networks did not fail independently in the same minute; something they share with the collector did: maintenance, a reboot, a common path. Spotting this is how operators correlate outages.</p>
<h2>4. Prefix counts expose policy</h2>
<p>Full feeds range from 845,477 to 880,273 prefixes. That 35,000-prefix spread is each network's filtering and export policy made visible: peering-rich networks and those that pass more-specific routes send more, while the large Tier-1 transit networks cluster tightly at 845k to 847k, consistent with strict filtering. You are reading routing policy from the outside.</p>
<h2>5. The collector is healthy</h2>
<p>Every Established neighbor shows <code>TblVer 1142409035</code> with <code>InQ</code> and <code>OutQ</code> at 0: no backlog, all in sync.</p>
<h2>The sessions that are not up</h2>
{table(['State', 'Meaning', 'Examples'], [
 ['<code>Active</code>', 'The router keeps trying to open TCP port 179; the far side does not answer (configuration removed, or a filter)', 'DigitalOcean (14061) ×4, Tata (6453), NTT (2914) ×2, Orange (5511), Microsoft (8075), LINX (5459)'],
 ['<code>Idle</code>', 'Not even trying: administratively down, a maximum-prefix limit tripped, or no route to the neighbor', '6539, 58511, 58901, RCN (6079) ×2'],
 ['<code>never</code>', 'Has not come up since the counters were last reset', 'most of the above'],
 ['a time with <code>Active</code>', 'Was up, and dropped that long ago', 'KPN (286) 13w3d, AS 3277, AS 1403'],
])}
<p>About half of the 57 configured peers are not exchanging routes. For a collector that is normal: contributors come and go, and the configuration waits for them.</p>
'''),
 ('ch01-5-what-is-exposed', 'What Is Exposed, and Your Turn', 'What a public BGP view reveals about any network, how attackers and defenders use it, and exercises to try yourself.', f'''
<p>Everything in this chapter is shared voluntarily. It is still a great deal of information, which is exactly why it matters.</p>
{table(['Exposed', 'From this output', 'Why it matters'], [
 ['Carrier BGP router addresses', '4.68.4.46, 12.0.1.63, 64.71.137.241 …', 'Real edge-router interfaces on TCP 179, reachable because collector sessions are multihop: a target for session attacks and floods'],
 ['Who participates', '22 full-table providers on five continents', 'A map of the vantage points'],
 ['Timing of events', 'the 5d13h reset cluster', 'When something happened, and what shares fate'],
 ['Each network\'s churn', 'updates per second', 'How busy or unstable a network\'s routing is'],
 ['Filtering policy', '845k vs 880k; Sprint 63k', 'Who drops invalid or more-specific routes, who exports customers only'],
 ['Global security posture', '67% of paths with no ROA, 17,810 invalid', 'Which address space is unprotected, and live leaks or hijacks'],
])}
<p>One command deeper, <code>show ip bgp &lt;prefix&gt;</code> reveals any organization's <strong>upstream providers</strong> (and whether it is single-homed), its <strong>peering relationships</strong>, its <strong>traffic engineering</strong> (prepending shows primary and backup), its <strong>communities</strong> (often city, PoP and customer type, and blackhole tags that reveal a DDoS in progress), its <strong>more-specific</strong> routes, and its <strong>RPKI</strong> status.</p>
<p>What is <strong>not</strong> exposed: configurations, passwords, keys, internal routing (OSPF, IS-IS), private addressing, traffic contents or volumes. BGP carries reachability only.</p>
<h2>Reconnaissance versus defense</h2>
{table(['An attacker uses it to…', 'You defend by…'], [
 ['Find a single upstream to flood', 'Multi-homing; DDoS scrubbing'],
 ['Find prefixes with no ROA to hijack', 'Publishing ROAs for every prefix; asking providers to filter invalid routes'],
 ['Find BGP session addresses', 'TCP-AO or MD5, GTSM (TTL security), port-179 filters, control-plane policing, maximum-prefix limits'],
 ['Read communities to map PoPs', 'Stripping internal communities at the edge'],
 ['Announce your space and watch it spread', 'Monitoring your own prefixes on public collectors, with alerting'],
])}
{callout('<strong>The defender\'s lesson.</strong> The same public data attackers use for reconnaissance is the best free early-warning system you have. If someone hijacks or leaks your address space, it appears on these collectors within seconds.')}
<h2>Your turn</h2>
<p>Log in (<code>telnet route-views.routeviews.org</code>, username <code>rviews</code>) and try:</p>
{table(['Command', 'Look for'], [
 ['<code>show ip bgp 8.8.8.8</code>', 'How many paths reach Google DNS, through whom, and with which communities'],
 ['<code>show ip bgp regexp _15169$</code>', 'Every prefix Google originates'],
 ['<code>show ip bgp regexp ^6939_</code>', 'The table as Hurricane Electric sees it'],
 ['<code>show ip bgp 1.1.1.0/24 longer-prefixes</code>', 'Cloudflare\'s prefix and any more-specifics: the shape a hijack takes'],
 ['<code>show ip bgp &lt;your own prefix&gt;</code>', '<strong>Your</strong> network as the world sees it: upstreams, prepends, communities, RPKI'],
])}
<p><strong>Exercise.</strong> Pick three Established neighbors and compute their updates per second. Which is the noisiest, and why might that be?</p>
<h2>The takeaway</h2>
<p>From one public login and one command you measured the Internet (917,000 IPv4 prefixes, 20 million paths, 3.6 GB of state), its churn (over a billion best-path changes), its security (a third of paths RPKI-valid, 17,810 invalid in plain sight) and the filtering policy of the world's largest carriers. Next: <a href="/bgp/ch02-1-summary-and-findings" style="color:var(--accent)">Chapter 2, a single path read attribute by attribute</a>.</p>
'''),
]

def page(i, slug, title, desc, body):
    n = len(PARTS)
    url = f'{SITE}/bgp/{slug}'
    full = f'{CH} · Part {i} of {n}: {title}'
    head_end = TEMPLATE.index('</head>'); head, rest = TEMPLATE[:head_end], TEMPLATE[head_end:]
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title)} — {SERIES}, Chapter 1 — Konstas Engineering Notes</title>', head)
    for k in ('name="description"', 'property="og:description"'):
        head = re.sub(rf'(<meta {k} content=")[^"]*(")', lambda m: m.group(1) + html.escape(desc) + m.group(2), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{url}\2', head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1) + html.escape(f'{SERIES} · {full}') + m.group(2), head)
    head = re.sub(r'(<meta property="og:type" content=")[^"]*(")', r'\1article\2', head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>',
        '<script type="application/ld+json">{"@context":"https://schema.org","@type":"TechArticle","headline":' + repr(full).replace("'", '"') +
        ',"isPartOf":{"@type":"CreativeWorkSeries","name":"Special Topics in BGP","url":"https://ikonstas70.github.io/bgp/"},'
        '"author":{"@type":"Person","name":"Ioannis Alexander Konstas","url":"https://ikonstas70.github.io/about"},"datePublished":"2026-11-03","url":"' + url + '"}</script>',
        head, flags=re.S)
    start = rest.index('<main>'); end = rest.index('</main>') + len('</main>')
    pre, post = rest[:start], rest[end:]
    prev_link = f'<a href="/bgp/{PARTS[i-2][0]}" style="color:var(--accent);text-decoration:none">&larr; Part {i-1}: {PARTS[i-2][1]}</a>' if i > 1 else '<a href="/bgp/" style="color:var(--accent);text-decoration:none">&larr; Series overview</a>'
    next_link = f'<a href="/bgp/{PARTS[i][0]}" style="color:var(--accent);text-decoration:none">Part {i+1}: {PARTS[i][1]} &rarr;</a>' if i < n else '<a href="/bgp/ch02-1-summary-and-findings" style="color:var(--accent);text-decoration:none">Chapter 2: Reading a Path &rarr;</a>'
    nav = (f'<div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:34px 0 14px;padding-top:14px;'
           f'border-top:1px solid hsl(43 45% 56% / .25);font-size:.92rem">{prev_link}<span>{next_link}</span></div>')
    parts_list = ''.join(f'<li>{"<strong>" if j == i else ""}<a href="/bgp/{s}" style="color:{"var(--accent)" if j == i else "var(--fg-dim)"};text-decoration:none">Part {j}: {t}</a>{"</strong>" if j == i else ""}</li>'
                         for j, (s, t, _, _) in enumerate(PARTS, 1))
    pill = 'display:inline-block;margin:4px 6px 4px 0;padding:7px 14px;border:1px solid hsl(43 45% 56% / .55);border-radius:999px;color:var(--accent);text-decoration:none;font-size:.88rem'
    from urllib.parse import quote
    share = (f'<div style="margin:18px 0 6px"><a href="https://github.com/ikonstas70" style="{pill};background:hsl(43 45% 56% / .12)" rel="noopener">Follow on GitHub</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url, safe="")}" style="{pill}" rel="noopener" target="_blank">Share on LinkedIn</a>'
             f'<a href="https://twitter.com/intent/tweet?url={quote(url, safe="")}&amp;text={quote(SERIES + ": " + title)}" style="{pill}" rel="noopener" target="_blank">Share on X</a></div>')
    main = f'''<main>
    <span class="tag">{SERIES} &middot; Chapter 1 &middot; Part {i} of {n}</span>
    <h1>{html.escape(title)}</h1>
    <p class="meta">{CH} &middot; 3 November 2026 &middot; Ioannis Alexander Konstas</p>
<div style="border:1px solid hsl(43 45% 56% / .35);border-left:3px solid var(--accent);background:hsl(0 0% 6%);border-radius:6px;padding:10px 14px;margin:0 0 22px;font-size:.9rem"><strong style="color:var(--accent)">Snapshot note.</strong> The session in this chapter was captured a few years before publication. The figures describe the Internet as it was then; the method is unchanged. For a current session, and how the numbers have moved since, see <a href="/bgp/ch02-8-from-problem-to-opportunity" style="color:var(--accent)">Chapter 2, Part 8</a>.</div>
{body}
{nav}
<div style="border:1px solid hsl(43 45% 56% / .25);border-radius:8px;padding:12px 18px;margin:14px 0;background:hsl(0 0% 6%)">
  <p style="margin:0 0 6px;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)">Chapter 1 &middot; One Login, the Whole Internet</p>
  <ol style="margin:0;padding-left:20px;font-size:.92rem">{parts_list}</ol>
</div>
{share}
<p style="font-size:.85rem;color:var(--fg-dim)">Only public services that their operators provide for exactly this purpose are used. More chapters: <a href="/bgp/" style="color:var(--accent)">see the series</a>. Text &copy; 2026 Ioannis Alexander Konstas; code samples under the <a href="/license">MIT License</a>.</p>
  </main>'''
    pre = pre.replace('<a href="/bgp/" class="active">BGP</a>', '<a href="/bgp/" class="active">BGP</a>')
    out = ROOT / 'bgp' / f'{slug}.html'
    out.write_text(head + pre + main + post)
    return out

for i, (slug, title, desc, body) in enumerate(PARTS, 1):
    print('built', page(i, slug, title, desc, body).relative_to(ROOT))
