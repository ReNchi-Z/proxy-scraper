import requests
import re  # <-- Ini yang harus ditambahkan
import time
from bs4 import BeautifulSoup

def scrape_proxies():
    base_url = "https://bestip.06151953.xyz/bestip/"
    regions = ["Asia", "America", "Europe"]
    proxies = set()

    for region in regions:
        url = f"{base_url}{region}?regex=true"
        try:
            print(f"Scraping {region}...")
            response = requests.get(url, timeout=15)
            ip_ports = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', response.text)
            proxies.update(ip_ports)
        except Exception as e:
            print(f"Error scraping {region}: {str(e)}")
    
    with open('rawProxy.txt', 'w') as f:
        f.write('\n'.join(proxies))
    return proxies

def check_proxy(proxy):
    api_url = f"https://api.renchi.workers.dev/api?ip={proxy}"
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if "✅ ACTIVE ✅" in data.get("proxyStatus", ""):
            return {
                "status": "active",
                "data": {
                    "ip": data["proxyHost"],
                    "port": data["proxyPort"],
                    "countryid": data["countryCode"],
                    "isp": data["isp"]
                }
            }
        return {"status": "dead"}
    except:
        return {"status": "error"}

if __name__ == "__main__":
    proxies = scrape_proxies()
    print(f"Total {len(proxies)} proxies ditemukan")
    
    with open('active.txt', 'w') as active, open('dead.txt', 'w') as dead:
        for i, proxy in enumerate(proxies, 1):
            print(f"Memeriksa {i}/{len(proxies)}: {proxy}")
            result = check_proxy(proxy)
            
            if result["status"] == "active":
                d = result["data"]
                active.write(f"{d['ip']},{d['port']},{d['countryid']},{d['isp']}\n")
            else:
                dead.write(f"{proxy}\n")
            
            time.sleep(1)
    
    print("Proses selesai!")
