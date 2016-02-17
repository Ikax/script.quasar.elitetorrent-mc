# coding: utf-8
__author__ = 'mancuniancol'

import common
from bs4 import BeautifulSoup
from quasar import provider

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()


def extract_torrents(data):
    filters.information()  # print filters settings
    sint = common.ignore_exception(ValueError)(int)
    results = []
    cont = 0
    if data is not None:
        soup = BeautifulSoup(data, 'html5lib')
        links = soup.find("table", class_="fichas-listado")
        if links is not None:
            links = links.tbody.findAll('tr')
            for link in links:
                columns = link.findAll('td')
                if len(columns) == 5:
                    a = columns[0].findAll('a', class_='nombre')
                    name = ""
                    for item in a:
                        name = item.text  # name
                    a = columns[0].findAll('a', class_='icono-bajar')
                    magnet = ""
                    for item in a:
                        magnet = settings.value["url_address"] + item['href']
                    size = None
                    seeds = columns[2].text  # seeds
                    peers = columns[3].text  # peers
                    # info_magnet = common.Magnet(magnet)
                    if filters.verify(name, size):
                        # magnet = common.getlinks(magnet)
                        cont += 1
                        results.append({"name": name.strip(),
                                        "uri": magnet,
                                        # "info_hash": info_magnet.hash,
                                        # "size": size.strip(),
                                        "seeds": sint(seeds),
                                        "peers": sint(peers),
                                        "language": settings.value.get("language", "es"),
                                        "provider": settings.name,
                                        "icon": settings.icon,
                                        })  # return the torrent
                        if cont >= int(settings.value.get("max_magnets", 10)):  # limit magnets
                            break
                    else:
                        provider.log.warning(filters.reason)
    provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Quasar<<<<<<<')
    return results


def search(query):
    info = {"query": query,
            "type": "general"}
    return search_general(info)


def search_general(info):
    info["extra"] = settings.value.get("extra", "")  # add the extra information
    query = filters.type_filtering(info, '+')  # check type filter and set-up filters.title
    url_search = "%s/busqueda/%s/modo:listado" % (settings.value["url_address"], query)
    provider.log.info(url_search)
    browser.open(url_search)
    return extract_torrents(browser.content)


def search_movie(info):
    info["type"] = "movie"
    settings.value["language"] = settings.value.get("language", "es")
    if settings.value["language"] == 'en':  # Title in english
        query = info['title'].encode('utf-8')  # convert from unicode
        if len(info['title']) == len(query):  # it is a english title
            query += ' ' + str(info['year'])  # Title + year
        else:
            query = common.IMDB_title(info['imdb_id'])  # Title + year
    else:  # Title en foreign language
        query = common.translator(info['imdb_id'], settings.value["language"], extra=False)  # Just title
    info["query"] = query
    return search_general(info)


def search_episode(info):
    settings.value["language"] = settings.value.get("language", "es")
    if info['absolute_number'] == 0:
        info["type"] = "show"
        if settings.value["language"] != 'es':
            info["query"] = info['title'].encode('utf-8') + ' s%02de%02d' % (
                info['season'], info['episode'])  # define query
        else:
            info["query"] = info['title'].encode('utf-8') + ' %sx%02d' % (
                info['season'], info['episode'])  # define query

    else:
        info["type"] = "anime"
        info["query"] = info['title'].encode('utf-8') + ' %02d' % info['absolute_number']  # define query anime
    return search_general(info)


# This registers your module for use
provider.register(search, search_movie, search_episode)

del settings
del browser
del filters
