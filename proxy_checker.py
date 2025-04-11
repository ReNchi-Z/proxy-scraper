import requests
import json
import time

# Fungsi untuk mengambil data proxy dari API
def fetch_proxy_data():
    api_urls = [
        "https://bestip.06151953.xyz/bestip/Asia?json=true",
        "https://bestip.06151953.xyz/bestip/America?json=true",
        "https://bestip.06151953.xyz/bestip/Europe?json=true"
    ]
    
    all_proxies = []
    
    for url in api_urls:
        try:
            print(f"Mengambil data dari {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                proxies = json.loads("[" + response.text.replace("}{", "},{") + "]")  # Fix format JSON
                all_proxies.extend(proxies)
                print(f"Found {len(proxies)} proxies")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return all_proxies

# Fungsi untuk memeriksa proxy
def check_proxy(proxy):
    api_url = f"https://api.renchi.workers.dev/api?ip={proxy['ip']}:{proxy['port']}"
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if "✅ ACTIVE ✅" in data.get("proxyStatus", ""):
            return {
                "status": "active",
                "data": {
                    "ip": proxy["ip"],
                    "port": proxy["port"],
                    "countryid": data["countryCode"],
                    "isp": data["isp"]
                }
            }
        return {"status": "dead"}
    except Exception as e:
        print(f"Error checking {proxy['ip']}:{proxy['port']} - {str(e)}")
        return {"status": "error"}

# Fungsi utama
def main():
    print("Memulai proses...")
    
    # Ambil data proxy
    proxies = fetch_proxy_data()
    print(f"Total {len(proxies)} proxy ditemukan")
    
    if not proxies:
        print("Tidak ada proxy yang ditemukan")
        return
    
    # Buka file output
    with open('active.txt', 'w') as active, open('dead.txt', 'w') as dead:
        # Proses setiap proxy
        for i, proxy in enumerate(proxies, 1):
            print(f"Memeriksa {i}/{len(proxies)}: {proxy['ip']}:{proxy['port']}")
            
            result = check_proxy(proxy)
            
            if result["status"] == "active":
                d = result["data"]
                active.write(f"{d['ip']},{d['port']},{d['countryid']},{d['isp']}\n")
            else:
                dead.write(f"{proxy['ip']}:{proxy['port']}\n")
            
            time.sleep(1)  # Delay untuk menghindari rate limit
    
    print("Proses selesai!")

if __name__ == "__main__":
    main()
