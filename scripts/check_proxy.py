import requests
import concurrent.futures
import json
import os
from datetime import datetime

API_URL = "https://api.renchi.workers.dev/api?ip={ip}"

PROXY_SOURCES = [
    "https://bestip.06151953.xyz/bestip/Asia?regex=true",
    "https://bestip.06151953.xyz/bestip/America?regex=true",
    "https://bestip.06151953.xyz/bestip/Europe?regex=true"
]

def fetch_proxies():
    proxies = []
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                proxies += response.text.strip().splitlines()
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
    return proxies

def check_proxy(proxy):
    if proxy.count(":") != 1:
        return "invalid", proxy
    ip, port = proxy.split(":")
    try:
        response = requests.get(API_URL.format(ip=ip), timeout=10)
        data = response.json()
        if data.get("status") == "active":
            return "active", proxy
    except Exception:
        pass
    return "dead", proxy

def save_results(active, dead):
    os.makedirs("result", exist_ok=True)
    with open("result/active.txt", "w") as f:
        f.write("\n".join(active))
    with open("result/dead.txt", "w") as f:
        f.write("\n".join(dead))

def main():
    print("Fetching proxies...")
    proxies = fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")

    active, dead = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_proxy, proxies)
        for status, proxy in results:
            if status == "active":
                active.append(proxy)
            elif status == "dead":
                dead.append(proxy)
            else:
                pass  # ignore invalid

    save_results(active, dead)

    print(f"Active: {len(active)}, Dead: {len(dead)}")

if __name__ == "__main__":
    main()
