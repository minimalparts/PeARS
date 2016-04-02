#####################################################################
# Make page representation as the WEIGHTED sum of the most 'important'
# words in the page (obtained via entropy calculation)
#####################################################################

import numpy as np
import math
import sys
import os
import re


path_to_PeARS = "/home/aurelie/PeARS-org/PeARS/demo/"
num_dimensions=400
stopwords=["","(",")","a","about","an","and","are","around","as","at","away","be","become","became","been","being","by","did","do","does","during","each","for","from","get","have","has","had","he","her","his","how","i","if","in","is","it","its","made","make","many","most","not","of","on","or","s","she","some","that","the","their","there","this","these","those","to","under","was","were","what","when","where","which","who","will","with","you","your"]

dm_dict={}		#Dictionary to store dm file
entropies_dict={}	#Word freqs in ukWac
doc_dists=[]		#Which files already have a distribution

#############################################
# Normalisation
#############################################

def normalise(v):
    norm=np.linalg.norm(v)
    if norm==0:
       return v
    return v/norm

#################################################
# Read dm file
#################################################

def readDM():
	with open(path_to_PeARS+"openvectors.dm") as f:
		dmlines=f.readlines()
		f.close()

	#Make dictionary with key=row, value=vector
	for l in dmlines:
		items=l.rstrip('\n').split('\t')
		row=items[0]
		vec=[float(i) for i in items[1:]]
		dm_dict[row]=normalise(vec)

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


############################################
# Compute similarities and return top n
############################################

def sim_to_matrix(vec,n):
        cosines={}
	c=0
        for k,v in dm_dict.items():
		cos=cosine_similarity(np.array(vec),np.array(v))
		cosines[k]=cos
		c+=1

        c=0
        for t in sorted(cosines, key=cosines.get, reverse=True):
                if c<n:
                        if t.isalpha() and t not in stopwords:
                                print t,cosines[t]
                                c+=1
                else:
                        break


#################################################
# Load entropy list
#################################################

def loadEntropies():
	f=open("ukwac.entropy.txt","r")
	for l in f:
		l=l.rstrip('\n')
		fields=l.split('\t')
		w=fields[0].lower()
		if w.isalpha() and w not in entropies_dict:			#Must have this cos lower() can match two instances of the same word in the list
			entropies_dict[w]=float(fields[1])
	f.close()

##################################################
# Get weights from file
##################################################

def weightFile(buff):
	word_dict={}
	words=buff.split()
	for w in words:
		w=w.lower()
		if w in entropies_dict and w not in stopwords:
		#if w in freqs_dict:
			if w in word_dict:
				word_dict[w]+=1
			else:
				word_dict[w]=1
	for k,v in word_dict.items():
		if math.log(entropies_dict[k]+1) > 0:
			word_dict[k]=float(v)/float(math.log(entropies_dict[k]+1))
	return word_dict


################################################
# Make vectors from weights
################################################

def mkVector(word_dict):
	#Initialise vbase and doc_dist vectors
	vbase=np.zeros(num_dimensions)
	#Add vectors together
	if len(word_dict) > 0:
		c=0
		for w in sorted(word_dict, key=word_dict.get, reverse=True):
			if c < 5:
				#print w,word_dict[w]
				if w in dm_dict:
					vbase=vbase+float(word_dict[w])*np.array(dm_dict[w])
			c+=1

		vbase=normalise(vbase)

	#Make string version of document distribution
	doc_dist_str=""
	for n in vbase:
		doc_dist_str=doc_dist_str+"%.6f" % n+" "

	#print "Computing nearest neighbours..."
	#sim_to_matrix(array(vbase),20)
	return doc_dist_str



def runScript(infile,out):
	readDM()
	loadEntropies()
	docdists=open(out,"w")

	f=open(infile,'r')
	buff=""
	line_counter=0
	for l in f:
		l=l.rstrip('\n')
		if "<doc" in l:
			doc_id=""
			m=re.search("<doc id=\"([0-9]+)\".*title=\"(.*)\"",l)
			doc_id=m.group(1)
			title=m.group(2).replace(' ','_')
			url="https://en.wikipedia.org/wiki/"+title
			print url
		else:
			if "</doc" not in l:
				if line_counter < 20:
					buff+=l+" "
					line_counter+=1
				else:
					continue
			else:
				v=weightFile(buff)
				s=mkVector(v)
				docdists.write(url+" "+s+"\n")
				buff=""
				line_counter=0
	f.close()
	docdists.close()

# when executing as script
if __name__ == '__main__':
    runScript(sys.argv[1],sys.argv[2])	
