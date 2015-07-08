################################################################
#NB: FOR FIREFOX USERS ONLY
#Little script that reads your browsing history and returns your
#20 most visited domains. Produces a urls.txt file for the
#domain of your choice, which can be fed to indexPages.py
###############################################################

import subprocess
import operator
import re
import os
from os.path import expanduser
from os import listdir
import indexPages

#Path to PeARS
path_to_PeARS=os.path.dirname(__file__)
#Path to Firefoc
path_to_Firefox= os.path.join(expanduser("~") ,".mozilla/firefox/")


#Check whether string contains any item in a set of chars
def containsChars(str, set):
    return 1 in [c in str for c in set]


def getFirefoxHistory():
	#Do not modify these paths
	path_to_output=os.path.join(path_to_PeARS, 'history.txt')
	path_to_cleaned_output=os.path.join(path_to_PeARS, 'history.pages')
	path_to_history=path_to_Firefox+'*.default/places.sqlite'

	#Get history from Firefox
	subprocess.call("sqlite3 "+path_to_history+" 'SELECT url FROM moz_places' > "+path_to_output, shell=True)

	pages=open(path_to_cleaned_output,'w')

	#Get rid of 'funny' pages (queries and such like) -- only keep http
	history=open(os.path.join(path_to_PeARS, "history.txt"),'r')
	for line in history:
		line=line.rstrip('\n')
		if not containsChars(line,'?&#,'):	#Discard lines which contain ?, &, # or , (could be search engine queries, etc)
			m=re.search('^http',line)
			if m:
				pages.write(line+'\n')
	history.close()
	pages.close()

def outputFavouriteDomains():
	history=open(os.path.join(path_to_PeARS, "history.pages"),'r')
	domains={}
	for line in history:
		m=re.search('(^http.*//[^/]*)/.*',line)
		if m:
			domain=m.group(1)
			if domain not in domains:
				domains[domain]=1
			else:
				domains[domain]=domains[domain]+1
	history.close()
	favs=[]
	c=0		#count
	print "Here are the ten domains you most frequently visit:"
	for k,v in sorted(domains.items(), key=operator.itemgetter(1), reverse=True)[0:20]:
		c+=1
		print "["+str(c)+"] "+k+" ("+str(v)+" pages visited)"
		favs.append(k)
	return favs

def grabPages(domain):
	with open(os.path.join(path_to_PeARS, "history.pages")) as f:
	    history = f.readlines()
	f.close()

	domainpages = open(os.path.join(path_to_PeARS, "urls.txt"),'w')

	for line in history:
		regex="^"+domain
		if re.search(regex, line):
#			print line
			domainpages.write(line)
	domainpages.close()


##############################
# Entry point
##############################

#Remove previous version of testPeARS.pages
if os.path.exists(os.path.join(path_to_PeARS, "test.pages")):
	os.remove(os.path.join(path_to_PeARS, "test.pages"))

getFirefoxHistory()
favourite_domains=outputFavouriteDomains()
domain_number=int(raw_input("Which domain would you like to index? (Enter a number) "))-1
domain=favourite_domains[domain_number]
print "Selecting pages for",domain,"..."
grabPages(domain)



