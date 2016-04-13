#######################################################################
# ./scorePages.py compares the query to each document
# Called by ./mkQueryPage.py
#######################################################################

from numpy import *
import webbrowser
import urllib
import sys
import re
import os
from operator import itemgetter
from .utils import mkQueryDist, cosine_similarity, print_timing
import getUrlOverlap


###############################################
# Get distributional score
###############################################

def scoreDS(query_dist,url_dict):
    DS_scores={}
    for url,doc_dist in url_dict.items():
    	score = cosine_similarity(doc_dist, query_dist)
    	DS_scores[url] = score
	#print url,score
    return DS_scores


###############################################
# Get url overlap score
###############################################

def scoreURL(query,url_dict):
    URL_scores={}
    for u in url_dict:
        URL_scores[u]=getUrlOverlap.runScript(query,u)
        #print v,"URL score",URL_scores[v]
    return URL_scores

##############################################
# Get URL-vector dict
#############################################

def getUrlDict(pear):
    url_dict={}
    if pear.endswith('/'):
        pear = pear[:-1]
    doc_dists = open(pear+"/urls.dists.txt")
    #doc_dists = urllib.urlopen(pear+"urls.dists.txt")
    for l in doc_dists:
        l = l.rstrip('\n')
	fields=l.split()
        url = fields[0]
	doc_dist =[float(i) for i in fields[1:]]
	url_dict[url]=doc_dist
    doc_dists.close()
    #print pear,"(",len(url_dict),"pages)",
    return url_dict


##############################################
# Get word clouds for a pear
##############################################


def loadWordClouds(pear):
    print "Loading word clouds..."
    url_wordclouds={}
    #word_clouds = urllib.urlopen(pear + "/wordclouds.txt")
    word_clouds = open(pear + "/wordclouds.txt")
    for l in word_clouds:
        l = l.rstrip('\n')
        fields = l.split()
	url=fields[0]
	cloud=""
	for f in fields[1:]:
		cloud+=f+" "
	cloud=cloud[:-1]
        url_wordclouds[url] = cloud

    word_clouds.close()
    return url_wordclouds


################################################
# Score documents for a pear
################################################

def scoreDocs(query, query_dist, url_dict):
    document_scores = {}  # Document scores
    DS_scores=scoreDS(query_dist,url_dict)
    URL_scores=scoreURL(query,url_dict)
    for v in url_dict:
        if v in DS_scores and v in URL_scores:
                if URL_scores[v] > 0.7 and DS_scores[v] > 0.2:                                      #If URL overlap high (0.2 because of averag e length of query=4 -- see getUrlOverlap --  and similarity okay
                        document_scores[v]=DS_scores[v]+URL_scores[v]*0.2                                #Boost DS score by a maximum of 0.2
                else:
                	document_scores[v]=DS_scores[v]
	if math.isnan(document_scores[v]):								    #Check for potential NaN -- messes up with sorting in bestURLs.
		document_scores[v]=0
    return document_scores	

#################################################
# Get best URLs
#################################################


def bestURLs(doc_scores):
    best_urls = []
    c = 0
    for w in sorted(doc_scores, key=doc_scores.get, reverse=True):
        if c < 50:
            best_urls.append(w)
	    print w, doc_scores[w]
            c += 1
        else:
            break
    return best_urls


################################################
# Prepare output
################################################


def output(best_urls, query, url_wordclouds):
    results = []
#	print query
    # If documents matching the query were found on the pear network...
    if len(best_urls) > 0:
        for u in best_urls:
            results.append([u, url_wordclouds[u]])
#			print "Getting snippet for",u
#			snippet=returnSnippet.runScript(query,pear,reverse_url_dict[u])
#			results.append([u,snippet])

    # Otherwise, open duckduckgo and send the query there
    else:
        print "No suitable pages found."
        duckquery = ""
        for w in query.rstrip('\n').split():
            duckquery = duckquery + w + "+"
#		print duckquery
        webbrowser.open_new_tab(
            "https://duckduckgo.com/?q=" +
            duckquery.rstrip('+'))
        link_snippet_pair = [
            "###", "No suitable recommendation. You were redirected to duckduckgo."]
        results.append(link_snippet_pair)

    return results

##############################################
# Main function
##############################################

def runScript(query,query_dist,pears):
	all_pears_doc_scores = {}  # Document scores
	all_url_wordclouds = {}
        for pear in pears:
        	wc=loadWordClouds(pear)
		for k,v in wc.items():
			all_url_wordclouds[k]=v
		url_dict=getUrlDict(pear)
		#document_scores=scoreDocs(query, query_dist, url_dict):	#with URL overlap
		document_scores=scoreDS(query_dist, url_dict)			#without URL overlap
		for k,v in document_scores.items():
			if v > 0.3:						#Doc must be good enough
				all_pears_doc_scores[k]=v
	best_urls=bestURLs(all_pears_doc_scores)
        return output(best_urls, query, all_url_wordclouds)

if __name__ == '__main__':
    runScript(sys.argv[1], sys.argv[2],sys.argv[3])
