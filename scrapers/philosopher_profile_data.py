import requests
from bs4 import BeautifulSoup
from default_ordered_dict import DefaultOrderedDict
import string
import urllib
import os
import re
import time


'''
This file contains the first steps of this project.

Scraped website philosophybasics to obtain the initial set of
philosophers for analysis.  More philosophers were added set later.

http://www.philosophybasics.com/historical.html
'''


def add_new(phil_dict, name, birth, death):
    '''
    INPUT:
        phil_dict - dictionary with philosopher info
        name - name of philosopher
        birth - year of philosopher's birth
        death - year of philosopher's death
    OUTPUT:
        phil_dict - philosopher dictionary with new philosopher added
    '''
    name, filepath = standardize_name(name, image=True)
    phil_dict[name]['time_period'] = determine_time_period(phil_dict, birth)
    phil_dict[name]['year_born'] = birth
    phil_dict[name]['year_died'] = death
    phil_dict[name]['image_path'] = filepath

    return phil_dict


def determine_time_period(phil_dict, birth):
    '''
    INPUT:
        phil_dict - dictionary with philosopher info
        birth - year of philosopher's birth
    OUTPUT:
        time_period - determined time period of philosopher

    This uses information about philosophers already known and uses it
    to determine the time period of newly added philosophers (improved upon
    later)
    '''
    time_periods = set([phil_dict[x]['time_period'] for x in phil_dict])
    for time_period in time_periods:
        years = [int(phil_dict[x]['year_born']) for x in phil_dict if phil_dict[x]['time_period'] == time_period]
        min_year = min(years) - 20
        max_year = max(years) + 20

        if birth in range(min_year, max_year):
            return time_period


def add_initial_philosophers(url, name, phil_dict, time_period, birth='BC', death='BC'):
    '''
    INPUT: url - the url that corresponds to the philosopher's profile
           name - name of philosopher
           phil_dict - the dictionary of philsoophers thus far
           time_period - time from which philosopher is from
           birth - Whether the philosopher was born in 'BC' or 'AD' era
           birth - Whether the philosopher died in 'BC' or 'AD' era
           western - Whether the philosopher is a western thinker or not

    OUTPUT: philosopher dictionary updated with new philosopher's information

    Add the philosopher's information to the dictionary
    '''
    # Request url
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    # first paragraph
    par = soup.select('p')[0].get_text()

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

    return phil_dict


def get_image(name, filepath):
    '''
    INPUT: filepath to save image to
    OUTPUT: filepath of image file
    Saves the image of given philosopher and returns filepath
    '''
    # Google images url with search terms of name
    img_url = '''https://www.google.com/search?site=imghp&tbm=isch&source=hp&biw=1440&bih=803&q={}&oq={}&
                    gs_l=img.3..0l10.1021.2400.0.2681.10.7.0.3.3.0.82.519.7.7.0....0...
                    1ac.1.64.img..0.10.523.IxXhEvSJyAw
               '''.format(name, name)
    # Request url
    r = requests.get(img_url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # source url
    url = soup.img['src']

    # Save image to inputted filepath
    urllib.request.urlretrieve(url, filepath)


def ancient_time_period(time_period):
    '''
    INPUT:
        time_period - time_period to scrape
    OUTPUT:
        phil_dict - dictionary containing ancient era philsopher data

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

    # Return list of philosopher names
    philosophers = [x.string for x in philosophers[min_slice:max_slice]]

    # Base url for philosopher profile pages
    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    # Determine url to get request from
    if time_period == 'presocratic':
        for name in philosophers:
            # Account for double name
            if name == 'Zeno of Elea':
                name_temp = 'Zeno_Elea'

            else:
                # Split name into needed part only
                name_temp = name.split()[0]


            url = base_url + name_temp.lower() + '.html'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period)

    elif time_period == 'socratic':
        for name in philosophers:
            name_temp = name.split()[0]

            url = base_url + name_temp.lower() + '.html'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period)

        phil_dict = thucydides(phil_dict)

    elif time_period == 'hellenistic':
        for name in philosophers:
            # Account for double name
            if name == 'Zeno of Citium':
                name_temp = 'Zeno_Citrium'
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

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'roman'
        for name in philosophers:
            if name == 'Cicero, Marcus Tullius':
                name_temp = 'Cicero'
                birth, death = 'BC', 'BC'
                url = base_url + name.lower() + '.html'

            elif name == 'Marcus Aurelius':
                name_temp = name.replace(' ', '_')

            elif name == 'St. Augustine of Hippo':
                name_temp = 'Augustine'
                birth, death = 'AD', 'AD'
                url = base_url + name_temp.lower() + '.html'

            else:
                name_temp = re.split(r'[,()\.]', name)[0]
                birth, death = 'AD', 'AD'
                url = base_url + name_temp.lower() + '.html'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict


def ancient_philosophers():
    '''
    INPUT:
        None
    OUTPUT:
        ancient - dictionary with information for all ancient era philosophers

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
    INPUT:
        time_period - time_period to scrape
    OUTPUT:
        phil_dict - dictionary containing medieval era philsopher data

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

    # Create list of philosopher names
    philosophers = [x.string for x in philosophers[min_slice:max_slice]]

    # Url for philosopher profile pages
    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    if time_period == 'medieval':

        for name in philosophers:

            if name == 'Bacon, Roger':
                url = base_url + 'bacon_roger.html'

            else:
                name_temp = re.split(r'[(),\." "]', name)[0]
                url = base_url + name_temp.lower() + '.html'

            birth, death = 'AD', 'AD'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'Renaissance'

        for name in philosophers:

            if name == 'Bacon, Sir Francis':
                url = base_url + 'bacon_francis.html'

            else:
                name_temp = name.split(',')[0]
                url = base_url + name_temp.lower() + '.html'

            birth, death = 'AD', 'AD'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict


def medieval_philosophers():
    '''
    INPUT:
        None
    OUTPUT:
        medieval - dictionary with information for all medieval era philosophers

    Combine all medieval philosophers into one dictionary
    '''
    medieval = medieval_time_period('medieval')
    renaissance = medieval_time_period('renaissance')

    medieval = medieval
    medieval.update(renaissance)

    return medieval


def modern_time_period(time_period):
    '''
    INPUT:
        time_period - time_period to scrape
    OUTPUT:
        phil_dict - dictionary containing modern era philsopher data

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

    philosophers = [x.string for x in philosophers[min_slice:max_slice]]

    base_url = 'http://www.philosophybasics.com/philosophers_'
    phil_dict = DefaultOrderedDict(dict)

    if time_period == 'reason':
        for name in philosophers:

            name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    elif time_period == 'enlightenment':
        for  name in philosophers:

            name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    else: # time_period == 'modern'
        for name in philosophers:

            if name == 'Friedrich Schelling':
                name_temp = 'Schelling'

            else:
                name_temp = name.split(',')[0]

            url = base_url + name_temp.lower() + '.html'
            birth, death = 'AD', 'AD'

            phil_dict = add_initial_philosophers(url, name, phil_dict, time_period, birth=birth, death=death)

    return phil_dict


def modern_philosophers():
    '''
    INPUT:
        None
    OUTPUT:
        modern - dictionary with information for all modern era philosophers

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
    INPUT:
        None
    OUTPUT:
        western - dictionary with information for all philosophers

    Combine all western philosophers into one dictionary
    '''
    ancient = ancient_philosophers()
    medieval = medieval_philosophers()
    modern = modern_philosophers()

    western = ancient
    western.update(medieval)
    western.update(modern)

    western = standardize_initial_dict(western)
    western = thucydides(western)

    return western


# Standardize name of philosopher
def standardize_name(name, image=False):
    '''
    INPUT:
        name - name of philosopher
        image - whether to seach and download image of philosopher
    OUTPUT:
        new_name - name formatted as: (title) First Last
        filepath - path where image is saved

    Standardize names of new entries into dictionary
    '''
    if 'Sir' in name:
        components = re.split(r', Sir ', name)
    else:
        components = re.split(r',', name)
    new_name = ' '.join(x for x in components[::-1])

    try:
        start = new_name.index('(')
        end = new_name.index(')')

        new_name = new_name[:start-1] + new_name[end+1:]

    except ValueError:
        pass

    filepath = os.path.expanduser('~') + '/philosophy_capstone/images/' + new_name.strip().lower().replace(' ', '_') + '.jpg'

    if image:
        get_image(new_name.strip(), filepath)

    return new_name.strip(), filepath


# Add consistency across dataset
def standardize_initial_dict(d, images=False):
    '''
    INPUT:
        d - dictionary of philosopher info
        images - whether to seach and download images of philosophers
    OUTPUT:
        new_d - philosopher dictionary with correctly formatted names

    Add Thucydides to dataframe (prominent philosopher not included in
    original scrape)
    '''
    if images: # Only set true on first run to load images
        # Make new directory images
        newpath = os.path.expanduser('~') + '/philosophy_capstone/images'
        if not os.path.exists(newpath):
            os.makedirs(newpath)

    # Create a new dictionary
    new_d = DefaultOrderedDict(dict)
    for key, value in d.iteritems():

        # Get cleaned name and filepath
        new_key, filepath = standardize_name(key, images)

        # Set the new key to the values of the dictionary
        new_d[new_key] = value
        if new_key == 'Voltaire':
            new_d[new_key]['year_born'] = 1694
            new_d[new_key]['year_died'] = 1778
        elif new_key == 'Marcus Tullius Cicero':
            new_d[new_key]['year_born'] = -1 * 106
            new_d[new_key]['year_died'] = -1 * 43

        # Save the filepath location of the image
        new_d[new_key]['image_path'] = filepath

    return new_d


# Add Thucydides (not in original scrape) to data
def thucydides(d):
    '''
    INPUT:
        d - dictionary of philosopher info
    OUTPUT:
        d - dictionary of philosophers with Thucydides added

    Add Thucydides to dataframe (prominent philosopher not included in
    original scrape)
    '''
    # Url to use for Thucydides
    url = 'https://en.wikipedia.org/wiki/Thucydides'

    # Request from url and parse html
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Get name
    name_tag = soup.select('h1#firstHeading')
    name = name_tag[0].string

    # Find lifespan, set other features in entry
    lifespan = soup.select('span')
    birth = lifespan[2].string
    death = lifespan[4].string
    time_period = 'socratic'
    western = True

    # Set the values in dictionary entry 'Thucydides'
    d[name]['year_born'] = -1 * int(filter(str.isdigit, birth))
    d[name]['year_died'] = -1 * int(filter(str.isdigit, death))
    d[name]['time_period'] = time_period

    return d
