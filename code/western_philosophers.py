import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from collections import defaultdict
from default_ordered_dict import DefaultOrderedDict
import re
import string
import urllib
import os

# WESTERN PHILOSOPHERS


def add_philosopher(url, name, phil_dict, time_period, birth='BC', death='BC', western=True):
    '''
    Add the philosopher's information to the dictionary

    INPUT: url - the url that corresponds to the philosopher's profile
           name - name of philosopher
           phil_dict - the dictionary of philsoophers thus far
           time_period - time from which philosopher is from
           birth - Whether the philosopher was born in 'BC' or 'AD' era
           birth - Whether the philosopher died in 'BC' or 'AD' era
           western - Whether the philosopher is a western thinker or not

    OUTPUT: philosopher dictionary updated with new philosopher's information
    '''
    # Request url
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Unidecode first paragraph
    par = unidecode(soup.select('p')[0].get_text())

    # Split text on parentheses
    split_par = re.split(r'[()]', par)

    # Calculate lifespan of philosopher
    all=string.maketrans('','')
    nodigs=all.translate(all, string.digits)

    # Check for item that contains years lived
    for item in split_par:
        lifespan = item.translate(all, nodigs)
        if len(lifespan) > 2:
            break
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

def get_image(name):
    '''
    Saves the image of given philosopher and returns filepath
    INPUT: name of philosopher
    OUTPUT: filepath of image file
    '''
    # Google images url with search terms of name
    img_url = '''https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1440&bih=803&q={}&oq={}&
                    gs_l=img.3..0l10.1021.2400.0.2681.10.7.0.3.3.0.82.519.7.7.0....0...
                    1ac.1.64.img..0.10.523.IxXhEvSJyAw
               '''.format(name, name)
    # Request url
    r = requests.get(img_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Unidecode source url
    url = unidecode(soup.img['src'])

    # Specify filepath for image and save it accordingly
    filepath = '../images/' + name.lower().replace(' ', '_') + '.jpg'
    urllib.urlretrieve(url, filepath)

    return filepath

def ancient_time_period(time_period):
    '''
    Get information for philosophers of a certain era for ancient time periods
    '''
    # Make Request to page of specific time period
    r = requests.get('http://www.philosophybasics.com/historical_' + time_period + '.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Determine the <a> tags that are philosopher names
    philosophers = soup.select('a')
    if time_period == 'presocratic':
        min_slice, max_slice = 11, 23

    elif time_period == 'socratic':
        min_slice, max_slice = 10, 14

    elif time_period == 'hellenistic':
        min_slice, max_slice = 10, 15

    else: # time_period == 'roman'
        min_slice, max_slice = 9, 14

    # Return list of unidecoded philosopher names
    philosophers = [unidecode(x.string) for x in philosophers[min_slice:max_slice]]

    # Base url for philosopher profile pages
    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    # Determine url to get request from
    if time_period == 'presocratic':
        for name in philosophers:
            # Account for double name
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

        phil_dict = thucydides(phil_dict)

    elif time_period == 'hellenistic':
        for name in philosophers:
            # Account for double name
            if name == 'Zeno of Citium':
                name = 'Zeno_Citrium'
                birth, death = 'BC', 'BC'
                url = base_url + 'zeno_citium.html'

            # Account for inconsistency in url pattern
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

def ancient_philosophers():
    '''
    Combine all ancient time period philosophers into one dictionary
    '''
    pre_socratic = ancient_time_period('presocratic')
    socratic = ancient_time_period('socratic')
    hellenistic = ancient_time_period('hellenistic')
    roman = ancient_time_period('roman')

    ancient = pre_socratic
    ancient.update(socratic)
    ancient.update(hellenistic)
    ancient.update(roman)

    return ancient

def medieval_time_period(time_period):
    '''
    Get information for philosophers of a certain era for medieval time periods
    '''
    # Make Request to page of specific time period
    r = requests.get('http://www.philosophybasics.com/historical_' + time_period + '.html')
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get names of each philosopher from specified time period
    philosophers = soup.select('a')

    # Determine which <a> tags are philosopher names
    if time_period == 'medieval':
        min_slice, max_slice = 8, 18

    else: # time_period == 'renaissance'
        min_slice, max_slice = 12, 16

    # Create list of unidecoded philosopher names
    philosophers = [unidecode(x.string) for x in philosophers[min_slice:max_slice]]

    # Url for philosopher profile pages
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


def medieval_philosophers():
    '''
    Combine all medieval philosophers into one dictionary
    '''
    medieval = medieval_time_period('medieval')
    renaissance = medieval_time_period('renaissance')

    medieval = medieval
    medieval.update(renaissance)

    return medieval

def modern_time_period(time_period):
    '''
    Get information for philosophers of a certain era for modern time period
    '''
    # Make Request to page of specific time period
    r = requests.get('http://www.philosophybasics.com/historical_' + time_period + '.html')
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

def modern_philosophers():
    '''
    Combine all modern philosopher groups into one dictionary
    '''
    reason = modern_time_period('reason')
    enlightenment = modern_time_period('enlightenment')
    modern = modern_time_period('modern')

    modern_phil = reason
    modern_phil.update(enlightenment)
    modern_phil.update(modern)

    return modern_phil

def western_philosophers():
    '''
    Combine all western philosophers into one dictionary
    '''
    ancient = ancient_philosophers()
    medieval = medieval_philosophers()
    modern = modern_philosophers()

    western = ancient
    western.update(medieval)
    western.update(modern)

    return western

def find_nationality(d):
    '''
    Determine the nationality of each philosopher
    INPUT: Dictionary (philosopher data)
    OUTPUT: Dictionary with added nationality feature
    '''
    time_periods = ['presocratic', 'socratic', 'hellenistic', 'roman', 'medieval', 'renaissance', 'reason', \
                   'enlightenment', 'modern']
    for time_period in time_periods:
        url = 'http://www.philosophybasics.com/historical_' + time_period + '.html'
        r = requests.get(url)
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

def thucydides(d):
    url = 'https://en.wikipedia.org/wiki/Thucydides'

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    name_tag = soup.select('h1#firstHeading')
    name = unidecode(name_tag[0].string)

    lifespan = soup.select('span')
    birth = unidecode(lifespan[2].string)
    death = unidecode(lifespan[4].string)
    nationality = 'Greek'
    time_period = 'Socratic'
    western = True

    d[name]['year_born'] = -1 * int(filter(str.isdigit, birth))
    d[name]['year_died'] = -1 * int(filter(str.isdigit, death))
    d[name]['time_period'] = time_period
    d[name]['Nationality'] = nationality
    d[name]['Western?'] = western

    return d

if __name__ == '__main__':
    western = western_philosophers()
    western = find_nationality(western)
    western = standardize_names(western)
