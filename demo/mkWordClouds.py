###############################################
# Make word clouds for document vectors
###############################################

import sys
import os
import numpy as np
from scipy.spatial import distance

path_to_PeARS = os.path.join(os.path.dirname(__file__),"users/")
stopwords=["","i","a","about","an","and","each","are","as","at","be","are","were","being","by","do","does","did","for","from","how","in","is","it","its","make","made","of","on","or","s","that","the","this","to","was","what","when","where","who","will","with","has","had","have","he","she","one","also","his","her","their","only","both","they","however","then","later","but","never","which","many"]
num_dimensions=400
dm_dict={}

#############################################
# Normalisation
#############################################

def normalise(v):
    norm=np.linalg.norm(v)
    if norm==0:
       return v
    return v/norm

#################################################
# Read dm file (but only top 10,000 words)
#################################################

def readDM():
	c=0
        #Make dictionary with key=row, value=vector
	dmlines=open("openvectors.dm",'r')
        for l in dmlines:
		if c < 10000:
			items=l.rstrip('\n').split('\t')
			row=items[0]
			vec=[float(i) for i in items[1:]]
			dm_dict[row]=normalise(vec)
			c+=1
		else:
			break
	dmlines.close()

#############################################
# Cosine function
#############################################

def cosine_similarity(peer_v, query_v):
    if np.linalg.norm(peer_v) !=0 and np.linalg.norm(query_v)!=0:
	    if len(peer_v) != len(query_v):
		raise ValueError("Peer vector and query vector must be "
				 " of same length")
	    num = np.dot(peer_v, query_v)
	    den_a = np.dot(peer_v, peer_v)
	    den_b = np.dot(query_v, query_v)
	    return num / (np.sqrt(den_a) * np.sqrt(den_b))
    else:
	return 0

############################################
# Compute similarities and return top n
############################################

def sim_to_matrix(vec,n):
	cosines={}
	for k,v in dm_dict.items():
		cos=cosine_similarity(np.array(vec),np.array(v))
		cosines[k]=cos

	topics=[]
	topics_s=""
	c=0
	for t in sorted(cosines, key=cosines.get, reverse=True):
		if c<n:
			if t.isalpha() and t not in stopwords:
				#print t,cosines[t]
				topics.append(t)
				topics_s+=t+" "
				c+=1
		else:
			break	
	return topics,topics_s[:-1]



###########################################
# Compute profile
###########################################

def computeWordClouds(pear):
	wordclouds={}				#Store vectors for this user in order to compute coherence
	#Open document distributions file
	doc_dists=open(path_to_PeARS+pear+"/urls.dists.txt","r")
	for l in doc_dists:
		l=l.rstrip('\n')
		url=l.split()[0]
		doc_dist=l.split()[1:]
		vdocdist=np.array([float(i) for i in doc_dist])
		if np.linalg.norm(vdocdist) > 0.0:
			topics,topics_s=sim_to_matrix(vdocdist,10)
			wordclouds[url]=topics_s
			#print url, topics_s
	doc_dists.close()
	return wordclouds


def printWordClouds(wc,user):
	wordclouds_file=open(path_to_PeARS+user+"/wordclouds.txt",'w')
	for k,v in wc.items():
		wordclouds_file.write(k+" "+v+"\n")
	wordclouds_file.close()		


###################
# Entry point
###################
def runScript(user):
	readDM()
	print "Computing wordclouds for",user
	wc=computeWordClouds(user)
	printWordClouds(wc,user)

if __name__ == '__main__':
	# when executing as script
	runScript(sys.argv[1])
