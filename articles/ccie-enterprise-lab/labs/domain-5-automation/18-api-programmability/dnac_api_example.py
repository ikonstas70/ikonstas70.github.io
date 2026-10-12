#!/usr/bin/env python3
"""
Cisco DNA Center API Interaction
Blueprint: §5.3.b — Interaction with Cisco DNA Center API

Prerequisites:
    pip install requests
"""

import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings()

DNAC_HOST = "https://sandboxdnac.cisco.com"
USERNAME = "devnetuser"
PASSWORD = "Cisco123!"


def get_auth_token() -> str:
    """Obtain authentication token from DNA Center (§5.3.b.i HTTP POST)"""
    url = f"{DNAC_HOST}/dna/system/api/v1/auth/token"
    resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    token = resp.json()["Token"]
    print(f"Token obtained: {token[:20]}...")
    return token


def get_network_devices(token: str) -> list:
    """GET all network devices (§5.3.b.i HTTP GET — monitoring endpoint)"""
    url = f"{DNAC_HOST}/dna/intent/api/v1/network-device"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    devices = resp.json()["response"]
    print(f"\nFound {len(devices)} devices:")
    for d in devices[:5]:
        print(f"  {d.get('hostname', 'N/A'):30} {d.get('managementIpAddress', 'N/A'):15} {d.get('type', 'N/A')}")
    return devices


def get_site_health(token: str) -> dict:
    """GET site health summary (§5.3.b.i — monitoring endpoint)"""
    url = f"{DNAC_HOST}/dna/intent/api/v1/site-health"
    headers = {"X-Auth-Token": token}
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp.json()


def provision_device(token: str, device_ip: str, site_id: str) -> str:
    """POST to provision a device to a site (§5.3.b.i — configuration endpoint)"""
    url = f"{DNAC_HOST}/dna/intent/api/v1/biz-service/site-management/provision-nfv"
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    payload = {
        "siteProfile": [{"site": {"siteId": site_id}}],
        "provisioning": [{"device": [{"ip": device_ip}]}]
    }
    resp = requests.post(url, json=payload, headers=headers, verify=False)
    task_id = resp.json().get("response", {}).get("taskId", "")
    print(f"Provision task ID: {task_id}")
    return task_id


if __name__ == "__main__":
    token = get_auth_token()
    devices = get_network_devices(token)
    health = get_site_health(token)
    print(f"\nSite health response keys: {list(health.keys())}")
