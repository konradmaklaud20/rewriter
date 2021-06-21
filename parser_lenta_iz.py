import difflib
import requests
from bs4 import BeautifulSoup
import datetime
import csv

pattern = r'/Корр. ТАСС \w+\s\w+/'
pattern2 = r'ИТАР-ТАСС \w+\s+\w+/'
date_dict = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
             "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"}

with open('paral_two_lenta_iz.csv', 'a', encoding='utf8') as f:
    writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
    writer.writeheader()


def write_csv(data):
    with open('paral_two_lenta_iz.csv', 'a', encoding='utf8') as f:
        writer = csv.DictWriter(f, fieldnames=["text1", "text2"])
        writer.writerow({'text1': data['text1'], 'text2': data['text2']})
        print(data)
        print('--------------------------------')
        print()

def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()


day_delta = datetime.timedelta(days=1)
start_date = datetime.date(2020, 6, 6)
end_date = datetime.date.today()
for d in range((end_date - start_date).days):
    try:
        dat = start_date + d * day_delta
        dat = str(dat)
        dat = dat.replace('-', '/')
        print(dat)
        r1 = requests.get('https://lenta.ru/news/{}'.format(dat))
        s1 = BeautifulSoup(r1.text, 'lxml')

        link_1 = ['https://lenta.ru' + i.find('a').get('href') for i in
                  s1.find_all('div', class_='item news b-tabloid__topic_news')]
        title_1 = [i.find('a').text.replace('\xa0', ' ') for i in
                   s1.find_all('div', class_='item news b-tabloid__topic_news')]

        d = {}
        for l in range(len(link_1)):
            d[title_1[l]] = link_1[l]

        for i in title_1:
            r = requests.get('https://iz.ru/search?text={}&sort=1&type=0&prd=0&date_from=&date_to='.format(i))
            s = BeautifulSoup(r.text, 'lxml')
            try:
                link_2 = [i.find('a').get('href') for i in s.find_all('div', class_='view-search')][0]
                title_2 = [i.find('a').text.strip() for i in s.find_all('div', class_='view-search')][0]
            except:
                title_2 = ''
            similarity_res = similarity(i, title_2)
            
            if similarity_res > 0.6:
               
                try:
                    r2 = requests.get(d[i])
                    s2 = BeautifulSoup(r2.text, 'lxml')
                    text1 = s2.find('div', itemprop="articleBody").text.strip().replace('\xa0', ' ')

                    r3 = requests.get(link_2)

                    s3 = BeautifulSoup(r3.text, 'lxml')

                    text2 = s3.find('article').text.strip().replace('\xa0', ' ').replace('\t', '').replace('\n', '').replace('  ', ' ')
                    ind = text2.find('Поделиться:')
                    ind2 = text2.upper().find('ЧИТАЙТЕ ТАКЖЕ')
                    text2 = text2[:ind]
                    text2 = text2[:ind2]
                    data = {'text1': text1, 'text2': text2}
                    write_csv(data)
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
