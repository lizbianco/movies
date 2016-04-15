# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 16:08:01 2016

@author: EBianco
"""

import requests
from bs4 import BeautifulSoup
import re
import dateutil.parser
from pprint import pprint
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException

url1 = 'http://www.boxofficemojo.com/movies/?id=atlasshruggedpart2.htm'
url2 = 'http://www.boxofficemojo.com/movies/?id=starwars4.htm'
url = url1
response = requests.get(url)
page = response.text
soup = BeautifulSoup(page, 'lxml')
driver = webdriver.PhantomJS()

#Tried and True Functions
def get_movie_value(soup, field_name):
    obj = soup.find(text=re.compile(field_name))
    if not obj:
        return None
    next_sibling = obj.findNextSibling()
    if next_sibling:
        return next_sibling.text
    else:
        return None
    
def get_dlg (string):
    try:
        obj = str(soup.find(text=re.compile('Domestic Lifetime Gross:')))
        obj = obj.split(':')
        obj = int(obj[1].replace('$','').replace(',',''))
        return obj
    except IndexError:
        return None

   
def get_the_players(soup, field_name):
    obj = soup.find(text = field_name)
    if not obj:
        return None
    elif field_name == 'Actors:':
        return obj.parent.parent.findNext('td')
    else:
        return obj.parent.parent.findNext('td').text
    
def get_adjusted(field_name):
    driver.get(url)
    inf_adjust_2016_selector = '//select[@name="ticketyr"]/option[@value="2016"]'
    driver.find_element_by_xpath(inf_adjust_2016_selector).click()
    go_button = driver.find_element_by_name("Go")
    go_button.click()
    if field_name == "DTotalAG":
        gross_selector = '//font[contains(text(), "Domestic Total")]/b'
        return driver.find_element_by_xpath(gross_selector).text
    elif field_name == "DLifetimeAG":
        try:
            gross_selector = '//b[contains(text(), "Domestic Lifetime Adj. Gross")]'
            item = driver.find_element_by_xpath(gross_selector).text
            items = item.split(':')
            return(items[1])
        except NoSuchElementException:
            return None
    
#Formatting Functions    
def to_date(datestring):
    date = dateutil.parser.parse(datestring)
    return date

def money_to_int(moneystring):
    moneystring = moneystring.replace('$','').replace(',','')
    return int(moneystring)

def runtime_to_minutes(runtimestring):
    runtime = runtimestring.split()
    try:
        minutes = int(runtime[0])*60 + int(runtime[2])
        return minutes
    except:
        return None

def budget_to_int(budgetstring):
    if budgetstring == 'N/A':
        return None
    else:
        budgetstring = budgetstring.replace('$','').replace(' million','')
        budget = int(budgetstring)*1000000
        return budget

def create_list(actors):
    if not actors:
        return None
    else:
        actor_list = []
        actors = str(actors)
        actors = actors.split('<br/>')
        for i in actors:
            i = re.sub('<.+?>', '', i)
            actor_list.append(i)
        return actor_list
    
    #function to create dict
def createdict():
    title_string = soup.find('title').text
    title = title_string.split('(')[0].strip()

    raw_release_date = get_movie_value(soup, 'Release Date')
    release_date = to_date(raw_release_date)

    raw_dtg = get_movie_value(soup, 'Domestic Total')
    domestic_total_gross = money_to_int(raw_dtg)

    dlg = get_dlg(dlg)

    raw_total_adj_gross = get_adjusted('DTotalAG')
    total_adj_gross = money_to_int(raw_total_adj_gross)

    raw_lifetime_adj_gross = get_adjusted('DLifetimeAG')
    if raw_lifetime_adj_gross is None:
        lifetime_adj_gross = None
    else:
        lifetime_adj_gross = money_to_int(raw_lifetime_adj_gross)

    raw_runtime = get_movie_value(soup, 'Runtime')
    runtime =runtime_to_minutes(raw_runtime)

    genre_string = soup.find(text=re.compile('Genre:'))
    genre=str(genre_string.findNextSibling())
    genre=genre.replace('<b>','').replace('</b>','')

    rating = get_movie_value(soup, 'MPAA Rating')

    budgetstring = get_movie_value(soup, 'Production Budget')
    budget = budget_to_int(budgetstring)


    series_raw = str(soup.find(text=re.compile('Series:')))
    series_raw = series_raw.split(': ')
    series = str(series_raw[1])


    director = get_the_players(soup, 'Director:')

    writer = get_the_players(soup, 'Writer:')

    producer = get_the_players(soup,'Producer:')

    composer = get_the_players(soup, 'Composer:')


    actors = get_the_players(soup, 'Actors:') 
    actor_list = create_list(actors)

    headers = ['domestic total adj gross(2016)', 'domestic lifetime adj gross(2016)', 'budget', 'actors', 'director', 'writer', 'producer', 'composer', 'series', 'movie title', 'domestic total gross', 'domestic lifetime', 'release date', 'runtime (mins)', 'rating', 'genre']

    movie_data = []
    movie_dict = dict(zip(headers, [total_adj_gross, lifetime_adj_gross, budget, actor_list, director, writer, producer, composer, series, title, domestic_total_gross, dlg, release_date, runtime, rating, str(genre)]))
    movie_data.append(movie_dict)

    pprint (movie_data)
    
    driverjs.close()
    