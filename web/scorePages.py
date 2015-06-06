#######################################################################
# ./scorePages.py compares the query to each document
# Called by ./mkQueryPage.py
####################################################################### 

from operator import itemgetter, attrgetter
from numpy import *
import scipy
from scipy.spatial.distance import cosine as scipy_cos_dist
import subprocess
import collections
import webbrowser
import urllib
import sys
import re
import time
import os

#Change this line to your PeARS folder path
path_to_PeARS="/home/aurelie/PeARS/web/"
dm_dict={}		#Dictionary to store dm file
url_dict={}		#Dictionary file ids - urls
reverse_url_dict={}	#Dictionary urls - file ids
doc_scores={}		#Document scores
url_wordclouds={}		#Stores correspondence between url and word cloud for this query
#url_snippets={}		#Stores correspondence between url and best snippet for this query

##### Helpful functions ########################################################################

#Timing function, just to know how long things take
def print_timing(func):
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s in scorePages took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper



##### Helpful functions end ####################################################################



#############################################
# Cosine function
#############################################

def cosine_distance(a, b):
	a=scipy.array(a,dtype=float)
	b=scipy.array(b,dtype=float)
	if len(a) != len(b):
		raise ValueError, "a and b must be same length"
	return 1-scipy_cos_dist(a,b)


#################################################
# Read dm file
#################################################

def readDM():
	with open(path_to_PeARS+"wikiwoods.dm") as f:
		dmlines=f.readlines()
		f.close()

	#Make dictionary with key=row, value=vector
	for l in dmlines:
		items=l.rstrip('\n').split('\t')
		row=items[0]
		vec=[float(i) for i in items[1:]]
		dm_dict[row]=vec

##############################################
# Read url file
##############################################

def loadURLs(pear):
	print "Loading URL dictionary for",pear
	path_to_dict=pear+"urls.dict.txt"

	d=urllib.urlopen(path_to_dict)
	for line in d:
		line=line.rstrip('\n')
		idfile=line.split()[0]
		url=line.split()[1]
		#print idfile,url
		url_dict[idfile]=url		#Record the pairs url - file name on pear
		reverse_url_dict[url]=idfile
	d.close()

##############################################
# Make distribution for query
##############################################

def mkQueryDist(query):
	words=query.rstrip('\n').split()

	#Only retain arguments which are in the distributional semantic space
	vecs_to_add = []
	for w in words:
		m=re.search('(.*_.).*',w)
		if m:
			w=m.group(1).lower()
		if w in dm_dict:
#				print "Adding",w,"to vecs_to_add"
			vecs_to_add.append(w)	

	vbase=array([])
	#Add vectors together
	if len(vecs_to_add) > 0:
		base=vecs_to_add[0]				#Take first word in vecs_to_add to start addition
		vbase=array(dm_dict[base])
		for item in range(1,len(vecs_to_add)):
#				print item,"Adding vector",vecs_to_add[item]
			vbase=vbase+array(dm_dict[vecs_to_add[item]]) 	
	
	return vbase

##############################################
# Get word clouds for a pear
##############################################

def loadWordClouds(pear):
	print "Loading word clouds..."
	word_clouds=urllib.urlopen(pear+"/wordclouds.txt")
	for l in word_clouds:
		l=l.rstrip('\n')
		fields=l.split(':')
		url_wordclouds[url_dict[fields[0]]]=fields[1]

	word_clouds.close()
		
	
################################################
# Score documents for a pear
################################################

@print_timing
def scoreDocs(query_dist,pear):
	dd=urllib.urlopen(pear+"/doc.dists.txt")
	doc_dists=dd.readlines()
	dd.close()
	#print "Done reading dd"

	for l in doc_dists:
		scoreSIM = 0.0		#Initialise score for similarity

		l=l.rstrip('\n')
		doc_id =  l.split(':')[0]
		doc_dist =  array(l.split(':')[1].split())
#		print doc_id,cosine_distance(doc_dist,query_dist)
		score=cosine_distance(doc_dist,query_dist)
		doc_scores[url_dict[doc_id]]=score
#		url_wordclouds[url_dict[doc_id]]=getWordCloud(pear,doc_id)
	return doc_scores

#################################################
# Get best URLs
#################################################

def bestURLs(doc_scores):
	best_urls=[]
	c=0
	for w in sorted(doc_scores, key=doc_scores.get, reverse=True):
		if c < 10:
			if doc_scores[w] > 0.3:					#Threshold - page must be good enough
				best_urls.append(w)
#				print w, doc_scores[w]
			c+=1
		else:
			break
	return best_urls


################################################
# Prepare output
################################################


def output(best_urls,query):
	results=[]
#	print query	
	#If documents matching the query were found on the pear network...
	if len(best_urls) > 0:
		for u in best_urls:
			results.append([u,url_wordclouds[u]])			
#			print "Getting snippet for",u
#			snippet=returnSnippet.runScript(query,pear,reverse_url_dict[u])
#			results.append([u,snippet])

	#Otherwise, open duckduckgo and send the query there
	else:
		print "No suitable pages found."
		duckquery=""
		for w in query.rstrip('\n').split():
			m = re.search('(.*)_.',w)
			if m:
				duckquery=duckquery+m.group(1)+"+"
#		print duckquery
		webbrowser.open_new_tab("https://duckduckgo.com/?q="+duckquery.rstrip('+'))
		link_snippet_pair=["###","No suitable recommendation. You were redirected to duckduckgo."]
		results.append(link_snippet_pair)

	return results

##############################################
#Main function, called by mkQueryPage.py
##############################################

# The @ decorator before the function invokes print_timing()
@print_timing
def runScript(pears,query):
	readDM()
	query_dist=mkQueryDist(query)
	best_urls=[]
        if len(pears) > 0:
		for pear in pears:
			#print pear
			loadURLs(pear)
			loadWordClouds(pear)
			scoreDocs(query_dist,pear)
		best_urls=bestURLs(doc_scores)
	return output(best_urls,query)	

if __name__ == '__main__':
    runScript(sys.argv[1], sys.argv[2])
