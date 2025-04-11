import aiohttp
import asyncio
import os
import json

SOURCE_URLS = [
    "https://bestip.06151953.xyz/bestip/Asia?regex=true",
    "https://bestip.06151953.xyz/bestip/America?regex=true",
    "https://bestip.06151953.xyz/bestip/Europe?regex=true"
]

RAW_PROXY_FILE = "rawproxy.txt"
OUTPUT_ACTIVE = "proxies/active.txt"
OUTPUT_DEAD = "proxies/dead.txt"
RENCHI_API = "https://api.renchi.workers.dev/api?ip={ip}"


async def fetch_json(session, url):
    async with session.get(url, timeout=20) as response:
        return await response.json()


async def fetch_proxies():
    proxies = set()
    async with aiohttp.ClientSession() as session:
        for url in SOURCE_URLS:
            try:
                data = await fetch_json(session, url)
                for item in data:
                    ip = item.get("ip")
                    port = item.get("port")
                    if ip and port:
                        proxies.add(f"{ip}:{port}")
                print(f"[+] {url} -> {len(data)} proxies fetched")
            except Exception as e:
                print(f"[!] Failed fetching from {url}: {e}")
    return list(proxies)


async def check_proxy(session, proxy):
    ip, port = proxy.split(":")
    try:
        async with session.get(RENCHI_API.format(ip=ip), timeout=10) as response:
            data = await response.json()
            return proxy if "✅ ACTIVE ✅" in data.get("proxyStatus", "") else None
    except:
        return None


async def check_all_proxies(proxies):
    active = []
    dead = []

    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)

    for proxy, result in zip(proxies, results):
        if result:
            active.append(proxy)
        else:
            dead.append(proxy)

    return active, dead


async def main():
    os.makedirs("proxies", exist_ok=True)

    print("Fetching proxies...")
    proxies = await fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")

    # Simpan ke rawproxy.txt
    with open(RAW_PROXY_FILE, "w") as f:
        f.write("\n".join(proxies))

    print("Checking proxies with Renchi API...")
    active, dead = await check_all_proxies(proxies)

    print(f"Active: {len(active)}, Dead: {len(dead)}")

    with open(OUTPUT_ACTIVE, "w") as f:
        f.write("\n".join(active))

    with open(OUTPUT_DEAD, "w") as f:
        f.write("\n".join(dead))


if __name__ == "__main__":
    asyncio.run(main())
