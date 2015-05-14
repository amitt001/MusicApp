import re
import sys
import json
import requests
import urlparse
from bs4 import BeautifulSoup as bs

"""
a simple youtube crawler
using all the python standard packages excpet bs4
part of my project. 

A file containing all the search quesries
reads file line by line->search youtube->get first link->add to the file
"""


def ySpider(query, base_url="http://youtube.com"):
    #remove any specail character, but space
    query = re.sub(r'[^a-zA-Z0-9 ]', '', query)
    #sub space with a +
    query = re.sub(r'\s', '+', query)
    search_query = 'results?search_query=' + query
    url = urlparse.urljoin(base_url, search_query)
    
    response = requests.get(url)
    #check status
    if response.status_code != 200:
        print('Check your internet connection or some other problems with network...exiting')
        sys.exit(-1)
    ysoup = bs(response.text)
    print ysoup.find('a', {'class': 'yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink     spf-link '})
    rellink = ysoup.find('a', {'class': 'yt-uix-tile-link yt-ui-ellipsis yt-ui-ellipsis-2 yt-uix-sessionlink     spf-link '}).get('href')
    return urlparse.urljoin(base_url, rellink)


def filereader(filename):
    data = {}
    with open(filename) as fobj, open('utubesongs', 'w') as wobj:
        for query in fobj.readlines():
            result = ySpider(query)
            data[query] = result
        json.dump(data, wobj)

if __name__ == '__main__':
    filereader('songslist.txt')