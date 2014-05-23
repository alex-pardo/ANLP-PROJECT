

''' 
 DEMONYMS
 FUNCTIONS OF MAI-ANLP DEMONYM PROJECT
 AUTHORS: DAVID SANCHEZ & ALEX PARDO
'''

# IMPORTS


import csv

import re
from string import *
import sys

from nltk import *
import locale

from wikitools import wiki
from wikitools import api
from wikitools import page
from wikitools import category

import numpy as np
from matplotlib import pyplot as plt


# FUNCTIONS


''' EXTRACT PAIRS OF COUNTRY-DEMONYM FROM WP '''
def demonyms_downloadDemonymsWP(filename, skip=False):
	
    locale.setlocale(locale.LC_ALL, '')

    lang = 'en'

    demonymPages = {'en':u'Demonym'}
    wikiAPI = {'en': "http://en.wikipedia.org/w/api.php"}

    extractionRules = [
        re.compile(u'^\*\[\[([\w]+)\]\] \u2192 ([\w]+)$',re.L), 
        re.compile(u'^\*\[\[([\w]+)\]\] \u2192 ([\w]+) \([\w]+ \"\'\'[\w]+\'\'\"\)$',re.L),
        re.compile(u'^\*\[\[([\w]+)\]\] \u2192 ([\w]+) \([\w|\W]+\)$',re.L),
        re.compile(u'^\*\[\[([\w]+)\]\] \u2192 ([\w]+) ([\w|\W]+)$',re.L),
        re.compile(u'^\*\[\[([\w]+ [\w]+)\]\] \u2192 ([\w]+ [\w]+)$',re.L),
        re.compile(u'^\*\[\[([\w]+ [\w]+)\]\] \u2192 ([\w]+ [\w]+) ([\w|\W]+)$',re.L)]

    ##inicializing the list of triples to extract
    ##The elements of each triple are:
    ##    location
    ##    demonym
    ##    identifier of the rule applied (just the index in the list)
    ##The identifier is useful for computing the coverage of each rule

    demonymTriples = []

    # An object of the class Wiki associated to the WP is built 

    site = wiki.Wiki(wikiAPI[lang])

    ##An object  of the class Page associated to the demonyms page

    pageDemonym = page.Page(site,demonymPages[lang])

    ##The lines of the page are read and translated into  Unicode
    ##We print the number of lines

    lines=pageDemonym.getWikiText().split('\n')
    lines = map(lambda x:demonyms_guessEncoding(x)[0],lines)
    len(lines)
   
    for linea in lines:
        if skip and ('==Irregular forms==' in linea.encode('utf-8')):
            break
        for ir in range(len(extractionRules)):
            r = extractionRules[ir]

            m = re.match(r,linea)
            if not m:
                #print linea.encode('utf-8')
                continue
            demonymTriples.append((m.group(1), m.group(2), ir))
            break
    print len(demonymTriples), 'triples have been obtained '
    with open(filename, 'w') as out_file:
    	for demonym in demonymTriples:
    		out_file.write(str(demonym[0] + ','+ demonym[1] + ',' + str(demonym[2])+'\n'))




''' PARSES THE RULE FILE AND EXTRACTS ADDING AND REPLACING RULES:
	EXAMPLE:
		adding rule: Italia + an = Italian (->an)// America + n = American (->n)
		replacing rule: Catalonia - onia + an = Catalan (onia->an) // Spain - in + nish = Spanish (in -> nish)

'''
def demonyms_showHistogram(filename, THRESHOLD=1, quiet=True):
	count_rules_diff, count_rules_end, total_words, n_end = demonyms_parseFile(filename, quiet)
	

	with open('replace_rules.csv','w') as f:
		d1 = {} 
		for rule in count_rules_diff:
			if count_rules_diff[rule] > THRESHOLD:
				d1[rule] = count_rules_diff[rule]
				tmp = rule.split("-->")
				f.write(tmp[0]+','+tmp[1]+'\n')

	with open('add_rules.csv','w') as f:
		d2 = {}
		for rule in count_rules_end:
			if count_rules_end[rule] > THRESHOLD:
				d2[rule] = count_rules_end[rule]
				tmp = rule.split("-->")
				f.write(tmp[0]+','+tmp[1]+'\n')


	

	if not quiet:
		print "\nFinal rules\n------------\n", 'DIFF:\n', sorted(count_rules_diff.items(), key=lambda x:x[1], reverse=True), 'ENDING:\n', sorted(count_rules_end.items(), key=lambda x:x[1], reverse=True) 
	
		X = np.arange(len(d1)+len(d2))
		plt.bar(X[:len(d1)], d1.values(), align='center', width=0.5, color='blue', label='SUBSTITUTION')
		plt.hold('on')
		
		plt.bar(X[len(d1):], d2.values(), align='center', width=0.5, color='green', label='ENDING->ADDING')
		plt.xticks(X, d1.keys()+d2.keys(), rotation='vertical')
		ymax = max(d1.values() + d2.values()) + 1
		plt.ylim(0, ymax)
		plt.legend(loc=2)
		plt.savefig('rules.png', bbox_inches='tight')

	print '\n\n####################################'
	print 'Total number of rules: ', len(count_rules_diff)+len(count_rules_end)
	print 'Number of rules (occurences >', str(THRESHOLD)+') : ', len(d1)+len(d2), '\n\n'

	


''' PARSES THE DEMONYM FILE '''
def demonyms_parseFile(filename, quiet=True):

	count_rules_diff={}
	count_rules_end={}
	total_words = 0
	n_end = 4

	try:
		with open(filename, 'r') as csvfile:
			data = csv.reader(csvfile, delimiter=',')
			#Read csv lines
			for row in data:
				total_words += 1
				count_rules_diff, count_rules_end, total_words, n_end = demonyms_generateRules(row, count_rules_diff, count_rules_end, total_words, n_end, quiet = quiet, method='diff')
				count_rules_diff, count_rules_end, total_words, n_end = demonyms_generateRules(row, count_rules_diff, count_rules_end, total_words, n_end, quiet = quiet, method='ending')
	except Exception as ex:
		print ex

	return count_rules_diff, count_rules_end, total_words, n_end

''' EXTRACTS THE RULE FOR A GIVEN PAIR COUNTRY,DEMONYM'''
def demonyms_generateRules(row, count_rules_diff, count_rules_end, total_words, n_end, quiet=True, method='diff'):

	country = row[0]
	denomyn = row[1]
	addList = [] #List with the new letters in the denonym that you will need to add in the country word
	delList = [] #List with the letters that you will need to remove in your contry word
	rule = {}


	#Iterate over the bigger word (normally it is the denomym)
	for i in xrange(0,len(denomyn)):
		if i<len(country):
			if(country[i]!=denomyn[i]):
				delList.append(country[i]) #Letter that needs to be removed
				addList.append(denomyn[i]) #Letter that it is not appearing in the country

		#Case that your country word is finished but you have letters in the denonym yet
		else:
			addList.append(denomyn[i])
			

	#Case that you is not needed to remove any letter of the country
	if len(delList)==0:
		if method == 'diff':
			delList.append(" ")
			#return
		else:
			#add a certain number of letters from the ending of the country
			for i in range(n_end):
				cnt = country[-i:]
				den = ''.join(addList)
				try:
					count_rules_end[cnt+"-->"+den] += 1
				except:
					count_rules_end[cnt+"-->"+den] = 1



	#Prints
	if not quiet:
		print country
		print denomyn
		print "Del list:"+str(delList)
		print "Add list:"+str(addList)
	

	if method == 'diff':
		key = ''.join(delList)
		value = ''.join(addList)
		if key+"-->"+value in count_rules_diff:
			count_rules_diff[key+"-->"+value] += 1
		else:
			count_rules_diff[key+"-->"+value] = 1

	return count_rules_diff, count_rules_end, total_words, n_end

	

''' DOWNLOADS A LIST OF CITIES AND A LIST OF COUNTRIES FROM WIKIPEDIA '''
def demonyms_parseCitiesAndCountries():
	wikiAPI = {'en': "http://en.wikipedia.org/w/api.php"}
	site = wiki.Wiki(wikiAPI['en'])


	cities = []
	countries = []
	rule = re.compile(u'.*\[\[([\w\s]+)\]\].*',re.L)
	r1 = re.compile(r'.*\[\[((List of )([A-Za-z]{1,}[\s]?)+)\]\].*')
	r2 = re.compile(r'.*\[\[([A-Z]{1}([a-z]{1,}[\s]*)+)\]\].*')
	re_country = re.compile(r'in\ *t*h*e*\ ([A-Z][a-z]+)')

	lists = ['List_of_cities_in_Africa', 'List_of_cities_in_Asia', 'List_of_cities_in_Oceania', 'List_of_cities_in_Europe']

	for l in lists:
	    p = page.Page(site, l, sectionnumber='1')

	    for line in p.getWikiText().split('\n'):
	        tmp = r1.findall(line)
	        if len(tmp) > 0:
	            link = tmp[0][0]
	            print link.encode('utf-8')
	            try:
	            	if link.encode('utf-8').endswith(re_country.findall(link.encode('utf-8'))[0]):
	            		countries.append(re_country.findall(link.encode('utf-8'))[0])
	            except:
	            	pass
	            sc = page.Page(site, link, sectionnumber='1')
	            try:
	                text = sc.getWikiText().split('\n')
	            except:
	                continue
	            text = map(lambda x:demonyms_guessEncoding(x)[0],text)
	            #print text
	            for line in text:
	                if 'ref' in line:
	                    continue
	                try:
	                    tmp = rule.findall(line)
	                    if len(tmp) > 0:
	                        if tmp[0] not in cities:
	                            if len(tmp[0].split(' ')) < 2:
	                                cities.append(tmp[0])
	                except Exception, e:
	                    pass
	                
	            print len(cities)  

	with open("cities.csv", 'w') as f:
	    for city in cities:
	        f.write(str(city + '\n'))

	with open("countries.csv", 'w') as f:
	    for country in countries:
	        f.write(str(country + '\n'))



''' GENERATES ALL THE POSSIBLE DEMONYMS FOR A GIVEN PLACE '''
def demonyms_generateDemonym(place, add, replace):
	candidates = []
	for rule in replace:
		if len(rule[0]) > 0 and place.endswith(rule[0]):
			candidates.append(place[:-len(rule[0])]+rule[1])
	for rule in add:
		if len(rule[0]) == 0 or place.endswith(rule[0]):
			candidates.append(place+rule[1])
	return candidates

''' FINDS THE GIVEN DEMONYM CANDIDATES IN THE WP PAGE OF THE GIVEN PLACE '''
def demonyms_matchCandidates(link, candidates):
	wikiAPI = {
    'en': "http://en.wikipedia.org/w/api.php"}
	site = wiki.Wiki(wikiAPI['en'])

	text = page.Page(site, link).getWikiText()
	score = 0
	rules = [0]*len(candidates)
	pos = 0
	for candidate in candidates:
		if demonyms_findWholeWord(candidate.lower())(text.lower()):
			score += 1
			rules[pos] += 1
		pos += 1
	return score, rules

''' FINDS A WHOLE WORD '''
def demonyms_findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

''' EXTRACTS THE RULES FROM THE FILES, READS THE SAMPLES (i.e. PLACES) AND PERFORMS THE MATCHING '''
def demonyms_findDemonyms(filename):
	add = []
	replace = []

	with open('add_rules.csv', 'r') as f:
		for line in f.readlines():
			line = line.replace('\n','')
			tmp = line.split(',')
			add.append((tmp[0],tmp[1]))

	with open('replace_rules.csv', 'r') as f:
		for line in f.readlines():
			line = line.replace('\n','')
			tmp = line.split(',')
			replace.append((tmp[0],tmp[1]))

	print 'There are', len(add), 'add rules and ', len(replace), 'replace rules.'

	matchings = 0
	test_len = 0
	output_lines = []
	f = open(filename, 'r')
	for line in f.readlines():
		line = line.replace('\n','')
		try:
			candidates = demonyms_generateDemonym(line, add, replace)
			score, rules = demonyms_matchCandidates(line, candidates)
			if score > 0:
				matching_rules = []
				for r in range(0, len(candidates)):
					if rules[r]:
						matching_rules.append(candidates[r])
				output_lines.append(line + ','  + str(matching_rules)+'\n')
			if score > 0:
				matchings += 1
			test_len += 1
		except: 
			pass
	f.close()
	with open(filename.replace('.csv', '_res.csv'),'w') as f:
		for line in output_lines:
			f.write(line)
	print '--> Results for', filename.replace('.csv', ''),':\n'
	print 'Number of matchings:', matchings, '; number of samples:', test_len, '(',np.round((matchings/float(test_len))*10000)/100.0,'%)'














    

##For detecting coding and transforming to Unicode

##########################################################################
# Guess Character Encoding
##########################################################################

# adapted from io.py in the docutils extension module (http://docutils.sourceforge.net)
# http://www.pyzine.com/Issue008/Section_Articles/article_Encodings.html

def demonyms_guessEncoding(data):
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

