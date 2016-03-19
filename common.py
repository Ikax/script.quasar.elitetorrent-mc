# library to access URL, translation title and filtering
# coding: utf-8
__author__ = 'mancuniancol'

import re
from os import path

import xbmc
import xbmcaddon
import xbmcgui

from bs4 import BeautifulSoup

season_names = {'en': 'season',
                'es': 'temporada',
                'fr': 'saison',
                'nl': 'seizoen',
                'ru': 'сезон',
                'it': 'stagione',
                'de': 'saison',
                'pt': 'temporada',
                }


class Settings:
    def __init__(self):
        # Objects
        self.dialog = xbmcgui.Dialog()
        self.pDialog = xbmcgui.DialogProgress()
        self.settings = xbmcaddon.Addon()

        # General information
        self.idAddon = self.settings.getAddonInfo('ID')  # gets name
        self.icon = self.settings.getAddonInfo('icon')
        self.fanart = self.settings.getAddonInfo('fanart')
        self.path = self.settings.getAddonInfo('path')
        self.name = self.settings.getAddonInfo('name')  # gets name
        self.cleanName = re.sub('.COLOR (.*?)]', '', self.name.replace('[/COLOR]', ''))
        self.value = {}  # it contains all the settings from xml file
        with open(path.join(self.path, "resources", "settings.xml"), 'r') as fp:
            data = fp.read()
        soup = BeautifulSoup(data)
        settings = soup.select("setting")
        for setting in settings:
            key = setting.attrs.get("id")
            if key is not None:
                self.value[key] = self.settings.getSetting(key)
        if 'url_address' in self.value and self.value['url_address'].endswith('/'):
            self.value['url_address'] = self.value['url_address'][:-1]


class Browser:
    def __init__(self):
        import cookielib

        self._cookies = None
        self.cookies = cookielib.LWPCookieJar()
        self.content = None
        self.status = None

    def create_cookies(self, payload):
        import urllib

        self._cookies = urllib.urlencode(payload)

    def open(self, url='', language='en', payload={}):
        import urllib2

        result = True
        if len(payload) > 0:
            self.create_cookies(payload)
        if self._cookies is not None:
            req = urllib2.Request(url, self._cookies)
            self._cookies = None
        else:
            req = urllib2.Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.71 Safari/537.36')
        req.add_header('Content-Language', language)
        req.add_header("Accept-Encoding", "gzip")
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))  # open cookie jar
        try:
            response = opener.open(req)  # send cookies and open url
            # borrow from provider.py Steeve
            if response.headers.get("Content-Encoding", "") == "gzip":
                import zlib

                self.content = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(response.read())
            else:
                self.content = response.read()
            response.close()
            self.status = 200
        except urllib2.HTTPError as e:
            self.status = e.code
            result = False
        except urllib2.URLError as e:
            self.status = e.reason
            result = False
        return result

    def open2(self, url=''):
        import httplib

        word = url.split("://")
        search = word[1]
        pos = search.find("/")
        conn = httplib.HTTPConnection(search[:pos])
        conn.request("GET", search[pos:])
        r1 = conn.getresponse()
        self.status = str(r1.status) + " " + r1.reason
        self.content = r1.read()
        if r1.status == 200:
            return True
        else:
            return False

    def login(self, url, payload, word):
        result = False
        self.create_cookies(payload)
        if self.open(url):
            result = True
            data = self.content
            if word in data:
                self.status = 'Wrong Username or Password'
                result = False
        return result


class Filtering:
    def __init__(self):
        self.settings = xbmcaddon.Addon()
        self.id_addon = self.settings.getAddonInfo('id')  # gets name
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.time_noti = int(self.settings.getSetting('time_noti'))  # time notification
        self.icon = self.settings.getAddonInfo('icon')
        self.name_provider = self.settings.getAddonInfo('name')  # gets name
        self.name_provider = re.sub('.COLOR (.*?)]', '', self.name_provider.replace('[/COLOR]', ''))
        self.reason = ''
        self.title = ''
        self.info = {}
        self.quality_allow = ['*']
        self.quality_deny = []
        self.title = ''
        self.max_size = 10.00  # 10 it is not limit
        self.min_size = 0.00
        # size
        if self.settings.getSetting('movie_min_size') == '':
            self.movie_min_size = 0.0
        else:
            self.movie_min_size = float(self.settings.getSetting('movie_min_size'))
        if self.settings.getSetting('movie_max_size') == '':
            self.movie_max_size = 10.0
        else:
            self.movie_max_size = float(self.settings.getSetting('movie_max_size'))
        if self.settings.getSetting('TV_min_size') == '':
            self.TV_min_size = 0.0
        else:
            self.TV_min_size = float(self.settings.getSetting('TV_min_size'))
        if self.settings.getSetting('TV_max_size') == '':
            self.TV_max_size = 10.0
        else:
            self.TV_max_size = float(self.settings.getSetting('TV_max_size'))

        # movie
        movie_qua1 = self.settings.getSetting('movie_qua1')  # 480p
        movie_qua2 = self.settings.getSetting('movie_qua2')  # HDTV
        movie_qua3 = self.settings.getSetting('movie_qua3')  # 720p
        movie_qua4 = self.settings.getSetting('movie_qua4')  # 1080p
        movie_qua5 = self.settings.getSetting('movie_qua5')  # 3D
        movie_qua6 = self.settings.getSetting('movie_qua6')  # CAM
        movie_qua7 = self.settings.getSetting('movie_qua7')  # TeleSync
        movie_qua8 = self.settings.getSetting('movie_qua8')  # Trailer
        # Accept File
        movie_key_allowed = self.settings.getSetting('movie_key_allowed').replace(', ', ',').replace(' ,', ',')
        movie_allow = re.split(',', movie_key_allowed)
        if movie_qua1 == 'Accept File': movie_allow.append('480p')
        if movie_qua2 == 'Accept File': movie_allow.append('HDTV')
        if movie_qua3 == 'Accept File': movie_allow.append('720p')
        if movie_qua4 == 'Accept File': movie_allow.append('1080p')
        if movie_qua5 == 'Accept File': movie_allow.append('3D')
        if movie_qua6 == 'Accept File': movie_allow.append('CAM')
        if movie_qua7 == 'Accept File': movie_allow.extend(['TeleSync', ' TS '])
        if movie_qua8 == 'Accept File': movie_allow.append('Trailer')
        # Block File
        movie_key_denied = self.settings.getSetting('movie_key_denied').replace(', ', ',').replace(' ,', ',')
        movie_deny = re.split(',', movie_key_denied)
        if movie_qua1 == 'Block File': movie_deny.append('480p')
        if movie_qua2 == 'Block File': movie_deny.append('HDTV')
        if movie_qua3 == 'Block File': movie_deny.append('720p')
        if movie_qua4 == 'Block File': movie_deny.append('1080p')
        if movie_qua5 == 'Block File': movie_deny.append('3D')
        if movie_qua6 == 'Block File': movie_deny.append('CAM')
        if movie_qua7 == 'Block File': movie_deny.extend(['TeleSync', '?TS?'])
        if movie_qua8 == 'Block File': movie_deny.append('Trailer')
        if '' in movie_allow: movie_allow.remove('')
        if '' in movie_deny: movie_deny.remove('')
        if len(movie_allow) == 0: movie_allow = ['*']
        self.movie_allow = movie_allow
        self.movie_deny = movie_deny
        # TV
        TV_qua1 = self.settings.getSetting('TV_qua1')  # 480p
        TV_qua2 = self.settings.getSetting('TV_qua2')  # HDTV
        TV_qua3 = self.settings.getSetting('TV_qua3')  # 720p
        TV_qua4 = self.settings.getSetting('TV_qua4')  # 1080p
        # Accept File
        TV_key_allowed = self.settings.getSetting('TV_key_allowed').replace(', ', ',').replace(' ,', ',')
        TV_allow = re.split(',', TV_key_allowed)
        if TV_qua1 == 'Accept File': TV_allow.append('480p')
        if TV_qua2 == 'Accept File': TV_allow.append('HDTV')
        if TV_qua3 == 'Accept File': TV_allow.append('720p')
        if TV_qua4 == 'Accept File': TV_allow.append('1080p')
        # Block File
        TV_key_denied = self.settings.getSetting('TV_key_denied').replace(', ', ',').replace(' ,', ',')
        TV_deny = re.split(',', TV_key_denied)
        if TV_qua1 == 'Block File': TV_deny.append('480p')
        if TV_qua2 == 'Block File': TV_deny.append('HDTV')
        if TV_qua3 == 'Block File': TV_deny.append('720p')
        if TV_qua4 == 'Block File': TV_deny.append('1080p')
        if '' in TV_allow: TV_allow.remove('')
        if '' in TV_deny: TV_deny.remove('')
        if len(TV_allow) == 0: TV_allow = ['*']
        self.TV_allow = TV_allow
        self.TV_deny = TV_deny

    def type_filtering(self, info, separator='%20'):
        from xbmcgui import Dialog
        from urllib import quote

        if 'movie' == info["type"]:
            self.use_movie()
        elif 'show' == info["type"]:
            self.use_TV()
            info["query"] = exception(info["query"])  # CSI series problem
        elif 'anime' == info["type"]:
            self.use_TV()
        self.title = info["query"] + ' ' + info["extra"]  # to do filtering by name
        self.info = info
        if self.time_noti > 0:
            dialog = Dialog()
            dialog.notification(self.name_provider, info["query"].title(), self.icon, self.time_noti)
            del Dialog
        return quote(info["query"].rstrip()).replace('%20', separator)

    def use_movie(self):
        self.quality_allow = self.movie_allow
        self.quality_deny = self.movie_deny
        self.min_size = self.movie_min_size
        self.max_size = self.movie_max_size

    def use_TV(self):
        self.quality_allow = self.TV_allow
        self.quality_deny = self.TV_deny
        self.min_size = self.TV_min_size
        self.max_size = self.TV_max_size

    def information(self):
        xbmc.log('[%s] Accepted Keywords: %s' % (self.id_addon, str(self.quality_allow)))
        xbmc.log('[%s] Blocked Keywords: %s' % (self.id_addon, str(self.quality_deny)))
        xbmc.log('[%s] min Size: %s' % (self.id_addon, str(self.min_size) + ' GB'))
        xbmc.log('[%s] max Size: %s' % (self.id_addon, (str(self.max_size) + ' GB') if self.max_size != 10 else 'MAX'))

    # validate keywords
    def included(self, value, keys, strict=False):
        value = ' ' + value + ' '
        if '*' in keys:
            res = True
        else:
            res1 = []
            for key in keys:
                res2 = []
                for item in re.split('\s', key):
                    item = item.replace('?', ' ')
                    if strict:
                        item = ' ' + item + ' '  # it makes that strict the comparation
                    if item.upper() in value.upper():
                        res2.append(True)
                    else:
                        res2.append(False)
                res1.append(all(res2))
            res = any(res1)
        return res

    # validate size
    def size_clearance(self, size):
        max_size1 = 100 if self.max_size == 10 else self.max_size
        res = False
        try:
            value = float(re.search('([0-9]*\.[0-9]+|[0-9]+)', size).group(0))
        except:
            value = 0
        value *= 0.001 if 'M' in size else 1
        if self.min_size <= value <= max_size1:
            res = True
        return res

    @staticmethod
    def normalize(name):
        from unicodedata import normalize
        import types

        if type(name) == types.StringType:
            unicode_name = name.decode('unicode-escape')
        else:
            unicode_name = name
        normalize_name = normalize('NFKD', unicode_name)
        return normalize_name.encode('ascii', 'ignore')

    @staticmethod
    def uncode_name(name):  # convert all the &# codes to char, remove extra-space and normalize
        from HTMLParser import HTMLParser

        name = name.replace('<![CDATA[', '').replace(']]', '')
        name = HTMLParser().unescape(name.lower())
        return name

    @staticmethod
    def unquote_name(name):  # convert all %symbols to char
        from urllib import unquote

        return unquote(name).decode("utf-8")

    def safe_name(self, value):  # make the name directory and filename safe
        value = self.normalize(value)  # First normalization
        value = self.unquote_name(value)
        value = self.uncode_name(value)
        value = self.normalize(
            value)  # Last normalization, because some unicode char could appear from the previous steps
        value = value.lower().title()
        keys = {'"': ' ', '*': ' ', '/': ' ', ':': ' ', '<': ' ', '>': ' ', '?': ' ', '|': ' ',
                "'": '', 'Of': 'of', 'De': 'de', '.': ' ', ')': ' ', '(': ' ', '[': ' ', ']': ' ', '-': ' '}
        for key in keys.keys():
            value = value.replace(key, keys[key])
        value = ' '.join(value.split())
        return value.replace('S H I E L D', 'SHIELD')

    # verify
    def verify(self, name, size):
        name = self.safe_name(name)
        self.title = self.safe_name(self.title)
        self.reason = name.replace(' - ' + self.name_provider, '') + ' ***Blocked File by'
        if self.included(name, [self.title], True):
            result = True
            if name is not None:
                if not self.included(name, self.quality_allow) or self.included(name, self.quality_deny):
                    self.reason += ", Keyword"
                    result = False
            if size is not None:
                if not self.size_clearance(size):
                    result = False
                    self.reason += ", Size"
        else:
            result = False
            self.reason += ", Name"
        self.reason = self.reason.replace('by,', 'by') + '***'
        return result


# find the name in different language
def translator(imdb_id, language, extra=True):
    import json

    browser1 = Browser()
    keywords = {'en': '', 'de': '', 'es': 'espa', 'fr': 'french', 'it': 'italian', 'pt': 'portug'}
    url_themoviedb = "http://api.themoviedb.org/3/find/%s?api_key=8d0e4dca86c779f4157fc2c469c372ca&language=%s" \
                     "&external_source=imdb_id" % (imdb_id, language)
    if browser1.open(url_themoviedb):
        movie = json.loads(browser1.content)
        title = movie['movie_results'][0]['title'].encode('utf-8')
        original_title = movie['movie_results'][0]['original_title'].encode('utf-8')
        if title == original_title and extra:
            title += ' ' + keywords[language]
    else:
        title = 'Pas de communication avec le themoviedb.org'
    return title.rstrip()


def size_int(size_txt):
    sint = ignore_exception(ValueError)(int)
    sfloat = ignore_exception(ValueError)(float)
    size_txt = size_txt.upper()
    size1 = size_txt.replace('B', '').replace('I', '').replace('K', '').replace('M', '').replace('G', '')
    size = sfloat(size1)
    if 'K' in size_txt:
        size *= 1000
    if 'M' in size_txt:
        size *= 1000000
    if 'G' in size_txt:
        size *= 1e9
    return sint(size)


class Magnet:
    def __init__(self, magnet):
        self.magnet = magnet + '&'
        # hash
        info_hash = re.search('urn:btih:(.*?)&', self.magnet)
        result = ''
        if info_hash is not None:
            result = info_hash.group(1)
        self.hash = result
        # name
        name = re.search('dn=(.*?)&', self.magnet)
        result = ''
        if name is not None:
            result = name.group(1).replace('+', ' ')
        self.name = result.title()
        # trackers
        self.trackers = re.findall('tr=(.*?)&', self.magnet)


def IMDB_title(IMDB_id):
    browser = Browser()
    result = ''
    if browser.open('http://www.omdbapi.com/?i=%s&r=json' % IMDB_id):
        data = browser.content.replace('"', '').replace('{', '').replace('}', '').split(',')
        result = data[0].split(":")[1] + ' ' + data[1].split(":")[1]
    return result


def exception(title):
    title = title.lower()
    title = title.replace('csi crime scene investigation', 'CSI')
    title = title.replace('law and order special victims unit', 'law and order svu')
    title = title.replace('law order special victims unit', 'law and order svu')
    return title


def getlinks(page):
    browser = Browser()
    result = ""
    if browser.open(page.encode("UTF-8")):
        content = re.findall('magnet:\?[^\'"\s<>\[\]]+', browser.content)
        if content is not None:
            result = content[0]
        else:
            content = re.findall('http(.*?).torrent', browser.content)
            if content is not None:
                result = 'http' + content[0] + '.torrent'
    return result


##http://stackoverflow.com/questions/2262333/is-there-a-built-in-or-more-pythonic-way-to-try-to-parse-a-string-to-an-integer
def ignore_exception(IgnoreException=Exception, DefaultVal=0):
    """ Decorator for ignoring exception from a function
    e.g.   @ignore_exception(DivideByZero)
    e.g.2. ignore_exception(DivideByZero)(Divide)(2/0)
    """

    def dec(function):
        def _dec(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except IgnoreException:
                return DefaultVal

        return _dec

    return dec
