#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request
from app import app, db
import findBestPears
import scorePages
import textblob_aptagger
from textblob import TextBlob, Word
import web
from web import form
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#from forms import SearchForm

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


@app.route('/')
@app.route('/index')
def index():
    query = request.args.get('q')
    if not query:
        return render_template("index.html")
    else:

        taggedquery = tagQuery(query)
        pears = findBestPears.runScript(taggedquery)
        pear_names = []
        for p in pears:
            pear_names.append(p[0])
            print p
        pages = scorePages.runScript(pear_names, taggedquery)
        if len(pears) == 0:
            pears = [['nopear',
                      'Sorry... no pears found :(',
                      './static/pi-pic.png']]
            print pears

        #'''remove the following lines after testing'''
        #pages = [['http://test.com', 'test']]

        return render_template('results.html', pears=pears,
                               query=query, results=pages)
