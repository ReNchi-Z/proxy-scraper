import requests
import json
import time
import concurrent.futures

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
            print(f"\nMengambil data dari {url}")
            response = requests.get(url, timeout=15)
            print(f"Status Code: {response.status_code}")
            print(f"Response Sample: {response.text[:200]}...")

            if response.status_code == 200:
                try:
                    proxies = json.loads(response.text)
                    if isinstance(proxies, list):
                        all_proxies.extend(proxies)
                        print(f"Found {len(proxies)} proxies (array format)")
                    else:
                        proxies = [json.loads(line) for line in response.text.splitlines() if line.strip()]
                        all_proxies.extend(proxies)
                        print(f"Found {len(proxies)} proxies (json lines format)")
                except json.JSONDecodeError:
                    fixed_text = "[" + response.text.replace("}{", "},{") + "]"
                    proxies = json.loads(fixed_text)
                    all_proxies.extend(proxies)
                    print(f"Found {len(proxies)} proxies (non-standard format)")
                    
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
    
    return all_proxies

# Fungsi untuk memeriksa proxy
def check_proxy(proxy):
    if not isinstance(proxy, dict):
        print(f"Invalid proxy format: {proxy}")
        return {"status": "error"}
    
    ip_port = f"{proxy.get('ip')}:{proxy.get('port')}"
    api_url = f"https://api.renchi.workers.dev/api?ip={ip_port}"
    
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if "✅ ACTIVE ✅" in data.get("proxyStatus", ""):
            return {
                "status": "active",
                "data": {
                    "ip": proxy["ip"],
                    "port": proxy["port"],
                    "countryid": data.get("countryCode", "??"),
                    "isp": data.get("isp", "unknown")
                }
            }
        return {"status": "dead"}
    except Exception as e:
        print(f"Error checking {ip_port}: {str(e)}")
        return {"status": "error"}

# Fungsi utama
def main():
    print("Memulai proses...")
    
    proxies = fetch_proxy_data()
    print(f"\nTotal {len(proxies)} proxy ditemukan")
    
    if not proxies:
        print("Tidak ada proxy yang ditemukan")
        return
    
    with open('active.txt', 'w', encoding='utf-8') as active, \
         open('dead.txt', 'w', encoding='utf-8') as dead:
        
        country_priority = ["ID", "SG", "MY", "JP"]
        
        def process_proxy(proxy):
            ip = proxy.get('ip', '')
            port = proxy.get('port', '')
            if not ip or not port:
                return None
            
            print(f"\nMemeriksa: {ip}:{port}")
            result = check_proxy(proxy)
            if result["status"] == "active":
                country = result["data"]["countryid"]
                print(f"Status: AKTIF - {ip}:{port} ({country})")
                return ("active", result["data"])
            elif result["status"] == "dead":
                print(f"Status: MATI - {ip}:{port}")
                return ("dead", f"{ip}:{port}")
            else:
                print(f"Status: ERROR - {ip}:{port}")
                return None
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(process_proxy, proxy) for proxy in proxies]
            results = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: (
            country_priority.index(x[1]['countryid']) if x[0] == "active" and x[1]['countryid'] in country_priority else float('inf')
        ))
        
        for status, data in results:
            if status == "active":
                active.write(f"{data['ip']},{data['port']},{data['countryid']},{data['isp']}\n")
            elif status == "dead":
                dead.write(f"{data}\n")
    
    print("\nProses selesai!")

if __name__ == "__main__":
    main()
