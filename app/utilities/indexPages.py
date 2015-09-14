############################################################
# indexPages.py takes a file with urls and indexes the
# corresponding pages on a particular pear (local folder, )
# which can then be transferred to a web server.
############################################################

import sys
import os
import re
import shutil
import subprocess
import runTextBlobTagger
import mkPositionalIndex
import runDistSem
import mkWordClouds
from os import listdir

path_to_PeARS=os.path.dirname(__file__)
url_dict={}		#Initialise a URL dictionary
reverse_url_dict={}	#Reverse URL dictionary, just for the purpose of indexing
new_files_ids=[]	#A holder for the new pages being processed, expressed as an ID number on the pear


#############################################################
# Load existing url dictionary
#############################################################

def loadURLs(pear):
	print "Loading URL dictionary for",pear
	path_to_dict=os.path.join(path_to_PeARS, pear+"/urls.dict.txt")

	if os.path.exists(path_to_dict):
		d=open(path_to_dict,'r')
		for line in d:
			line=line.rstrip('\n')
			idfile=line.split()[0]
			url=line.split()[1]
			url_dict[url]=idfile		#Record the pairs url - file name on pear
		d.close()


#############################################################
# Print updated url dictionary
#############################################################

def printURLs(pear):
	print "Printing/updating URL dictionary for",pear
	path_to_dict=os.path.join(path_to_PeARS, pear+"/urls.dict.txt")

	d=open(path_to_dict,'w')
	for k,v in url_dict.items():
		line=v+" "+k
		d.write(line+'\n')
	d.close()

#############################################################
# Grab pages in input file using the text-only browser lynx
#############################################################

def lynx(pages_file,pear):
	print "Lynxing pages..."

	c = len(url_dict)	#Initialise counter to number of existing files on that pear

	pages = open(pages_file,'r')

	for url in pages:
		url=url.rstrip('\n')
		if url not in url_dict:		#Don't lynx again a page that is available already on that pear
			command = "lynx -dump -nolist "+url
			print "Executing",command
			t = open("lynx.tmp",'w')
			lynx_url=url.replace("(","\(").replace(")","\)")
			subprocess.call(["lynx","-dump", "-nolist", lynx_url], stdout=t)
			t.close()
			file_id=str(c)+".txt"
			lynxfile = open (os.path.join(path_to_PeARS, pear+"/originals/"+file_id),'w')
			lynxfile.write("### "+url+'\n')	#Record URL of the page
			url_dict[url]=file_id	#Record URL - pear file id pair
			reverse_url_dict[file_id]=url	#Record file id - url pair, to be used in indexing function
			new_files_ids.append(file_id)

			lynxtmp = open (os.path.join(path_to_PeARS, "lynx.tmp"),'r')
			for lynxline in lynxtmp:
				regex="[0-9]*\. http"
				if not re.search(regex,lynxline):	#Don't include lynx 'footnotes' with links
					cleanline=re.sub(r"\[.+\]", "", lynxline)
					lynxfile.write(cleanline)
			lynxfile.close()
			os.remove(os.path.join(path_to_PeARS, "lynx.tmp"))
			c+=1

	pages.close()

#########################################################
# Tag pages for that domain using runTextBlobTagger.py
#########################################################


def postag(pear):
	print "POS-tagging pages..."

	for file_id in new_files_ids:
		lynx_file=os.path.join(path_to_PeARS, pear+"/originals/"+file_id)
		lemmatised_file=os.path.join(path_to_PeARS, pear+"/lemmas/"+file_id)
		runTextBlobTagger.runScript(lynx_file,lemmatised_file)


#########################
# Update index for pear
#########################

def index(pear):
	print "Indexing pages on "+pear
	for file_id in new_files_ids:
#	for i in range(0,40):
#		file_id=str(i)+".txt"
		lemmatised_file=os.path.join(path_to_PeARS, pear+"/lemmas/"+file_id)
		mkPositionalIndex.runScript(lemmatised_file,pear)

##############################
# Run distributional semantics
##############################

def distsem(pear):
	print "Making distributional semantics representations on "+pear
	for file_id in new_files_ids:
		print "Processing file",file_id
		runDistSem.runScript(file_id,pear)

###########################################
# Update shared_pears_ids.txt file
###########################################

def update_shared_ids(pear):
	dist=""
	pear_profile=open(os.path.join(path_to_PeARS, pear+"/profile.txt"),"r")
	for l in pear_profile:
		l=l.rstrip('\n')
		m=re.search("^pear_id:",l)
		if m:
			dist=l.split(':')[1]
	pear_profile.close()

	pears_dists=[]
	pears_ids=open(os.path.join(path_to_PeARS, "shared_pears_ids.txt"),'r')
	for l in pears_ids:
		l=l.rstrip('\n')
		m=re.search(pear,l)
		if not m:
			pears_dists.append(l)
	pears_dists.append(pear+"|"+dist)
	pears_ids.close()

	pears_ids=open(os.path.join(path_to_PeARS, "shared_pears_ids.txt"),'w')
	for l in pears_dists:
		pears_ids.write(l+'\n')
	pears_ids.close()



###################
# Entry point
###################
def runScript(a1,a2):
	pages_file = a1 #File containing pages to be processed
	pear = a2 #The pear which will host these pages (local folder)

        if not os.path.isdir(os.path.join(path_to_PeARS, pear)):
            os.makedirs(os.path.join(path_to_PeARS, pear))
        if not os.path.exists(os.path.join(path_to_PeARS, "shared_pears_ids.txt")):
            open(os.path.join(path_to_PeARS, "shared_pears_ids.txt"),'w').close()
        if not os.path.isdir(os.path.join(path_to_PeARS, pear+"/originals")):
            os.makedirs(os.path.join(path_to_PeARS, pear+"/originals"))
        if not os.path.isdir(os.path.join(path_to_PeARS,pear+"/lemmas")):
            os.makedirs(os.path.join(path_to_PeARS, pear+"/lemmas"))
        if not os.path.isdir(os.path.join(path_to_PeARS, pear+"/distsem")):
            os.makedirs(os.path.join(path_to_PeARS, pear+"/distsem"))
        if not os.path.isdir(os.path.join(path_to_PeARS, pear+"/indexes")):
            os.makedirs(os.path.join(path_to_PeARS, pear+"/indexes"))
        if not os.path.exists(os.path.join(path_to_PeARS, pear+"/doc.dists.txt")):
            open(os.path.join(os.path.join(path_to_PeARS, pear+"/doc.dists.txt")),'w').close()		#Touch file if it doesn't exist
        if not os.path.exists(os.path.join(path_to_PeARS, pear+"/profile.txt")):
            profile=open(os.path.join(path_to_PeARS, pear+"/profile.txt"),'w')
            init_pear_id=""
            for i in range(300):
                init_pear_id+="0 "
            profile.write("name = "+pear+"\n")
            profile.write("message = Glad to help you with your search!"+"\n")
            profile.write("pear_id:"+init_pear_id+"\n")
            profile.close()

	loadURLs(pear)
	lynx(pages_file,pear)
	printURLs(pear)
	postag(pear)
	distsem(pear)
	index(pear)
	update_shared_ids(pear)
	mkWordClouds.runScript(pear)
	print "Finished! Thank you!"

if __name__ == '__main__':
	# when executing as script
	runScript(sys.argv[1],sys.argv[2])
