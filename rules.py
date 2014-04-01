#David Sanchez Pinsach
#Alex Pardo Fernandez

#Script to generate the rules beetween country and denomyn

import csv
import matplotlib.pyplot as plt
import numpy as np


count_rules={}
total_words = 0

def showHistogram(filename, THRESHOLD=1, quiet=True):
	''' Method to main that calls the parseFile method'''
	parseFile(filename, quiet)
	
	d = {} 
	for rule in count_rules:
		if count_rules[rule] > THRESHOLD:
			d[rule] = count_rules[rule]

	X = np.arange(len(d))
	plt.bar(X, d.values(), align='center', width=0.5)
	plt.xticks(X, d.keys(), rotation='vertical')
	ymax = max(d.values()) + 1
	plt.ylim(0, ymax)

	print "\nFinal rules\n------------\n", sorted(count_rules.items(), key=lambda x:x[1], reverse=True)
	print '\n\n####################################'
	print 'Total number of rules: ', len(count_rules)
	print 'Number of rules (occurences >', str(THRESHOLD)+') : ', len(d), '\n\n'

	plt.show()



def parseFile(filename, quiet=True):
	''' Method to read the demonyms.csv file'''
	global total_words
	try:
		with open(filename, 'r') as csvfile:
			data = csv.reader(csvfile, delimiter=',')
			#Read csv lines
			for row in data:
				total_words += 1
				generateRules(row)
	except Exception as ex:
		print ex


def generateRules(row, quiet=True):
	''' Method to generate add and delete rules between country or city and denomyn'''
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
				rule[country[i]] = denomyn[i]

		#Case that your country word is finished but you have letters in the denonym yet
		else:
			addList.append(denomyn[i])
			if len(delList) > 0:
				rule[delList[-1]] = rule[delList[-1]]+denomyn[i]

	#Case that you is not needed to remove any letter of the country
	if len(rule)==0:
		rule[" "]=''.join(addList)
		delList.append(" ")

	#Prints
	if not quiet:
		print country
		print denomyn
		print "Del list:"+str(delList)
		print "Add list:"+str(addList)
		print "Rule:"+str(rule)+"\n"
	
	key = ''.join(delList)
	value = ''.join(addList)
	if key+"-->"+value in count_rules:
		count_rules[key+"-->"+value] += 1
	else:
		count_rules[key+"-->"+value] = 1

	



