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
<blockquote>Chapter 1 read the summary of a route collector. This chapter reads the routes themselves. Everything here comes from one public session on Route Views (AS 6447) and seven commands. The output is real; the interpretation is the point.</blockquote>

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
<p>The next four parts take the findings one by one, with the output that proves each.</p>
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
<p><code>show ip bgp community 3356:2</code> lists everything Lumen tagged with its Europe region value: Cloudflare via Swisscom, China Telecom (AS 4134) and Akamai (AS 20940) space among them. A single community query reconstructs which networks a carrier hears in a region. That is the basis for mapping any network\'s connectivity from the outside, the subject of Chapter 3.</p>
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
<p>Seven commands showed how BGP chooses among equal paths, how carriers label routes by region and relationship, how a content network\'s policy and internal addressing leak through attributes, how prepends and more-specifics shape traffic, and where RPKI is strong and where it is thin. None of it required access to any of those networks. Next: mapping a network from the outside.</p>
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
