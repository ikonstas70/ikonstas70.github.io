#!/usr/bin/env python3
"""
NETCONF/YANG Interaction with Cisco IOS XE
Blueprint: §5.3.c — Interaction with Cisco IOS XE API via NETCONF/YANG

Prerequisites:
    pip install ncclient requests
    IOS XE device must have NETCONF enabled:
        netconf-yang
        restconf
"""

from ncclient import manager
import json
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import urllib3
urllib3.disable_warnings()

# Device connection parameters
DEVICE = {
    "host": "10.255.1.1",   # CORE-1 loopback
    "port": 830,
    "username": "admin",
    "password": "Lab@2024#EI",
    "hostkey_verify": False,
    "device_params": {"name": "iosxe"}
}

RESTCONF_BASE = "https://10.255.1.1/restconf/data"
AUTH = HTTPBasicAuth("admin", "Lab@2024#EI")
HEADERS = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}


def get_ospf_neighbors_netconf():
    """Retrieve OSPF neighbor state via NETCONF (§5.3.c.i)"""
    filter_xml = """
    <filter>
      <ospf-oper-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf-oper">
        <ospf-state>
          <ospf-instance>
            <af>
              <topology>
                <link-scope-lsas/>
              </topology>
            </af>
          </ospf-instance>
        </ospf-state>
      </ospf-oper-data>
    </filter>
    """
    with manager.connect(**DEVICE) as m:
        response = m.get(filter=("subtree", filter_xml))
        print("OSPF Neighbor Data (NETCONF):")
        print(response.xml)
        return response.xml


def configure_loopback_restconf(loopback_num: int, ipv4: str, ipv6: str):
    """Configure a loopback interface via RESTCONF (§5.3.c.ii)"""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-native:native/interface/Loopback={loopback_num}"
    payload = {
        "Cisco-IOS-XE-native:Loopback": {
            "name": loopback_num,
            "ip": {
                "address": {
                    "primary": {
                        "address": ipv4.split("/")[0],
                        "mask": "255.255.255.255"
                    }
                }
            },
            "ipv6": {
                "address": {
                    "prefix-list": [{"prefix": ipv6}]
                }
            }
        }
    }
    resp = requests.put(url, json=payload, headers=HEADERS, auth=AUTH, verify=False)
    print(f"Configure Loopback{loopback_num}: HTTP {resp.status_code}")
    return resp.status_code == 204


def get_bgp_summary_restconf():
    """Retrieve BGP summary via RESTCONF (§5.3.c.ii)"""
    url = f"{RESTCONF_BASE}/Cisco-IOS-XE-bgp-oper:bgp-state-data/neighbors"
    resp = requests.get(url, headers=HEADERS, auth=AUTH, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
        return data
    print(f"Error: HTTP {resp.status_code}")
    return None


def configure_grpc_telemetry_netconf():
    """Configure model-driven telemetry via NETCONF (§5.3.d)"""
    config_xml = """
    <config>
      <mdt-config-data xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-mdt-cfg">
        <mdt-subscription>
          <subscription-id>101</subscription-id>
          <base>
            <stream>yang-push</stream>
            <encoding>encode-kvgpb</encoding>
            <xpath>/ios-stats:ospf-oper-data/ospf-state</xpath>
            <period>3000</period>
          </base>
          <mdt-receivers>
            <address>10.10.1.100</address>
            <port>57500</port>
            <protocol>grpc-tcp</protocol>
          </mdt-receivers>
        </mdt-subscription>
      </mdt-config-data>
    </config>
    """
    with manager.connect(**DEVICE) as m:
        response = m.edit_config(target="running", config=config_xml)
        print(f"gRPC Telemetry config: {response}")


if __name__ == "__main__":
    print("=== NETCONF: Get OSPF Neighbors ===")
    get_ospf_neighbors_netconf()

    print("\n=== RESTCONF: Get BGP Summary ===")
    get_bgp_summary_restconf()

    print("\n=== RESTCONF: Configure Loopback99 ===")
    configure_loopback_restconf(99, "10.255.99.1/32", "2001:db8:ff:99::1/128")

    print("\n=== NETCONF: Configure gRPC Telemetry ===")
    configure_grpc_telemetry_netconf()
