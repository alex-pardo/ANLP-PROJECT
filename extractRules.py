

from Tkinter import Tk
from tkFileDialog import askopenfilename
import csv


def parseFile(filename):
	demonyms = []
	with open(filename, 'r') as csvfile:
		data = csv.reader(csvfile, delimiter=',')
		for row in data:
			demonyms.append((row[0], row[1]))#, row[2]))
	return demonyms



def extractRules():
	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
	filename = askopenfilename(initialdir="./",title='Please select a csv file') # show an "Open" dialog box and return the path to the selected file
	demonyms = parseFile(filename)
	print len(demonyms)



if __name__ == "__main__":
    extractRules()