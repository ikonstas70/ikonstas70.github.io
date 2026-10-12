# IPv4 Addressing Schema — CCIE Enterprise Infrastructure Lab

## Loopback Addresses (10.255.X.X/32)

| Router     | Role           | Loopback0        |
|------------|----------------|------------------|
| CORE-1     | P Router       | 10.255.1.1/32    |
| CORE-2     | P Router       | 10.255.1.2/32    |
| CORE-3     | P Router       | 10.255.1.3/32    |
| CORE-4     | P Router       | 10.255.1.4/32    |
| EDGE-1     | PE Router      | 10.255.2.1/32    |
| EDGE-2     | PE Router      | 10.255.2.2/32    |
| EDGE-3     | PE Router      | 10.255.2.3/32    |
| EDGE-4     | PE Router      | 10.255.2.4/32    |
| BORDER-1   | ASBR           | 10.255.3.1/32    |
| BORDER-2   | ASBR           | 10.255.3.2/32    |
| HUB-WC-1   | DMVPN Hub West | 10.255.4.1/32    |
| HUB-WC-2   | DMVPN Hub West | 10.255.4.2/32    |
| SPK-WC-1   | DMVPN Spoke    | 10.255.4.11/32   |
| SPK-WC-2   | DMVPN Spoke    | 10.255.4.12/32   |
| SPK-WC-3   | DMVPN Spoke    | 10.255.4.13/32   |
| HUB-EC-1   | DMVPN Hub East | 10.255.5.1/32    |
| HUB-EC-2   | DMVPN Hub East | 10.255.5.2/32    |
| SPK-EC-1   | DMVPN Spoke    | 10.255.5.11/32   |
| SPK-EC-2   | DMVPN Spoke    | 10.255.5.12/32   |
| SPK-EC-3   | DMVPN Spoke    | 10.255.5.13/32   |
| CE-CORP-1  | CE (VRF CORP)  | 10.255.6.1/32    |
| CE-CORP-2  | CE (VRF CORP)  | 10.255.6.2/32    |

## Point-to-Point Links (10.0.X.Y/31)

| Link                    | Subnet          | Side A (.0) | Side B (.1) |
|-------------------------|-----------------|-------------|-------------|
| CORE-1 — CORE-2         | 10.0.12.0/31    | CORE-1      | CORE-2      |
| CORE-1 — CORE-3         | 10.0.13.0/31    | CORE-1      | CORE-3      |
| CORE-2 — CORE-4         | 10.0.24.0/31    | CORE-2      | CORE-4      |
| CORE-3 — CORE-4         | 10.0.34.0/31    | CORE-3      | CORE-4      |
| CORE-1 — EDGE-1         | 10.0.101.0/31   | CORE-1      | EDGE-1      |
| CORE-2 — EDGE-2         | 10.0.102.0/31   | CORE-2      | EDGE-2      |
| CORE-3 — EDGE-3         | 10.0.103.0/31   | CORE-3      | EDGE-3      |
| CORE-4 — EDGE-4         | 10.0.104.0/31   | CORE-4      | EDGE-4      |
| EDGE-1 — BORDER-1       | 10.0.201.0/31   | EDGE-1      | BORDER-1    |
| EDGE-4 — BORDER-2       | 10.0.204.0/31   | EDGE-4      | BORDER-2    |
| EDGE-2 — HUB-WC-1       | 10.0.210.0/31   | EDGE-2      | HUB-WC-1   |
| EDGE-2 — HUB-WC-2       | 10.0.211.0/31   | EDGE-2      | HUB-WC-2   |
| EDGE-3 — HUB-EC-1       | 10.0.220.0/31   | EDGE-3      | HUB-EC-1   |
| EDGE-3 — HUB-EC-2       | 10.0.221.0/31   | EDGE-3      | HUB-EC-2   |
| EDGE-1 — CE-CORP-1      | 10.1.100.0/31   | EDGE-1      | CE-CORP-1  |
| EDGE-4 — CE-CORP-2      | 10.1.200.0/31   | EDGE-4      | CE-CORP-2  |

## DMVPN Tunnel Addresses

| Tunnel       | Subnet           | Hub-1 (.254) | Hub-2 (.253) | Spokes (.1/.2/.3) |
|--------------|------------------|--------------|--------------|-------------------|
| West Tunnel0 | 172.16.10.0/24   | HUB-WC-1     | HUB-WC-2    | SPK-WC-1/2/3      |
| East Tunnel0 | 172.16.20.0/24   | HUB-EC-1     | HUB-EC-2    | SPK-EC-1/2/3      |

## VRF Prefixes

| VRF    | RD        | RT              | Prefix Space    |
|--------|-----------|-----------------|-----------------|
| CORP   | 65000:100 | 65000:100       | 10.10.0.0/16    |
| RETAIL | 65000:200 | 65000:200       | 10.20.0.0/16    |

## eBGP (BORDER Routers)

| Router   | AS    | Upstream Peer    | Peer AS |
|----------|-------|------------------|---------|
| BORDER-1 | 65001 | 198.51.100.2     | 65100   |
| BORDER-2 | 65001 | 203.0.113.2      | 65200   |
