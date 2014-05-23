
import functions as f

FILENAME = 'demonyms.csv'
skipIrregulars = True
quiet = True
th = 3

print '###########################'
print ' Extracting rules from WP'
print '###########################'
f.demonyms_downloadDemonymsWP(FILENAME, skipIrregulars)

f.demonyms_showHistogram(FILENAME, th, quiet)

print '##################################'
print ' Downloading cities and contries'
print '##################################'

f.demonyms_parseCitiesAndCountries()

print '####################'
print ' Obtaining results'
print '####################'

f.demonyms_findDemonyms('countries.csv')

f.demonyms_findDemonyms('cities.csv')
