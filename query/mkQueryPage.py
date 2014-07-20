###################################################################
# ./mkQueryPage starts a web server to take and process user search
###################################################################



from composes.utils import io_utils
from composes.similarity.cos import CosSimilarity
import topicaliseQueryBrowser
import compareQuerySentenceBrowser
import subprocess
import web
from web import form


#########################################
# Start server for POS tagger on port 2020
#########################################

subprocess.call('nohup java -mx300m -classpath ~/stanford-postagger-2014-06-16/stanford-postagger.jar edu.stanford.nlp.tagger.maxent.MaxentTaggerServer -model ~/stanford-postagger-2014-06-16/models/english-left3words-distsim.tagger -outputFormatOptions lemmatize -outputFormat inlineXML -port 2020 >& /dev/null &', shell=True)


###############################
# Render search form
###############################


render = web.template.render('templates/')

urls = ('/', 'index')
app = web.application(urls, globals())

myform = form.Form( 
    form.Textbox("search", 
        form.notnull))

class index: 
    def GET(self): 
        form = myform()
        # make sure you create a copy of the form by calling it (line above)
        # Otherwise changes will appear globally
        return render.formtest(form)
    def POST(self): 
        form = myform() 
        if not form.validates(): 
            return render.formtest(form)
        else:
	    query=form['search'].value
	    pears=topicaliseQueryBrowser.runScript(query)
	    pages=compareQuerySentenceBrowser.runScript()
	    return render.results(pears,pages,query)

if __name__=="__main__":
    web.internalerror = web.debugerror
    app.run()
