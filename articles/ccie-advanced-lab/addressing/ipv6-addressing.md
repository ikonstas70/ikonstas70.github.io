# IPv6 Addressing Plan — Advanced CCIE RS Lab

## Design Principles
- Full dual-stack deployment across MPLS backbone and DMVPN regions
- OSPFv3 area 0 for backbone IPv6 routing
- 6PE for carrying IPv6 prefixes over MPLS (labeled-unicast)
- DMVPN tunnels carry both IPv4 (EIGRP) and IPv6 (EIGRPv6 named mode)

## Loopback Interfaces (2001:db8:ff:ZONE::ROUTER-ID/128)

| Router     | Zone Code | IPv6 Loopback                |
|------------|-----------|------------------------------|
| CORE-1     | 1         | 2001:db8:ff:1::1/128         |
| CORE-2     | 1         | 2001:db8:ff:1::2/128         |
| CORE-3     | 1         | 2001:db8:ff:1::3/128         |
| CORE-4     | 1         | 2001:db8:ff:1::4/128         |
| EDGE-1     | 2         | 2001:db8:ff:2::1/128         |
| EDGE-2     | 2         | 2001:db8:ff:2::2/128         |
| EDGE-3     | 2         | 2001:db8:ff:2::3/128         |
| EDGE-4     | 2         | 2001:db8:ff:2::4/128         |
| BORDER-1   | 3         | 2001:db8:ff:3::1/128         |
| BORDER-2   | 3         | 2001:db8:ff:3::2/128         |
| HUB-WC-1   | 4         | 2001:db8:ff:4::1/128         |
| HUB-WC-2   | 4         | 2001:db8:ff:4::2/128         |
| SPK-WC-1   | 4         | 2001:db8:ff:4::11/128        |
| SPK-WC-2   | 4         | 2001:db8:ff:4::12/128        |
| SPK-WC-3   | 4         | 2001:db8:ff:4::13/128        |
| HUB-EC-1   | 5         | 2001:db8:ff:5::1/128         |
| HUB-EC-2   | 5         | 2001:db8:ff:5::2/128         |
| SPK-EC-1   | 5         | 2001:db8:ff:5::11/128        |
| SPK-EC-2   | 5         | 2001:db8:ff:5::12/128        |
| SPK-EC-3   | 5         | 2001:db8:ff:5::13/128        |
| CE-CORP-1  | 6         | 2001:db8:ff:6::1/128         |
| CE-CORP-2  | 6         | 2001:db8:ff:6::2/128         |

## Point-to-Point Links (2001:db8:0:LINK-ID::/64)

| Link               | Network                  | Router A                    | Router B                    |
|--------------------|--------------------------|-----------------------------|-----------------------------|
| CORE-1 — CORE-2    | 2001:db8:0:12::/64       | 2001:db8:0:12::1/64         | 2001:db8:0:12::2/64         |
| CORE-1 — CORE-3    | 2001:db8:0:13::/64       | 2001:db8:0:13::1/64         | 2001:db8:0:13::3/64         |
| CORE-2 — CORE-4    | 2001:db8:0:24::/64       | 2001:db8:0:24::2/64         | 2001:db8:0:24::4/64         |
| CORE-3 — CORE-4    | 2001:db8:0:34::/64       | 2001:db8:0:34::3/64         | 2001:db8:0:34::4/64         |
| CORE-1 — EDGE-1    | 2001:db8:0:101::/64      | 2001:db8:0:101::1/64        | 2001:db8:0:101::e1/64       |
| CORE-2 — EDGE-2    | 2001:db8:0:102::/64      | 2001:db8:0:102::2/64        | 2001:db8:0:102::e2/64       |
| CORE-3 — EDGE-3    | 2001:db8:0:103::/64      | 2001:db8:0:103::3/64        | 2001:db8:0:103::e3/64       |
| CORE-4 — EDGE-4    | 2001:db8:0:104::/64      | 2001:db8:0:104::4/64        | 2001:db8:0:104::e4/64       |
| EDGE-1 — BORDER-1  | 2001:db8:0:201::/64      | 2001:db8:0:201::e1/64       | 2001:db8:0:201::b1/64       |
| EDGE-4 — BORDER-2  | 2001:db8:0:204::/64      | 2001:db8:0:204::e4/64       | 2001:db8:0:204::b2/64       |
| EDGE-1 — CE-CORP-1 | 2001:db8:0:c100::/64     | 2001:db8:0:c100::e1/64      | 2001:db8:0:c100::c1/64      |
| EDGE-4 — CE-CORP-2 | 2001:db8:0:c200::/64     | 2001:db8:0:c200::e4/64      | 2001:db8:0:c200::c2/64      |

## DMVPN IPv6 Tunnel Addressing

| Region     | Tunnel IPv6 Prefix   | Hub-1                   | Hub-2                   | Spokes (.11/.12/.13)         |
|------------|----------------------|-------------------------|-------------------------|------------------------------|
| DMVPN West | 2001:db8:10::/48     | 2001:db8:10::fe/64      | 2001:db8:10::fd/64      | ::1/64, ::2/64, ::3/64       |
| DMVPN East | 2001:db8:20::/48     | 2001:db8:20::fe/64      | 2001:db8:20::fd/64      | ::1/64, ::2/64, ::3/64       |

## Customer VRF IPv6 Prefixes

| VRF    | IPv6 Prefix          | CE-CORP-1 LAN         | CE-CORP-2 LAN         |
|--------|----------------------|-----------------------|-----------------------|
| CORP   | 2001:db8:100::/48    | 2001:db8:100:1::/64   | 2001:db8:100:2::/64   |
| RETAIL | 2001:db8:200::/48    | 2001:db8:200:1::/64   | 2001:db8:200:2::/64   |

## 6PE Configuration Summary

6PE allows IPv6 prefixes to be forwarded over an MPLS backbone without native IPv6 support on P routers.

- **PE routers:** Loopback0 used as `mpls ipv6 source-interface`
- **iBGP address-family:** `address-family ipv6` with `send-label` on PE-to-PE sessions
- **P routers:** IPv4/MPLS only — no IPv6 required on transit links
- **CE routers:** Native IPv6 toward PE, no MPLS awareness

## OSPFv3 Area Design

| Area | Routers                        | Type   |
|------|--------------------------------|--------|
| 0    | CORE-1,2,3,4 + EDGE-1,2,3,4   | Backbone|
| 100  | CE-CORP-1 facing               | Regular|
| 200  | CE-CORP-2 facing               | Regular|

## Protocol-Specific IPv6 Notes

- **OSPF MD5 auth (OSPFv3):** Uses IPsec AH (area authentication sha1)
- **EIGRP IPv6 named mode:** `address-family ipv6 unicast autonomous-system 100` under `router eigrp DMVPN-FABRIC`
- **BGP IPv6:** `address-family ipv6 unicast` on PE routers, route-reflector on CORE-1/CORE-2
- **BFD IPv6:** `ipv6 ospf bfd` + `neighbor X bfd` under BGP
