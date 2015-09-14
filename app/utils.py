################################################################
# utils includes all the utility methods being used throughout
# the codebase
################################################################



from numpy import *
import re
import pdb
import time
from .models import WikiWoods

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


##############################################
# Make distribution for query
##############################################

def mkQueryDist(query):
    words = query.rstrip('\n').split()

    # Only retain arguments which are in the distributional semantic space
    vecs_to_add = []
    for w in words:
        word = WikiWoods.query.filter(WikiWoods.word==w).first()
        if word:
            vecs_to_add.append(word)
        else:
            w=w[0].upper()+w[1:]                                                #Did user carelessly forget to capitalise a proper noun?
            word = WikiWoods.query.filter(WikiWoods.word==w).first()
            if word:
                vecs_to_add.append(word)


    vbase = array([])
    # Add vectors together
    if len(vecs_to_add) > 0:
        # Take first word in vecs_to_add to start addition
        vbase = array([float(i) for i in vecs_to_add[0].vector.split(',')])
        for item in range(1, len(vecs_to_add)):
            vbase = vbase + array([float(i) for i in vecs_to_add[item].vector.split(',')])

    return vbase



# Timing function, just to know how long things take


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s in scorePages took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res
    return wrapper


