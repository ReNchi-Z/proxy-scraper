import asyncio
import aiohttp
import json
import os
from datetime import datetime

PROXY_SOURCES = os.getenv("PROXY_SOURCES", "").split("\n")
OUTPUT_ACTIVE = "proxies/active.txt"
OUTPUT_DEAD = "proxies/dead.txt"

async def fetch_proxies():
    proxies = set()
    for url in PROXY_SOURCES:
        if not url.strip():
            continue
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.text()
                        try:
                            json_data = json.loads(data)
                            for item in json_data:
                                ip = item.get("ip") or item.get("proxyHost")
                                port = item.get("port") or item.get("proxyPort")
                                if ip and port:
                                    proxies.add(f"{ip}:{port}")
                        except json.JSONDecodeError:
                            lines = data.strip().split("\n")
                            for line in lines:
                                if ":" in line:
                                    proxies.add(line.strip())
        except Exception as e:
            print(f"Failed to fetch from {url}: {e}")
    return list(proxies)

async def check_proxy(session, proxy):
    url = f"https://api.renchi.workers.dev/api?ip={proxy}"
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                result = await response.json()
                status = result.get("proxyStatus", "").lower()
                if "active" in status:
                    return "active", proxy
                else:
                    return "dead", proxy
            else:
                return "dead", proxy
    except Exception as e:
        return "dead", proxy

async def main():
    print("Fetching proxies...")
    proxies = await fetch_proxies()
    print(f"Total proxies fetched: {len(proxies)}")

    active = []
    dead = []

    connector = aiohttp.TCPConnector(limit=100)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [check_proxy(session, proxy) for proxy in proxies]
        for future in asyncio.as_completed(tasks):
            status, proxy = await future
            if status == "active":
                active.append(proxy)
            else:
                dead.append(proxy)

    print(f"Active: {len(active)}, Dead: {len(dead)}")

    with open(OUTPUT_ACTIVE, "w") as f:
        f.write("\n".join(active))

    with open(OUTPUT_DEAD, "w") as f:
        f.write("\n".join(dead))

if __name__ == "__main__":
    asyncio.run(main())
