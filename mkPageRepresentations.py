####################################################################
#./mkPageRepresentations v0.1 is a script which takes lemmatised web
# pages and builds bag-of-words (BOW) representations for them,
# one BOW per sentence. In addition, it outputs one distribution
# per sentence -- the addition of all word vectors in that sentence.
# ./mkPageRepresentations is called by ./getDomainPages
####################################################################

from composes.semantic_space.space import Space
from composes.utils import io_utils
from composes.composition.weighted_additive import WeightedAdditive
from composes.similarity.cos import CosSimilarity
import sys
import os
import re


numDims = 300	#Number of dimensions in the space
pears_home = "/home/aurelie/PeARS/"

###### Helpful functions #######################################################################

def mkNullVector(fileName, vectorName, numDims):
	null_vector=vectorName+" "
	for i in range(numDims):
		null_vector+="0.0 "
	filetmp = open(fileName, "w" )	
	filetmp.write(null_vector.strip())
	filetmp.close()


###### Helpful functions end ##################################################################



domain=sys.argv[1]

############################################
# Set up directories, etc
############################################


#Create directory for page representations
if not os.path.isdir("domains/"+domain+"-pagereps/"):
	os.makedirs("domains/"+domain+"-pagereps/")

#Open new document distributions file for (over)writing
docdists=open("domains/"+domain+".doc.dists","w")
	

#Load the semantic space
my_space = io_utils.load(pears_home+"query/wikiwoods.ppmi.nmf_300.row.nocaps.pkl")

#Load rows of space (words for which a distribution is available)
rows = open( pears_home+"query/wikiwoods.rows", "r" )
dists = []
for l in rows:
	l=l.rstrip('\n')
	dists.append(l)
rows.close()

my_comp=WeightedAdditive(alpha = 1, beta = 1);



##################################################
# Iterate through all lemmatised files and process
##################################################

listing=os.listdir("domains/"+domain+"-lemmas/")

for file in listing:
	print "Processing",file,"..."
	lines = []
        f=open("domains/"+domain+"-lemmas/"+file,"r")
        lines=f.readlines()
        f.close()
        
	#Get page URL
	url=""
	m=re.search('###\s(.*)',lines[0])
	if m:
		url=m.group(1)

	#Remove distribution of previous document
	if os.path.exists("document.dm"):
		os.remove("document.dm")

	#Open representation file for writing
	rep=open("domains/"+domain+"-pagereps/"+file,"w")

	#Write file info
	rep.write("<page>\n")
	rep.write("\t<url="+url+"/>\n")
	rep.write("\t<sentences>\n")

	i=1	#Iterator - start at line 2 (ignore URL line)

	#Iterate through file lines 
	while i < len(lines):
		sentenceNumber = i
		
		words=lines[i].rstrip('\n').split()

		#Remove any old addition.dm file in the directory and start from scratch with a new null vector
		if os.path.exists("addition.dm"):
			os.remove("addition.dm")
			mkNullVector("addition.dm","_addition_",numDims)

		#If new document being processed, create a document.dm file
		if not os.path.exists("document.dm"):
			mkNullVector("document.dm", "_document_", numDims)



		#Only retain arguments which are in the distributional semantic space
		#And while at it, make the BOW representation
		BOW=""
		vecs_to_add = []
		for w in words:
			m=re.search('(.*_.).*',w)
			if m:
				w=m.group(1).lower()
			BOW=BOW+w+" "
			if w in dists:
				vecs_to_add.append(w)	
		BOW=BOW.rstrip(' ')	#Remove last space


		if len(vecs_to_add) > 1:

			composed_space=Space.build(data="addition.dm", format="dm")
			composed_document_space=Space.build(data="document.dm", format="dm")

			for a in range(len(vecs_to_add)):
				#print "Adding",vecs_to_add[arg]
				composed_space = my_comp.compose([(vecs_to_add[a], "_addition_", "_addition_")],(my_space,composed_space))

			#print composed_space.id2row
			composed_space.export("./addition", format="dm")

			#add sentence to document distribution and export to document.dm
			composed_document_space = my_comp.compose([("_addition_", "_document_", "_document_")],(composed_space,composed_document_space))
			composed_document_space.export("./document", format="dm")

		if os.path.exists("addition.dm"):
			add=open("addition.dm","r")
			addition=add.readlines()
			add.close()
		
		dist=""
		m=re.search('_addition_\s(.*)',addition[0])
		if m:
			dist=re.sub('\t', r' ', m.group(1))
		rep.write("\t\t<sentence id="+str(sentenceNumber)+">\n")
		rep.write("\t\t<BOW>"+BOW+"</BOW>\n")
		rep.write("\t\t<DIST>"+dist+"</DIST>\n")
		rep.write("\t\t</sentence>\n")
		i+=1
	
	rep.write("\t</sentences>\n")
	rep.write("</page>\n")

	if os.path.exists("document.dm"):
		doc=open("document.dm")
		document=doc.readlines()
		doc.close()

	m=re.search('_document_(\s.*)',document[0])
	if m:
		docdists.write(file+m.group(1)+"\n")
	
	rep.close()	

docdists.close()
