#David Sanchez Pinsach
#Alex Pardo Fernandez

#Script to generate the rules beetween country and denomyn

import csv
import matplotlib.pyplot as plt
import numpy as np


count_rules_diff={}
count_rules_end={}
total_words = 0
n_end = 4

def showHistogram(filename, THRESHOLD=1, quiet=True):
	''' Method to main that calls the parseFile method'''
	parseFile(filename, quiet)
	
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


	X = np.arange(len(d1)+len(d2))
	plt.bar(X[:len(d1)], d1.values(), align='center', width=0.5, color='blue', label='SUBSTITUTION')
	plt.hold('on')
	
	plt.bar(X[len(d1):], d2.values(), align='center', width=0.5, color='green', label='ENDING->ADDING')
	plt.xticks(X, d1.keys()+d2.keys(), rotation='vertical')
	ymax = max(d1.values() + d2.values()) + 1
	plt.ylim(0, ymax)
	plt.legend(loc=2)

	print "\nFinal rules\n------------\n", 'DIFF:\n', sorted(count_rules_diff.items(), key=lambda x:x[1], reverse=True), 'ENDING:\n', sorted(count_rules_end.items(), key=lambda x:x[1], reverse=True) 
	print '\n\n####################################'
	print 'Total number of rules: ', len(count_rules_diff)+len(count_rules_end)
	print 'Number of rules (occurences >', str(THRESHOLD)+') : ', len(d1)+len(d2), '\n\n'

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
				generateRules(row, quiet, method='diff')
				generateRules(row, quiet, method='ending')
	except Exception as ex:
		print ex


def generateRules(row, quiet=True, method='diff'):
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

	



