# IPv4 Addressing Plan — Advanced CCIE RS Lab

## Loopback Interfaces (10.255.X.X/32)

| Router     | Zone         | Loopback0        |
|------------|--------------|------------------|
| CORE-1     | MPLS Core    | 10.255.1.1/32    |
| CORE-2     | MPLS Core    | 10.255.1.2/32    |
| CORE-3     | MPLS Core    | 10.255.1.3/32    |
| CORE-4     | MPLS Core    | 10.255.1.4/32    |
| EDGE-1     | Provider Edge| 10.255.2.1/32    |
| EDGE-2     | Provider Edge| 10.255.2.2/32    |
| EDGE-3     | Provider Edge| 10.255.2.3/32    |
| EDGE-4     | Provider Edge| 10.255.2.4/32    |
| BORDER-1   | Internet Edge| 10.255.3.1/32    |
| BORDER-2   | Internet Edge| 10.255.3.2/32    |
| HUB-WC-1   | DMVPN West   | 10.255.4.1/32    |
| HUB-WC-2   | DMVPN West   | 10.255.4.2/32    |
| SPK-WC-1   | DMVPN West   | 10.255.4.11/32   |
| SPK-WC-2   | DMVPN West   | 10.255.4.12/32   |
| SPK-WC-3   | DMVPN West   | 10.255.4.13/32   |
| HUB-EC-1   | DMVPN East   | 10.255.5.1/32    |
| HUB-EC-2   | DMVPN East   | 10.255.5.2/32    |
| SPK-EC-1   | DMVPN East   | 10.255.5.11/32   |
| SPK-EC-2   | DMVPN East   | 10.255.5.12/32   |
| SPK-EC-3   | DMVPN East   | 10.255.5.13/32   |
| CE-CORP-1  | Customer     | 10.255.6.1/32    |
| CE-CORP-2  | Customer     | 10.255.6.2/32    |

## Point-to-Point Links (10.0.X.Y/31)

| Link                   | Network        | Router A IP  | Router B IP  |
|------------------------|----------------|--------------|--------------|
| CORE-1 — CORE-2        | 10.0.12.0/31   | 10.0.12.0    | 10.0.12.1    |
| CORE-1 — CORE-3        | 10.0.13.0/31   | 10.0.13.0    | 10.0.13.1    |
| CORE-2 — CORE-4        | 10.0.24.0/31   | 10.0.24.0    | 10.0.24.1    |
| CORE-3 — CORE-4        | 10.0.34.0/31   | 10.0.34.0    | 10.0.34.1    |
| CORE-1 — EDGE-1        | 10.0.101.0/31  | 10.0.101.0   | 10.0.101.1   |
| CORE-2 — EDGE-2        | 10.0.102.0/31  | 10.0.102.0   | 10.0.102.1   |
| CORE-3 — EDGE-3        | 10.0.103.0/31  | 10.0.103.0   | 10.0.103.1   |
| CORE-4 — EDGE-4        | 10.0.104.0/31  | 10.0.104.0   | 10.0.104.1   |
| EDGE-1 — BORDER-1      | 10.0.201.0/31  | 10.0.201.0   | 10.0.201.1   |
| EDGE-4 — BORDER-2      | 10.0.204.0/31  | 10.0.204.0   | 10.0.204.1   |
| EDGE-2 — HUB-WC-1      | 10.0.210.0/31  | 10.0.210.0   | 10.0.210.1   |
| EDGE-2 — HUB-WC-2      | 10.0.211.0/31  | 10.0.211.0   | 10.0.211.1   |
| EDGE-3 — HUB-EC-1      | 10.0.220.0/31  | 10.0.220.0   | 10.0.220.1   |
| EDGE-3 — HUB-EC-2      | 10.0.221.0/31  | 10.0.221.0   | 10.0.221.1   |
| EDGE-1 — CE-CORP-1     | 10.1.100.0/31  | 10.1.100.0   | 10.1.100.1   |
| EDGE-4 — CE-CORP-2     | 10.1.200.0/31  | 10.1.200.0   | 10.1.200.1   |

## DMVPN Tunnel Subnets

| Region     | Tunnel Network  | Hub-1 IP     | Hub-2 IP     | Spoke IPs           |
|------------|-----------------|--------------|--------------|---------------------|
| DMVPN West | 172.16.10.0/24  | 172.16.10.254| 172.16.10.253| .1, .2, .3          |
| DMVPN East | 172.16.20.0/24  | 172.16.20.254| 172.16.20.253| .1, .2, .3          |

## VRF Definitions

| VRF Name | Route Distinguisher | Import RT   | Export RT   |
|----------|---------------------|-------------|-------------|
| CORP     | 65000:100           | 65000:100   | 65000:100   |
| RETAIL   | 65000:200           | 65000:200   | 65000:200   |

## eBGP Uplinks (BORDER Routers)

| Router   | AS    | Upstream Peer  | Upstream AS | Link Network      |
|----------|-------|----------------|-------------|-------------------|
| BORDER-1 | 65001 | 198.51.100.2   | 65100       | 198.51.100.0/30   |
| BORDER-2 | 65001 | 203.0.113.2    | 65200       | 203.0.113.0/30    |

## VLAN Scheme

| VLAN | Name              | Purpose                        |
|------|-------------------|--------------------------------|
| 100  | MGMT-OOB          | Out-of-band management         |
| 110  | CORE-BACKBONE     | CORE router backbone segment   |
| 201  | CORE1-EDGE1-UPLINK| CORE-1 to EDGE-1               |
| 202  | CORE2-EDGE2-UPLINK| CORE-2 to EDGE-2               |
| 203  | CORE3-EDGE3-UPLINK| CORE-3 to EDGE-3               |
| 204  | CORE4-EDGE4-UPLINK| CORE-4 to EDGE-4               |
| 301  | EDGE1-BORDER1     | EDGE-1 to BORDER-1             |
| 304  | EDGE4-BORDER2     | EDGE-4 to BORDER-2             |
| 401  | CE-CORP-1-FACING  | CE-CORP-1 customer segment     |
| 402  | CE-CORP-2-FACING  | CE-CORP-2 customer segment     |

## AS Numbers

| Entity        | AS Number |
|---------------|-----------|
| MPLS Core     | 65000     |
| BORDER (both) | 65001     |
| Simulated ISP1| 65100     |
| Simulated ISP2| 65200     |
| CE Customer   | 65500     |

## MPLS Label Range

- Custom label range: 1000–9999
- LDP Router-ID: Loopback0 on each P/PE router
