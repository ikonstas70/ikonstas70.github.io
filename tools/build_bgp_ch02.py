#!/usr/bin/env python3
"""Builds Chapter 2 of the BGP series (bgp/ch02-*.html): a technical field report from a live
Route Views session, using bgp/index.html's head, header and footer.
    python3 tools/build_bgp_ch02.py
"""
import html, pathlib, re
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://ikonstas70.github.io'
TEMPLATE = (ROOT / 'bgp/index.html').read_text()
SERIES = "Special Topics in BGP"
NUM = 2
SHORT = "Reading a Path"
CH = f"Chapter {NUM}: {SHORT}"

def table(head, rows, num=()):
    th = ''.join(f'<th>{h}</th>' for h in head)
    trs = ''.join('<tr>' + ''.join(f'<td{" style=\"text-align:right\"" if i in num else ""}>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

def callout(text, kind='gold'):
    color = {'gold': 'var(--accent)', 'warn': 'hsl(36 70% 58%)'}[kind]
    return (f'<div style="border:1px solid hsl(43 45% 56% / .30);border-left:3px solid {color};background:hsl(0 0% 6%);'
            f'border-radius:6px;padding:12px 16px;margin:18px 0">{text}</div>')

def term(text):
    return f'<pre><code>{html.escape(text.strip())}</code></pre>'

def finding(n, title, sev, body):
    col = {'High': 'hsl(36 70% 58%)', 'Medium': 'var(--accent)', 'Info': 'var(--fg-dim)'}[sev]
    return (f'<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:8px;padding:12px 16px;margin:14px 0;background:hsl(0 0% 6%)">'
            f'<p style="margin:0 0 6px"><span style="font-size:.75rem;letter-spacing:.14em;text-transform:uppercase;color:{col}">Finding {n} &middot; {sev}</span></p>'
            f'<p style="margin:0 0 6px;font-weight:600">{title}</p><div style="font-size:.95rem">{body}</div></div>')

def kpis(items):
    cells = ''.join(f'<div style="border:1px solid hsl(43 45% 56% / .30);border-top:2px solid var(--accent);border-radius:8px;padding:12px 14px;background:hsl(0 0% 6%)">'
                    f'<b style="display:block;font:1.5rem var(--serif);color:var(--accent)">{v}</b><span style="font-size:.8rem;color:var(--fg-dim)">{t}</span></div>' for v, t in items)
    return f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0">{cells}</div>'

# ---------------------------------------------------------------------------------------------
PARTS = [
 ('ch02-1-summary-and-findings', 'Summary and Key Findings',
  'A field report from one public Route Views session: seven commands, ten findings, and why each one matters to anyone who runs a network.', f'''
<blockquote>Chapter 1 read the summary of a route collector, from a snapshot taken on 17 October 2021. This chapter reads the routes themselves, in a live session. Everything here comes from one public session on Route Views (AS 6447) and seven commands. The output is real; the interpretation is the point.</blockquote>

<h2>Watch the session</h2>
<video controls playsinline preload="metadata" poster="/bgp/ch02/poster.jpg" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px;background:#000">
  <source src="/bgp/ch02/route-views-field-report.mp4" type="video/mp4">
</video>
<p style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">Eleven read-only commands on the public Route Views collector, 3 November 2026, with what to notice in each (1 min 34 s). Follow it step by step in <a href="/bgp/ch02-10-the-session-command-by-command" style="color:var(--accent)">Part 10: The Session, Command by Command</a>.</p>

<h2>Scope and method</h2>
<p>Vantage point: <code>route-views.routeviews.org</code>, the University of Oregon collector that peers with more than twenty full-table providers and filters nothing. Because it filters nothing, it shows the Internet as it actually is, including what a production router would have dropped.</p>
{table(['#', 'Command', 'What it answers'], [
 ['1', '<code>show ip bgp 8.8.8.8</code>', 'Every path to Google Public DNS, with all attributes'],
 ['2', '<code>show ip bgp 1.1.1.0/24</code>', 'Every path to Cloudflare DNS, with all attributes'],
 ['3', '<code>show ip bgp 1.1.1.0/24 longer-prefixes</code>', 'Is anyone announcing a more-specific of 1.1.1.0/24?'],
 ['4', '<code>show ip bgp regexp ^6939_</code>', 'The Internet as Hurricane Electric hands it to the collector'],
 ['5', '<code>show ip bgp community 3356:2</code>', 'Every route Lumen tagged with one community value'],
 ['6', '<code>show ip bgp rpki table</code>', 'The validated ROA payloads the router checks routes against'],
 ['7', '<code>show ip bgp rpki servers</code>', 'The health of the router\'s link to its RPKI caches'],
])}
{kpis([('15 / 16', 'paths to 8.8.8.8 and 1.1.1.1'), ('11', 'Cloudflare routers revealed by one attribute'), ('700,457', 'validated ROA entries in the router'), ('97%', 'RTR connection failure rate on one cache')])}

<h2>Key findings</h2>
{table(['#', 'Finding', 'Why it matters', 'Weight'], [
 ['1', 'Best path to 8.8.8.8 is via a university network (AS 101), not a Tier 1', 'When paths tie, BGP decides by age or router ID, not quality', 'Info'],
 ['2', 'Google and Cloudflare are one hop away from almost every provider', 'Direct peering, not transit, is how the large content networks reach the world', 'Info'],
 ['3', 'Lumen communities reveal region and relationship (peer or customer)', 'Communities are a public map of a carrier\'s business', 'Medium'],
 ['4', 'Cloudflare asks Lumen to prepend three times toward China Telecom and China Unicom', 'Traffic engineering intent is visible to anyone', 'Medium'],
 ['5', 'The AGGREGATOR attribute exposes 11 internal Cloudflare router IDs (10.34.x.x)', 'Internal addressing and site count leak through a legacy attribute', 'Medium'],
 ['6', 'The collector cannot decode Large Communities; it forwards them as unknown', 'Optional transitive attributes cross routers that do not understand them', 'High'],
 ['7', 'Prepending up to nine times, and whole blocks of more-specifics with no ROA', 'Unprotected more-specifics are exactly what a sub-prefix hijack needs', 'High'],
 ['8', 'ROAs with maxLength 24 on /22s authorize every /24 inside', 'A loose maxLength turns a forged-origin hijack into an RPKI-valid route', 'High'],
 ['9', 'The two RPKI caches disagree by about 136,000 entries', 'Validation depends on which cache the router trusts at that moment', 'Medium'],
 ['10', 'RTR runs over plain TCP; one cache failed 97% of connection attempts', 'Origin validation is only as strong as the transport and cache behind it', 'High'],
])}
{callout('<strong>What matters, in one sentence.</strong> A public collector shows not only where traffic goes, but why: business relationships, engineering intent, internal addressing and security gaps, for any network, without touching it.')}
<p>Parts 2 to 5 take the findings one by one, with the output that proves each. <a href="/bgp/ch02-6-router-telemetry" style="color:var(--accent)">Part 6</a> reads the router's own telemetry: CPU, memory, traffic, per-peer counters and access control. <a href="/bgp/ch02-7-leaks-and-possible-hijacks" style="color:var(--accent)">Part 7</a> investigates every multiple-origin conflict for leaks and possible hijacks, fairly. <a href="/bgp/ch02-8-from-problem-to-opportunity" style="color:var(--accent)">Part 8</a> turns it all around, and <a href="/bgp/ch02-9-the-proposal-secure-peering" style="color:var(--accent)">Part 9</a> proposes a peering design that is more secure and exposes far less. Part 8 uses a second session on the same collector to show the problems shrinking where operators act, and why that is an opportunity rather than a threat.</p>
'''),

 ('ch02-2-anatomy-of-a-route', 'Anatomy of a Route: 8.8.8.8',
  'Fifteen paths to Google Public DNS, read attribute by attribute: best-path selection, communities, and attributes the router cannot decode.', f'''
<h2>The output</h2>
<p>One prefix, <code>8.8.8.0/24</code>, and 15 paths, one per full-table neighbor that carries it. Three of them, trimmed:</p>
{term("""
route-views> show ip bgp 8.8.8.8
BGP routing table entry for 8.8.8.0/24, version 1488664824
Paths: (15 available, best #9, table default)
  Not advertised to any peer
  Refresh Epoch 1
  3356 15169
    4.68.4.46 from 4.68.4.46 (4.69.184.201)
      Origin IGP, metric 0, localpref 100, valid, external
      Community: 3356:3 3356:86 3356:576 3356:666 3356:901 3356:2012
      path 7F16D449CE88 RPKI State valid
  Refresh Epoch 1
  57866 15169
    37.139.139.17 from 37.139.139.17 (37.139.139.17)
      Origin IGP, metric 0, localpref 100, valid, external
      Community: 57866:200 65102:41441 65103:1 65104:31
      unknown transitive attribute: flag 0xE0 type 0x20 length 0x30
        value 0000 E20A 0000 0065 0000 00C8 0000 E20A ...
  Refresh Epoch 1
  101 15169
    209.124.176.223 from 209.124.176.223 (209.124.176.224)
      Origin IGP, localpref 100, valid, external, best
      Community: 101:20400 101:22200 101:24100
""")}

<h2>Reading each line</h2>
{table(['Line', 'Meaning'], [
 ['<code>version 1488664824</code>', 'The table version when this prefix last changed best path'],
 ['<code>15 available, best #9</code>', 'Fifteen candidate paths; the ninth listed won'],
 ['<code>Not advertised to any peer</code>', 'A collector: it learns, it never announces'],
 ['<code>Refresh Epoch 2</code>', 'A route refresh has been requested on that session once (seen on Swisscom, AS 3303)'],
 ['<code>3356 15169</code>', 'The AS path: Lumen, then Google. Read right to left: origin last'],
 ['<code>4.68.4.46 from 4.68.4.46 (4.69.184.201)</code>', 'Next hop, the peer that sent it, and that peer\'s BGP router ID'],
 ['<code>Origin IGP, metric 0, localpref 100</code>', 'Origin code, MED and local preference: identical for every peer here, because a collector applies no policy'],
 ['<code>RPKI State valid</code>', 'The origin, AS 15169, matches a published ROA'],
])}

{finding(1, 'The best path is via the University of Washington (AS 101)', 'Info', '''
<p>Ten of the fifteen paths are two hops long (provider, then Google). With equal local preference, equal length, the same origin code and MED only comparable within one neighbor AS, the Cisco decision process falls through to the tie-breakers: the <strong>oldest</strong> external path, then the lowest router ID. Path #9 won because it has been stable longest, not because it is faster or better.</p>
<p><strong>Why it matters:</strong> in your own network, if you do not set local preference deliberately, the exit your traffic takes is decided by which session flapped least recently. That is not a policy; it is an accident.</p>''')}

{finding(2, 'Google is one hop from almost everyone', 'Info', '''
<p>Path lengths: ten paths are <code>X 15169</code>, five are <code>X Y 15169</code>. Hurricane Electric, Lumen, AT&amp;T, Swisscom, IIJ, Coloclue and others all connect to Google directly. The three-hop paths are research and regional networks reaching Google through one upstream.</p>
<p><strong>Why it matters:</strong> the content giants built their own global networks and peer directly with access and transit providers. For most destinations users care about, the "Tier 1 hierarchy" is no longer the path.</p>''')}

{finding(3, 'Lumen\'s communities are a public map of its business', 'Medium', '''
<p>The path via Lumen carries <code>3356:3 3356:86 3356:576 3356:666 3356:901 3356:2012</code>. Lumen publishes the meaning of its informational communities: a region value (<code>3356:3</code> for North America, <code>3356:2</code> for Europe), country and city or PoP codes, and a relationship tag. On this route <code>3356:666</code> marks a route learned from a <strong>peer</strong>; on Cloudflare\'s route (Part 3) Lumen adds <code>3356:123</code>, its <strong>customer</strong> tag.</p>
<p><strong>Why it matters:</strong> from one public line you learn that Google peers with Lumen in North America while Cloudflare buys transit from it. Communities tell you where a route entered a carrier and on what commercial terms. Check the current Lumen community guide before relying on any single value.</p>''')}

{finding(6, 'The router does not understand Large Communities, and passes them on anyway', 'High', '''
<p><code>unknown transitive attribute: flag 0xE0 type 0x20</code> is attribute type 32, the <strong>Large Community</strong> (RFC 8092). This collector\'s software shows it as raw hex. Decoding it, 12 bytes per community:</p>''' + term("""
0000 E20A | 0000 0065 | 0000 00C8   ->  57866:101:200
0000 E20A | 0000 0066 | 0000 A1E1   ->  57866:102:41441
0000 E20A | 0000 0067 | 0000 0001   ->  57866:103:1
0000 E20A | 0000 0068 | 0000 001F   ->  57866:104:31
""") + '''
<p>They mirror the standard communities on the same path (<code>65102:41441</code>, <code>65103:1</code>, <code>65104:31</code>): AS 57866 tags its routes both ways. Coloclue (AS 8283) does the same: <code>8283:0:1</code>, <code>8283:5:1</code>, <code>8283:8:26</code>.</p>
<p><strong>Why it matters:</strong> flag <code>0xE0</code> means optional, transitive, partial. BGP\'s rule is that a router must forward an optional transitive attribute it does not recognize. That rule is what lets new features spread, and it is also how a single malformed attribute has crossed many networks and reset sessions far from its source. Your edge should be running code that handles unknown attributes gracefully (RFC 7606, "treat-as-withdraw"), and you should know whether it does.</p>''')}

<h2>One more attribute</h2>
<p>The path through AS 12552 carries <code>Extended Community: 0x43:100:0</code>. Type <code>0x43</code> is a non-transitive extended community; the format matches the origin-validation-state community of RFC 8097, which one network uses to tell its own routers the RPKI result. It is meant to stay inside that network. Seeing it here suggests it leaked across the boundary: harmless on a collector, but a sign of an edge that does not scrub internal markings.</p>
'''),

 ('ch02-3-cloudflare-and-the-hidden-attributes', 'Cloudflare 1.1.1.1 and the Attributes That Leak',
  'Sixteen paths to 1.1.1.0/24: action communities that reveal engineering intent, an aggregator attribute that reveals internal routers, and a clean more-specific check.', f'''
<h2>Sixteen paths, one ROA</h2>
{term("""
route-views> show ip bgp 1.1.1.0/24
BGP routing table entry for 1.1.1.0/24, version 1509109845
Paths: (16 available, best #12, table default)
  3356 13335, (aggregated by 13335 10.34.9.112)
    4.68.4.46 from 4.68.4.46 (4.69.184.201)
      Origin IGP, metric 0, localpref 100, valid, external, atomic-aggregate
      Community: 3356:3 3356:22 3356:100 3356:123 3356:575 3356:901 3356:2012
                 13335:10028 65003:4134 65003:4837 65003:58453
  7018 13335, (aggregated by 13335 10.34.2.204)
    12.0.1.63 from 12.0.1.63 (12.0.1.63)
      Origin IGP, localpref 100, valid, external, atomic-aggregate, best
      Community: 7018:2500 7018:37171
""")}
<p>Twelve of the sixteen paths are direct (<code>X 13335</code>). Four reach Cloudflare through a transit network, and three of those four go through Lumen. Hurricane Electric\'s path is <code>6939 3356 13335</code>: from this vantage point HE reaches 1.1.1.0/24 through Lumen rather than directly.</p>

{finding(4, 'Cloudflare\'s traffic engineering is visible in Lumen\'s communities', 'Medium', '''
<p>Lumen supports <strong>action communities</strong> that its customers attach to ask for treatment downstream: <code>65000:AS</code> do not announce to that AS, and <code>65001:AS</code> to <code>65003:AS</code> prepend one to three times toward it. Cloudflare\'s route carries:</p>''' + table(['Community', 'Requested action'], [
 ['<code>65003:4134</code>', 'Prepend three times toward AS 4134 (China Telecom)'],
 ['<code>65003:4837</code>', 'Prepend three times toward AS 4837 (China Unicom)'],
 ['<code>65003:58453</code>', 'Prepend three times toward AS 58453 (China Mobile International)'],
 ['<code>13335:100xx</code>', 'Cloudflare\'s own tags, which differ per path and appear to identify the site that announced it'],
]) + '''
<p><strong>Why it matters:</strong> the request was meant for Lumen, but Lumen forwards the communities, so the whole Internet can read Cloudflare\'s policy toward specific networks. Your own action communities are just as public unless your provider strips them. Treat them as published.</p>''')}

{finding(5, 'One legacy attribute reveals eleven internal routers', 'Medium', '''
<p>Each path carries <code>atomic-aggregate</code> and an <strong>AGGREGATOR</strong> attribute: the AS and router ID of the router that built the aggregate. Across the sixteen paths there are <strong>eleven different</strong> router IDs, all in private space: 10.34.0.16, 10.34.2.204, 10.34.3.248, 10.34.6.80, 10.34.7.24, 10.34.8.168, 10.34.9.112, 10.34.23.128, 10.34.24.72, 10.34.130.6, 10.34.130.16.</p>
<p>This is anycast made visible: the same prefix is originated at many sites, and each peer hears it from a different one. The attribute also discloses the internal addressing plan (10.34.0.0/16 for router IDs) and a lower bound on the number of sites peering with these networks.</p>
<p><strong>Why it matters:</strong> AGGREGATOR is rarely useful today and is sent by default when you aggregate. If you summarize routes, check what your router puts in it. Internal router IDs are reconnaissance data you did not mean to publish.</p>''')}

<h2>The more-specific check</h2>
{term("""
route-views> show ip bgp 1.1.1.0/24 longer-prefixes
     Network          Next Hop            Metric LocPrf Weight Path
V*   1.1.1.0/24       132.198.255.253                        0 1351 13335 i
V*                    217.192.89.50                          0 3303 3356 13335 i
...
V*>                   12.0.1.63                              0 7018 13335 i
V*                    202.232.0.2                            0 2497 13335 i
""")}
<p>Only the /24 itself, sixteen paths, all RPKI <code>V</code>alid. No one is announcing a more-specific, and the ROA (<code>1.1.1.0/24, maxLength 24, AS 13335</code>, seen in Part 5) is tight. A /24 is also the longest IPv4 prefix most networks accept, so a sub-prefix hijack would be filtered almost everywhere. This is what good looks like, and it is the template for your own address space.</p>
{callout('<strong>Defender\'s check.</strong> Run <code>show ip bgp &lt;your prefix&gt; longer-prefixes</code> on a public collector every day. Any line you did not announce is a leak or a hijack in progress.')}
'''),

 ('ch02-4-reading-the-table', 'Reading the Table: Prepending, More-Specifics and maxLength',
  'Listings filtered by neighbor, community and AS: what prepending, deaggregation, MED and loose ROAs look like in real routes.', f'''
<h2>A filtered view hides the best path</h2>
<p>A listing filtered to paths that cross Lumen (AS 3356) shows many prefixes with no <code>&gt;</code> at all:</p>
{term("""
N*   5.3.64.0/20      4.68.4.46       0   0 3356 9002 9002 9002 9002 9002 57304 57304 9049 39028 i
N*                    208.51.134.254  0   0 3549 3356 9002 9002 9002 9002 9002 57304 57304 9049 39028 i
N*   5.3.64.0/22      4.68.4.46       0   0 3356 9002 9002 9002 9002 9002 57304 57304 9049 39028 i
N*   5.3.68.0/22      4.68.4.46       0   0 3356 9002 9002 9002 9002 9002 57304 57304 9049 39028 i
V*   5.3.85.0/24      4.68.4.46       0   0 3356 9002 57304 9049 i
""")}
<p>The best path for those prefixes goes through another neighbor, so the filter removed it. Lesson for troubleshooting: <code>regexp</code> and <code>community</code> views show matching paths, not the router\'s decision. Always confirm with <code>show ip bgp &lt;prefix&gt;</code>.</p>

{finding(7, 'Prepending, and blocks of more-specifics with no ROA', 'High', '''
<p>Three patterns in the lines above, all common, all readable by anyone:</p>''' + table(['Pattern', 'Where', 'Reading'], [
 ['Five-fold prepend', '<code>9002 9002 9002 9002 9002</code> (RETN)', 'That path is deliberately made long so it is used only as a backup. The same prefixes without prepends (5.3.85.0/24) show the policy is set per prefix'],
 ['Origin prepend', '<code>57304 57304</code>, <code>9049 9049 9049</code>', 'Networks further down also lengthen their own paths: three layers of traffic engineering on one route'],
 ['Nine-fold prepend', '<code>34984</code> ×9 on 2.19.193.0/24', 'Extreme prepending. Beyond three or four it rarely changes anything, and it makes the route easier to out-compete with a forged shorter path'],
 ['Aggregate plus more-specifics', '5.3.64.0/20 and four /22s inside it, same path', 'Deaggregation: more entries in every router\'s table, usually for inbound traffic engineering'],
 ['RPKI NotFound', '<code>N*</code> on the /20 and every /22', 'No ROA covers any of them. Anyone can announce a /23 or /24 inside, and no origin-validating router would object'],
]) + '''
<p><strong>Why it matters:</strong> a sub-prefix hijack wins on longest match, regardless of path length. Unprotected more-specifics are the exact gap it exploits. Publish ROAs for every prefix you announce, with maxLength equal to the length you actually announce.</p>''')}

<h2>MED shows the carrier\'s internal distance</h2>
<p>On routes from Lumen\'s legacy Global Crossing network (AS 3549) the metric column is populated: <code>18891</code>, <code>18810</code>, <code>5644</code>. That network sets MED from its internal IGP cost. Akamai (AS 20940) prefixes arrive with either 18810 or 5644: two groups of routes leaving that backbone at different internal distances. MED is meant for the neighbor; published to a collector, it becomes a rough map of a carrier\'s backbone.</p>

<h2>Hurricane Electric\'s view, and a maxLength trap</h2>
{term("""
route-views> show ip bgp regexp ^6939_
V*>  1.6.0.0/22       64.71.137.241     0 6939 9583 i
V*>  1.6.1.0/24       64.71.137.241     0 6939 9583 i
V*>  1.6.2.0/24       64.71.137.241     0 6939 9583 i
V*   1.6.7.0/24       64.71.137.241     0 6939 6453 4755 9583 i
N*   1.1.64.0/19      64.71.137.241     0 6939 2519 i
V*   1.0.182.0/24     64.71.137.241     0 6939 38040 23969 23969 23969 23969 23969 i
""")}
<p>Every path starts with 6939 because that is the filter. Inside it: Sify (AS 9583) announces /22s and many /24s within them, some only via Tata (<code>6453 4755</code>) as a different inbound path; a block with no ROA at all (<code>N*</code>, AS 2519); and a five-fold origin prepend from AS 23969.</p>

{finding(8, 'A loose maxLength makes forged routes valid', 'High', '''
<p>The RPKI table (Part 5) shows Sify\'s ROAs as <code>1.6.0.0/22, maxLength 24, AS 9583</code>. That one ROA authorizes the /22, both /23s and all four /24s. Some of those /24s are announced; the others are not. Anyone who forges AS 9583 as the origin (a <em>forged-origin</em> hijack) can announce an unannounced /24 and it will be RPKI <strong>valid</strong>, and it will beat the /22 on longest match.</p>
<p>Compare Cloudflare\'s <code>1.1.1.0/24, maxLength 24</code>, which authorizes exactly what is announced. RFC 9319 recommends avoiding maxLength except where every covered prefix is actually announced.</p>
<p><strong>Why it matters:</strong> RPKI only checks the origin. A ROA that authorizes more than you announce widens the hole it was supposed to close.</p>''')}

<h2>One community, many networks</h2>
<p><code>show ip bgp community 3356:2</code> lists everything Lumen tagged with its Europe region value: Cloudflare via Swisscom, China Telecom (AS 4134) and Akamai (AS 20940) space among them. A single community query reconstructs which networks a carrier hears in a region. That is the basis for mapping any network\'s connectivity from the outside.</p>
'''),

 ('ch02-5-rpki-under-the-hood', 'RPKI Under the Hood, and What to Do About It',
  'The router\'s ROA table and its link to the RPKI caches: what the counters reveal, the two weaknesses they expose, and a checklist for your own network.', f'''
<h2>The ROA table</h2>
{term("""
route-views> show ip bgp rpki table
700457 BGP sovc network entries using 112073120 bytes of memory
796106 BGP sovc record entries using 25475392 bytes of memory

Network              Maxlen  Origin-AS  Source  Neighbor
1.0.0.0/24           24      13335      0       128.223.157.89/3323
1.0.0.0/24           24      13335      0       128.223.157.83/3323
1.0.128.0/17         19      23969      0       128.223.157.89/3323
1.6.0.0/22           24      9583       0       128.223.157.89/3323
1.6.132.240/29       29      9583       0       128.223.157.89/3323
""")}
{table(['Value', 'Reading'], [
 ['700,457 network entries, 112 MB', 'Unique (prefix, maxLength) entries from the RPKI: about 160 bytes each'],
 ['796,106 records, 25 MB', 'Prefix-to-origin records; some prefixes are authorized for more than one AS (1.6.136.0/24 for both 9583 and 132215)'],
 ['Every line twice', 'One copy per cache: <code>.83</code> and <code>.89</code>, both on TCP port 3323'],
 ['<code>1.0.128.0/17</code> maxLength 19', 'A loose ROA: also authorizes /18s and /19s'],
 ['<code>1.6.132.240/29</code>', 'A /29 ROA. Valid, but a /29 is not accepted by most networks, so it protects nothing on the public Internet'],
])}
<p>A ROA authorizes; it does not require an announcement. China Telecom (AS 4134) has ROAs for 1.1.4.0/22, 1.1.16.0/20 and 1.3.0.0/16, none of which appear in Hurricane Electric\'s listing. Authorized but unseen space is normal, and is worth monitoring: an announcement there from any other origin is invalid by design.</p>

<h2>The link to the caches</h2>
{term("""
route-views> show ip bgp rpki servers
BGP SOVC neighbor is 128.223.157.83/3323 connected to port 3323
Flags 64, Refresh time is 300, Serial number is 449, Session ID is 60017
  Prefixes 1029914
  Connection attempts: 1920
  Connection failures: 1390
  Errors sent: 200
  Errors received: 13
Connection state is ESTAB ... Mininum incoming TTL 0, Outgoing TTL 255
uptime: 1000789147 ms
BGP SOVC neighbor is 128.223.157.89/3323 connected to port 3323
Flags 64, Refresh time is 300, Serial number is 39, Session ID is 11737
  Prefixes 1165838
  Connection attempts: 3046
  Connection failures: 2958
uptime: 27750949 ms
""")}
{table(['Counter', 'Cache .83', 'Cache .89', 'Reading'], [
 ['Prefixes', '1,029,914', '1,165,838', 'The caches disagree by 135,924 entries'],
 ['Serial / session', '449 / 60017', '39 / 11737', 'Independent caches, separately restarted'],
 ['Session uptime', '11.6 days', '7.7 hours', '.89 reconnected today'],
 ['Connection attempts / failures', '1,920 / 1,390 (72%)', '3,046 / 2,958 (97%)', 'Long histories of failed connections'],
 ['Errors sent / received', '200 / 13', '55 / 23', 'Protocol errors in both directions'],
 ['Refresh time', '300 s', '300 s', 'A new ROA takes up to five minutes to reach the router after the cache has it'],
 ['Transport', 'TCP 3323', 'TCP 3323', 'Plain RTR: no TLS, no SSH, no TTL check (incoming TTL 0)'],
], num=(1, 2))}

{finding(9, 'The two caches do not agree', 'Medium', '''
<p>About 136,000 entries separate the caches. They may run different validator software, different trust anchors, or include IPv6 differently. Whatever the cause, the router\'s view of "valid" depends on which cache is up. With one cache reconnecting today, there were hours when the router may have had only one cache\'s view.</p>
<p><strong>Why it matters:</strong> run at least two caches from <em>different</em> validator implementations, monitor their counts and serial numbers, and alert when they diverge or when one falls behind.</p>''')}

{finding(10, 'Origin validation rests on a fragile, unauthenticated link', 'High', '''
<p>RTR (RFC 8210) here runs over plain TCP with no transport security and no TTL protection, and the connection history shows thousands of failures. Anyone who can reach that TCP session or impersonate a cache can feed the router a false ROA set: mark good routes invalid, or bad ones valid.</p>
<p><strong>Why it matters:</strong> on your own routers, keep RTR on a protected management network, use SSH or TLS transport where the platform supports it, and decide deliberately what happens when every cache is unreachable. Most routers fall back to "NotFound" for everything, which silently turns origin validation off.</p>''')}

<h2>Checklist for your own network</h2>
{table(['Area', 'Do this', 'Finding'], [
 ['Local preference', 'Set it explicitly for customers, peers and transit; never leave exit choice to tie-breakers', '1'],
 ['Communities', 'Strip internal and action communities at the edge; assume anything you send is public', '3, 4'],
 ['Aggregation', 'Check what AGGREGATOR exposes; avoid publishing private router IDs', '5'],
 ['Attribute handling', 'Run code with RFC 7606 error handling; know how it treats unknown attributes', '6'],
 ['ROAs', 'One ROA per announced prefix, maxLength equal to the announced length', '7, 8'],
 ['Prepending', 'Three or fewer; use communities toward your upstream for finer control', '7'],
 ['RPKI caches', 'Two or more, different implementations, monitored for divergence', '9'],
 ['RTR transport', 'Protected network, SSH or TLS, an alarm when all caches are down', '10'],
 ['Monitoring', 'Watch your prefixes and their more-specifics on public collectors, daily', 'all'],
])}

<h2>Your turn</h2>
<p>On <code>route-views.routeviews.org</code> (username <code>rviews</code>). Start with <code>terminal length 0</code> to avoid the <code>--More--</code> prompt, and type commands exactly: IOS rejects abbreviations it cannot resolve, as <code>how ip bgp</code> shows.</p>
{table(['Command', 'Look for'], [
 ['<code>show ip bgp &lt;your prefix&gt;</code>', 'Which path wins and why; your communities as others see them'],
 ['<code>show ip bgp &lt;your prefix&gt; longer-prefixes</code>', 'Anything you did not announce'],
 ['<code>show ip bgp regexp _&lt;your AS&gt;$</code>', 'Everything originated in your name'],
 ['<code>show ip bgp rpki table | include &lt;your AS&gt;</code>', 'Your ROAs and their maxLength'],
])}
<p><strong>Exercise.</strong> Find a prefix with an AGGREGATOR attribute from a network other than Cloudflare. How many distinct router IDs can you collect, and what do they say about the network\'s size?</p>
<h2>The takeaway</h2>
<p>Seven commands showed how BGP chooses among equal paths, how carriers label routes by region and relationship, how a content network\'s policy and internal addressing leak through attributes, how prepends and more-specifics shape traffic, and where RPKI is strong and where it is thin. None of it required access to any of those networks. The last part asks the more useful question: what can be done about it, and why that is an opportunity.</p>
'''),
 ('ch02-6-router-telemetry', 'Router Telemetry: The Collector Under Load',
  'The collector\'s own health: software, uptime, CPU, memory, interface and protocol counters, per-peer statistics, IPv6 and access control, read with public commands.', f'''
<blockquote>So far we read the routes. This part reads the router that holds them. Every command below is available to the public login, and every one says something about how a full-table BGP router behaves, and what it costs to run one.</blockquote>

<h2>The platform</h2>
{term('''
route-views> show version
Cisco IOS XE Software, Version 03.16.10.S - Extended Support Release
Cisco IOS Software, ASR1000 Software (X86_64_LINUX_IOSD-ADVENTERPRISEK9-M), Version 15.5(3)S10
Compiled Thu 19-Sep-19
route-views uptime is 2 years, 42 weeks, 3 days, 4 hours, 12 minutes
''')}
{table(['Measure', 'Value', 'Reading'], [
 ['Hardware', 'Cisco ASR 1000', 'A carrier-class edge router doing a research job'],
 ['Software', 'IOS XE 3.16.10.S, built September 2019', 'An older release train. It explains Finding 6: this code predates native display of Large Communities, so they appear as raw hex'],
 ['Uptime', '2 years 42 weeks', 'No reload, so no new software image, in almost three years'],
 ['Most BGP sessions', 'up 1w4d', 'The router did not reboot; something reset BGP about 11.6 days ago. The RPKI cache session (1,003,583,971 ms, 11.6 days) reset at the same time'],
])}
{callout('<strong>Correlation, done properly.</strong> In Chapter 1, sessions sharing one uptime pointed to a shared event. Here the router uptime rules out a reboot, and the RPKI session uptime matches the BGP resets to within hours: a control-plane event, not a power cycle. Two counters, one conclusion.')}

<h2>CPU and memory</h2>
{term('''
CPU utilization for five seconds: 100%/1%; one minute: 87%; five minutes: 85%
 PID  5Sec   1Min   5Min Process
 589  0.00% 16.38% 10.79% Virtual Exec
 323  0.00%  3.89%  5.07% BGP Scanner
 362  1.35%  1.54%  2.58% BGP Router

Processor Pool Total: 10113380176 Used: 8050934976 Free: 2062445200
 362  BGP Router   holding 7064510264
''')}
{table(['Measure', 'Value', 'Reading'], [
 ['CPU now', '100% (5 s), 87% (1 min), 85% (5 min)', 'Running hot. Only 1% is interrupt time; the load is processes'],
 ['CPU, last 72 hours', 'peaks at 100% most hours, average 30-40%', 'Sustained bursts, not a one-off'],
 ['Top visible process', '<code>Virtual Exec</code>, 10.8% (5 min)', '<strong>That is us</strong>: public users running <code>show</code> commands over a million-prefix table'],
 ['BGP Scanner and Router', '5.1% and 2.6%', 'Walking the table and processing updates. The rest of the load sits outside the IOS process list, which the router itself points out'],
 ['Memory', '8.05 GB of 10.1 GB used (79.6%), low-water free 1.78 GB', 'Comfortable today, but the table grows every month'],
 ['BGP process memory', '7.06 GB', 'IPv4 BGP 3.15 GB plus IPv6 BGP 0.85 GB of tables, plus working memory'],
])}
<p><strong>Why it matters:</strong> a full-table router is sized by CPU and memory, not bandwidth. The public CLI is itself a load: every <code>show ip bgp regexp</code> walks over a million entries. Production routers keep that load off the control plane by exporting data through BMP (the BGP Monitoring Protocol: the <code>BGP BMP Server</code> process is running here) or streaming telemetry, instead of interactive logins.</p>

<h2>Interfaces and traffic</h2>
{table(['Counter', 'Value', 'Reading'], [
 ['Active interface', 'one 10 Gb/s port', 'Three other ports administratively down'],
 ['Rate', '278 kb/s in, 70 kb/s out', 'Collecting the whole Internet\'s routing needs almost no bandwidth'],
 ['Interface errors', '0 input, 0 CRC, 0 output', 'A clean physical path'],
 ['Input queue drops', '271,639 drops, 22,525 flushes', 'Packets for the CPU were dropped when the control-plane queue was full: the hot CPU, seen from the wire'],
 ['Unknown protocol drops', '3,607,986', 'Frames for protocols the router does not run'],
], num=(1,))}

<h2>Internet background radiation</h2>
{term('''
route-views> show ip traffic
  UDP  Rcvd: 3301919260 total, 3299988429 no port
  TCP  Rcvd: 2882739298 total, 20694483 no port
  ICMP Sent: 248397808 echo reply
''')}
{table(['Counter', 'Value', 'Reading'], [
 ['UDP received', '3.30 billion', '<strong>99.94%</strong> to ports nothing listens on: scans, reflection attempts, backscatter'],
 ['TCP to closed ports', '20.7 million', 'Port scans against the router'],
 ['ICMP echo replies sent', '248 million', 'The router has answered a quarter of a billion pings'],
 ['ARP requests received', '2.23 billion', 'A busy shared network segment'],
], num=(1,))}
<p><strong>Why it matters:</strong> any public address receives this, all the time. Every one of those packets reaches a router\'s CPU unless it is filtered first. Control-plane policing (CoPP), an infrastructure ACL that permits only BGP from configured peers, and rate-limited ICMP are the standard answer, and the input-queue drops above show what happens when the CPU is already busy.</p>

<h2>BGP at the protocol level</h2>
{table(['Counter', 'Received', 'Sent', 'Reading'], [
 ['Messages', '3.78 billion', '88.2 million', 'A collector listens; it barely talks'],
 ['Updates', '3.72 billion', '0', 'It has never announced a single route'],
 ['OPEN', '5,623', '<strong>1,080,531</strong>', 'Over a million attempts to open sessions with peers that do not answer: the <code>Active</code> sessions in the summary, retrying for years'],
 ['NOTIFICATION', '877', '4,976', 'Sessions closed with an error code, mostly by the collector'],
], num=(1, 2))}

<h2>One session up close: Hurricane Electric</h2>
{table(['Counter', 'Value', 'Reading'], [
 ['Up for', '12 weeks 2 days', 'The longest-lived full feed'],
 ['Updates received', '36.3 million', 'About 5 per second, around the clock'],
 ['Prefixes received in total', '89.3 million, for 1.10 million current', 'Each prefix replaced about 81 times in 84 days'],
 ['Withdrawals', '74.1 M implicit, 14.1 M explicit', 'Most changes replace a route rather than remove it'],
 ['Used as best path', '488,762 prefixes', '43% of the collector\'s best paths come from this one peer'],
 ['Keepalives', '137,600 sent, 4 received', 'HE sends updates so often it never needs to send keepalives: any message resets the hold timer'],
 ['Outbound policy denied', '900,366,637', 'Every route the collector could have announced, blocked by policy'],
 ['Hold time', '180 s negotiated (600 configured locally)', 'The lower value wins'],
 ['Transport', 'multihop up to 255 hops, minimum incoming TTL 0', 'No TTL security (GTSM). Normal for a collector peering across the Internet; a risk on a production edge'],
 ['Lifetime', '46 connections established, 45 dropped', 'Sessions come and go over the years'],
], num=(1,))}
<p>Lumen (AS 3356) for comparison: 2.42 million updates in 11.6 days, about 2.4 per second, with a 90-second hold time. Hurricane Electric is roughly twice as busy, consistent with its very large peering footprint.</p>

<h2>IPv6 is ahead of IPv4</h2>
{table(['Measure', 'IPv4', 'IPv6'], [
 ['Prefixes', '1,129,606', '263,159'],
 ['Paths RPKI valid', '70.8%', '<strong>83.0%</strong>'],
 ['Paths RPKI not found', '29.1%', '17.0%'],
 ['Paths RPKI invalid', '0.03%', '0.05%'],
 ['BGP memory', '3.15 GB', '0.85 GB'],
])}
<p>Newer address space was allocated after RPKI existed, and it shows: IPv6 is better protected than IPv4 by twelve points. AS 20912's IPv6 session reset 1 day 13 hours ago, and Verizon\'s IPv6 session has been <code>Active</code> for almost two years.</p>

<h2>Access control</h2>
{table(['Observation', 'Reading'], [
 ['<code>show tcp brief</code>: <em>Command authorization failed</em>', 'Per-command authorization through TACACS+ (the <code>TPLUS</code> process): the public account can read routes but not everything. Least privilege, done right'],
 ['<code>show ip bgp dampening parameters</code>: not enabled', 'Correct for a collector, which must record every change, flaps included'],
 ['<code>show users</code>: ten public sessions, one idle for over a year', 'No idle timeout on the public lines. A handful of forgotten sessions can exhaust the terminal lines and lock everyone out'],
 ['<code>show users</code> lists other users\' addresses and hostnames', 'A privacy leak on a shared public service. We do not reproduce them here'],
 ['<code>show ip interface brief</code> shows the management port\'s private address', 'Minor internal addressing disclosure'],
])}

{finding(11, 'The collector\'s control plane runs hot and is reachable by anyone', 'Medium', '''
<p>CPU at 85-100%, input-queue drops, 3.3 billion unsolicited UDP packets, and a public login that adds its own load. None of this breaks the collector\'s mission, but each is a lesson for a production router.</p>
<p><strong>What to do on your own routers:</strong> CoPP and an infrastructure ACL in front of the CPU; GTSM on eBGP sessions; idle timeouts on every terminal line; per-command authorization; and BMP or streaming telemetry for monitoring instead of interactive scraping.</p>''')}
'''),
 ('ch02-7-leaks-and-possible-hijacks', 'Leaks and Possible Hijacks, Assessed Fairly',
  'Every prefix with conflicting origins on the collector, classified with RPKI: what is authorized, what cannot be judged, what is a mistake, and whether anything looks like a deliberate hijack.', f'''
<blockquote>A route with two origins is the classic signature of a hijack. It is also the signature of anycast, DDoS protection, a network migration and a typing error. Calling something a hijack is an accusation, so this part follows one rule: classify with evidence, and say plainly when the evidence is not enough.</blockquote>

<h2>The method</h2>
{term('''
route-views> show ip bgp inconsistent-as
route-views> show bgp ipv6 unicast inconsistent-as
''')}
<p>Both commands list every prefix that reaches the collector with <strong>more than one origin AS</strong> (a MOAS conflict). For each one we compared the RPKI state of each origin's paths, counted how many of the collector's feeds carry each origin, and checked whether the conflicting origin is simply the other origin's upstream provider. We also scanned the collected paths for the shape of a route leak: a smaller network sitting between two large carriers.</p>

<h2>What it looks like</h2>
<figure style="margin:22px 0"><img src="/bgp/ch02/ipv6-origin-conflicts.jpg" alt="IPv6 prefixes with conflicting origins on Route Views" loading="lazy" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px">
<figcaption style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">Three classes in one screen, from <code>show bgp ipv6 unicast inconsistent-as</code>. <strong>2A13:EDC0:FFFF::/48</strong>: two origins (AS 216211 and AS 40792), both <code>V</code>alid: authorized. <strong>2C0F:EEA8:9000::/36</strong>: two origins (AS 328306 and AS 39356), both <code>N</code>ot found: cannot be judged. <strong>2C0F:EF68::/32</strong>: an <code>{{211612}}</code> AS_SET left by aggregation at AS 37662, the deprecated form that makes the true origin ambiguous.</figcaption></figure>

<h2>What we found</h2>
{kpis([('1,329', 'prefixes with conflicting origins (1,125 IPv4, 204 IPv6)'), ('64%', 'authorized: every origin has a valid ROA'), ('33%', 'cannot be judged: no ROA for any origin'), ('3.5%', 'one origin valid, the other invalid')])}
{table(['Class', 'IPv4', 'IPv6', 'What it usually is', 'Verdict'], [
 ['Every origin RPKI-valid', '678', '170', 'Anycast, DDoS scrubbing services, migrations, multi-homed customers with ROAs for both origins', 'Authorized'],
 ['No ROA for any origin', '402', '30', 'Could be anything, legitimate or not', 'Not enough evidence'],
 ['One origin valid, one invalid', '42', '4', 'See below: mostly stale or mistaken announcements', 'Misconfiguration, contained'],
 ['Every path invalid', '1', '0', 'A ROA that does not match the route actually used', 'Report to the owner'],
 ['AS_SET or mixed', '2', '0', 'Old-style aggregation (deprecated by RFC 9774)', 'Not enough evidence'],
], num=(1, 2))}

<h2>The 46 real conflicts, read one by one</h2>
<p>In every one of them, the RPKI-valid origin is seen by almost the whole collector (median <strong>14</strong> feeds), and the invalid origin by almost nobody (median <strong>1</strong> feed). That is origin validation working: the invalid announcement exists, but the large networks that drop invalid routes do not pass it on. The patterns behind them:</p>
{table(['Pattern', 'Example', 'Reading'], [
 ['A provider still announcing space it delegated', '38.51.236.0/24: ROA for AS 271907, also announced by AS 174 (Cogent, whose block 38.0.0.0/8 it is)', 'The customer has a ROA for its own origin; the provider\'s old announcement was never removed. Seven Cogent cases, five GTT (four in IPv6), one Lumen'],
 ['Address space leased to a cloud', '8.236.0.0/15: ROA for AS 396982 (Google Cloud); Lumen (AS 3356) also originates it from its 8.0.0.0/8 block', 'A lease or transfer where the original holder still announces the block. Four feeds carry the Lumen version, all through Lumen itself'],
 ['Bring-your-own-IP in a cloud', '212.103.45.0/24: ROA for AS 202280, also originated by Microsoft (AS 8075)', 'A customer prefix announced by the cloud without a matching ROA for the cloud\'s AS'],
 ['A prepend typing error', '103.182.177.0/24: path ends <code>… 9498 133296 3</code>; 103.234.137.0/24 ends <code>… 9498 133317 8</code>', 'AS 3 and AS 8 are universities that would never originate these prefixes. Someone meant "prepend three times" and appended the number 3 as an AS. A classic configuration mistake, not an attack'],
 ['Every path invalid', '112.142.192.0/21: two origins, neither authorized, carried by all fifteen feeds', 'The ROA does not match the route in use. Either it changed very recently or it is simply wrong: a case for a quiet message to the owner'],
])}

<h2>Route leaks</h2>
<p>A leak shows up as a <em>valley</em> in the AS path: a smaller network between two large carriers, for example a customer re-announcing one provider\'s routes to another. Scanning every path collected in this chapter for a large carrier, then a non-carrier, then another large carrier found <strong>no such pattern</strong>. That is a sample, not the whole table, but it is the expected result where BGP Roles, maximum-prefix limits and RPKI filtering are in place.</p>

<h2>Is anything a deliberate hijack?</h2>
{finding(12, 'No evidence of an active, deliberate hijack in this snapshot', 'Info', '''
<p>A deliberate hijack has a recognizable shape: an unrelated origin, often for a more-specific prefix, spreading through many networks. Nothing in this snapshot has that shape. Every invalid origin is either the legitimate holder's own provider, a cloud acting for a customer, or a typing error, and almost all of them were stopped after one hop.</p>
<p>What the data <strong>does</strong> show is plenty of misconfiguration, and RPKI containing it. The 432 conflicts with no ROA at all are the honest gap: for those, a collector alone cannot tell legitimate from malicious, and no one should claim otherwise.</p>''')}

<h2>Fairness in reporting</h2>
{table(['Do', 'Do not'], [
 ['Call a conflict "invalid" or "unauthorized" when RPKI says so', 'Call it a "hijack" without evidence of intent and spread'],
 ['Note how many networks carry it, and through whom', 'Name a network as an attacker because it appears in a path'],
 ['Check the obvious explanations first: provider, cloud, typo, migration', 'Publish other people\'s session details or addresses'],
 ['Tell the prefix holder privately and give them time to fix it', 'Treat a single snapshot as a history'],
])}
<p>Confirming intent takes more than one view: route history (when did the origin first appear?), several collectors (RIPE RIS, other Route Views collectors), registry data, and ideally a word with the operators involved.</p>
'''),
 ('ch02-8-from-problem-to-opportunity', 'From Problem to Opportunity',
  'A second session on the same collector shows routing security improving where operators act. What can be done about each finding, by whom, and why it is an opportunity.', f'''
<blockquote>Every finding in this chapter is public. That is the uncomfortable part, and it is also the opportunity: the same visibility that helps an attacker plan lets every defender measure, fix and verify, for free, in minutes.</blockquote>

<h2>A second session: the trend</h2>
<p>The same collector, the same command, two snapshots <strong>five years apart</strong>: the one read in Chapter 1, captured on 17 October 2021, and a fresh session on 3 November 2026.</p>
{table(['Measure', 'Chapter 1 (17 Oct 2021)', 'This session (3 Nov 2026)', 'Change'], [
 ['Table version', '1,142,409,165', '1,517,803,889', 'the counter keeps climbing'],
 ['Paths, RPKI <strong>valid</strong>', '6,502,331 (32.6%)', '11,656,019 (70.8%)', '<strong>more than double</strong> the share'],
 ['Paths, RPKI <strong>not found</strong>', '13,437,858 (67.3%)', '4,793,951 (29.1%)', 'down by more than half'],
 ['Paths, RPKI <strong>invalid</strong>', '17,810 (0.09%)', '5,350 (0.03%)', '<strong>down 70%</strong>'],
 ['IPv4 network entries', '916,896', '1,129,606', 'the table keeps growing'],
 ['Full-table peers', '22', '15', 'a smaller peer mix this time'],
], num=(1, 2))}
<p>A caution before the conclusion: the peer mix changed (fifteen full feeds now, twenty-two then), so absolute path counts are not directly comparable. The <em>shares</em> are, and over those five years they moved decisively: the IPv4 table grew by more than 200,000 prefixes while the share of paths with no ROA fell from two thirds to under a third. Where networks publish ROAs and their providers drop invalid routes, invalid announcements stop spreading. RPKI is not a theory any more; you can watch it work from a public login.</p>
{kpis([('70.8%', 'of paths now RPKI-valid'), ('5,350', 'invalid paths left, down from 17,810'), ('0', 'unexpected more-specifics on the blocks we checked'), ('15', 'paths per block: every major carrier carries them')])}

<h2>The opportunity, in four sentences</h2>
<ol>
 <li><strong>Visibility is symmetric.</strong> What an attacker reads on a collector, you can read first, and every hijack or leak of your space appears there within seconds.</li>
 <li><strong>The fixes are cheap.</strong> A ROA takes minutes in the registry portal. Stripping communities and aggregator data is a few lines of policy. Monitoring is free.</li>
 <li><strong>The enforcement is already built.</strong> Lumen, AT&amp;T, Hurricane Electric, Arelion, NTT and most large carriers drop RPKI-invalid routes. Publish a correct ROA and the world's largest networks enforce it for you, at no cost.</li>
 <li><strong>The gaps are measurable.</strong> Every finding here can be checked before and after a fix with the same public command. Few security controls are that easy to prove.</li>
</ol>

<h2>From each finding to a fix</h2>
{table(['Finding', 'Problem', 'What can be done', 'Who', 'Effort'], [
 ['1 Tie-breakers', 'Exit choice decided by session age', 'Explicit local preference per customer, peer and transit', 'Your network', 'Hours'],
 ['3 Communities', 'Region and business relationships published', 'Strip informational communities you do not need to send; document the ones you do', 'Every AS', 'Hours'],
 ['4 Action communities', 'Engineering intent readable by anyone', 'Ask upstreams to remove action communities after acting on them', 'Upstream carriers', 'A request'],
 ['5 AGGREGATOR', 'Internal router IDs exposed', 'Set a neutral router ID on aggregating routers, or originate the aggregate without it', 'Content and cloud networks', 'Minutes'],
 ['6 Unknown attributes', 'Malformed data can cross networks', 'Run code with RFC 7606 error handling; filter attributes you do not use at the edge', 'Every AS', 'Upgrade cycle'],
 ['7 Unprotected more-specifics', 'Sub-prefix hijack target', 'One ROA per announced prefix; aggregate where traffic engineering allows', 'Address holders', 'Minutes per prefix'],
 ['8 Loose maxLength', 'Forged-origin hijack becomes valid', 'Replace maxLength ROAs with exact-length ROAs (RFC 9319)', 'Address holders', 'Minutes per prefix'],
 ['9 Cache divergence', 'Validity depends on which cache answers', 'Two or more caches, different software, alert on count and serial drift', 'Router operators', 'A day'],
 ['10 Plain RTR', 'Validation feed can be tampered with or lost', 'Protected management network, SSH or TLS transport, alarm on total cache loss', 'Router operators', 'A day'],
 ['12 Origin conflicts', 'Stale and mistaken origins look like hijacks', 'Remove old provider announcements; ROAs for every origin that should announce; ROA updates with every lease or cloud move', 'Address holders and providers', 'Minutes per prefix'],
 ['11 Control plane', 'Hot CPU, queue drops, scan traffic reaching the router', 'CoPP, infrastructure ACL, GTSM, idle timeouts, BMP or streaming telemetry', 'Router operators', 'Days'],
])}

<h2>Proof that the fixes work: three clean blocks</h2>
<p>The same session checked three blocks that serve ordinary websites and cloud servers: a CDN block, a static-site hosting block and a public-cloud block. All three are what good looks like.</p>
{table(['Block', 'Operator', 'Paths', 'RPKI', 'More-specifics', 'Upstreams visible'], [
 ['104.21.32.0/20', 'Cloudflare (13335)', '16', 'all valid', 'none', 'direct peering with almost every network'],
 ['185.199.110.0/24', 'Fastly, serving GitHub Pages (54113)', '15', 'all valid', '(a /24: none possible)', 'direct peering, plus Internet2, RETN, Liberty Global'],
 ['150.136.0.0/16', 'Oracle Cloud (31898)', '15', 'all valid, maxLength 16', 'none', 'Arelion, NTT, Lumen, Cogent, GTT, Internet2'],
], num=(2,))}
<p>The Oracle block is the model case. Its ROA authorizes exactly the /16, at exactly length 16. If anyone announced a /24 inside it, every origin-validating carrier would mark it <strong>invalid</strong> on length alone and drop it. The block is also reachable through six independent upstreams, so there is no single provider to flood. A small business renting servers inside a block like this inherits that protection without owning an AS or writing a single ROA.</p>
{callout('<strong>The lesson for organizations that do not own address space:</strong> you inherit your providers\' routing security. Ask them three questions before you buy: Do you publish exact-length ROAs for the blocks I will use? Do you drop RPKI-invalid routes? How many upstreams carry my block? The answers are visible on a public collector, so you can check them yourself.')}

<h2>What still remains, and what comes next</h2>
<p>Origin validation answers one question: <em>is this origin allowed to announce this prefix?</em> It does not check the path. A forged-origin announcement of an exact-length prefix (pretending to be the real origin) still validates. Two newer standards close that gap and are worth tracking now:</p>
{table(['Technology', 'What it adds', 'Status'], [
 ['ASPA (Autonomous System Provider Authorization)', 'Each network publishes its legitimate upstream providers; routers reject paths that could not have happened', 'IETF draft with validator and router support emerging; publish ASPA objects as registries offer them'],
 ['BGP Roles and OTC (RFC 9234)', 'Sessions declare customer, peer or provider; an Only-To-Customer attribute stops route leaks automatically', 'Standard; supported in several open-source and commercial routers'],
 ['RPKI-based route-server filtering at IXPs', 'Exchange route servers drop invalid routes for all members at once', 'Widely deployed at major exchanges'],
])}

<h2>A 30-60-90 day plan</h2>
{table(['When', 'If you hold address space', 'If you rent it (cloud, CDN, ISP)'], [
 ['First 30 days', 'Publish exact-length ROAs for every announced prefix; remove maxLength', 'List every public block you depend on; check each one on a collector'],
 ['By 60 days', 'Enable origin validation (drop invalids); two RTR caches, monitored', 'Ask providers the three questions above; record the answers'],
 ['By 90 days', 'Strip internal and action communities; neutral aggregator IDs; daily collector monitoring with alerts', 'Set up free monitoring of those blocks and their more-specifics; review yearly at renewal'],
])}

<h2>The takeaway</h2>
<p>The routing table is the most honest security report on the Internet: anyone can read it, nobody can edit it, and it updates every second. Read once, it lists what is exposed. Read twice, it shows that the exposure shrinks wherever operators act. Each fix in this chapter costs minutes to days, and the result is enforced by the largest networks on the planet. That is the opportunity. <a href="/bgp/ch02-9-the-proposal-secure-peering" style="color:var(--accent)">Part 9</a> turns it into a concrete design.</p>
<p style="font-size:.95rem;color:var(--fg-dim)">Want this review run against your own address space or providers? Write to <a href="mailto:info@konstas.us" style="color:var(--accent)">info@konstas.us</a>.</p>
'''),
 ('ch02-9-the-proposal-secure-peering', 'The Proposal: Secure, Low-Exposure Peering',
  'A concrete design for peering that is more secure and exposes far less: layered controls, a reference architecture, a configuration template and a maturity path, mapped to every finding.', f'''
<blockquote>The findings showed what leaks and what can be forged. This part proposes the answer: a peering design built on three rules. Accept only what can be verified. Announce only what you own. Expose nothing that is not required for routing to work.</blockquote>

<h2>Design goals</h2>
{table(['Goal', 'Meaning', 'Findings it answers'], [
 ['Verified in', 'Every route accepted is checked for origin, and as standards mature, for path', '7, 8, 9, 10'],
 ['Minimal out', 'Announce only owned and customer prefixes, with nothing internal attached', '3, 4, 5'],
 ['Hardened sessions', 'A BGP session can only be formed by the intended peer, and cannot be overwhelmed', '6, 11'],
 ['Protected control plane', 'The router\'s CPU serves routing first; noise and the public never reach it', '11'],
 ['Observed without exposure', 'Full visibility for the operator, none for the public', '11, all'],
 ['Deliberate decisions', 'Exit selection and failover are policy, not tie-breakers', '1, 2'],
])}

<h2>Reference architecture</h2>
<figure style="margin:22px 0"><svg viewBox="0 0 900 470" role="img" aria-label="Secure peering reference architecture" style="width:100%;height:auto;display:block;background:hsl(0 0% 5%);border:1px solid hsl(43 45% 56% / .35);border-radius:10px;font-family:Inter,sans-serif">
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="hsl(43 45% 56%)"/></marker></defs>
<g font-size="13" fill="hsl(0 0% 92%)">
<rect x="30" y="24" width="190" height="56" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="125" y="48" text-anchor="middle">Transit providers</text><text x="125" y="66" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">two or more, diverse</text>
<rect x="355" y="24" width="190" height="56" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="450" y="48" text-anchor="middle">IXP route servers</text><text x="450" y="66" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">RPKI-filtered</text>
<rect x="680" y="24" width="190" height="56" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="775" y="48" text-anchor="middle">Private peers (PNI)</text><text x="775" y="66" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">large content networks</text>
<line x1="125" y1="80" x2="300" y2="140" stroke="hsl(43 45% 56%)" marker-end="url(#ar)"/><line x1="450" y1="80" x2="450" y2="140" stroke="hsl(43 45% 56%)" marker-end="url(#ar)"/><line x1="775" y1="80" x2="600" y2="140" stroke="hsl(43 45% 56%)" marker-end="url(#ar)"/>
<rect x="200" y="142" width="500" height="120" rx="10" fill="hsl(43 45% 56% / .10)" stroke="hsl(43 45% 56%)"/>
<text x="450" y="166" text-anchor="middle" font-size="15" fill="hsl(43 45% 56%)">Edge routers (two, separate sites)</text>
<text x="450" y="190" text-anchor="middle" font-size="12">Session: TCP-AO or MD5 · GTSM · iACL on TCP 179 · BGP Roles · max-prefix</text>
<text x="450" y="210" text-anchor="middle" font-size="12">Import: drop RPKI-invalid · ASPA · bogons · too-specific · own space · path sanity</text>
<text x="450" y="230" text-anchor="middle" font-size="12">Export: own and customer prefixes only · strip communities · neutral router ID</text>
<text x="450" y="250" text-anchor="middle" font-size="12">Control plane: CoPP · rate-limited ICMP · SSH only · AAA · idle timeouts</text>
<line x1="300" y1="262" x2="160" y2="330" stroke="hsl(43 45% 56%)" stroke-dasharray="4 3" marker-end="url(#ar)"/><line x1="450" y1="262" x2="450" y2="330" stroke="hsl(43 45% 56%)" stroke-dasharray="4 3" marker-end="url(#ar)"/><line x1="600" y1="262" x2="740" y2="330" stroke="hsl(43 45% 56%)" stroke-dasharray="4 3" marker-end="url(#ar)"/>
<rect x="40" y="332" width="240" height="72" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="160" y="356" text-anchor="middle">RPKI validators ×2</text><text x="160" y="374" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">different software</text><text x="160" y="390" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">RTR over SSH, management VRF</text>
<rect x="330" y="332" width="240" height="72" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="450" y="356" text-anchor="middle">Private BMP collector</text><text x="450" y="374" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">plus streaming telemetry</text><text x="450" y="390" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">no public login on the edge</text>
<rect x="620" y="332" width="240" height="72" rx="8" fill="hsl(0 0% 8%)" stroke="hsl(0 0% 40%)"/><text x="740" y="356" text-anchor="middle">External watch</text><text x="740" y="374" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">public collectors, hijack alerts</text><text x="740" y="390" text-anchor="middle" font-size="11" fill="hsl(0 0% 62%)">your prefixes, daily</text>
<text x="450" y="440" text-anchor="middle" font-size="12" fill="hsl(0 0% 62%)">Solid: BGP sessions. Dashed: out-of-band validation and monitoring, never reachable from the Internet.</text>
</g></svg><figcaption style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">Reference design: what enters, what leaves, and how the edge is watched without being exposed.</figcaption></figure>

<h2>The controls, layer by layer</h2>
{table(['Layer', 'Control', 'Stops', 'Standard'], [
 ['Identity', 'Exact-length ROAs for every announced prefix, no maxLength', 'Sub-prefix and forged-origin hijacks', 'RFC 6480, RFC 9319'],
 ['Identity', 'ASPA objects listing your real upstream providers', 'Forged paths and many leaks', 'IETF ASPA draft'],
 ['Identity', 'IRR route objects and PeeringDB records that match reality', 'Being filtered by careful peers', 'MANRS'],
 ['Session', 'TCP-AO (or MD5 where AO is not supported)', 'Spoofed resets and injected sessions', 'RFC 5925'],
 ['Session', 'GTSM (<code>ttl-security hops 1</code>) on direct peerings', 'Remote attacks on TCP 179', 'RFC 5082'],
 ['Session', 'Infrastructure ACL: TCP 179 only from configured neighbors', 'Scans and floods against BGP', 'BCP 194'],
 ['Session', 'BGP Roles with strict mode', 'Route leaks between providers and peers', 'RFC 9234'],
 ['Session', 'Maximum-prefix limit per neighbor, with warning threshold', 'A peer leaking a full table into a peering session', 'BCP 194'],
 ['Import', 'Drop RPKI-invalid; later, ASPA-invalid', 'Hijacks and leaks other networks did not stop', 'RFC 6811, RFC 8893'],
 ['Import', 'Drop bogon prefixes and ASNs, prefixes longer than /24 (IPv4) or /48 (IPv6), your own space, absurd paths', 'Garbage, hijack shapes, loops', 'BCP 194'],
 ['Import', 'RFC 7606 error handling on current software', 'Malformed attributes resetting sessions', 'RFC 7606'],
 ['Export', 'Explicit prefix list of own and customer routes only', 'Accidental leaks of learned routes', 'MANRS'],
 ['Export', 'Delete internal and informational communities; ask upstreams to strip action communities', 'Publishing business relationships and intent', 'Best practice'],
 ['Export', 'Public loopback as router ID; no AGGREGATOR with internal addresses', 'Internal addressing disclosure', 'Best practice'],
 ['Export', 'Prepend three times or fewer; steer with upstream communities', 'Long paths that are easy to undercut', 'Best practice'],
 ['Control plane', 'CoPP, rate-limited ICMP, management in a separate VRF or out-of-band', 'Background noise and floods reaching the CPU', 'Vendor guides'],
 ['Control plane', 'SSH only, AAA with per-command authorization, idle timeouts, no public CLI on the edge', 'Credential theft, line exhaustion, information leaks', 'Vendor guides'],
 ['Validation', 'Two validators from different implementations, RTR over SSH on the management network, alarms on divergence and total loss', 'A single bad or missing cache disabling validation', 'RFC 8210'],
 ['Visibility', 'BMP to a private collector and streaming telemetry; external watch of your prefixes on public collectors', 'Flying blind, or exposing a looking glass to learn what you already know', 'RFC 7854'],
 ['Hygiene', 'Anti-spoofing on customer edges (source address validation)', 'Your network being used for reflection attacks', 'BCP 38, MANRS'],
])}

<h2>Peering strategy: better, not only safer</h2>
{table(['Choice', 'Why it is better'], [
 ['Two or more transit providers, on separate routers and sites', 'No single upstream to flood or lose; the clean public-cloud block in Part 8 had six'],
 ['IXP route servers with RPKI filtering', 'Many peers in one session, with invalid routes already removed by the exchange'],
 ['Private interconnects with the largest content networks', 'Shorter, more predictable paths for most traffic, as the one-hop paths to Google and Cloudflare showed'],
 ['Local preference by relationship: customer &gt; peer &gt; transit', 'Traffic follows the business, not the oldest session'],
 ['Graceful shutdown community before maintenance', 'Traffic moves off a session before it drops (RFC 8326)'],
 ['Join MANRS', 'A public commitment to filtering, anti-spoofing, coordination and validation that peers can check'],
])}

<h2>A configuration template</h2>
<p>A compact FRRouting example of the import and export policy for one transit session. The same structure maps directly to IOS XR, Junos or BIRD.</p>
{term('''
! FRRouting example. Documentation addresses (RFC 5737) and ASNs (RFC 5398).
rpki
 rpki cache 10.0.0.10 3323 preference 1        ! validator A, management network
 rpki cache 10.0.0.11 3323 preference 2        ! validator B, different software
exit
!
router bgp 64500
 bgp router-id 192.0.2.1                         ! public loopback, not an internal address
 neighbor 198.51.100.1 remote-as 64510
 neighbor 198.51.100.1 description TRANSIT-A
 neighbor 198.51.100.1 ttl-security hops 1       ! GTSM: only a directly connected peer
 neighbor 198.51.100.1 password <secret>         ! TCP-AO where both sides support it
 neighbor 198.51.100.1 local-role customer strict ! RFC 9234: leak prevention
 address-family ipv4 unicast
  neighbor 198.51.100.1 route-map TRANSIT-IN in
  neighbor 198.51.100.1 route-map EDGE-OUT out
  neighbor 198.51.100.1 maximum-prefix 1200000 90
 exit-address-family
!
ip prefix-list OWN       seq 5  permit 192.0.2.0/24           ! exactly what we announce
ip prefix-list BOGONS    seq 5  permit 10.0.0.0/8 le 32       ! plus the full bogon list
ip prefix-list TOO-LONG  seq 5  permit 0.0.0.0/0 ge 25 le 32
bgp community-list standard INTERNAL permit 64500:1000      ! our informational tags
bgp as-path access-list LONG-PATH seq 5 permit (_[0-9]+){50,}
!
route-map TRANSIT-IN deny 10
 match rpki invalid                              ! origin validation
route-map TRANSIT-IN deny 20
 match ip address prefix-list BOGONS
route-map TRANSIT-IN deny 30
 match ip address prefix-list TOO-LONG
route-map TRANSIT-IN deny 40
 match ip address prefix-list OWN                ! our own space never comes from outside
route-map TRANSIT-IN deny 50
 match as-path LONG-PATH
route-map TRANSIT-IN permit 100
!
route-map EDGE-OUT permit 10
 match ip address prefix-list OWN                ! announce only what we own
 set comm-list INTERNAL delete                   ! publish nothing internal
route-map EDGE-OUT deny 100
''')}
<p>Two lines in it carry most of the value: <code>match rpki invalid</code> on the way in and <code>match ip address prefix-list OWN</code> on the way out. Everything else narrows what can go wrong.</p>

<h2>Every finding, answered</h2>
{table(['#', 'Finding', 'Answered by'], [
 ['1', 'Best path by tie-breaker', 'Local preference by relationship'],
 ['2', 'Content one hop away', 'Private interconnects and route servers'],
 ['3', 'Communities reveal the business', 'Delete informational communities on export'],
 ['4', 'Action communities published', 'Ask upstreams to strip them after use'],
 ['5', 'AGGREGATOR exposes internal routers', 'Public loopback router ID, no internal AGGREGATOR'],
 ['6', 'Unknown attributes pass through', 'Current software with RFC 7606; filter unused attributes'],
 ['7', 'Prepends and unprotected more-specifics', 'Exact ROAs for every prefix; three prepends or fewer'],
 ['8', 'Loose maxLength', 'Exact-length ROAs (RFC 9319)'],
 ['9', 'Caches disagree', 'Two validators, different software, divergence alarms'],
 ['10', 'Plain RTR', 'RTR over SSH on the management network'],
 ['11', 'Hot, reachable control plane', 'CoPP, iACL, GTSM, idle timeouts, BMP instead of a public CLI'],
])}

<h2>Maturity path</h2>
{table(['Level', 'What is in place', 'Typical time'], [
 ['1 · Baseline', 'Exact ROAs, explicit export lists, bogon and too-specific filters, max-prefix, GTSM, iACL, CoPP, SSH and AAA', '30 days'],
 ['2 · Validated', 'Origin validation enforced, two validators, RTR protected, communities scrubbed, neutral router IDs, external prefix monitoring, MANRS', '60 to 90 days'],
 ['3 · Assured', 'TCP-AO, BGP Roles strict, ASPA published and verified, BMP and streaming telemetry, graceful shutdown in every maintenance', 'Within a year'],
])}

<h2>For organizations that do not run BGP</h2>
<p>Most businesses never configure a BGP session; they rent addresses from cloud, CDN and access providers. The same principles still apply, one level up:</p>
<ul>
 <li><strong>Choose providers by routing security:</strong> exact-length ROAs, origin validation enforced, several upstreams. All three are visible on a public collector.</li>
 <li><strong>Expose nothing you do not have to:</strong> put public services behind a CDN, keep management interfaces reachable only through a VPN, and close every port that is not serving users.</li>
 <li><strong>Watch your blocks:</strong> free alerting on the prefixes you depend on tells you about a hijack before your users do.</li>
</ul>

<h2>The takeaway</h2>
<p>Secure peering is not one product; it is a short list of controls that each close one gap found in this chapter. Verify what comes in, announce only what you own, keep everything internal inside, and watch from the outside. Done together, they turn a router that tells the world about your business into one that tells it only where your addresses are, which is all BGP ever needed to say.</p>
<p style="font-size:.95rem;color:var(--fg-dim)">To have this design reviewed against your own network or providers, write to <a href="mailto:info@konstas.us" style="color:var(--accent)">info@konstas.us</a>.</p>
'''),
 ('ch02-10-the-session-command-by-command', 'The Session, Command by Command',
  'The recorded Route Views session, step by step: eleven read-only commands, their real output, what each shows and why it matters.', '''
<blockquote>The recorded session, one command at a time: the exact command, the real output, what you are looking at, and why it matters. Every command is read-only and works on the public login, so you can repeat each step yourself.</blockquote>
<video controls playsinline preload="metadata" poster="/bgp/ch02/poster.jpg" style="display:block;width:100%;height:auto;border:1px solid hsl(43 45% 56% / .35);border-radius:10px;background:#000">
  <source src="/bgp/ch02/route-views-field-report.mp4" type="video/mp4">
</video>
<p style="font-size:.85rem;color:var(--fg-dim);margin-top:8px">Session recorded 3 November 2026 on <code>route-views.routeviews.org</code> (username <code>rviews</code>). Start with <code>terminal length 0</code>. In commands 3, 7 and 8, each path's RPKI line is folded onto the path it belongs to.</p>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 1 of 11</p>
<h2 style="margin:0 0 12px">The size of the Internet and its RPKI posture</h2>
<pre><code>route-views&gt; show ip bgp summary | include table version|RPKI|network entries|BGP using
BGP table version is 1517822914, main routing table version 1517822914
Path RPKI states: 11656636 valid, 4793762 not found, 5344 invalid
1129444 network entries using 280102112 bytes of memory
BGP using 3150829866 total bytes of memory</code></pre>
<p><strong>What you see.</strong> The table version counts every best-path change since BGP started: over 1.5 billion. Of 16.4 million IPv4 paths, 11.66 million (70.8%) are RPKI-valid, 4.79 million (29.1%) have no ROA, and 5,344 (0.03%) contradict one. The collector holds 1,129,444 IPv4 networks in 3.15 GB of memory.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> This is the Internet's security score in one line. Two thirds of paths are now cryptographically checkable, and the invalid share is tiny because most large carriers drop invalid routes.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 2 of 11</p>
<h2 style="margin:0 0 12px">IPv6 is better protected than IPv4</h2>
<pre><code>route-views&gt; show bgp ipv6 unicast summary | include RPKI|network entries
Path RPKI states: 2314874 valid, 472953 not found, 1425 invalid
263194 network entries using 71588768 bytes of memory</code></pre>
<p><strong>What you see.</strong> The IPv6 table: 263,194 networks, 2.31 million valid paths (83.0%), 472,953 not found (17.0%), 1,425 invalid (0.05%).</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> IPv6 space was allocated after RPKI existed, and it is twelve points better protected than IPv4. If you run IPv6, publishing ROAs is the easiest win you have.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 3 of 11</p>
<h2 style="margin:0 0 12px">Fifteen paths to Google DNS, and why one wins</h2>
<pre><code>route-views&gt; show ip bgp 8.8.8.8 | include Paths|^  [0-9]|best|RPKI
Paths: (15 available, best #9, table default)
  1351 214292 15169                               RPKI valid
  3303 15169                                      RPKI valid
  8283 15169                                      RPKI valid
  3356 15169                                      RPKI valid
  20130 6939 15169                                RPKI valid
  3549 3356 15169                                 RPKI valid
  57866 15169                                     RPKI valid
  20912 15169                                     RPKI valid
  101 15169                                       RPKI valid
      Origin IGP, localpref 100, valid, external, best
  3333 1257 15169                                 RPKI valid
  4826 15169                                      RPKI valid
  7018 15169                                      RPKI valid
  49788 12552 15169                               RPKI valid
  6939 15169                                      RPKI valid
  2497 15169                                      RPKI valid</code></pre>
<p><strong>What you see.</strong> Fifteen paths to 8.8.8.0/24, every one RPKI-valid. Ten are two hops (provider, then Google AS 15169); five go through one more network. Path #9, through the University of Washington (AS 101), is marked <code>best</code>.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> With equal preference and length, BGP falls through to tie-breakers such as route age. The best path is the oldest stable one, not the fastest. In your own network, set local preference on purpose.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 4 of 11</p>
<h2 style="margin:0 0 12px">Cloudflare: one prefix, no more-specifics, all valid</h2>
<pre><code>route-views&gt; show ip bgp 1.1.1.0/24 longer-prefixes
BGP table version is 1517823485, local router ID is 128.223.51.103
Status codes: s suppressed, d damped, h history, * valid, &gt; best, i - internal,
              r RIB-failure, S Stale, m multipath, b backup-path, f RT-Filter,
              x best-external, a additional-path, c RIB-compressed,
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI validation codes: V valid, I invalid, N Not found
     Network          Next Hop            Metric LocPrf Weight Path
V*   1.1.1.0/24       132.198.255.253                        0 1351 13335 i
V*                    217.192.89.50                          0 3303 3356 13335 i
V*                    94.142.247.3                           0 8283 13335 i
V*                    208.51.134.254           0             0 3549 3356 13335 i
V*                    4.68.4.46                0             0 3356 13335 i
V*                    140.192.8.16                           0 20130 23352 13335 i
V*                    162.251.163.2                          0 53767 13335 i
V*                    209.124.176.223                        0 101 13335 i
V*                    77.39.192.30                           0 20912 13335 i
V*                    193.0.0.56                             0 3333 13335 i
V*                    37.139.139.17            0             0 57866 13335 i
V*&gt;                   12.0.1.63                              0 7018 13335 i
V*                    114.31.199.16                          0 4826 13335 i
V*                    91.218.184.60                          0 49788 13335 i
V*                    64.71.137.241                          0 6939 3356 13335 i
V*                    202.232.0.2                            0 2497 13335 i</code></pre>
<p><strong>What you see.</strong> Only one entry: 1.1.1.0/24 itself, sixteen paths, all <code>V</code>alid, no more-specifics. Twelve paths are direct to Cloudflare (AS 13335); AT&amp;T's path is best (<code>&gt;</code>).</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> This is what good looks like: an exact-length ROA and nobody announcing a smaller block inside it. Run the same command on your own prefixes; any extra line is a leak or a hijack.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 5 of 11</p>
<h2 style="margin:0 0 12px">Leaked internal router IDs in the AGGREGATOR attribute</h2>
<pre><code>route-views&gt; show ip bgp 1.1.1.0/24 | include aggregated
  1351 13335, (aggregated by 13335 10.34.2.204)
  3303 3356 13335, (aggregated by 13335 10.34.23.128)
  8283 13335, (aggregated by 13335 10.34.6.80)
  3549 3356 13335, (aggregated by 13335 10.34.0.16)
  3356 13335, (aggregated by 13335 10.34.9.112)
  20130 23352 13335, (aggregated by 13335 10.34.3.248)
  53767 13335, (aggregated by 13335 10.34.24.72)
  101 13335, (aggregated by 13335 10.34.9.112)
  20912 13335, (aggregated by 13335 10.34.130.16)
  3333 13335, (aggregated by 13335 10.34.6.80)
  57866 13335, (aggregated by 13335 10.34.6.80)
  7018 13335, (aggregated by 13335 10.34.2.204)
  4826 13335, (aggregated by 13335 10.34.8.168)
  49788 13335, (aggregated by 13335 10.34.130.6)
  6939 3356 13335, (aggregated by 13335 10.34.0.16)
  2497 13335, (aggregated by 13335 10.34.7.24)</code></pre>
<p><strong>What you see.</strong> Each path names the router that built the aggregate: eleven different 10.34.x.x addresses across sixteen paths.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> The AGGREGATOR attribute leaks private router IDs and shows how many sites announce this anycast prefix. If you aggregate, check what your router puts in this field.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 6 of 11</p>
<h2 style="margin:0 0 12px">A loose ROA: only two of four /24s announced, all four authorized</h2>
<pre><code>route-views&gt; show ip bgp 1.6.0.0/22 longer-prefixes | include /2
V*   1.6.0.0/22       209.124.176.223                        0 101 11164 4637 64049 55836 9583 i
V*   1.6.1.0/24       209.124.176.223                        0 101 11164 4637 64049 55836 9583 i
V*   1.6.2.0/24       209.124.176.223                        0 101 11164 4637 64049 55836 9583 i</code></pre>
<p><strong>What you see.</strong> Three entries inside 1.6.0.0/22: the /22 and two /24s (1.6.1.0 and 1.6.2.0). The filter shows one line per prefix. 1.6.0.0/24 and 1.6.3.0/24 are not announced, yet the ROA (maxLength 24) authorizes all four.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> Anyone forging AS 9583 as the origin could announce the two missing /24s, and they would be RPKI-valid and win on longest match. Fix: exact-length ROAs only (RFC 9319).</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 7 of 11</p>
<h2 style="margin:0 0 12px">Not a hijack: a prepend typing error (AS 3 appended)</h2>
<pre><code>route-views&gt; show ip bgp 103.182.177.0/24 | include ^  [0-9]|RPKI
  1351 64049 55836 9583 133296                    RPKI valid
  3303 2914 9583 133296                           RPKI valid
  3356 64049 55836 9583 133296                    RPKI valid
  3549 3356 64049 55836 9583 133296               RPKI valid
  8283 64049 55836 9583 133296                    RPKI valid
  57866 50673 133296 133296 133296 133296 133296  RPKI valid
  20130 6939 64049 55836 9583 133296              RPKI valid
  20912 9002 2914 9583 133296                     RPKI valid
  101 11164 4637 64049 55836 9583 133296          RPKI valid
  3333 64049 55836 9583 133296                    RPKI valid
  4826 64049 55836 9583 133296                    RPKI valid
  7018 2914 9583 133296                           RPKI valid
  49788 12552 6797 9498 133296 3                  RPKI invalid
  2497 2914 9583 133296                           RPKI valid
  6939 64049 55836 9583 133296                    RPKI valid</code></pre>
<p><strong>What you see.</strong> Fourteen valid paths end in the real origin, AS 133296. One, through AS 49788, ends <code>133296 3</code> and is <strong>invalid</strong>: AS 3 appears as the origin.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> AS 3 is a university that would never originate this prefix. Someone meant "prepend three times" and typed the number as an AS. A mistake, not an attack, and RPKI stopped it after one hop.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 8 of 11</p>
<h2 style="margin:0 0 12px">Not a hijack: a provider still announcing leased space</h2>
<pre><code>route-views&gt; show ip bgp 8.236.0.0/15 | include ^  [0-9]|RPKI
  1351 214292 15169 396982                        RPKI valid
  8283 15169 396982                               RPKI valid
  3303 15169 396982                               RPKI valid
  3356                                            RPKI invalid
  3549 3356                                       RPKI invalid
  20130 6939 3356                                 RPKI invalid
  20912 15169 396982                              RPKI valid
  57866 15169 396982                              RPKI valid
  101 15169 396982                                RPKI valid
  3333 1257 15169 396982                          RPKI valid
  4826 15169 396982                               RPKI valid
  7018 15169 396982                               RPKI valid
  49788 12552 15169 396982                        RPKI valid
  6939 3356                                       RPKI invalid
  2497 15169 396982                               RPKI valid</code></pre>
<p><strong>What you see.</strong> Eleven paths end in Google Cloud (AS 396982) and are valid. Four end in Lumen (AS 3356) and are invalid, all of them through Lumen.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> 8.236.0.0/15 is part of Lumen's 8.0.0.0/8 and has been leased to Google Cloud, which holds the ROA. Lumen's old announcement was never withdrawn. Stale, not malicious; the fix is one line in Lumen's configuration.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 9 of 11</p>
<h2 style="margin:0 0 12px">The RPKI caches behind origin validation</h2>
<pre><code>route-views&gt; show ip bgp rpki servers | include neighbor is|Prefixes|attempts|failures
BGP SOVC neighbor is 128.223.157.83/3323 connected to port 3323
  Prefixes 1029922
  Connection attempts: 1920
  Connection failures: 1390
BGP SOVC neighbor is 128.223.157.89/3323 connected to port 3323
  Prefixes 1165839
  Connection attempts: 3046
  Connection failures: 2958</code></pre>
<p><strong>What you see.</strong> Two RPKI caches, both connected. They hold 1,029,922 and 1,165,839 entries, about 136,000 apart. Lifetime failure counts are 1,390 of 1,920 and 2,958 of 3,046 connection attempts.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> Origin validation is only as good as its cache. Run at least two validators from different software, protect the RTR session, and alert when they disagree.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 10 of 11</p>
<h2 style="margin:0 0 12px">The collector under load</h2>
<pre><code>route-views&gt; show processes cpu | include CPU utilization
CPU utilization for five seconds: 42%/1%; one minute: 43%; five minutes: 36%</code></pre>
<p><strong>What you see.</strong> CPU at 42% over five seconds, 43% over one minute and 36% over five minutes. An hour earlier, during the telemetry run, the same command showed 85-100%.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> Load swings with BGP churn and with the number of people querying the public login. Production routers keep monitoring off the control plane with BMP or streaming telemetry.</p>
</div>
<div style="border:1px solid hsl(43 45% 56% / .28);border-radius:10px;padding:16px 18px;margin:26px 0;background:hsl(0 0% 5%)">
<p style="margin:0 0 4px;font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;color:var(--accent)">Command 11 of 11</p>
<h2 style="margin:0 0 12px">Internet background radiation hitting the router</h2>
<pre><code>route-views&gt; show ip traffic | include no port|echo reply
        248400084 echo, 8852167 echo reply, 1360 mask requests, 0 mask replies, 0 quench
  Sent: 0 redirects, 6527233 unreachable, 10679955 echo, 248400084 echo reply
  Rcvd: 3301919288 total, 522 checksum errors, 3299988430 no port 0 finput
  Rcvd: 2882788712 total, 39971 checksum errors, 20694751 no port</code></pre>
<p><strong>What you see.</strong> ICMP: 248.4 million echo requests received and answered. UDP: 3.30 billion packets received, 3.2999 billion to ports nothing listens on. TCP: 2.88 billion received, 20.7 million to closed ports.</p>
<p style="margin-bottom:0"><strong>Why it matters.</strong> This is the background noise every public address receives. All of it reaches a router's CPU unless control-plane policing and an infrastructure ACL filter it first.</p>
</div>
<h2>The session in one table</h2>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Command</th><th>Result</th></tr></thead><tbody><tr><td>1</td><td>Size and RPKI posture</td><td>70.8% valid, 5,344 invalid</td></tr><tr><td>2</td><td>IPv6 posture</td><td>83.0% valid</td></tr><tr><td>3</td><td>Best path to Google DNS</td><td>tie-breaker, not quality</td></tr><tr><td>4</td><td>Cloudflare more-specifics</td><td>none: textbook</td></tr><tr><td>5</td><td>AGGREGATOR</td><td>11 internal router IDs exposed</td></tr><tr><td>6</td><td>Loose ROA</td><td>2 unannounced /24s pre-authorized</td></tr><tr><td>7</td><td>Typing error</td><td>AS 3 as origin, contained</td></tr><tr><td>8</td><td>Stale provider route</td><td>Lumen still announces leased space</td></tr><tr><td>9</td><td>RPKI caches</td><td>136,000 entries apart</td></tr><tr><td>10</td><td>CPU</td><td>36-43% now, 85-100% earlier</td></tr><tr><td>11</td><td>Background noise</td><td>3.3 billion UDP to closed ports</td></tr></tbody></table></div>
<p>Each result is explained in depth in Parts 2 to 9, the fixes are in <a href="/bgp/ch02-9-the-proposal-secure-peering" style="color:var(--accent)">Part 9</a>, and the conclusions and recommendations in <a href="/bgp/ch02-11-conclusion-and-recommendations" style="color:var(--accent)">Part 11</a>.</p>
'''),
 ('ch02-11-conclusion-and-recommendations', 'Conclusion and Recommendations',
  'What two live sessions on a public route collector prove, and a prioritized set of recommendations for network operators, organizations that rent address space, providers and exchanges, and collector operators.', f'''
<blockquote>Two read-only sessions on one public router, a few dozen commands, no access to any network we discussed. This part draws the conclusions and turns them into recommendations, in priority order.</blockquote>

<h2>Conclusions</h2>
{table(['#', 'Conclusion', 'Evidence'], [
 ['1', '<strong>The routing table is public, and it is a security report.</strong> Business relationships, traffic engineering, internal addressing and security gaps are readable by anyone, for any network.', 'Communities (Finding 3), action communities (4), AGGREGATOR router IDs (5), prepends and more-specifics (7)'],
 ['2', '<strong>RPKI works, and it is winning.</strong> Seven in ten IPv4 paths and more than eight in ten IPv6 paths are now valid; invalid announcements reach about one feed in fourteen.', 'Parts 7 and 8: 70.8% and 83.0% valid today; invalid paths down 70% since October 2021'],
 ['3', '<strong>Most "hijacks" are mistakes.</strong> Of 1,329 conflicting origins, none had the shape of a deliberate attack; the real conflicts were stale provider routes, cloud announcements and typing errors.', 'Part 7: 64% authorized, 33% unjudgeable, 3.5% contained misconfiguration, no route leaks in the sample'],
 ['4', '<strong>Origin validation has blind spots.</strong> It does not check paths, it is weakened by loose maxLength, and it depends on caches that can disagree or disappear.', 'Findings 8, 9 and 10; the one-third of conflicts with no ROA at all'],
 ['5', '<strong>The control plane is the soft target.</strong> A full-table router is CPU- and memory-bound, and the Internet throws billions of unsolicited packets at it.', 'Part 6: CPU 36-100%, input-queue drops, 3.3 billion UDP packets to closed ports'],
 ['6', '<strong>The fixes are cheap and verifiable.</strong> Almost every gap closes with minutes to days of work, and every fix can be checked from the same public login.', 'Parts 8 and 9'],
])}

<h2>Recommendations, in priority order</h2>
{table(['Priority', 'Recommendation', 'Closes', 'Effort'], [
 ['1', 'Publish an <strong>exact-length ROA</strong> for every prefix you announce; remove maxLength', 'Sub-prefix and forged-origin hijacks (7, 8)', 'Minutes per prefix'],
 ['2', '<strong>Drop RPKI-invalid routes</strong> on every external session', 'Hijacks and leaks others did not stop (12)', 'Hours'],
 ['3', 'Announce from an <strong>explicit export list</strong> only, with internal communities deleted', 'Leaks and business disclosure (3, 4)', 'Hours'],
 ['4', 'Protect every session: <strong>GTSM, TCP-AO or MD5, infrastructure ACL, maximum-prefix</strong>', 'Session attacks and floods (11)', 'Hours to days'],
 ['5', 'Put <strong>CoPP</strong> in front of the router CPU and keep management out-of-band', 'Control-plane overload (11)', 'Days'],
 ['6', 'Run <strong>two RPKI validators</strong> from different software, RTR protected, divergence alarms', 'Cache disagreement and loss (9, 10)', 'A day'],
 ['7', '<strong>Monitor your prefixes</strong> and their more-specifics on public collectors, with alerts', 'Undetected hijacks and leaks (all)', 'An afternoon'],
 ['8', 'Remove <strong>stale origins</strong>: old provider announcements, leased space, cloud BYOIP without ROAs', 'Self-inflicted invalids (12)', 'Minutes per prefix'],
 ['9', 'Set <strong>local preference by relationship</strong> and use upstream communities instead of long prepends', 'Accidental path selection (1, 7)', 'Hours'],
 ['10', 'Adopt <strong>BGP Roles</strong> now and publish <strong>ASPA</strong> as registries support it', 'Route leaks and forged paths', 'Within a year'],
])}

<h2>By audience</h2>
{table(['If you are…', 'Start with', 'Then'], [
 ['A network that runs BGP', 'Recommendations 1 to 4 this month', '5 to 10 over the next quarter; join MANRS to make the commitment public'],
 ['An organization renting addresses (cloud, CDN, ISP)', 'List every block you depend on and check it on a collector', 'Ask providers about exact ROAs, invalid filtering and upstream diversity; monitor those blocks'],
 ['A transit provider or cloud', 'Withdraw announcements for space you have delegated or leased; ROAs for customer BYOIP', 'Strip customers\' action communities after acting on them; neutral aggregator IDs'],
 ['An Internet exchange', 'RPKI filtering on route servers', 'BGP Roles and maximum-prefix on every member session'],
 ['A security team (SOC)', 'Add BGP alerts for your prefixes to the incident playbook', 'Treat a new origin or more-specific for your space as a priority incident'],
])}

<h2>For public collector operators</h2>
<p>Route Views is a public good, and this chapter could not exist without it. Three small, respectful suggestions emerged from the telemetry: an <strong>idle timeout</strong> on public terminal lines (one session had been idle for over a year), restricting <strong><code>show users</code></strong> so the public cannot see each other\'s addresses, and a pointer to the <strong>BMP and archive feeds</strong> for heavy queries, to keep interactive load off a busy control plane.</p>

<h2>Limits of this report</h2>
<ul>
 <li>Two snapshots from one collector, five years apart: Chapter 1\'s capture of 17 October 2021 and the sessions of 3 November 2026. Peer mixes differ between them, so we compare shares, not counts.</li>
 <li>RPKI states are this router\'s view; other validators may differ slightly at any moment.</li>
 <li>The leak scan covered the paths collected here, not the full table.</li>
 <li>No intent is attributed to any network. Conflicts were classified by evidence; where the evidence was insufficient, we said so.</li>
</ul>

{callout('<strong>Final word.</strong> BGP was built on trust, and the routing table still shows what that trust exposes. It also shows something more important: where networks publish what they own, validate what they accept and announce only what they should, the problems shrink, visibly, from one session to the next. Every network can make that change, and every change can be verified from a public login.')}
<p style="font-size:.95rem;color:var(--fg-dim)">For a review of your own address space, providers or peering design, write to <a href="mailto:info@konstas.us" style="color:var(--accent)">info@konstas.us</a>.</p>
'''),
]

# ---------------------------------------------------------------------------------------------
def page(i, slug, title, desc, body):
    n = len(PARTS)
    url = f'{SITE}/bgp/{slug}'
    full = f'{CH} · Part {i} of {n}: {title}'
    head_end = TEMPLATE.index('</head>'); head, rest = TEMPLATE[:head_end], TEMPLATE[head_end:]
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title)} — {SERIES}, Chapter {NUM} — Konstas Engineering Notes</title>', head)
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
    a = 'style="color:var(--accent);text-decoration:none"'
    prev_link = f'<a href="/bgp/{PARTS[i-2][0]}" {a}>&larr; Part {i-1}: {PARTS[i-2][1]}</a>' if i > 1 else f'<a href="/bgp/ch01-5-what-is-exposed" {a}>&larr; Chapter 1</a>'
    next_link = f'<a href="/bgp/{PARTS[i][0]}" {a}>Part {i+1}: {PARTS[i][1]} &rarr;</a>' if i < n else f'<a href="/bgp/" {a}>Series overview &rarr;</a>'
    nav = (f'<div style="display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin:34px 0 14px;padding-top:14px;'
           f'border-top:1px solid hsl(43 45% 56% / .25);font-size:.92rem">{prev_link}<span>{next_link}</span></div>')
    parts_list = ''.join(f'<li>{"<strong>" if j == i else ""}<a href="/bgp/{s}" style="color:{"var(--accent)" if j == i else "var(--fg-dim)"};text-decoration:none">Part {j}: {t}</a>{"</strong>" if j == i else ""}</li>'
                         for j, (s, t, _, _) in enumerate(PARTS, 1))
    pill = 'display:inline-block;margin:4px 6px 4px 0;padding:7px 14px;border:1px solid hsl(43 45% 56% / .55);border-radius:999px;color:var(--accent);text-decoration:none;font-size:.88rem'
    share = (f'<div style="margin:18px 0 6px"><a href="https://github.com/ikonstas70" style="{pill};background:hsl(43 45% 56% / .12)" rel="noopener">Follow on GitHub</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url, safe="")}" style="{pill}" rel="noopener" target="_blank">Share on LinkedIn</a>'
             f'<a href="https://twitter.com/intent/tweet?url={quote(url, safe="")}&amp;text={quote(SERIES + ": " + title)}" style="{pill}" rel="noopener" target="_blank">Share on X</a></div>')
    main = f'''<main>
    <span class="tag">{SERIES} &middot; Chapter {NUM} &middot; Part {i} of {n}</span>
    <h1>{html.escape(title)}</h1>
    <p class="meta">{CH} &middot; A field report from Route Views &middot; 3 November 2026 &middot; Ioannis Alexander Konstas</p>
{body}
{nav}
<div style="border:1px solid hsl(43 45% 56% / .25);border-radius:8px;padding:12px 18px;margin:14px 0;background:hsl(0 0% 6%)">
  <p style="margin:0 0 6px;font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)">Chapter {NUM} &middot; {SHORT}</p>
  <ol style="margin:0;padding-left:20px;font-size:.92rem">{parts_list}</ol>
</div>
{share}
<p style="font-size:.85rem;color:var(--fg-dim)">All output is from Route Views, a public collector operated for exactly this purpose. Network names are from public registry data; community meanings are from the operators' public documentation and may change. More chapters: <a href="/bgp/" style="color:var(--accent)">see the series</a>. Text &copy; 2026 Ioannis Alexander Konstas; code samples under the <a href="/license">MIT License</a>.</p>
  </main>'''
    out = ROOT / 'bgp' / f'{slug}.html'
    out.write_text(head + pre + main + post)
    return out

if __name__ == '__main__':
    for i, (slug, title, desc, body) in enumerate(PARTS, 1):
        print('built', page(i, slug, title, desc, body).relative_to(ROOT))
