import requests

article_id = "0554598001" # From user screenshot
folder_3 = article_id[:3]
folder_2 = article_id[:2]

urls_to_test = [
    f"https://lp2.hm.com/hmgoepprod?set=source[/{folder_3}/{article_id}.jpg],origin[dam],category[],type[LOOKBOOK],res[m],hmver[1]&call=url[file:/product/main]",
    f"https://lp2.hm.com/hmgoepprod?set=source[/{folder_3}/{article_id}.jpg],origin[dam],category[],type[DESCRIPTIVESTILLLIFE],res[m],hmver[1]&call=url[file:/product/main]",
    f"https://lp2.hm.com/hmgoepprod?set=source[/{folder_2}/{article_id}.jpg],origin[dam],category[],type[LOOKBOOK],res[m],hmver[1]&call=url[file:/product/main]",
    f"http://img.hm.com/is/image/hmprod/{article_id}", # Older format?
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"Testing URLS for Article: {article_id}")

for i, url in enumerate(urls_to_test):
    try:
        print(f"\n--- Test {i+1} ---")
        print(f"URL: {url}")
        res = requests.get(url, headers=headers, timeout=5)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("SUCCESS! This URL works.")
            if len(res.content) < 1000:
                print("WARNING: Content too small, might be an empty placeholder.")
            else:
                print("Content looks valid (size > 1KB).")
    except Exception as e:
        print(f"Error: {e}")
