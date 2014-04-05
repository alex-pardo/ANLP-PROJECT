#David Sanchez Pinsach
#Alex Pardo Fernandez

#Script to download demonyms from Wikipedia and to show the histogram of the 

import rules as r
import wpDownload as wp

FILENAME = 'demonyms.csv'
skipIrregulars = True
quiet = True
th = 3
wp.download(FILENAME, skipIrregulars)
r.showHistogram(FILENAME, th, quiet)