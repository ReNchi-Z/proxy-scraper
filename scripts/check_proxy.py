import aiohttp
import asyncio
import os
from aiohttp import ClientTimeout

RAW_PROXY_FILE = "proxies/rawproxy.txt"
ACTIVE_FILE = "proxies/active.txt"
DEAD_FILE = "proxies/dead.txt"

PROXY_SOURCES = [
    "https://bestip.06151953.xyz/bestip/Asia?regex=true",
    "https://bestip.06151953.xyz/bestip/America?regex=true",
    "https://bestip.06151953.xyz/bestip/Europe?regex=true",
]

async def fetch_raw_proxies():
    proxies = set()
    os.makedirs("proxies", exist_ok=True)
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        for url in PROXY_SOURCES:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data:
                            ip = item.get("ip")
                            port = item.get("port")
                            if ip and port:
                                proxies.add(f"{ip}:{port}")
                        print(f"[+] {url} -> {len(data)} proxies fetched")
                    else:
                        print(f"[!] Failed fetching {url} (Status {resp.status})")
            except Exception as e:
                print(f"[!] Error fetching {url}: {e}")

    with open(RAW_PROXY_FILE, "w") as f:
        for proxy in proxies:
            f.write(proxy + "\n")
    print(f"[+] Total proxies saved: {len(proxies)}")

async def check_proxy(session, proxy):
    url = f"https://api.renchi.workers.dev/api?ip={proxy}"
    try:
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                if "ACTIVE" in data.get("proxyStatus", ""):
                    return proxy, True
    except:
        pass
    return proxy, False

async def main():
    await fetch_raw_proxies()

    with open(RAW_PROXY_FILE, "r") as f:
        proxies = [line.strip() for line in f if line.strip()]

    active, dead = [], []
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)

    for proxy, is_active in results:
        (active if is_active else dead).append(proxy)

    with open(ACTIVE_FILE, "w") as f:
        f.write("\n".join(active))
    with open(DEAD_FILE, "w") as f:
        f.write("\n".join(dead))

    print(f"[✓] Done! Active: {len(active)}, Dead: {len(dead)}")

if __name__ == "__main__":
    asyncio.run(main())
