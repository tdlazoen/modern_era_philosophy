import numpy as np
import pandas as pd
from requests import get
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import defaultdict
from default_ordered_dict import DefaultOrderedDict
import re
import string
import urllib
import os

# WESTERN PHILOSOPHERS

# Add the philosopher into the dictionary
def add_philosopher(url, name, phil_dict, time_period, birth='BC', death='BC', western=True):
    r = get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Unidecode first paragraph
    par = unidecode(soup.select('p')[0].get_text())
    sentences = par.split('.')

    # Calculate lifespan of philosopher
    all=string.maketrans('','')
    nodigs=all.translate(all, string.digits)

    # Check for sentence that contains years person lived
    for sentence in sentences:
        lifespan = sentence.translate(all, nodigs)
        if len(lifespan) > 2:
            break

    # Check if there were extra numbers in the sentence
    if len(lifespan) > 8:
        lifespan = lifespan[:8]

    # Set Philosopher information (Make year negative if BC)
    middle = len(lifespan) / 2
    try:
        phil_dict[name]['year_born'] = -1 * int(lifespan[:middle]) if birth == 'BC' else int(lifespan[:middle])
        phil_dict[name]['year_died'] = -1 * int(lifespan[middle:]) if death == 'BC' else int(lifespan[middle:])

    # Fill in with null values if can't be read in
    except ValueError:
        phil_dict[name]['year_born'] = float('NaN')
        phil_dict[name]['year_died'] = float('NaN')

    phil_dict[name]['time_period'] = time_period
    phil_dict[name]['Western?'] = western

    return phil_dict

# Gets the image of specified philosopher
def get_image(name):
    img_url = '''https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1440&bih=803&q={}&oq={}&
                    gs_l=img.3..0l10.1021.2400.0.2681.10.7.0.3.3.0.82.519.7.7.0....0...
                    1ac.1.64.img..0.10.523.IxXhEvSJyAw
               '''.format(name, name)

    r = get(img_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    url = unidecode(soup.img['src'])

    filepath = 'images/' + name.lower().replace(' ', '_') + '.jpg'
    urllib.urlretrieve(url, filepath)

    return filepath

# Get information for philosophers of a certain era
# for ancient time periods
def ancient_time_period(time_period):
    # Make Request to page of specific time period
    r = get('http://www.philosophybasics.com/historical_' + time_period + '.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get names of each philosopher from specified time period
    philosophers = soup.select('a')
    if time_period == 'presocratic':
        min_slice, max_slice = 11, 23

    elif time_period == 'socratic':
        min_slice, max_slice = 10, 14

    elif time_period == 'hellenistic':
        min_slice, max_slice = 10, 15

    else: # time_period == 'roman'
        min_slice, max_slice = 9, 14

    philosophers = [unidecode(x.string) for x in philosophers[min_slice:max_slice]]

    # Base url for web pages
    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    # Determine url to get request from
    if time_period == 'presocratic':
        for name in philosophers:

            if name == 'Zeno of Elea':
                name = 'Zeno_Elea'

            else:
                # Split name into needed part only
                name = name.split()[0]


            url = base_url + name.lower() + '.html'

            phil_dict = add_philosopher(url, name, phil_dict, time_period)

    elif time_period == 'socratic':
        for name in philosophers:
            name = name.split()[0]

            url = base_url + name.lower() + '.html'

            phil_dict = add_philosopher(url, name, phil_dict, time_period)

    elif time_period == 'hellenistic':
        for name in philosophers:
            if name == 'Zeno of Citium':
                name = 'Zeno_Citrium'
                birth, death = 'BC', 'BC'
                url = base_url + 'zeno_citium.html'

            elif name == 'Philo of Alexandria':
                name = 'Philo'
                birth, death = 'BC', 'AC'
                url = base_url + name.lower() + '.html'

            else:
                birth, death = 'BC', 'BC'
                url = base_url + name.lower() + '.html'

            if name == 'Plotinus':
                birth, death = 'AC', 'AC'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'roman'
        for name in philosophers:
            if name == 'Cicero, Marcus Tullius':
                name = 'Cicero'
                birth, death = 'BC', 'BC'
                url = base_url + name.lower() + '.html'

            elif name == 'St. Augustine of Hippo':
                name = 'Augustine'
                birth, death = 'AD', 'AD'
                url = base_url + name.lower() + '.html'

            else:
                name = name.split(r'[, \. ' ']')[0]
                birth, death = 'AD', 'AD'
                url = base_url + name.lower() + '.html'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict

# Group dictionaries from ancient time period together
def ancient_philosophers():
    pre_socratic = ancient_time_period('presocratic')
    socratic = ancient_time_period('socratic')
    hellenistic = ancient_time_period('hellenistic')
    roman = ancient_time_period('roman')

    ancient = pre_socratic
    ancient.update(socratic)
    ancient.update(hellenistic)
    ancient.update(roman)

    return ancient

# Get information for philosophers of a certain era
# for medieval time periods
def medieval_time_period(time_period):
    # Make Request to page of specific time period
    r = get('http://www.philosophybasics.com/historical_' + time_period + '.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get names of each philosopher from specified time period
    philosophers = soup.select('a')

    if time_period == 'medieval':
        min_slice, max_slice = 8, 18

    else: # time_period == 'renaissance'
        min_slice, max_slice = 12, 16

    philosophers = [unidecode(x.string) for x in philosophers[min_slice:max_slice]]

    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    if time_period == 'medieval':

        for name in philosophers:

            if name == 'Bacon, Roger':
                url = base_url + 'bacon_roger.html'

            else:
                name = name.split(r'[, ' ']')[0]
                url = base_url + name.lower() + '.html'

            birth, death = 'AD', 'AD'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'Renaissance'

        for name in philosophers:

            if name == 'Bacon, Sir Francis':
                name = 'Sir_Francis_Bacon'
                url = base_url + 'bacon_francis.html'

            else:
                name = name.split(',')[0]
                url = base_url + name.lower() + '.html'

            birth, death = 'AD', 'AD'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict

# Combine dictionaries from medieval time period
def medieval_philosophers():
    medieval = medieval_time_period('medieval')
    renaissance = medieval_time_period('renaissance')

    medieval = medieval
    medieval.update(renaissance)

    return medieval

# Get information for philosophers of a certain era
# for modern time periods
def modern_time_period(time_period):
    # Make Request to page of specific time period
    r = get('http://www.philosophybasics.com/historical_' + time_period + '.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get names of each philosopher from specified time period
    philosophers = soup.select('a')

    if time_period == 'reason' or time_period == 'enlightenment':
        min_slice, max_slice = 9, 16

    else: # time_period == 'modern'
        min_slice, max_slice = 8, 36

    philosophers = [unidecode(x.string) for x in philosophers[min_slice:max_slice]]

    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    if time_period == 'reason':
        for name in philosophers:

            name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    elif time_period == 'enlightenment':
        for  name in philosophers:

            name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'modern'
        for name in philosophers:

            if name == 'Friedrich Schelling':
                name_temp = 'Schelling'

            else:
                name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_philosopher(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict

# Group modern philosophers together
def modern_philosophers():
    reason = modern_time_period('reason')
    enlightenment = modern_time_period('enlightenment')
    modern = modern_time_period('modern')

    modern_phil = reason
    modern_phil.update(enlightenment)
    modern_phil.update(modern)

    return modern_phil

# Combine all western philosophers into one dictionary
def western_philosophers():
    ancient = ancient_philosophers()
    medieval = medieval_philosophers()
    modern = modern_philosophers()

    western = ancient
    western.update(medieval)
    western.update(modern)

    return western

def find_nationality(d):
    time_periods = ['presocratic', 'socratic', 'hellenistic', 'roman', 'medieval', 'renaissance', 'reason', \
                   'enlightenment', 'modern']
    for time_period in time_periods:
        url = 'http://www.philosophybasics.com/historical_' + time_period + '.html'
        r = get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        content = soup.select('font font')

        nationals = []
        for i in xrange(len(content)):
            lst_words = [unidecode(x) for x in content[i].get_text().strip().split('\n')]
            if len(lst_words) > 1:
                nationals.append(lst_words)

        nationals = [item for lst in nationals for item in lst]

        i = 0
        for name in d.iterkeys():
            if d[name]['time_period'] == time_period:

                components = re.split(r'\)', nationals[i])

                d[name]['Nationality'] = components[-1].strip()

                i += 1

    return d

def standardize_names(d, images=False):
    new_d = DefaultOrderedDict(dict)
    for key, value in d.iteritems():
        components = re.split(r',', key)
        new_key = ' '.join(x for x in components[::-1])

        new_d[new_key.strip()] = value

        if images: # Only set true on first run to load images
            newpath = './images'
            if not os.path.exists(newpath):
                os.makedirs(newpath)

            filepath = get_image(new_key.strip())
            new_d[new_key.strip()]['Image'] = filepath

    return new_d

if __name__ == '__main__':
    western = western_philosophers()
    western = find_nationality(western)
    western = standardize_names(western)
