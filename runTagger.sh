#runTagger.sh calls the Stanford tagger
#USAGE: ./runTagger.sh [full path of file to tag] [full path of output file]
#EXAMPLE: ./runTagger.sh /home/aurelie/PeARS/fileToTag.txt /home/aurelie/PeARS/output.txt

cd /home/aurelie/stanford-postagger-2014-06-16/
java -mx300m -classpath stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTagger -model models/english-left3words-distsim.tagger -textFile $1  -outputFormatOptions lemmatize -outputFormat inlineXML > $2
