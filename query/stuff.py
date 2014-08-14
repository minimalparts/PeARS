#similarity.py
#USAGE: python similarity [space file] [word1] [word2]
#EXAMPLE: python kneighbours ~/UkWac/dissect/ANs/ANs.kpl car_n dog_n
#-------
from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
import sys
import re

def egrep(f,search_string):
	for line in open(f):
	 m = re.search(search_string, line)
	 if m:
	   print line


#load a semantic space
#my_space = io_utils.load(sys.argv[1])

PTfile = open( "pi-topics.tmp", "r" )	#Open pi-topic file

#Get user search

score = 0	#Initialise score

for l in PTfile:
	l=l.rstrip('\n')
	#print l
	words =  l.split()
	pi=words[0]
	topic=words[1]

	f="/home/aurelie/PEARS/"+pi+"/doc.topics.index"
	topic_search="TOPICS:.* "+topic+" |TOPICS:.* "+topic+"$"
	egrep(f,topic_search)

	for w in words:
		pos = ""
		m = re.search('.*_([A-Z])[A-Z]*$', w)
		if m:
			pos = m.group(1)
			if pos=='A' or pos=='V' or pos=='N':
				m = re.search('(.*_[A-Z])[A-Z]*$', w)
				if m:
					wordcoarsepos = m.group(1)
					#print wordcoarsepos
					
					for qw in querywords:
						#compute similarity between two words in the space
						sim = my_space.get_sim(wordcoarsepos, qw, CosSimilarity())
						score += sim
						numPairs += 1
score = score / numPairs
print score
