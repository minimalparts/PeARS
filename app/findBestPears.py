################################################################
# findBestPeARS.py identifies best pears on the network for a
# particular query.
# USAGE: called by mkQueryPage.py when user enters a query
################################################################

from numpy import *
import urllib
import sys
import re
import os
import time


shared_pears_ids = os.path.join(
    os.path.dirname(__file__),
    "shared_pears_ids.txt")
dm_dict = {}  # Dictionary to store dm file


# Timing function, just to know how long things take
def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '%s in findBestPears took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res
    return wrapper


#############################################
# Cosine function
#############################################

def cosine_similarity(peer_v, query_v):
    if len(peer_v) != len(query_v):
        raise ValueError("Peer vector and query vector must be "
                         " of same length")
    num=multiply(peer_v,query_v).sum()
    den_a=multiply(peer_v,peer_v).sum()
    den_b=multiply(query_v,query_v).sum()
    return num / (sqrt(den_a) * sqrt(den_b))



#################################################
# Read dm file
#################################################

def readDM():
    with open(os.path.join(os.path.dirname(__file__), "wikiwoods.dm")) as f:
        dmlines = f.readlines()
        f.close()

    # Make dictionary with key=row, value=vector
    for l in dmlines:
        items = l.rstrip('\n').split('\t')
        row = items[0]
        vec = [float(i) for i in items[1:]]
        dm_dict[row] = vec


##############################################
# Make distribution for query
##############################################

def mkQueryDist(query):
    words = query.rstrip('\n').split()

    # Only retain arguments which are in the distributional semantic space
    vecs_to_add = []
    for w in words:
        m = re.search('(.*_.).*', w)
        if m:
            w = m.group(1).lower()
        if w in dm_dict:
            #				print "Adding",w,"to vecs_to_add"
            vecs_to_add.append(w)

    vbase = array([])
    # Add vectors together
    if len(vecs_to_add) > 0:
        # Take first word in vecs_to_add to start addition
        base = vecs_to_add[0]
        vbase = array(dm_dict[base])
        for item in range(1, len(vecs_to_add)):
            #				print item,"Adding vector",vecs_to_add[item]
            vbase = vbase + array(dm_dict[vecs_to_add[item]])

    return vbase


###################################################
# Sort scores and output n best pears
###################################################

def outputBestPears(pears_scores):
    pears = []
    num_best = 3  # Top best pears to search
    count = 0
    for w in sorted(pears_scores, key=pears_scores.get, reverse=True):
        if count < num_best:
            #               print w, pears_scores[w]
            pears.append(w)
            count += 1
        else:
            break

    #####################
    # Output helpful pears
    #####################

    r = []
    # Retrieve pear.profile data
    for pear in pears:
        profile = []
        pi_name = ""
        pi_picture = ""
        pi_message = ""
        base_url = pear + '/'
        profile_file = urllib.urlopen(base_url + "profile.txt")

        profile.append(pear)
        for line in profile_file:
            m = re.search('^message = (.*)', line)
            if m:
                pi_message = m.group(1)
                profile.append(pi_message)
        # web browser won't let us access local image from localhost, so using
        # generic picture
        profile.append("./static/pi-pic.png")

        r.append(profile)
#		print profile

    return r


#############################################
# Main function, called by mkQueryPage.py
##############################################

# The @ decorator before the function invokes print_timing()
@print_timing
def runScript(query):
    # load a semantic space
    readDM()
    best_pears = []
    query_v = mkQueryDist(query)

    #############################################################
    # Calculate score for each pear in relation to the user query
    #############################################################

    if len(query_v) > 0:
        sp = open(shared_pears_ids, 'r')
        pears = sp.readlines()
        sp.close()

        pears_scores = {}
        for l in pears:
            l = l.rstrip('\n')
            pear_name = l.split('|')[0]
            pear_v = array(l.split('|')[1].split())
	    pear_v = [double(i) for i in pear_v]
            score = cosine_similarity(pear_v, query_v)
            pears_scores[pear_name] = score

        best_pears = outputBestPears(pears_scores)
    return best_pears

if __name__ == '__main__':
    # when executing as script
    runScript(sys.argv[1])
