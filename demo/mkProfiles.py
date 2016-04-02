###############################################
# Make user profiles by adding document vectors
###############################################

import sys
import numpy as np
from scipy.spatial import distance

path_to_PeARS = "/home/aurelie/PeARS-org/PeARS/demo/users/"
stopwords=["","i","a","about","an","and","each","are","as","at","be","are","were","being","by","do","does","did","for","from","how","in","is","it","its","make","made","of","on","or","s","that","the","this","to","was","what","when","where","who","will","with","has","had","have","he","she","one","also","his","her","their","only","both","they","however","then","later","but","never","which","many"]
num_dimensions=400
dm_dict={}

###############################################
# Read list of users
###############################################

def readUsers(usernames_file):
	#print "Getting users..."
	users=[]
	f=open(usernames_file,'r')
	for l in f:
		l=l.rstrip('\n')
		users.append(l)
	f.close()
	return users

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

############################################
# Compute coherence
############################################
def coherence(vecs):
	coh=0.0
	counter=0
	if len(vecs) > 1:
		matrix=np.array(vecs)
		#print matrix
		dist_m=distance.cdist(matrix,matrix,'cosine')
		#print dist_m
		for i in range(0,len(vecs)-1):
			for j in range(i+1,len(vecs)):
				cosine=1-dist_m[i][j]
				#print cosine
				coh+=cosine
				counter+=1		
		coh = float(coh)/float(counter)
	else:
		coh=1
	#print coh
	return coh



###########################################
# Compute profile
###########################################

def computePearDist(pear):
	vbase=np.zeros(num_dimensions)
	vecs_for_coh=[]				#Store vectors for this user in order to compute coherence
	#Open document distributions file
	doc_dists=open(path_to_PeARS+pear+"/"+pear+".urls.dists.txt","r")
	for l in doc_dists:
		l=l.rstrip('\n')
		doc_dist=l.split()[1:]
		vdocdist=np.array([float(i) for i in doc_dist])
		vbase=vbase+vdocdist
		#print vdocdist[:10]
		if np.linalg.norm(vdocdist) > 0.0:
			vecs_for_coh.append(vdocdist)
	doc_dists.close()

	vbase=normalise(vbase)
	#Make string version of distribution
	dist_str=""
	for n in vbase:
		dist_str=dist_str+"%.6f" % n+" "
	dist_str=dist_str.rstrip(' ')


	#coh=0
	coh=coherence(vecs_for_coh)
	#print coh
	return vbase,dist_str,coh


def createProfileFile(pear,pear_dist,topics_s,coh):
	profile=open(path_to_PeARS+pear+"/"+pear+".profile.txt",'w')
	profile.write("name = "+pear+"\n")
	profile.write("topics = "+topics_s+"\n")
	profile.write("coherence = "+str(coh)+"\n")
	profile.write("pear_id:"+pear_dist+"\n")	
	profile.close()		


###################
# Entry point
###################
def runScript(user):
	readDM()
	print "Computing pear for",user
	#try:
	v,print_v,coh=computePearDist(user)
	topics,topics_s=sim_to_matrix(v,20)
	createProfileFile(user,print_v,topics_s,coh)
	#except:
	#	print "ERROR: PERHAPS PEAR NOT FOUND?"

if __name__ == '__main__':
	# when executing as script
	runScript(sys.argv[1])
