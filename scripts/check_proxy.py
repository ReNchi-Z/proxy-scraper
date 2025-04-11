import requests 
import concurrent.futures 
import json 
import os from datetime import datetime

API untuk pengecekan proxy

API_URL = "https://api.renchi.workers.dev/api?ip={ip}"

Sumber URL proxy

URLS = [ "https://bestip.06151953.xyz/bestip/Asia?regex=true", "https://bestip.06151953.xyz/bestip/America?regex=true", "https://bestip.06151953.xyz/bestip/Europe?regex=true", ]

Direktori hasil

os.makedirs("result", exist_ok=True)

ACTIVE_FILE = "result/active.txt" DEAD_FILE = "result/dead.txt"

def fetch_proxies(): proxies = set() for url in URLS: try: res = requests.get(url, timeout=10) if res.status_code == 200: proxies.update(res.text.strip().splitlines()) except Exception as e: print(f"Gagal fetch {url}: {e}") return list(proxies)

def check_proxy(proxy): ip, port = proxy.split(":") try: res = requests.get(API_URL.format(ip=ip), timeout=10) data = res.json() if data.get("proxyStatus") == "✅ ACTIVE ✅": return "active", proxy except: pass return "dead", proxy

def main(): proxies = fetch_proxies() active = [] dead = []

with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    results = executor.map(check_proxy, proxies)
    for status, proxy in results:
        if status == "active":
            active.append(proxy)
        else:
            dead.append(proxy)

with open(ACTIVE_FILE, "w") as f:
    f.write("\n".join(active))

with open(DEAD_FILE, "w") as f:
    f.write("\n".join(dead))

print(f"Done! Active: {len(active)}, Dead: {len(dead)}")

if name == "main": main()

