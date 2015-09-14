from textblob import TextBlob, Word

#######################################
# Lemmatise query
#######################################

def lemmatiseQuery(query):
    lemmatised_query = ""
    for surface_word in query.split():
        try:
            lemma = Word(surface_word).lemmatize()
            lemmatised_query = lemmatised_query + lemma + " "
            lemma_verb = Word(surface_word).lemmatize('v')                              #Hack. Now we don't have POSs anymore, we must check whether the word might be an irregular verb ('was', 'would')
            if lemma_verb != lemma:
                lemmatised_query = lemmatised_query + lemma_verb + " "                  #Only include if different. So 'calls' (plural noun or 3.sing verb) would end up with just one mention
        except:
            lemmatised_query = lemmatised_query + surface_word + " "
        print lemmatised_query
    return lemmatised_query

