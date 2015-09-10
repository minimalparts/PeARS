import textblob_aptagger
from textblob import TextBlob, Word
#########################################
# Start POS tagger
#########################################

pt = textblob_aptagger.PerceptronTagger()

#######################################
# Tag query
#######################################


def tagQuery(query):
    taggedquery = ""
    try:
        tags = pt.tag(query)
        if len(tags) > 0:
            for word in tags:
                surface = word[0]
                pos = word[1]
#				print word
                try:
                    if pos[0] == 'N' or pos[0] == 'V':
                        tag = Word(surface).lemmatize(
                            pos[0].lower()) + "_" + pos[0]
                    else:
                        if pos[0] == 'J':
                            # Hack -- convert pos J to pos A because that's how
                            # adjectives are represented in dm file
                            tag = Word(surface).lemmatize().lower() + "_A"
                        else:
                            tag = Word(surface).lemmatize(
                            ).lower() + "_" + pos[0]
                    taggedquery = taggedquery + tag + " "
                except:
                    taggedquery = taggedquery + surface + "_" + pos[0] + " "
    except:
        print "ERROR processing query", query
    return taggedquery
