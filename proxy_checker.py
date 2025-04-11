import requests
import re
import time
from bs4 import BeautifulSoup

# User-Agent untuk menghindari blokir
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_proxies():
    base_url = "https://bestip.06151953.xyz/bestip/"
    regions = ["Asia", "America", "Europe"]
    proxies = set()

    for region in regions:
        url = f"{base_url}{region}?regex=true"
        try:
            print(f"Scraping {region}...")
            response = requests.get(url, headers=HEADERS, timeout=15)
            
            # Debug: Simpan response ke file untuk inspeksi
            with open(f'debug_{region}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Dua metode ekstraksi
            ip_ports = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b', response.text)
            
            # Alternatif dari tag <pre>
            soup = BeautifulSoup(response.text, 'html.parser')
            pre_content = soup.find('pre')
            if pre_content:
                ip_ports += re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+\b', pre_content.text)
            
            proxies.update(ip_ports)
            print(f"Found {len(ip_ports)} IPs in {region}")
            
        except Exception as e:
            print(f"Error scraping {region}: {str(e)}")
    
    with open('rawProxy.txt', 'w') as f:
        f.write('\n'.join(proxies))
    return proxies

def check_proxy(proxy):
    api_url = f"https://api.renchi.workers.dev/api?ip={proxy}"
    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10)
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
    except Exception as e:
        print(f"Error checking {proxy}: {str(e)}")
        return {"status": "error"}

if __name__ == "__main__":
    print("Memulai proses scraping...")
    proxies = scrape_proxies()
    print(f"Total {len(proxies)} proxies ditemukan")
    
    if not proxies:
        print("Tidak ada proxy yang ditemukan, periksa debug_[region].html untuk investigasi")
    else:
        with open('active.txt', 'w') as active, open('dead.txt', 'w') as dead:
            for i, proxy in enumerate(proxies, 1):
                print(f"Memeriksa {i}/{len(proxies)}: {proxy}")
                result = check_proxy(proxy)
                
                if result["status"] == "active":
                    d = result["data"]
                    active.write(f"{d['ip']},{d['port']},{d['countryid']},{d['isp']}\n")
                else:
                    dead.write(f"{proxy}\n")
                
                time.sleep(1)  # Menghindari rate limit
    
    print("Proses selesai!")
