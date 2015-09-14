####################################################################
#./runDistSem.py is a script which takes lemmatised web
# pages and  outputs one distribution per sentence -- the addition
# of all word vectors in that sentence.
# ./runDistSem.py is called by indexPages.py
####################################################################

from numpy import *
import sys
import os
import re


path_to_PeARS = os.path.dirname(__file__)
pear=""	#Initialise variable for the pear we're adding page representations to

dm_dict={}		#Dictionary to store dm file

#################################################
# Read dm file
#################################################

def readDM():
	with open(os.path.join(path_to_PeARS, "wikiwoods.dm")) as f:
		dmlines=f.readlines()
		f.close()

	#Make dictionary with key=row, value=vector
	for l in dmlines:
		items=l.rstrip('\n').split('\t')
		row=items[0]
		vec=[float(i) for i in items[1:]]
		dm_dict[row]=vec

##################################################
# Process lemmatised file
##################################################

def processFile(lemma_file,pear):
	doc_dist=[]						#Holder for document distribution
	for x in range(300):					#Initialise doc_dist
		doc_dist.append(0)
	doc_dist=array(doc_dist)

	lines = []
        f=open(os.path.join(path_to_PeARS, pear+"/lemmas/"+lemma_file),"r")
        lines=f.readlines()
        f.close()

	#Get page URL
	url=""
	m=re.search('###\s(.*)',lines[0])
	if m:
		url=m.group(1)

	#Open representation file for writing
	rep=open(os.path.join(path_to_PeARS, pear+"/distsem/"+lemma_file),"w")

	#Write file info
	rep.write("<page>\n")
	rep.write("\t<url="+url+"/>\n")
	rep.write("\t<sentences>\n")

	i=1	#Iterator - start at line 2 (ignore URL line)

	#Iterate through file lines
	while i < len(lines):
		sentenceNumber = i

		words=lines[i].rstrip('\n').split()
#		print "Sentence",sentenceNumber,":",words

		#Only retain arguments which are in the distributional semantic space
		vecs_to_add = []
		for w in words:
			m=re.search('(.*_.).*',w)
			if m:
				w=m.group(1).lower()
			if w in dm_dict:
#				print "Adding",w,"to vecs_to_add"
				vecs_to_add.append(w)

		#Initialise vbase
		vbase=[]
		for x in range(300):
			vbase.append(0)
		vbase=array(vbase)


		#Add vectors together
		if len(vecs_to_add) > 0:
			base=vecs_to_add[0]				#Take first word in vecs_to_add to start addition
			vbase=array(dm_dict[base])
			for item in range(1,len(vecs_to_add)):
#				print item,"Adding vector",vecs_to_add[item]
				vbase=vbase+array(dm_dict[vecs_to_add[item]])

		#Make string version of distribution
		dist_str=""
		for n in vbase:
			dist_str=dist_str+"%.6f" % n+" "

		if i==1:						#First iteration
			doc_dist=vbase					#Initialise doc_dist as distribution for first sentence
		else:
			doc_dist=doc_dist+vbase				#Otherwise, add new sentence distribution to document distribution

		rep.write("\t\t<sentence id="+str(sentenceNumber)+">\n")
		rep.write("\t\t<DIST>"+dist_str.rstrip(' ')+"</DIST>\n")
		rep.write("\t\t</sentence>\n")
		i+=1

	rep.write("\t</sentences>\n")
	rep.write("</page>\n")

	rep.close()

	#Make string version of document distribution
	doc_dist_str=""
	for n in doc_dist:
		doc_dist_str=doc_dist_str+"%.6f" % n+" "

	return doc_dist_str

def updateDocDistFile(pear,file_name,doc_dist):
	#Open document distributions file for appending
	docdists=open(os.path.join(path_to_PeARS, "doc.dists"),"a")
	docdists.write(file_name+":"+doc_dist+"\n")
	docdists.close()

def updatePearDist(pear,doc_dist):
	to_print=[]
	#Open document distributions file
	pear_profile=open(os.path.join(path_to_PeARS, pear+"/profile.txt"),"r")
	for l in pear_profile:
		l=l.rstrip('\n')
		m=re.search("^pear_id:",l)
		if m:
			current_dist=l.split(':')[1]
			vbase=array([float(i) for i in current_dist.split()])
			vdocdist=array([float(i) for i in doc_dist.split()])
			vbase=vbase+vdocdist

			#Make string version of distribution
			dist_str=""
			for n in vbase:
				dist_str=dist_str+"%.6f" % n+" "
			to_print.append("pear_id:"+str(dist_str))
		else:
			to_print.append(l)
	pear_profile.close()

	pear_profile=open(os.path.join(path_to_PeARS, pear+"/profile.txt"),"w")
	for l in to_print:
		pear_profile.write(l+"\n")
	pear_profile.close()


def runScript(file_name,pear_name):
	pear=pear_name		#Record pear name
	readDM()		#Load the semantic space
	docdist=processFile(file_name,pear)
	if docdist!="":                                         #If document not empty
		updateDocDistFile(pear,file_name,docdist)
		updatePearDist(pear,docdist)

# when executing as script
if __name__ == '__main__':
    runScript(sys.argv[1],sys.argv[2])	#Input file and pear
