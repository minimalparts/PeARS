#similarity.py
#USAGE: python similarity [space file] [word1] [word2]
#EXAMPLE: python kneighbours ~/UkWac/dissect/ANs/ANs.kpl car_n dog_n
#-------
from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
from operator import itemgetter, attrgetter
import webbrowser
import sys
import re



#load a semantic space
#my_space = io_utils.load(sys.argv[1])

PTfile = open( "pi-topics.tmp", "r" )	#Open pi-topic file
Qfile = open("query.tmp", "r") 		#Open query file

#Get user search
query=Qfile.readline().rstrip('\n')
querywords=query.split()
#querywords=["financial","crisis"]
querylength=len(querywords)

scores = []	#Initialise score
docs = []	#Initialise docs

for l in PTfile:
	l=l.rstrip('\n')
	#print l
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
	#print "TOPIC: ",topic,"DOMAIN: ",domain
	piaddress="/home/aurelie/PEARS/"+pi+"/"+domain+"/"
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
					if loc not in docs:
						docs.append(loc)
						#print pi,domain,doc,url

for doc in docs:
	pagescore=0.0
	bestSentence=""
	bestSentenceScore=0.0
	numSentences=0
	#print "Opening "+doc[0]+"..."+doc[1]+"..."+doc[2]+"..."+doc[3]
	for dline in open("/home/aurelie/PEARS/"+doc[0]+"/"+doc[1]+"/pages/"+doc[2]):
		m3 = re.search('<BOW>',dline)
		if m3:
			numSentences+=1
			dline=dline.replace('<BOW>','')
			dline=dline.replace('</BOW>','')
			dlinewords=dline.split()
				#Get score by word overlap
			scoreWO=0.0
			for qw in querywords:
				for w in dlinewords:
#					m4=re.search('(.*)_[A-Z]',w)
#					if m4:
#						w=m4.group(1).lower()
					#print w,qw,scoreWO,querylength,numSentences
					if w == qw:
						scoreWO+=1
						break
			scoreWO = scoreWO / querylength
			pagescore+=scoreWO
			if scoreWO > bestSentenceScore:
				bestSentence=dline
				bestSentenceScore=scoreWO
				#print "New best sentence: "+bestSentence
        if numSentences > 0:
		pagescore = pagescore / numSentences
	#print m3.group(1),pagescore,bestSentence
	if pagescore > 0:
		doc_score=[doc[3],pagescore,bestSentence]
		scores.append(doc_score)

if len(scores) > 0:
	scores_sorted=sorted(scores, key=itemgetter(1), reverse=True)
	for s in scores_sorted:
		#print s[0],s[1],s[2]
		print s[0]
		sys.stdout.flush()
		for w in querywords:
			#print ":"+w+":"
			m = re.search('.*?((\S+.\S ){0,3}%s (\S+.\S ){0,3}).*?'%w, s[2], re.IGNORECASE)
			if m:
				print m.group(1)
				sys.stdout.flush()
else:
	duckquery=""
	for w in querywords:
		duckquery+=w+"+"
	webbrowser.open_new_tab("https://duckduckgo.com/?q="+duckquery)
