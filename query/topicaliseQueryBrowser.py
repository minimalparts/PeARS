################################################################
#topicaliseQueryBrowser.py
#USAGE: to be called by mkQueryPage.py when user enters a query
################################################################

from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from operator import itemgetter, attrgetter
import subprocess
import sys
import re
import os
import time

#Timing function, just to know how long things take
def print_timing(func):
	def wrapper(*arg):
		t1 = time.time()
		res = func(*arg)
		t2 = time.time()
		print '%s in topicaliseQueryBrowser took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
		return res
	return wrapper

# The @ decorator before the function invokes print_timing()
@print_timing

##############################################
#Main function, called by mkQueryPage.py
##############################################

def runScript(query):
	#load a semantic space
	my_space = io_utils.load("bnc.ppmi.nmf_300.pkl")

	#Remove any old pi-topics file in the directory
	if os.path.exists("pi-topics.tmp"):
		os.remove("pi-topics.tmp")

	topic_scores=[]		#Initialise topic_scores, a liste to record the scores allocated to each topic in topic-keys file
	#weightWO=3		#Weight for word ovelap score

	#Load rows of space (words for which a distribution is available)
	rows = open( "bnc.rows", "r" )
	dists = []
	for l in rows:
		l=l.rstrip('\n')
		dists.append(l)
	rows.close()

	#Open topic-keys file
	TKfile = open( "topic.keys", "r" )

	querytmp = open( "query.tmp", "w" )	#Hack to make sure encoding from web.py is ok: first write query to a file, then read it
	querytmp.write(query)
	querytmp.close()
	q=open("query.tmp", "r")
	query=q.readline()
	query = query.rstrip('\n')
        q.close()

	##########################################################
	#Lemmatise query by calling POS tagger server on port 2020
	##########################################################

	querywords=[]

	#Call POS tagger
	query2lemma = query.replace(" ","+")
	subprocess.call('wget -O query.lemmas http://localhost:2020/?'+query2lemma, shell=True)

	#Process result of POS tagger
	QLfile = open( "query.lemmas", "r" )
	sn=0	#Record sentence number. We're only interested in sentence 2
	querylemmas=""
	for l in QLfile:
		if "HTTP/" in l:
			break
		if sn == 2 and ">+<" not in l:
			m1=re.search('lemma=\"(\S+)\"',l)	
			m2=re.search('pos=\"(.)',l)
			if m1 and m2:
				lemma=m1.group(1)+"_"+m2.group(1)
				querywords.append(lemma)
				querylemmas=querylemmas+m1.group(1)+"_"+m2.group(1)+" "
		if re.search("^.sentence",l):
			sn+=1
	QLfile.close()
	querylength = len(querywords)

	#Write lemmas to query.tmp file
	querytmp = open( "query.tmp", "w" )
	querytmp.write(querylemmas.rstrip())
	querytmp.close()

		
	#############################################################
	#Calculate score for each topic in relation to the user query
	#############################################################
	
	for l in TKfile:
		scoreWO = 0.0		#Initialise score for word overlap
		scoreSIM = 0.0		#Initialise score for similarity
		numPairs = 0.0		#Initialise number of word pairs processed for similarity

		l=l.rstrip('\n')
		words =  l.split()
		
		#Get score by word overlap
		for w in words:
			for qw in querywords:
				if w == qw:
					scoreWO+=1
		scoreWO = scoreWO / querylength

		#Get score by similarity
		for w in words:
			if w in dists:
				for qw in querywords:
					if qw in dists:
						#compute similarity between two words in the space
						sim = my_space.get_sim(w, qw, CosSimilarity())
						scoreSIM += sim
						numPairs += 1
		if numPairs > 0:
			scoreSIM = scoreSIM / numPairs
		overallScore=scoreWO+scoreSIM		#Overall score is simply the word overlap and similarity scores added together
		topic_score = (overallScore,l)
		topic_scores.append(topic_score)



	###################################################
	#Sort scores and output n best topics
	###################################################

	#Sort all scores
	topic_scores_sorted=sorted(topic_scores, key=itemgetter(0), reverse=True)
	#List of useful pears
	pears=[]

	#Print best 3 topics
	c=0
	for ts in topic_scores_sorted:
		if c < 3:
			pear = ""
			topic = ""
			m = re.search('^([^:]*): .*', ts[1])		#Find pear ID
			if m:
				pear = m.group(1)
			m = re.search('^[^:]*: (\S+-[0-9]+) ', ts[1])	#Find topic ID
			if m:
				topic = m.group(1)
			if pear not in pears:
				pears.append(pear)
			#print pear,topic
			pearstmp = open( "pi-topics.tmp", "a" )		#Output pear/topic pair to pi-topics.tmp file
			pearstmp.write(pear+" "+topic+"\n")
			pearstmp.close()
			c+=1
		else:
			break


	#Output string of helpful pears
	r=""
	pcount=1				#Counter to prevent comma at the end of string
	for pear in pears:
		if pcount != len(pears):
			r=r+pear+","	
			pcount+=1
		else:
			r=r+pear
	return r



if __name__ == '__main__':
    # when executing as script
    runScript()
