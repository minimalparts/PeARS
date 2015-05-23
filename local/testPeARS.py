#Little script to test PeARS if you're using it for the first time
import subprocess
import operator
import re
import os
from os import listdir
import indexPages

#Path to PeARS
path_to_PeARS="/home/aurelie/PeARS/"
#Path to Firefoc
path_to_Firefox="/home/aurelie/.mozilla/firefox/"


#Check whether string contains any item in a set of chars
def containsChars(str, set):
    return 1 in [c in str for c in set]


def getFirefoxHistory():
	#Do not modify these paths
	path_to_output=path_to_PeARS+'history.txt'
	path_to_cleaned_output=path_to_PeARS+'history.pages'
	path_to_history=path_to_Firefox+'*.default/places.sqlite'

	#Get history from Firefox
	subprocess.call("sqlite3 "+path_to_history+" 'SELECT url FROM moz_places' > "+path_to_output, shell=True)

	pages=open(path_to_cleaned_output,'w')

	#Get rid of 'funny' pages (queries and such like) -- only keep http
	history=open(path_to_PeARS+"history.txt",'r')
	for line in history:
		line=line.rstrip('\n')
		if not containsChars(line,'?&#,'):	#Discard lines which contain ?, &, # or , (could be search engine queries, etc)
			m=re.search('^http',line)
			if m:
				pages.write(line+'\n')
	history.close()
	pages.close()

def outputFavouriteDomains():
	history=open(path_to_PeARS+"history.pages",'r')
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
	print "Here are the ten domains you most frequently visit:"
	for k,v in sorted(domains.items(), key=operator.itemgetter(1), reverse=True)[0:10]:
		print k, v	
		favs.append(k)
	return favs	

def grabPages(domain):
	with open(path_to_PeARS+"history.pages") as f:
	    history = f.readlines()
	f.close()

	domainpages = open (path_to_PeARS+"test.pages",'a')

	c=0	#count	
	for line in history:
		regex="^"+domain
		if re.search(regex, line):
#			print line
			domainpages.write(line)	
			if c > 3:	#If enough pages found, stop
				break
			else:
				c+=1	#Increment count
	domainpages.close()

def createPear():
	pear_name=raw_input("Give a name to your pear: ")
	while os.path.isdir(path_to_PeARS+pear_name):
		pear_name=raw_input("This pear name already exists. Please give another name: ")
	print "Creating pear",pear_name,"..."
	os.makedirs(path_to_PeARS+pear_name)
	return pear_name

##############################
# Entry point
##############################

#Print welcome message
input_ok=0

#Remove previous version of testPeARS.pages
if os.path.exists(path_to_PeARS+"test.pages"):
	os.remove(path_to_PeARS+"test.pages")

while input_ok==0:
	browser=raw_input("Hi. Welcome to PeARS. Are you using Firefox as your main browser? (y/n) ")
	if browser=='y':
		getFirefoxHistory()
		favourite_domains=outputFavouriteDomains()
		grab_pages=raw_input("I'll select 50 pages from these domains. Okay? (y/q) ")
		if grab_pages=='y':
			for f in favourite_domains:
				print "Selecting pages for",f,"..."
				grabPages(f)
			#pear_name=createPear()
			#indexPages.runScript(path_to_PeARS+"test.pages",pear_name)
		input_ok=1
	else:
		if browser=='n':
			print "Ok. I'll use a predefined list of webpages to show you the PeARS functionalities..."
			input_ok=1




