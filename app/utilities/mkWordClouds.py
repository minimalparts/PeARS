#Make word cloud from positional index for a given pear
#The index has the form
#word,word_freq:doc1,freq_in_doc1(pos1,pos2,...posn);doc2,freq_in_doc2(pos1,pos2,...posn), etc
#to,993427:23,2(3,6);35,1(34)

import sys
import os
import re
import math
import operator

path_to_PeARS = os.path.dirname(__file__)
index={}		#This is the positional index, of the form word:WordEntry
document_names=[]	#This is a temporary vector holding single document names
tfidfs={}
word_clouds={}

#WordEntry contains all the information pertaining to a word
#(freq, docs in which it appears)
class WordEntry:
     def __init__(self, freq):
         self.freq=freq
	 self.docs=[]


#Load existing index file
def load_index(path_to_index):
	index_file=open(path_to_index)
	for line in index_file:
		try:
			line=line.rstrip('\n')
			pair=line.split(':')
			word_freq=pair[0].split(',')
			word=word_freq[0]
			freq=int(word_freq[1])
			index[word]=WordEntry(freq)

			docs=pair[1].rstrip(';')	#Remove last ; before splitting
			docs=docs.split(';')
			for d in docs:
				name=d.split(',')[0]
				if name not in document_names:
					document_names.append(name)
				m=re.search(',([0-9]+)',d)
				dfreq=0
				if m:
					dfreq_str=m.group(1)
					dfreq=int(dfreq_str)
				#print name,dfreq
				m=re.search(',[0-9]+\[(.*)\]',d)
				positions=[]
				if m:
					positions_strings=m.group(1).split(", ")
					#print positions_strings
					positions=[]
					for p in positions_strings:
						intp=int(p)
						positions.append(intp)
				index[word].docs.append([name,dfreq,positions])
		except:
			#print "ERROR processing",line
			continue

def calculateTFIDF():
	for k,v in index.items():
		word=k
		documents=v.docs

		idf=math.log(len(document_names)/len(v.docs))
		for d in documents:
			doc_name=d[0]+".txt"
			tf=d[1]
			tfidf=tf*idf

			if doc_name in tfidfs:
				tfidfs[doc_name][word]=tfidf
			else:
				tfidfs[doc_name]={}			#Declare dictionary word-tfidf
				tfidfs[doc_name][word]=tfidf
#			print doc_name,str(tfidf),word


def computeWordClouds():
	non_alpha = re.compile('[\W_]+')                                        #non-alpha characters   
	for doc_name,tfidf_dict in tfidfs.items():
		cloud=""
		c=0
		for k,v in sorted(tfidf_dict.items(), key=operator.itemgetter(1), reverse=True):
			if c > 9:
				break
			else:
				m=re.search("_N|_V|_A",k)
				if m:
                                        word=k[0:-2]
                                        m2=non_alpha.search(word)
                                        if not m2 and word.lower() not in cloud.lower():                #if word alphanumeric and is not already in cloud
                                                cloud=cloud+word+" "
                                                c+=1
		cloud.rstrip(' ')
		word_clouds[doc_name]=cloud




def writeWordClouds(path_to_clouds):
	out=open(path_to_clouds,'w')
	for k,v in word_clouds.items():
#		print k,v
		line=k+":"+v
		out.write(line+'\n')


def runScript(pear):
	index.clear()

	path_to_index=os.path.join(path_to_PeARS, pear+"/index.txt")
	path_to_clouds=os.path.join(path_to_PeARS, pear+"/wordclouds.txt")
	if os.path.exists(path_to_index):
		load_index(path_to_index)
		calculateTFIDF()
		computeWordClouds()
		writeWordClouds(path_to_clouds)
	else:
		print "ERROR: index file does not exist. Bye."

# when executing as script
if __name__ == '__main__':
    runScript(sys.argv[1])	#Input pear
