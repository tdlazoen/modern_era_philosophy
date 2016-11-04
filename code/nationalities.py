import requests
from bs4 import BeautifulSoup
import re
import json

def get_countries_nationalities():
    r = requests.get('https://www.englishclub.com/vocabulary/world-countries-nationality.htm')

    soup = BeautifulSoup(r.content, 'html.parser')
    countries = soup.select('tr > td:nth-of-type(1)')
    countries = [x.text.lower().strip() for x in countries]
    countries = [re.split(r'[\(\)]', x)[0].strip() for x in countries]

    nationalities = soup.select('tr > td:nth-of-type(2)')
    nationalities = [x.text.lower().strip() for x in nationalities]

    exceptions = ['united kingdom', 'belarus', 'croatia', 'madagascar', \
                  'monaco', 'papua new guinea', 'saudi arabia', 'serbia', \
                  'slovenia', 'tajikistan', 'turkmenistan', 'united arab emirates', \
                  'united kingdom']

    drop = [countries.index('liechtenstein'), \
            countries.index('myanmar see burma'), \
            countries.index('new zealand'), \
            countries.index('solomon islands'), \
            countries.index('trinidad and tobago'), \
            countries.index('vatican city')]

    for i, idx in enumerate(drop):
        countries.pop(idx-i)
        nationalities.pop(idx-i)

    for i in range(len(countries)):
        if countries[i] == 'united states of america':
            countries[i] = 'united states'
            nationalities[i] = 'american'
        elif countries[i] in exceptions:
            nationalities[i] = countries[i].split()[-1].strip()
        elif countries[i] == 'luxembourg':
            nationalities[i] = 'luxembourgish'

    return countries, nationalities

if __name__ == '__main__':
    countries, nationalities = get_countries_nationalities()
    nationality_dict = {c: n for c, n in zip(countries, nationalities)}

    with open('../data/nationalities.json', 'w') as f:
        json.dump(nationality_dict, f)
