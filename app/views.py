#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request
from app import app, db
import findBestPears
import scorePages
import textblob_aptagger
from textblob import TextBlob,Word
import web
from web import form
import os
#from forms import SearchForm

#########################################
# Start POS tagger
#########################################

pt=textblob_aptagger.PerceptronTagger()

#######################################
# Tag query
#######################################

def tagQuery(query):
    taggedquery=""
    try:
        tags=pt.tag(query)
        if len(tags) > 0:
            for word in tags:
                surface=word[0]
                pos=word[1]
#				print word
                try:
                    if pos[0] == 'N' or pos[0] == 'V':
                        tag=Word(surface).lemmatize(pos[0].lower())+"_"+pos[0]
                    else:
                        if pos[0] == 'J':
                            tag=Word(surface).lemmatize().lower()+"_A"		#Hack -- convert pos J to pos A because that's how adjectives are represented in dm file
                        else:
                            tag=Word(surface).lemmatize().lower()+"_"+pos[0]
                    taggedquery=taggedquery+tag+" "
                except:
                    taggedquery=taggedquery+surface+"_"+pos[0]+" "
    except:
        print "ERROR processing query",query
    return taggedquery



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/search', methods = ['POST'])
def search():
    query = request.form['q']
    #print pt.tag(query)
    taggedquery=tagQuery(query)
    #print taggedquery
    pears=findBestPears.runScript(taggedquery)
    #print "The best pears are: ",pears
    pear_names=[]
    for p in pears:
        pear_names.append(p[0])
    pages=scorePages.runScript(pear_names,taggedquery)

    if len(pears) == 0:						#When no results were found...
        pears=[['nopear','Sorry... no pears found :(','./static/pi-pic.png']]				#Hack to have something to display in the pears area of results page

    return render_template('results.html', pears=pears, query=query, results=pages)



