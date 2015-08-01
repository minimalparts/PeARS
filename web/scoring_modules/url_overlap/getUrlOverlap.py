########################################################################
# getUrlOverlap.py takes a (raw, non-lemmatised) query and a URL and 
# calculates the dice coefficient between the two strings (jaccard also 
# available). Higher scores represent higher match between query and url.
# To be integrated as a module in final search algorithm
# USAGE: python ./getUrlOverlap.py  wikipedia https://en.wikipedia.org/
########################################################################


import sys
import re

def jaccard(a, b):
	c = a.intersection(b)
	return float(len(c)) / (len(a) + len(b) - len(c))

def dice(a, b):
	c = a.intersection(b)
	return float(2*len(c)) / (len(a) + len(b))

def scoreUrlOverlap(query,url):
	url=url.rstrip('/')		#Strip last backslash if there is one
	m=re.search('.*/([^/]+)',url)	#Get last element in url
	if m:
		url=m.group(1)
	
	#print jaccard(set(query.lower()), set(url.lower()))
	return dice(set(query.lower()), set(url.lower()))


def runScript(query,url):
	#print scoreUrlOverlap(query,url)
	return scoreUrlOverlap(query,url)

# when executing as script
if __name__ == '__main__':
    runScript(sys.argv[1],sys.argv[2])      #Input query,url

