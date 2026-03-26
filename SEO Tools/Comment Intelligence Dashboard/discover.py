import requests
from bs4 import BeautifulSoup
import urllib.parse

HEADERS = {"User-Agent": "Mozilla/5.0"}

def search_google(query, num_results=10):
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num={num_results}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    links = []
    for a in soup.select("a"):
        href = a.get("href")
        if href and "/url?q=" in href:
            link = href.split("/url?q=")[1].split("&")[0]
            if "google.com" not in link:
                links.append(link)
    return list(set(links))

def discover(seed_site, topic_keywords):
    queries = [f"{topic_keywords} site:{seed_site}"]  # you can add more operators
    urls = []
    for q in queries:
        urls.extend(search_google(q))
    return list(set(urls))