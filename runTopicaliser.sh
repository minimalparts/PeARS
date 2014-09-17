#runTopicaliser.sh calls the MALLET topicalisation tool
#USAGE: ./runTopicaliser.sh [name of directory with files to process (should be located in data/)] [number of topics required]
#EXAMPLE: ./runTopicaliser.sh wikipedia

cd /home/aurelie/mallet-2.0.7

dir=$1
numtopics=$2

bin/mallet import-dir --input data/$dir/ --output $dir.mallet --keep-sequence --remove-stopwords
bin/mallet train-topics --input $dir.mallet   --num-topics $numtopics --output-state topic-state.gz   --output-doc-topics $dir.doc.topics   --output-topic-keys $dir.topic.keys
