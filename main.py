import math

import requests
from bs4 import BeautifulSoup
import collections
import re
import json


def get_list_film_by_year(year):
    wiki_page = 'https://ru.wikipedia.org/wiki/Категория:Фильмы_' + str(year) + '_года'
    links = get_links_films(wiki_page)
    response = requests.get(wiki_page)
    soup = BeautifulSoup(response.text, 'lxml')

    p_tags = soup.find_all("p")
    p_text = "".join(str(p) for p in p_tags)
    pattern = r'Показано (\d+) страниц из (\d+)'

    matches = re.findall(pattern, p_text)
    try:
        all_pages = math.ceil(int(matches[0][1]) / int(matches[0][0]))
    except IndexError:
        all_pages = 1

    cur_page = wiki_page
    for i in range(all_pages - 1):
        response = requests.get(cur_page)
        soup = BeautifulSoup(response.text, 'lxml')
        next_page = soup.find_all("a", string=lambda text: text and 'Следующая страница' in text)[0].get('href')
        next_page = "https://ru.wikipedia.org" + next_page
        links += get_links_films(next_page)
        cur_page = next_page

    return links


def get_links_films(wiki_page):
    links = []
    response = requests.get(wiki_page)
    soup = BeautifulSoup(response.text, 'lxml')

    mv = soup.find_all(id="mw-pages")
    for page in mv:
        films = page.find_all(class_='mw-category-group')
        for film in films:
            ul_elements = film.find_all('ul')
            for ul in ul_elements:
                li_elements = ul.find_all('li')
                for li in li_elements:
                    a_elements = li.find_all('a')
                    for a in a_elements:
                        try:
                            if '/wiki/' in str(a['href']):
                                links.append('https://ru.wikipedia.org' + a['href'])
                        except KeyError:
                            continue
    return links


def infobox(wiki_page):
    try:
        response = requests.get(wiki_page)
        soup = BeautifulSoup(response.text, 'lxml').find_all("table", {"class": "infobox"})[0]
    except:
        return None
    ret = collections.defaultdict(dict)
    section = ""
    for tr in soup.find_all("tr"):
        th = tr.find_all("th")
        if not any(th):
            continue
        th = th[0]
        if str(th.get("colspan")) == '2':
            section = th.get_text(separator=" ", strip=True)
            continue
        k = th.get_text(separator=" ", strip=True).replace('ы', '')

        try:
            v = tr.find_all("td")[0].get_text(separator=", ", strip=True)
            if k == 'Год':
                ret[section][k] = clear_year(v)
            elif k == 'Жанр':
                ret[section][k] = clear_genre(v)
            else:
                ret[section][k] = clear_text(v)
        except IndexError:
            continue
    return dict(ret)


def clear_year(text):
    match = re.search(r'\d{4}', text)
    if match:
        return match.group()
    else:
        return None


def clear_text(text):
    pattern = r'\[.*?\]'
    result = re.sub(pattern, '', text)
    result = re.sub(r'\s{2,}', ' ', result)
    result = re.sub(r'\s*,\s*', ', ', result)
    result = re.sub(r'\s+([.])', r'\1', result)
    result = result.replace('\xa0', ' ')
    result = result.strip()
    return result


def clear_genre(text):
    clean_string = re.sub(r'[^\w\s-]', ' ', text)
    clean_string = re.sub(r'\b[иИ0-9A-Za-z]\b', '', clean_string)
    clean_string = re.sub(r'\s\s+', '|', clean_string.strip())
    return clean_string


def get_plot(wiki_page):
    response = requests.get(wiki_page)
    soup = BeautifulSoup(response.text, 'lxml')
    H2 = soup.select('h2')
    plot_h2 = None
    for h2 in H2:
        if "Сюжет" in h2.text:
            plot_h2 = h2
    try:
        return clear_text(plot_h2.find_all_next("p")[0].get_text(strip=1, separator=' '))
    except Exception as e:
        return None


def get_all_films_info():
    all_links = []
    movies = []
    for year in range(1900, 2024):
        all_links += get_list_film_by_year(year)
        print('YEAR ', year, "DONE")
    cnt = 1
    for link in all_links:
        try:
            print(cnt, '/', len(all_links))
            cnt += 1
            data = {
                'title': None,
                'year': None,
                'director': None,
                'genre': None,
                'country': None,
                'plot': None
            }
            plot = get_plot(link)
            inf = infobox(link)
            if inf is None:
                continue
            data['title'] = list(inf.keys())[0]
            try:
                data['genre'] = inf[data['title']]['Жанр']
            except KeyError:
                data['genre'] = None
            try:
                data['director'] = inf[data['title']]['Режиссёр']
            except KeyError:
                data['director'] = None
            try:
                data['year'] = inf[data['title']]['Год']
            except KeyError:
                data['year'] = None
            try:
                data['country'] = inf[data['title']]['Страна']
            except KeyError:
                try:
                    data['country'] = inf[data['title']]['Страны']
                except KeyError:
                    data['country'] = None
            data['plot'] = get_plot(link)
            movies.append(data)


        except Exception as e:
            continue
    with open("movies_data.json", "w", encoding='utf-8') as file:
        json.dump(movies, file, indent=2, ensure_ascii=False)


get_all_films_info()
