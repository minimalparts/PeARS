import sys
import os
import re
import subprocess
import shutil
from os import listdir
from socket import *

home="/home/aurelie/PeARS/"
mallet_path="/home/aurelie/mallet-2.0.7/"

domain = sys.argv[1] #beginning of domain name, *must* start as in history.pages, e.g. http://stackoverflow.com
dir = sys.argv[2] #how that domain will be referred to in the directory structure, e.g. stackoverflow




#################################
#Retrieve relevant history pages
#################################

if os.path.exists(home+dir+".log"):
	os.remove(home+dir+".log")

#Erase previous versions of this directory

if os.path.isdir(home+"domains/"+dir):
	shutil.rmtree(home+"domains/"+dir)
if os.path.isdir(home+"domains/"+dir+"-lemmas/"):
	shutil.rmtree(home+"domains/"+dir+"-lemmas/")
if os.path.isdir(home+"domains/"+dir+"-pagereps/"):
	shutil.rmtree(home+"domains/"+dir+"-pagereps/")

#If no domains directory exists, create one

if not os.path.isdir(home+"domains/"):
	os.makedirs(home+"domains/")

print "Hi! Creating page representations, topics and index for domain",dir,"!"

with open("history.pages") as f:
    history = f.readlines()
f.close()

domainpages = open (home+"domains/"+dir+".pages",'w')

for line in history:
	regex="^"+domain
	if re.search(regex, line):
		domainpages.write(line)


#Use the following if you have a file with a list of domain names. 'domain' is then the name of the file, 'dir' the name you chose for that group of files

#domains = open(home+domain,'r')
#for domline in domains:
#	regex="^"+domline.rstrip('\n')
#	print regex
#	for line in history:
#		if re.search(regex, line):
#			print line
#			domainpages.write(line)

domainpages.close()

log = open (home+dir+".log",'w')

#############################################################
# Grab pages for that domain using the text-only browser lynx
#############################################################

print "Lynxing pages..."

os.makedirs(home+"domains/"+dir)
os.makedirs(home+"domains/"+dir+"-lemmas")

c = 0	#Initialise counter

domainpages = open(home+"domains/"+dir+".pages",'r')

for line in domainpages:
	log.write("Lynxing "+line.rstrip('\n')+"...\n")
	
	command = "lynx -dump "+line
	print "Executing",command
	t = open("lynx.tmp",'w')
	subprocess.call(["lynx","-dump", line], stdout=t)
	t.close()
	lynxfile = open (home+"domains/"+dir+"/"+str(c)+".lynx",'w')
	lynxfile.write("### "+line)	#Record URL of the page

	lynxtmp = open (home+"lynx.tmp",'r')
	for lynxline in lynxtmp:
		regex="[0-9]*\. http"
		if not re.search(regex,lynxline):	#Don't include lynx 'footnotes' with links
			cleanline=re.sub(r"\[.+\]", "", lynxline)			
			lynxfile.write(cleanline)
	lynxfile.close()
	os.remove(home+"lynx.tmp")
	c+=1

domainpages.close()

#########################################################
# Tag pages for that domain using the stanford POS tagger
#########################################################

print "POS-tagging pages..."
for f in listdir(home+"domains/"+dir+"/"):
	flemmas=open(home+"domains/"+dir+"-lemmas/"+f,'w')

	log.write("POS-tagging "+f+"...")
	
	postagtmp=open("postag.tmp",'w')
	
	#Delete first line of file + record url
	c = 0
	url = ""
	flines=open(home+"domains/"+dir+"/"+f,'r')
	for line in flines:
		if c > 0:
			postagtmp.write(line)
		else:
			url=line
			flemmas.write(url)
		c+=1	

	postagtmp.close()

	fileIn=home+"postag.tmp"
	fileOut=home+"tagger.out"
	command="./runTagger.sh "+fileIn+" "+fileOut
	#print command
	subprocess.call(command, shell=True)


	taggedfile=open("tagger.out",'r')
	for line in taggedfile:
		regex="pos.*lemma"
		if re.search(regex,line):
			m=re.search('pos=.([^\"]*). lemma=.([^\"]*)',line)	#Process lines to get words_POS output format
			if m:
				pos=m.group(1)
				lemma=m.group(2)
				flemmas.write(lemma+"_"+pos+" ")
		regex="<.sentence"
		if re.search(regex,line):
			flemmas.write('\n')	#One sentence per line
				
	taggedfile.close()

	flemmas.close()

os.remove(home+"postag.tmp")


############################
#Topic modelling with MALLET
############################

print "Topic modelling..."

if not os.path.isdir(mallet_path+"data/"):
	os.makedirs(mallet_path+"data/")

if not os.path.isdir(mallet_path+"data/"+dir):
	os.makedirs(mallet_path+"data/"+dir)


numpages = 0

for f in listdir(home+"domains/"+dir+"-lemmas/"):
	flemmas= open(home+"domains/"+dir+"-lemmas/"+f)
	mallet_file=open(mallet_path+"data/"+dir+"/"+f,'w')

	c = 0
	for line in flemmas:
		if c == 0:
			mallet_file.write(line)
		else:
			line=re.sub(r"_(.)[^ ]*", r"-\1", line)	#Only retain first letter of POS tag
			mallet_file.write(line)
		c+=1
			

	mallet_file.close()
	flemmas.close()
	
	numpages+=1

numtopics = int(numpages / 10) + 1	#Number of topics, roughly a tenth of the number of pages for that domain. +1 in case numpages < 10
	
command="./runTopicaliser.sh "+dir+" "+str(numtopics)
#print command
subprocess.call(command, shell=True)


##########################
#Produce topic-page index
##########################

print "Building topic-page index..."

doctopics=open(mallet_path+dir+".doc.topics",'r')
topicpageindex=open(mallet_path+dir+".doc.topics.index",'w')

c=0
url=""
for line in doctopics:
	if c > 0:						#Skip first line of file
		m=re.search('file:(\S*)\s',line)	
		if m:
			f=m.group(1)				#Record file path
			flines=open(f,'r')
			c2=0
			for l in flines:
				if c2 ==0:
					url=l.rstrip('\n')			#Record URL
					url=url.replace(r'### ','')
					c2+=1
				else:
					break
			flines.close()
		m=re.search('file:\S*/([0-9]*\.lynx)',line)
		if m:
			fn=m.group(1)				#Record file name, e.g. 14.lynx

		m=re.search('\.lynx\s([0-9]\s[0-9]\..*)',line)
		if m:
			topics=m.group(1)
			topics=re.sub(r"\s+[0-9]\.[0-9]+\s+", " ", topics)	#Get rid of probabilities for each topic		
			topics=re.sub(r"\s+$", "", topics)	#Get rid of final space
			topics=topics.split(' ')
			topicnumber=5				#Keep 5 best topics for each document
			if len(topics) < topicnumber:		#In case document has less than 5 topics
				topicnumber=len(topics)
			topicsline=""
			for c2 in range(topicnumber):
				topicsline=topicsline+topics[c2]+" "
			topicpageindex.write("FILE: "+fn+" URL: "+url+" TOPICS: "+topicsline+"\n")

	c+=1

doctopics.close()
topicpageindex.close()


#########################
# Run page representation
#########################

print "Making page representations..."
command="python "+home+"mkPageRepresentations.py"+" "+dir
subprocess.call(command, shell=True)

print "Finished! Thank you!"
