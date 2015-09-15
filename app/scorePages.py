#######################################################################
# ./scorePages.py compares the query to each document
# Called by ./mkQueryPage.py
#######################################################################

from operator import itemgetter, attrgetter
from numpy import *
import subprocess
import collections
import webbrowser
import urllib
import sys
import re
import os
from .utils import mkQueryDist, cosine_similarity, print_timing

import getUrlOverlap

# Change this line to your PeARS folder path
dm_dict = {}  # Dictionary to store dm file
url_dict = {}  # Dictionary file ids - urls
reverse_url_dict = {}  # Dictionary urls - file ids
doc_scores = {}  # Document scores
url_wordclouds = {}  # Stores correspondence between url and word cloud for this query
# url_snippets={}         #Stores correspondence between url and best
# snippet for this query

##############################################
# Read url file
##############################################


def loadURLs(pear):
    print "Loading URL dictionary for", pear
    if pear.endswith('/'):
        pear = pear[:-1]
    path_to_dict = pear + "/urls.dict.txt"

    d = urllib.urlopen(path_to_dict)
    #d = open(path_to_dict)
    for line in d:
        line = line.rstrip('\n')
        idfile = line.split()[0]
        url = line.split()[1]
        # print idfile,url
        url_dict[idfile] = url  # Record the pairs url - file name on pear
        reverse_url_dict[url] = idfile
    d.close()


##############################################
# Get word clouds for a pear
##############################################


def loadWordClouds(pear):
    print "Loading word clouds..."
    word_clouds = urllib.urlopen(pear + "/wordclouds.txt")
    #word_clouds = open(pear + "/wordclouds.txt")
    for l in word_clouds:
        l = l.rstrip('\n')
        fields = l.split(':')
        url_wordclouds[url_dict[fields[0]]] = fields[1]

    word_clouds.close()


###############################################
# Get distributional score
###############################################

@print_timing
def scoreDS(query_dist, pear):
    dd = urllib.urlopen(pear + "/doc.dists.txt")
    #dd = open(pear + "/doc.dists.txt")
    doc_dists = dd.readlines()
    dd.close()
    # print "Done reading dd"

    DS_scores = {}
    for l in doc_dists:
        l = l.rstrip('\n')
        doc_id = l.split(':')[0]
        doc_dist = array(l.split(':')[1].split())
        doc_dist = [double(i) for i in doc_dist]
	#print url_dict[doc_id],cosine_similarity(doc_dist,query_dist)
        score = cosine_similarity(doc_dist, query_dist)
        DS_scores[url_dict[doc_id]] = score
        # url_wordclouds[url_dict[doc_id]]=getWordCloud(pear,doc_id)
    return DS_scores


###############################################
# Get url overlap score
###############################################

@print_timing
def scoreURL(query):
    q = re.sub("_.", '', query)
    URL_scores = {}
    for k, v in url_dict.items():
        URL_scores[v] = getUrlOverlap.runScript(q, v)
        # print query,v,URL_scores[v]
    return URL_scores

################################################
# Score documents for a pear
################################################


@print_timing
def scoreDocs(query, query_dist, pear):
    DS_scores = scoreDS(query_dist, pear)
    URL_scores = scoreURL(query)
    for k, v in url_dict.items():
        if v in DS_scores and v in URL_scores:
#	    if DS_scores[v] > 0.4:
#		print v, DS_scores[v]
            if URL_scores[v] > 0.7 and DS_scores[v] > 0.4:  # If URL overlap high and similarity okay
                print v, DS_scores[v], URL_scores[v]
                # Boost DS score by a maximum of 0.2 (thresholds to be updated
                # when we have proper evaluation data)
                doc_scores[v] = DS_scores[v] + URL_scores[v] * 0.2
            else:
                doc_scores[v] = DS_scores[v]
    return doc_scores

#################################################
# Get best URLs
#################################################


def bestURLs(doc_scores):
    best_urls = []
    c = 0
    for w in sorted(doc_scores, key=doc_scores.get, reverse=True):
        if c < 10:
            if doc_scores[w] > 0.4:  # Threshold - page must be good enough
                best_urls.append(w)
		print w, doc_scores[w]
            c += 1
        else:
            break
    return best_urls


################################################
# Prepare output
################################################


def output(best_urls, query):
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
# Main function, called by mkQueryPage.py
##############################################

# The @ decorator before the function invokes print_timing()


@print_timing
def runScript(pears, query):
    query_dist = mkQueryDist(query)
    best_urls = []
    if len(pears) > 0:
        for pear in pears:
            # print pear
            loadURLs(pear)
            loadWordClouds(pear)
            scoreDocs(query, query_dist, pear)
        best_urls = bestURLs(doc_scores)
    return output(best_urls, query)

if __name__ == '__main__':
    runScript(sys.argv[1], sys.argv[2])
