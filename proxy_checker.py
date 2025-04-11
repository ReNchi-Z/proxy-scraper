import requests
import json
from datetime import datetime
import time

# Fungsi untuk scraping IP:Port
def scrape_proxies():
    base_url = "https://bestip.06151953.xyz/bestip/"
    regions = ["Asia", "America", "Europe"]
    
    proxies = set()  # Menggunakan set untuk menghindari duplikat
    
    for region in regions:
        url = f"{base_url}{region}?regex=true"
        try:
            print(f"Scraping {region}...")
            response = requests.get(url, timeout=15)
            # Mencari semua IP:Port dengan regex
            ip_ports = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+', response.text)
            proxies.update(ip_ports)
        except Exception as e:
            print(f"Error scraping {region}: {str(e)}")
    
    # Simpan ke rawProxy.txt
    with open('rawProxy.txt', 'w') as f:
        f.write('\n'.join(proxies))
    
    return proxies

# Fungsi untuk cek proxy
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
        else:
            return {"status": "dead"}
            
    except Exception as e:
        print(f"Error checking {proxy}: {str(e)}")
        return {"status": "error"}

# Main process
if __name__ == "__main__":
    # Scraping proxy
    proxies = scrape_proxies()
    print(f"Total {len(proxies)} proxies ditemukan")
    
    # File output
    active_file = open('active.txt', 'w')
    dead_file = open('dead.txt', 'w')
    
    # Check semua proxy
    for i, proxy in enumerate(proxies, 1):
        print(f"Checking {i}/{len(proxies)}: {proxy}")
        result = check_proxy(proxy)
        
        if result["status"] == "active":
            data = result["data"]
            active_file.write(f"{data['ip']},{data['port']},{data['countryid']},{data['isp']}\n")
        else:
            dead_file.write(f"{proxy}\n")
        
        # Delay untuk menghindari rate limit
        time.sleep(1)
    
    active_file.close()
    dead_file.close()
    
    print("Proses selesai!")
