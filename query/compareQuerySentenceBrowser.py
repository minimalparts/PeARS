#######################################################################
# ./compareQuerySentenceBrowser.py compares the query to each document
# in the relevant topic, on the relevant pi, and returns scores for 
# each document.
# Called by ./mkQueryPage.py
####################################################################### 

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from operator import itemgetter, attrgetter
import webbrowser
import sys
import re
import time

#Change this line to your PeARS folder path
pears_home="/home/aurelie/PeARS/"

#Timing function, just to know how long things take
def print_timing(func):
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s in compareQuerySentence took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper

# The @ decorator before the function invokes print_timing()
@print_timing

##############################################
#Main function, called by mkQueryPage.py
##############################################

def runScript():
	PTfile = open( "pi-topics.tmp", "r" )	#Open pi-topic file
	Qfile = open("query.tmp", "r") 		#Open query file

	#Get user search from file
	query=Qfile.readline().rstrip('\n')
	querywords=query.split()
	querylength=len(querywords)

	scores = []	#Initialise score
	docs = [] 	#Initialise docs


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
		
		m = re.search('-([0-9]+)', words[1])
		if m:
			topic=m.group(1)
		m=re.search('(\S+)-', words[1])
		if m:
			domain=m.group(1)

		piaddress=pears_home+pi+"/"+domain+"/"
		topic_search="TOPICS:.* "+topic+" |TOPICS:.* "+topic+"$"
		
		for fline in open(piaddress+domain+".doc.topics.index"):
			m1 = re.search(topic_search, fline)
		 	if m1:
		   		m2 = re.search('FILE: (.*\.lynx) URL', fline)
				if m2:
					doc=m2.group(1)
					m3 = re.search('.*URL: (.*) TOPICS.*', fline)
					if m3:
						url=m3.group(1)
						loc=[pi,domain,doc,url]
						if loc 	not in docs:
							docs.append(loc)



	########################################################
	# For each document identified as potentially relevant,
	# get a score against user query
	########################################################

	for doc in docs:					
		pagescore=0.0
		bestSentence=""
		bestSentenceScore=0.0
		numSentences=0
		
		for dline in open(pears_home+doc[0]+"/"+doc[1]+"/pages/"+doc[2]):
			m3 = re.search('<BOW>',dline)
			if m3:
				scoreWO=0.0
				numSentences+=1
				dline=dline.replace('<BOW>','')
				dline=dline.replace('</BOW>','')
				dlinewords=dline.split()		#Find BOW representation of sentence
  
				for qw in querywords:
					for w in dlinewords:
						if w == qw:
							scoreWO+=1
							break
				scoreWO = scoreWO / querylength		#Sentence score is proportional to how many words from the query are contained in the sentence
				if scoreWO > bestSentenceScore:
					bestSentence=dline		#Record most relevant sentence for that document, for display in the results
					bestSentenceScore=scoreWO
				pagescore+=scoreWO
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
			duckquery+=w+"+"
		webbrowser.open_new_tab("https://duckduckgo.com/?q="+duckquery)

	return results

if __name__ == '__main__':
    # test1.py executed as script
    runScript()
