import requests

working_proxies = []

# proxyscrape.com
proxy_scrape_list_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&protocol=socks4&skip=0&proxy_format=protocolipport&format=json&limit=50&timeout=20000"
proxy_scrape_response = requests.get(proxy_scrape_list_url)

proxy_scrape_proxies = proxy_scrape_response.json().get('proxies',[])

for proxy in proxy_scrape_proxies:
    proxy_url = proxy.get('proxy',"")
    try:
        test_response = requests.get('https://www.youtube.com', proxies={'http': proxy_url, 'https': proxy_url}, timeout=5)
        if test_response.status_code == 200:
            print(f"success {proxy_url}")
            working_proxies.append(proxy_url)
    except requests.exceptions.RequestException:
        # Handle exceptions for failed requests
        print(f"fail {proxy_url}")
        continue



# proxy_list_url = "https://proxylist.geonode.com/api/proxy-list?protocols=socks4%2Chttp%2Chttps%2Csocks5&limit=500&page=1&sort_by=upTime&sort_type=desc"
# proxy_response = requests.get(proxy_list_url)

# if proxy_response.status_code == 200:
#     proxies_data = proxy_response.json().get('data', [])
    
#     for proxy in proxies_data:
#         proxy_ip = proxy['ip']
#         proxy_port = proxy['port']
#         protocols = proxy['protocols']
        
#         for protocol in protocols:
#             proxy_url = f'{protocol}://{proxy_ip}:{proxy_port}'
            
#             try:
#                 test_response = requests.get('https://www.youtube.com', proxies={'http': proxy_url, 'https': proxy_url}, timeout=5)
#                 if test_response.status_code == 200:
#                     print(f"success {proxy_url}")
#                     working_proxies.append(proxy_url)
#             except requests.exceptions.RequestException:
#                 # Handle exceptions for failed requests
#                 print(f"fail {proxy_url}")
#                 continue

# else:
#     print(f"Failed to fetch proxies. Status code: {proxy_response.status_code}")
