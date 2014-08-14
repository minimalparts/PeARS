#similarity.py
#USAGE: python similarity [space file] [word1] [word2]
#EXAMPLE: python kneighbours ~/UkWac/dissect/ANs/ANs.kpl car_n dog_n
#-------
from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from operator import itemgetter, attrgetter
import subprocess
import time
import sys
import re
import os

t1=time.time()

if os.path.exists("pi-topics.tmp"):
	os.remove("pi-topics.tmp")

topic_scores=[]
#weightWO=3	#Weight for word ovelap score

t2=time.time()
print 't before loading semantic space:  %0.3f' % ((t2-t1)*1000)
#load a semantic space
my_space = io_utils.load(sys.argv[1])
t3=time.time()
print 't after loading semantic space: %0.3f' % ((t3-t2)*1000)

#Load rows of space (words for which a distribution is available)
rows = open( "bnc.rows", "r" )
dists = []
for l in rows:
	l=l.rstrip('\n')
	dists.append(l)
rows.close()

#Open topic-keys file
TQfile = open( "topic.keys", "r" )

#Get user search
#query = raw_input("search: ").lower()

#query = query.rstrip('\n')
query="financial crisis"
#query="financial_J crisis_N"
#querywords = query.split()
#querywords = ["cat"]


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


for l in TQfile:
	#t41=time.time()
	scoreWO = 0.0		#Initialise score for word overlap
	scoreSIM = 0.0		#Initialise score for similarity
	numPairs = 0.0		#Initialise number of word pairs processed for similarity

	l=l.rstrip('\n')
	#print l
	words =  l.split()
	
	#Get score by word overlap
	for w in words:
		for qw in querywords:
			if w == qw:
				scoreWO+=1
	scoreWO = scoreWO / querylength
	#t42=time.time()
	#print 't after score by overlap: %0.3f' % ((t42-t41)*1000)

	#Get score by similarity
	for w in words:
		if w in dists:
			for qw in querywords:
				if qw in dists:
					#compute similarity between two words in the space
					sim = my_space.get_sim(w, qw, CosSimilarity())
					#print w,qw,sim
					scoreSIM += sim
					numPairs += 1
	if numPairs > 0:
		scoreSIM = scoreSIM / numPairs
	#t43=time.time()
	#print 't after score by similarity: %0.3f' % ((t43-t42)*1000)
	

	#overallScore=weightWO*scoreWO+scoreSIM		#scoreWO is potentially more important so get weighted
	overallScore=scoreWO+scoreSIM	
	#print scoreWO,scoreSIM,overallScore
	#print "---"
	topic_score = (overallScore,l)
	topic_scores.append(topic_score)


t5=time.time()
print 't after main loop: %0.3f' % ((t5-t3)*1000)

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
		m = re.search('^([^:]*): .*', ts[1])
		if m:
			pear = m.group(1)
		m = re.search('^[^:]*: (\S+-[0-9]+) ', ts[1])
		if m:
			topic = m.group(1)
		pear_topic=[pear,topic]
		#pears.append(pear_topic)
		#print pear,topic
		pearstmp = open( "pi-topics.tmp", "a" )
		pearstmp.write(pear+" "+topic+"\n")
		pearstmp.close()
		
		#print ts[0],ts[1]
		c+=1
	else:
		break
