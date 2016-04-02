################################################################
# utils includes all the utility methods being used throughout
# the codebase
################################################################



from numpy import *
import re
import pdb
import time
import os
from .models import OpenVectors

stopwords=["","(",")","a","about","an","and","are","around","as","at","away","be","become","became","been","being","by","did","do","does","during","each","for","from","get","have","has","had","her","his","how","i","if","in","is","it","its","made","make","many","most","of","on","or","s","some","that","the","their","there","this","these","those","to","under","was","were","what","when","where","who","will","with","you","your"]

########################################################
# Normalise array
########################################################

def normalise(v):
    norm=linalg.norm(v)
    if norm==0: 
       return v
    return v/norm

#############################################
# Cosine function
#############################################

def cosine_similarity(peer_v, query_v):
    if len(peer_v) != len(query_v):
        raise ValueError("Peer vector and query vector must be "
                         " of same length")
    num = dot(peer_v, query_v)
    den_a = dot(peer_v, peer_v)
    den_b = dot(query_v, query_v)
    return num / (sqrt(den_a) * sqrt(den_b))

#################################################
# Load entropy list
#################################################

def loadEntropies():
	entropies_dict={}
	entropies_file = os.path.join(
	    os.path.dirname(__file__),
	    "ukwac.entropy.txt")
	f=open(entropies_file,"r")
	for l in f:
		l=l.rstrip('\n')
		fields=l.split('\t')
		w=fields[0].lower()
		if w.isalpha() and w not in entropies_dict:			#Must have this cos lower() can match two instances of the same word in the list
			entropies_dict[w]=float(fields[1])
	f.close()
	return entropies_dict

##############################################
# Make distribution for query
##############################################

def mkQueryDist(query,entropies):
    words = query.rstrip('\n').split()

    # Only retain arguments which are in the distributional semantic space
    vecs_to_add = []
    for w in words:
        word = OpenVectors.query.filter(OpenVectors.word==w).first()
        if word:
            vecs_to_add.append(word)
        else:
            w=w[0].upper()+w[1:]                                                #Did user carelessly forget to capitalise a proper noun?
            word = OpenVectors.query.filter(OpenVectors.word==w).first()
            if word:
                vecs_to_add.append(word)


    vbase = array([])
    # Add vectors together
    if len(vecs_to_add) > 0:
        # Take first word in vecs_to_add to start addition
        vbase = array([float(i) for i in vecs_to_add[0].vector.split(',')])
        for item in range(1, len(vecs_to_add)):
	    w = vecs_to_add[item]
	    if w in entropies and math.log(entropies[w]+1) > 0:
		weight=float(1)/float(math.log(entropies[w]+1))
		vbase = vbase + weight*array([float(i) for i in vecs_to_add[item].vector.split(',')])
	    else:
		vbase = vbase + array([float(i) for i in vecs_to_add[item].vector.split(',')])

    vbase=normalise(vbase)
    return vbase


##############################################
# Read pears  ids
##############################################

def readPears():
	shared_pears_ids = os.path.join(
	    os.path.dirname(__file__),
	    "shared_pears_ids.txt")

        pears_ids={}
        sp=open(shared_pears_ids,'r')
        for l in sp:
                l=l.rstrip('\n')
                items=l.split()
                pear_name =  items[0]
                pear_dist =[float(i) for i in items[1:]]
                pears_ids[pear_name]=pear_dist
        sp.close()
        return pears_ids




# Timing function, just to know how long things take


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s in scorePages took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res
    return wrapper


