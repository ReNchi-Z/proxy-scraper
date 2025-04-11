import requests
import concurrent.futures
import json
import os
from datetime import datetime

SOURCES = [
    "https://bestip.06151953.xyz/bestip/Asia?regex=true",
    "https://bestip.06151953.xyz/bestip/America?regex=true",
    "https://bestip.06151953.xyz/bestip/Europe?regex=true"
]

API_URL = "https://api.renchi.workers.dev/api?ip={}"
ACTIVE_FILE = "result/active.txt"
DEAD_FILE = "result/dead.txt"

def fetch_proxies():
    proxies = set()
    for url in SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                data = response.json()
                for item in data:
                    ip = item.get("ip")
                    port = item.get("port")
                    if ip and port:
                        proxies.add(f"{ip}:{port}")
                print(f"[+] {url} -> {len(data)} proxies fetched")
            else:
                print(f"[-] Failed to fetch from {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"[!] Error fetching from {url}: {e}")
    return proxies

def check_proxy(proxy):
    try:
        response = requests.get(API_URL.format(proxy), timeout=10)
        result = response.json()
        status = result.get("status")
        if status == "ok":
            return "active", proxy
    except:
        pass
    return "dead", proxy

def save_results(active, dead):
    with open(ACTIVE_FILE, "w") as a:
        a.write("\n".join(active))
    with open(DEAD_FILE, "w") as d:
        d.write("\n".join(dead))

def main():
    proxies = fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")

    active, dead = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_proxy, proxies)
        for status, proxy in results:
            if status == "active":
                active.append(proxy)
            else:
                dead.append(proxy)

    print(f"Active: {len(active)}, Dead: {len(dead)}")
    save_results(active, dead)

if __name__ == "__main__":
    main()
