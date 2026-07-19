# IPv6 Addressing Schema — CCIE Enterprise Infrastructure Lab

## IPv6 Loopbacks (2001:db8:ff:X::Y/128)

| Router     | IPv6 Loopback0              |
|------------|-----------------------------|
| CORE-1     | 2001:db8:ff:1::1/128        |
| CORE-2     | 2001:db8:ff:1::2/128        |
| CORE-3     | 2001:db8:ff:1::3/128        |
| CORE-4     | 2001:db8:ff:1::4/128        |
| EDGE-1     | 2001:db8:ff:2::1/128        |
| EDGE-2     | 2001:db8:ff:2::2/128        |
| EDGE-3     | 2001:db8:ff:2::3/128        |
| EDGE-4     | 2001:db8:ff:2::4/128        |
| BORDER-1   | 2001:db8:ff:3::1/128        |
| BORDER-2   | 2001:db8:ff:3::2/128        |
| HUB-WC-1   | 2001:db8:ff:4::1/128        |
| HUB-WC-2   | 2001:db8:ff:4::2/128        |
| SPK-WC-1   | 2001:db8:ff:4::11/128       |
| SPK-WC-2   | 2001:db8:ff:4::12/128       |
| SPK-WC-3   | 2001:db8:ff:4::13/128       |
| HUB-EC-1   | 2001:db8:ff:5::1/128        |
| HUB-EC-2   | 2001:db8:ff:5::2/128        |
| SPK-EC-1   | 2001:db8:ff:5::11/128       |
| SPK-EC-2   | 2001:db8:ff:5::12/128       |
| SPK-EC-3   | 2001:db8:ff:5::13/128       |
| CE-CORP-1  | 2001:db8:ff:6::1/128        |
| CE-CORP-2  | 2001:db8:ff:6::2/128        |

## IPv6 Point-to-Point Links (2001:db8:0:XY::/64)

| Link              | Subnet                  | Side A (::1) | Side B (::2) |
|-------------------|-------------------------|--------------|--------------|
| CORE-1 — CORE-2   | 2001:db8:0:12::/64      | CORE-1       | CORE-2       |
| CORE-1 — CORE-3   | 2001:db8:0:13::/64      | CORE-1       | CORE-3       |
| CORE-2 — CORE-4   | 2001:db8:0:24::/64      | CORE-2       | CORE-4       |
| CORE-3 — CORE-4   | 2001:db8:0:34::/64      | CORE-3       | CORE-4       |
| CORE-1 — EDGE-1   | 2001:db8:0:101::/64     | CORE-1       | EDGE-1       |
| CORE-2 — EDGE-2   | 2001:db8:0:102::/64     | CORE-2       | EDGE-2       |
| CORE-3 — EDGE-3   | 2001:db8:0:103::/64     | CORE-3       | EDGE-3       |
| CORE-4 — EDGE-4   | 2001:db8:0:104::/64     | CORE-4       | EDGE-4       |
| EDGE-1 — BORDER-1 | 2001:db8:0:201::/64     | EDGE-1       | BORDER-1     |
| EDGE-4 — BORDER-2 | 2001:db8:0:204::/64     | EDGE-4       | BORDER-2     |
| EDGE-1 — CE-CORP-1| 2001:db8:1:100::/64     | EDGE-1       | CE-CORP-1    |
| EDGE-4 — CE-CORP-2| 2001:db8:1:200::/64     | EDGE-4       | CE-CORP-2    |

## VRF IPv6 Space

| VRF    | IPv6 Prefix          |
|--------|----------------------|
| CORP   | 2001:db8:10::/48     |
| RETAIL | 2001:db8:20::/48     |

## IPv6 Routing

- OSPFv3 Process 1, Area 0 on backbone (CORE + EDGE routers)
- MP-BGP address-family ipv6 on PE routers
- 6PE: IPv6 labeled-unicast over MPLS backbone
- DHCPv6 prefix delegation: 2001:db8:pd::/48 pool
