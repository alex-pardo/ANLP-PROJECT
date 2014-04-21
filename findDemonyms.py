
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

def generateDemonym(place, add, replace):
	candidates = []
	for rule in replace:
		if len(rule[0]) > 0 and place.endswith(rule[0]):
			candidates.append(place[:-len(rule[0])]+rule[1])
	for rule in add:
		if len(rule[0]) == 0 or place.endswith(rule[0]):
			candidates.append(place+rule[1])
	return candidates


def matchCandidates(link, candidates):
	text = page.Page(site, link).getWikiText()
	if 'demonym' in text.lower():
		score = 0
		for candidate in candidates:
			if findWholeWord(candidate.lower())(text.lower()):
				score += 1
		return score
	else:
		raise NameError('No demonym')

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

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

matchings = 0
test_len = 0
f = open('cities.csv', 'r')
for line in f.readlines():
	line = line.replace('\n','')
	try:
		candidates = generateDemonym(line, add, replace)
		score = matchCandidates(line, candidates)
		print line, score
		if score > 0:
			matchings += 1
		test_len += 1
	except: 
		pass
f.close()
print matchings, test_len




