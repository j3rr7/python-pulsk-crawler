import requests
import bs4
import re
import csv
import json

BASE_URL = "https://www.pulsk.com"
ADDITIONAL_URL = [
    "/beautiful-girl", "/gosip-selebriti", "/misteri", "/rumah-dekorasi",
    "/selfie", "/musik-film-buku", "/kartun-dan-anime", "/cerita-fiksi",
    "/life", "/kesehatan-fitness", "/olahraga", "/travelling", "/video",
    "/otomotif", "/kuliner-cooking", "/fashion", "/flora-fauna", "/lucu-lucu",
    "/berita-peristiwa", "/WOW-Keren"
]
INDEXING_URL = "/{PAGE}/top/{index}"
CONST_DEPTH = 300
CURRENT_DEPTH = 0
LIST_OF_URLS = []
VISITED_SITE = []


def extract_data(items):
    global LIST_OF_URLS, VISITED_SITE, CURRENT_DEPTH, CONST_DEPTH

    if CURRENT_DEPTH >= CONST_DEPTH:
        return

    for item in items:
        try:
            extract_links(item)

            total_photos = item.find('div', class_='total-photo')
            img_url = item.find('img')['src']
            raw_title = item.find('div', class_='entry-description')
            raw_author = item.find('div', class_='poster')
            raw_tag = item.find('div', class_='category-label')
            raw_stats = item.find('div', class_='stats')
            raw_view = raw_stats.find('span', class_='views').text
            raw_time = raw_stats.findAll('span')[1].text
            views = re.findall('\d*\,?\d+', raw_view)
            times = re.findall('\d.*[a-zA-Z]+', raw_time)
            res_data = {
                'total-photos': total_photos.text if total_photos else '-1',
                'title': raw_title.text if raw_title else 'None',
                'image_url': img_url if img_url else 'None',
                'article_url': BASE_URL + raw_title.find('a')['href'],
                'author_url:': BASE_URL + raw_author.find('a')['href'],
                'author_name': raw_author.text if raw_author else 'None',
                'tag_url': BASE_URL + raw_tag.find('a')['href'],
                'tag': raw_tag.text if raw_tag else 'None',
                'views': views[0] if views else 'None',
                'time': times[0] if times else 'None',
            }

            CURRENT_DEPTH += 1

            with open('result.csv', 'a', newline='', encoding='UTF-8') as f:
                writer = csv.writer(f)
                writer.writerow(res_data.values())

        except Exception as e:
            print("ERROR: ", e)


def extract_links(item):
    global LIST_OF_URLS, VISITED_SITE, CURRENT_DEPTH, CONST_DEPTH

    links = item.findAll('a')
    if CURRENT_DEPTH < CONST_DEPTH:
        for i in links:
            if BASE_URL + i['href'] not in VISITED_SITE:
                LIST_OF_URLS.append(BASE_URL + i['href'])
                VISITED_SITE.append(BASE_URL + i['href'])


def main():
    global LIST_OF_URLS, ADDITIONAL_URL, VISITED_SITE, CURRENT_DEPTH, CONST_DEPTH

    base = requests.get(BASE_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
    if base.status_code == 200:
        raw_data = bs4.BeautifulSoup(base.text, 'html.parser')
        # with open('index.html', 'r') as f:
        # raw_data = bs4.BeautifulSoup(f.read(), 'html.parser')
        items = raw_data.find_all('div', class_='item article')
        extract_data(items)
        print("Total links: ", len(LIST_OF_URLS))

        # while ADDITIONAL_URL:
        #    base = requests.get(BASE_URL + ADDITIONAL_URL.pop(), headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        #    raw_data = bs4.BeautifulSoup(base.text, 'html.parser')
        #    items = raw_data.find_all('div', class_='item article')
        #    extract_data(items)
        #    print("Total links: ", len(LIST_OF_URLS))

        while LIST_OF_URLS:
            base = requests.get(LIST_OF_URLS.pop(), headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
            if base.status_code == 200:
                raw_data = bs4.BeautifulSoup(base.text, 'html.parser')
                items = raw_data.find_all('div', class_='item article')
                extract_data(items)
            print("Total updated links: ", len(LIST_OF_URLS))

        print(f"total depth: {CURRENT_DEPTH}\n")
        print(f"total visited: {len(VISITED_SITE)}\n")
        with open("stats.txt", "w") as f:
            f.write(f"total depth: {CURRENT_DEPTH}\n")
            f.write(f"total visited: {len(VISITED_SITE)}\n")
            f.write(json.dumps(VISITED_SITE, indent=2))


if __name__ == '__main__':
    main()
