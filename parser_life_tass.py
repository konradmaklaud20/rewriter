import requests
from bs4 import BeautifulSoup
import datetime
import json
import csv
import re

pattern = r'/Корр. ТАСС \w+\s\w+/'
pattern2 = r'ИТАР-ТАСС \w+\s+\w+/'
date_dict = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
             "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"}

with open('paral_two_life_tass.csv', 'a', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
    writer.writeheader()


def write_csv(data):
    with open('paral_two_life_tass.csv', 'a', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
        writer.writerow({'text1': data['text1'], 'text2': data['text2']})
        print(data)
        print('--------------------------------')
        print()
        
        
is_next = True
link_life = "https://api.corr.life/public/sections/5e01383bf4352e43d960b258/posts?after=1620421324133"

while is_next is True:

    r_life = requests.get(link_life)
    js_life = dict(json.loads(r_life.text))
    next_page = "https://api.corr.life/public/sections/5e01383bf4352e43d960b258/posts?after=" + \
                str(js_life['meta']["last"])
    link_life = next_page
    if js_life['meta']["last"] != '':
        is_next = True
    for news in js_life['data']:
        title_life = news['title']
        link_news_life = "https://life.ru/p/" + str(news["index"])
        date_life = str(news["publicationDate"][:7].split('-')[1]) + '.' + str(news["publicationDate"][:7].split('-')
                                                                               [0])

        try:
            h = {"type": ["default", "article", "event"], "sections": [], "searchStr": title_life, "sort": "score",
                 "from": 0, "size": 20}

            r = requests.post('https://tass.ru/userApi/search',
                              json=h, timeout=30)

            link_tass = "https://tass.ru" + dict(json.loads(r.text)[0])['link']

            title_tass = dict(json.loads(r.text)[0])['title']
            date_tass = dict(json.loads(r.text)[0])['date']
            date_tass = str(datetime.datetime.utcfromtimestamp(date_tass).strftime('%Y-%m'))
            date_tass = date_tass.split('-')
            date_tass = date_tass[1] + '.' + date_tass[0]

            if date_tass == date_life:

                r33 = requests.get(link_tass)
                s33 = BeautifulSoup(r33.text, 'lxml')
                text2 = str(' '.join([i.text.strip().replace('\n', ' ') for i in s33.find_all('div', class_='text-block')]))

                if len(text2) > 10:
                    ind1 = text2.find('/ТАСС/')
                    ind2 = text2.find('/ИТАР-ТАСС/')
                    if ind1 != -1:
                        text2 = text2[ind1 + len('/ТАСС/. '):]

                    if ind2 != -1:
                        text2 = text2[ind2 + len('/ИТАР-ТАСС/. '):]

                    if '/Корр. ТАСС' in text2:
                        ind_e = [(m.start(0), m.end(0)) for m in re.finditer(pattern, text2)][0][1]
                        text2 = text2[ind_e + 2:]

                    if 'ИТАР-ТАСС' in text2:
                        ind_e = [(m.start(0), m.end(0)) for m in re.finditer(pattern2, text2)][0][1]
                        text2 = text2[ind_e + 2:]

                    r2_life = requests.get(link_news_life)
                    s2_life = BeautifulSoup(r2_life.text, 'lxml')

                    text_life = " ".join(
                        [i.text.strip() for i in s2_life.find('div', class_="col-2 col-m").find_all('p')])

                    if len(text2) < 3000 and len(text_life) < 3000:
                        data = {'text1': text2.replace('\xa0', ' '), 'text2': text_life.replace('\xa0', ' ')}
                        write_csv(data)
        except Exception:
            pass
