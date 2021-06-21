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

with open('paral_two_kommersant_tass.csv', 'a', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
    writer.writeheader()


def write_csv(data):
    with open('paral_two_kommersant_tass.csv', 'a', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
        writer.writerow({'text1': data['text1'], 'text2': data['text2']})
        print(data)
        print('--------------------------------')
        print()

day_delta = datetime.timedelta(days=1)
start_date = datetime.date(2020, 8, 8)
end_date = datetime.date.today()

for d in range((end_date - start_date).days):
    dat = start_date + d * day_delta
    dat = str(dat)
    print(dat)
    r1 = requests.get('https://www.kommersant.ru/archive/news/day/{}'.format(dat))
    s1 = BeautifulSoup(r1.text, 'lxml')
    all_links = ['https://www.kommersant.ru' + i.find('a').get('href') for i in s1.find_all('li', class_='archive_date_result__item')]
    all_title = [i.find('a').text.strip()[i.find('a').text.strip().rfind('\n'):].replace('\n', '').replace('  ', '') for i in s1.find_all('li', class_='archive_date_result__item')]
    assert len(all_title) == len(all_links)
    d = {}
    for i in range(len(all_links)):
        d[all_title[i]] = all_links[i]

    for title in all_title:
        try:
            search = title

            h = {"type": ["default", "article", "event"], "sections": [], "searchStr": search, "sort": "score", "from": 0, "size": 20}

            r = requests.post('https://tass.ru/userApi/search',
                              json=h)
            link_tass = "https://tass.ru" + dict(json.loads(r.text)[0])['link']
            title_tass = dict(json.loads(r.text)[0])['title']
            date_tass = dict(json.loads(r.text)[0])['date']
            date_tass = str(datetime.datetime.utcfromtimestamp(date_tass).strftime('%Y-%m'))
            if date_tass == str(dat[:7]):
                r2 = requests.get(d[title])
                s2 = BeautifulSoup(r2.text, 'lxml')
                text1 = s2.find('div', class_='article_text_wrapper').text.strip().replace('\n', ' ')

                r3 = requests.get(link_tass)
                s3 = BeautifulSoup(r3.text, 'lxml')
                text2 = ' '.join([i.text.strip().replace('\n', ' ') for i in s3.find_all('div', class_='text-block')])
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

                data = {'text1': text1, 'text2': text2}
                write_csv(data)

        except Exception as e:
            pass
