

import re
from string import *
import sys

from nltk import *
import locale

from wikitools import wiki
from wikitools import api
from wikitools import page
from wikitools import category


wikiAPI = {
    'en': "http://en.wikipedia.org/w/api.php"}


site = wiki.Wiki(wikiAPI['en'])

##An object  of the class Page associated to the demonyms page

cities = []
rule = re.compile(u'.*\[\[([\w\s]+)\]\].*',re.L)
r1 = re.compile(r'.*\[\[((List of )([A-Za-z]{1,}[\s]?)+)\]\].*')
r2 = re.compile(r'.*\[\[([A-Z]{1}([a-z]{1,}[\s]*)+)\]\].*')

lists = ['List_of_cities_in_Africa', 'List_of_cities_in_Asia', 'List_of_cities_in_Oceania', 'List_of_cities_in_Europe']
#lists = ['List_of_cities_in_Europe']
for l in lists:
    p = page.Page(site, l, sectionnumber='1')

    for line in p.getWikiText().split('\n'):
        tmp = r1.findall(line)
        if len(tmp) > 0:
            link = tmp[0][0]
            print link.encode('utf-8')
            sc = page.Page(site, link, sectionnumber='1')
            try:
                text = sc.getWikiText().split('\n')
            except:
                continue
            text = map(lambda x:guess_encoding(x)[0],text)
            #print text
            for line in text:
                if 'ref' in line:
                    continue
                try:
                    #print rule.match(line).group()[0]
                    tmp = rule.findall(line)
                    if len(tmp) > 0:
                        if tmp[0] not in cities:
                            if len(tmp[0].split(' ')) < 2:
                                cities.append(tmp[0])
                except Exception, e:
                    pass
                

                # m = re.match(rule,line)
                # print m.group()[0]

            print len(cities)  

with open("cities.csv", 'w') as f:
    for city in cities:
        f.write(str(city + '\n'))



##For detecting coding and transforming to Unicode

##########################################################################
# Guess Character Encoding
##########################################################################

# adapted from io.py in the docutils extension module (http://docutils.sourceforge.net)
# http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html

def guess_encoding(data):
    """
    Given a byte string, attempt to decode it.
    Tries the standard 'UTF8' and 'latin-1' encodings,
    Plus several gathered from locale information.

    The calling program *must* first call::

        locale.setlocale(locale.LC_ALL, '')

    If successful it returns C{(decoded_unicode, successful_encoding)}.
    If unsuccessful it raises a C{UnicodeError}.
    """
    successful_encoding = None
    # we make 'utf-8' the first encoding
    encodings = ['utf-8']
    #
    # next we add anything we can learn from the locale
    try:
        encodings.append(locale.nl_langinfo(locale.CODESET))
    except AttributeError:
        pass
    try:
        encodings.append(locale.getlocale()[1])
    except (AttributeError, IndexError):
        pass
    try: 
        encodings.append(locale.getdefaultlocale()[1])
    except (AttributeError, IndexError):
        pass
    #
    # we try 'latin-1' last
    encodings.append('latin-1')
    for enc in encodings:
        # some of the locale calls 
        # may have returned None
        if not enc:
            continue
        try:
            decoded = unicode(data, enc)
            successful_encoding = enc

        except (UnicodeError, LookupError):
            pass
        else:
            break
    if not successful_encoding:
         raise UnicodeError(
        'Unable to decode input data.  Tried the following encodings: %s.'
        % ', '.join([repr(enc) for enc in encodings if enc]))
    else:
         return (decoded, successful_encoding)

