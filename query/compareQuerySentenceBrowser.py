#######################################################################
# ./compareQuerySentenceBrowser.py compares the query to each document
# in the relevant topic, on the relevant pi, and returns scores for 
# each document.
# Called by ./mkQueryPage.py
####################################################################### 

from composes.utils import io_utils
from composes.semantic_space.space import Space
from composes.composition.weighted_additive import WeightedAdditive
from composes.similarity.cos import CosSimilarity
from operator import itemgetter, attrgetter
import webbrowser
import urllib
import sys
import re
import time
import os

#Change this line to your PeARS folder path
pears_home="/home/aurelie/PeARS/"

numDims = 300   #Number of dimensions in the space

##### Helpful functions ########################################################################

#Timing function, just to know how long things take
def print_timing(func):
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s in compareQuerySentence took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper



def mkNullVector(fileName, vectorName, numDims):
        null_vector=vectorName+" "
        for i in range(numDims):
                null_vector+="0.0 "
        filetmp = open(fileName, "w" )
        filetmp.write(null_vector.strip())
        filetmp.close()

##### Helpful functions end ####################################################################






##############################################
#Main function, called by mkQueryPage.py
##############################################

# The @ decorator before the function invokes print_timing()
@print_timing
def runScript():
	PTfile = open( "pi-topics.tmp", "r" )	#Open pi-topic file
	Qfile = open("query.tmp", "r") 		#Open query file

	my_space = io_utils.load(pears_home+"query/wikiwoods.ppmi.nmf_300.row.nocaps.pkl")	#Load semantic space

	#Get user search from file
	query=Qfile.readline().rstrip('\n')
	querywords=query.split()
	querylength=len(querywords)

	scores = []	#Initialise score
	docs = [] 	#Initialise docs
	
	mkNullVector("query.dm","_query_",numDims)	#Initialise query vector
	
	#Load rows of space (words for which a distribution is available)
	rows = open( "wikiwoods.rows", "r" )
	dists = []
	for l in rows:
		l=l.rstrip('\n')
		dists.append(l)
	rows.close()

	#Add distributions of query words into _query_ vector, living in query_space 
	query_space=Space.build(data="query.dm", format="dm")
	my_comp=WeightedAdditive(alpha = 1, beta = 1);

	for a in range(len(querywords)):
		if a in dists:
			query_space = my_comp.compose([(querywords[a], "_query_", "_query_")],(my_space,query_space))

	#print composed_space.id2row
	query_space.export("./query", format="dm")

	###############################################################
	# For each topic in PTfile, find on the relevant file all pages
	# classified under that topic
	###############################################################

	for l in PTfile:
		l=l.rstrip('\n')
		words =  l.split()
		pi=words[0]
		topic=""
		domain=""
		piaddress=""
		
		m = re.search('-([0-9]+)', words[1])
		if m:
			topic=m.group(1)
		m=re.search('(\S+)-', words[1])
		if m:
			domain=m.group(1)

		#Are we using a local folder named 'Pi...' as the searchable directory, or an actual web server?
		if "Pi" in pi:
			piaddress=pears_home+pi
			index=open(piaddress+"/"+domain+"/"+domain+".doc.topics.index")
			distFile=piaddress+"/"+domain+"/"+domain+".doc.dists"
		else:
			piaddress="http://"+pi
			index=urllib.urlopen(piaddress+"/"+domain+"/"+domain+".doc.topics.index")
			distFile=piaddress+"/"+domain+"/"+domain+".doc.dists"

		#Read the document_space from distFile
		if os.path.exists(distFile): 	#If distFile has been computed for this topic
			composed_document_space=Space.build(data=distFile, format="dm")

		topic_search="TOPICS:.* "+topic+" |TOPICS:.* "+topic+"$"

		for fline in index:
			m1 = re.search(topic_search, fline)
			if m1:
				m2 = re.search('FILE: (.*\.lynx) URL', fline)
				if m2:
					doc=m2.group(1)
					if os.path.exists(distFile): 	#If distFile has been computed for this topic
						docScore=composed_document_space.get_sim(doc, "_query_", CosSimilarity(), space2=query_space)
						if docScore > 0.5:	#Only consider documents over a certain threshold
							m3 = re.search('.*URL: (.*) TOPICS.*', fline)
							if m3:
								url=m3.group(1)
								loc=[pi,domain,doc,url]
								if loc 	not in docs:
									docs.append(loc)
					else:
						m3 = re.search('.*URL: (.*) TOPICS.*', fline)
						if m3:
							url=m3.group(1)
							loc=[pi,domain,doc,url]
							if loc 	not in docs:
								docs.append(loc)
						

		index.close()


	########################################################
	# For each document identified as potentially relevant,
	# get a score against user query
	########################################################

	for doc in docs:					
		pagescore=0.0
		bestSentence=""
		bestSentenceScore=0.0
		numSentences=0
		
		#Are we using a local folder named 'Pi...' as the searchable directory, or an actual web server?
		if "Pi" in doc[0]:
			peardoc=open(pears_home+doc[0]+"/"+doc[1]+"/pages/"+doc[2])
		else:
			peardoc=urllib.urlopen("http://"+doc[0]+"/"+doc[1]+"/pages/"+doc[2])
		
		for dline in peardoc:
			m3 = re.search('<BOW>',dline)
			if m3:
				scoreWO=0.0
				numSentences+=1
				dline=dline.replace('<BOW>','')
				dline=dline.replace('</BOW>','')
				dlinewords=dline.split()		#Find BOW representation of sentence
  
				for qw in querywords:
					for w in dlinewords:
						if w.lower() == qw.lower():
							scoreWO+=1
							break
				scoreWO = scoreWO / querylength		#Sentence score is proportional to how many words from the query are contained in the sentence
				if scoreWO > bestSentenceScore:
					bestSentence=dline		#Record most relevant sentence for that document, for display in the results
					bestSentenceScore=scoreWO
				pagescore+=scoreWO
				if numSentences > 30:			#For speed (and accuracy!), only process first 30 sentences of the file
					break
		if numSentences > 0:
			pagescore = pagescore / numSentences		#Document score is the sum of all sentence scores over the number of sentences
		if pagescore > 0:
			doc_score=[doc[3],pagescore,bestSentence]
			scores.append(doc_score)

	results=[]	#Initialise results




	############################
	# Prepare results for output
	############################


	#If documents matching the query were found on the Pi network...
	if len(scores) > 0:
		scores_sorted=sorted(scores, key=itemgetter(1), reverse=True)
		for s in scores_sorted:
			excerpt=""
			for w in querywords:
				m = re.search('((\S+_\S ){0,5}%s (\S+_\S ){0,5})'%w, s[2], re.IGNORECASE)	#Dumb excerpt from best sentence (in lemmatised form!)
				if m:
					excerpt=excerpt+m.group(1)+"..."
			link_sent=[s[0],re.sub(r'_.',r'',excerpt)]
			results.append(link_sent)

	#Otherwise, open duckduckgo and send the query there
	else:
		duckquery=""
		for w in querywords:
			m = re.search('(.*)_.',w)
			if m:
				duckquery+=m.group(1)+"+"
		webbrowser.open_new_tab("https://duckduckgo.com/?q="+duckquery)
		link_sent=["#######","No suitable recommendation. You were redirected to duckduckgo."]
		results.append(link_sent)

	return results

if __name__ == '__main__':
    # test1.py executed as script
    runScript()
