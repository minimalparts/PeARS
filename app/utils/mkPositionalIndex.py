#Make/update positional index for a given file
#The index has the form
#word,word_freq:doc1,freq_in_doc1(pos1,pos2,...posn);doc2,freq_in_doc2(pos1,pos2,...posn), etc
#to,993427:23,2(3,6);35,1(34)

import sys
import os
import re

path_to_PeARS = os.path.dirname(__file__)
index={}		#This is the positional index, of the form word:WordEntry
individual_index={}	#This is the positional index for the individual file
word_positions={}	#This is a temporary dictionary with positions for each word in the document being processed

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


##########################################
#Read new document
##########################################

def readWordPositions(input_file):
	c=0	#Initialise wordcount for this document

	f=open(input_file,'r')
	for line in f:
		line=line.rstrip('\n')
		words=line.split()

		for w in words:
			m=re.search('(.*_.).*',w)
			if m:
				w=m.group(1)
			c+=1
			if w not in word_positions:
				word_positions[w]=[c]
			else:
				word_positions[w].append(c)

def mkWordEntries(docname):
	for k,v in word_positions.items():
		#General index
		if k not in index:
			entry=WordEntry(len(v))
			entry.docs.append([docname,len(v),v])
			index[k]=entry
		else:
			entry=index[k]
			entry.freq+=len(v)
			entry.docs.append([docname,len(v),v])
			index[k]=entry
		#Individual index
		if k not in individual_index:
			entry=WordEntry(len(v))
			entry.docs.append([docname,len(v),v])
			individual_index[k]=entry
		else:
			entry=individual_index[k]
			entry.freq+=len(v)
			entry.docs.append([docname,len(v),v])
			individual_index[k]=entry

def writeIndex(path_to_index):
	out=open(path_to_index,'w')
	for k,v in index.items():
		line=k+","+str(v.freq)+":"
		for d in v.docs:
			line=line+d[0]+","+str(d[1])+str(d[2])+";"
		out.write(line+'\n')

def writeIndividualIndex(path_to_ind_index):
	out=open(path_to_ind_index,'w')
	for k,v in individual_index.items():
		line=k+","+str(v.freq)+":"
		for d in v.docs:
			line=line+d[0]+","+str(d[1])+str(d[2])+";"
		out.write(line+'\n')

def runScript(a1,a2):
	input_file=a1
	pear = a2 #The pear which will host these pages (local folder or Raspberry Pi)

	index.clear()
	individual_index.clear()
	word_positions.clear()

	if os.path.exists(input_file):
		path_to_index=os.path.join(path_to_PeARS, pear+"/index.txt")
		if os.path.exists(path_to_index):
			load_index(path_to_index)

		m=re.search(".*\/(.*)\.txt",input_file)
		docname=m.group(1)
		path_to_ind_index=os.path.join(path_to_PeARS, pear+"/indexes/"+docname+".txt")

		readWordPositions(input_file)
		mkWordEntries(docname)
		writeIndex(path_to_index)
		writeIndividualIndex(path_to_ind_index)
	else:
		print "ERROR: file",input_file,"does not exist. Bye."

# when executing as script
if __name__ == '__main__':
    runScript(sys.argv[1],sys.argv[2])	#Input file and pear
