import requests
import os

sources = [
    "https://bestip.06151953.xyz/bestip/Asia?regex=true",
    "https://bestip.06151953.xyz/bestip/America?regex=true",
    "https://bestip.06151953.xyz/bestip/Europe?regex=true"
]

raw_proxy_file = "proxies/rawproxy.txt"
active_file = "proxies/active.txt"
dead_file = "proxies/dead.txt"
log_file = "proxies/log.txt"

# Buat folder proxies
os.makedirs("proxies", exist_ok=True)

# Scrap proxies
all_proxies = set()
print("[*] Scraping proxies...")
for url in sources:
    try:
        res = requests.get(url, timeout=15)
        lines = res.text.splitlines()
        count = 0
        for line in lines:
            line = line.strip()
            if ":" in line:
                all_proxies.add(line)
                count += 1
        print(f"[+] {url} -> {count} proxies fetched")
    except Exception as e:
        print(f"[!] Error fetching from {url}: {e}")

# Simpan ke rawproxy.txt
with open(raw_proxy_file, "w") as f:
    for proxy in all_proxies:
        f.write(proxy + "\n")
print(f"[+] Total proxies saved: {len(all_proxies)}")

# Reset hasil & log
open(active_file, "w").close()
open(dead_file, "w").close()
open(log_file, "w").close()

active = []
dead = []

# Cek satu-satu ke API renchi
print("[*] Checking proxies...")
for proxy in all_proxies:
    url = f"https://api.renchi.workers.dev/api?ip={proxy}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("status") == "success":
            active.append(proxy)
            with open(log_file, "a") as log:
                log.write(f"[✓] {proxy} is ACTIVE\n")
        else:
            dead.append(proxy)
            with open(log_file, "a") as log:
                log.write(f"[✗] {proxy} is DEAD (bad response)\n")
    except Exception as e:
        dead.append(proxy)
        with open(log_file, "a") as log:
            log.write(f"[✗] {proxy} is DEAD ({str(e)})\n")

# Simpan hasil
with open(active_file, "w") as f:
    f.write("\n".join(active))
with open(dead_file, "w") as f:
    f.write("\n".join(dead))

print(f"[✓] Done! Active: {len(active)}, Dead: {len(dead)}")
