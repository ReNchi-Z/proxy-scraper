import asyncio
import aiohttp
import os

API_URL = "https://api.renchi.workers.dev/api?ip={}"

async def check_proxy(session, proxy):
    ip = proxy.split(':')[0]
    try:
        async with session.get(API_URL.format(ip), timeout=10) as res:
            data = await res.json()
            if "✅" in data.get("proxyStatus", ""):
                return "active", proxy
            else:
                return "dead", proxy
    except:
        return "dead", proxy

async def main():
    sources = os.getenv("PROXY_SOURCES", "").splitlines()
    proxies = set()
    
    async with aiohttp.ClientSession() as session:
        for url in sources:
            try:
                async with session.get(url, timeout=10) as res:
                    if res.status == 200:
                        text = await res.text()
                        proxies.update([line.strip() for line in text.splitlines() if line.strip()])
            except:
                continue

    tasks = []
    async with aiohttp.ClientSession() as session:
        for proxy in proxies:
            tasks.append(check_proxy(session, proxy))

        results = await asyncio.gather(*tasks)

    os.makedirs("result", exist_ok=True)
    with open("result/active.txt", "w") as a, open("result/dead.txt", "w") as d:
        for status, proxy in results:
            if status == "active":
                a.write(proxy + "\n")
            else:
                d.write(proxy + "\n")

if __name__ == "__main__":
    asyncio.run(main())
