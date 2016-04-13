################################################################
# findBestPeARS.py identifies best pears on the network for a
# particular query.
# USAGE: called by mkQueryPage.py when user enters a query
################################################################

import numpy as np
from math import isnan
import urllib
import re
from .utils import cosine_similarity, print_timing


num_best_pears=5



###################################################
# Sort scores and output n best pears
###################################################

def outputBestPears(pears_scores):
    pears = []
    count = 0
    for w in sorted(pears_scores, key=pears_scores.get, reverse=True):
        if count < num_best_pears:
            print w, pears_scores[w]
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
	if pear.endswith('/'):
	        pear = pear[:-1]
        #profile_file = urllib.urlopen(base_url + "profile.txt")
        profile_file = open(pear+"/profile.txt")

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
    return r


#############################################
# Main function, called by mkQueryPage.py
##############################################

# The @ decorator before the function invokes print_timing()
@print_timing
def runScript(query_dist,pears_ids):
    best_pears = []

    #############################################################
    # Calculate score for each pear in relation to the user query
    #############################################################

    if len(query_dist) > 0:
        pears_scores = {}
	for pear_name,v in pears_ids.items():
		scoreSIM = 0.0          #Initialise score for similarity
		score=cosine_similarity(np.array(v),query_dist)
		if not isnan(score):
			pears_scores[pear_name]=score
			print pear_name,score
        best_pears=outputBestPears(pears_scores)
    return best_pears

