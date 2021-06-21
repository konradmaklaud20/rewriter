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

with open('paral_two_360tv_tass_ria.csv', 'a', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
    writer.writeheader()


def write_csv(data):
    with open('paral_two_360tv_tass_ria.csv', 'a', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
        writer.writerow({'text1': data['text1'], 'text2': data['text2']})
        print(data)
        print('--------------------------------')
        print()


for i in range(1, 10000):
    try:
        print("i: ", i)
        r_360_s = requests.get('https://360tv.ru/web-api/v1/get_typed_page/?is_face=true&page={}'.format(i))
        s_360_s = BeautifulSoup(r_360_s.text, 'lxml')
        all_links_360 = ["https:" + i.get("href") for i in s_360_s.find_all('a', {"class": "g360_grid-tile"})]

        for link_360 in all_links_360:
            r_360 = requests.get(link_360)
            s_360 = BeautifulSoup(r_360.text, 'lxml')
            date_360 = s_360.find('span', {"class": "iv-pubdate"}).text
            for k in date_dict.keys():
                if k in date_360:
                    date_360 = date_360.replace(k, date_dict[k])
                    date_360 = '.'.join(date_360[:10].split())[3:]
            title_360 = s_360.find('h1', {"class": "content-header"}).text.strip()
            text_360 = s_360.find('p', {"class": "news-lead"}).text.strip() \
                       + " " + s_360.find('section', {"class": "news-text js-mediator-article"}).text.strip()

            try:
                r2 = requests.get('https://ria.ru/services/search/getmore/?query={}&tags_limit=20&sort=relevance'.format(title_360))
                s2 = BeautifulSoup(r2.text, 'lxml')
                title_ria = s2.find('div', class_='list-item__content').find('a', class_='list-item__title color-font-hover-only').text.strip()
                date_ria = s2.find('div', class_='list-item__date').text.strip()[:-7]

                if date_ria[-4] == '2':
                    for k in date_dict.keys():
                        if k in date_ria:
                            date_ria = date_ria.replace(k, date_dict[k])
                            date_ria = '.'.join(date_ria[:10].split())[3:]

                            if len(date_ria.split('.')[0]) == 1:
                                date_ria = '0' + date_ria

                else:
                    for k in date_dict.keys():
                        if k in date_ria:
                            date_ria = date_ria.replace(k, date_dict[k])
                            date_ria = '.'.join(date_ria.split()).split('.')[1] + '.2021'

                link_ria = s2.find('div', class_='list-item__content').find('a', class_='list-item__title color-font-hover-only').get('href')
                
                if date_ria == date_360 and 'Дайджест' not in title_ria:

                    r3 = requests.get(link_ria)
                    s3 = BeautifulSoup(r3.text, 'lxml')
                    text_ria = ' '.join([i.text.strip() for i in s3.find_all('div', class_='article__block', attrs={"data-type": "text"})]).replace('\n', ' ')
                    ind_1_ria = text_ria.find('— РИА Новости.')
                    if ind_1_ria != -1:
                        text_ria = text_ria[ind_1_ria + len('— РИА Новости. '):]

                    ind_2_ria = text_ria.find('- РИА Новости.')
                    if ind_2_ria != -1:
                        text_ria = text_ria[ind_2_ria + len('- РИА Новости. '):]

                    ind_3_ria = text_ria.find('– РИА Новости.')
                    if ind_3_ria != -1:
                        text_ria = text_ria[ind_3_ria + len('– РИА Новости. '):]

                    ind_4_ria = text_ria.find('/ Радио Sputnik.')
                    if ind_4_ria != -1:
                        text_ria = text_ria[ind_4_ria + len('/ Радио Sputnik. '):]

                    if len(text_ria) < 3000 and len(text_360) < 3000:
                        data = {'text1': text_ria.replace('\xa0', ' '), 'text2': text_360.replace('\xa0', ' ')}
                        write_csv(data)

            except Exception:
                pass

            try:

                h = {"type": ["default", "article", "event"], "sections": [], "searchStr": title_360, "sort": "score",
                     "from": 0, "size": 20}

                r = requests.post('https://tass.ru/userApi/search',
                                  json=h, timeout=30)
                link_tass = "https://tass.ru" + dict(json.loads(r.text)[0])['link']

                title_tass = dict(json.loads(r.text)[0])['title']
                date_tass = dict(json.loads(r.text)[0])['date']
                date_tass = str(datetime.datetime.utcfromtimestamp(date_tass).strftime('%Y-%m'))
                date_tass = date_tass.split('-')
                date_tass = date_tass[1] + '.' + date_tass[0]

                if date_tass == date_360:

                    r33 = requests.get(link_tass)
                    s33 = BeautifulSoup(r33.text, 'lxml')
                    text2 = ' '.join([i.text.strip().replace('\n', ' ') for i in s33.find_all('div', class_='text-block')])
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

                        if len(text2) < 3000 and len(text_360) < 3000:
                            data = {'text1': text2.replace('\xa0', ' '), 'text2': text_360.replace('\xa0', ' ')}
                            write_csv(data)

            except Exception as e:
                pass
    except Exception as e:
        print(e)
