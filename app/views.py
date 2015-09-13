#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request
from app import app, db
import findBestPears
import scorePages
import os
import sys
reload(sys)
from lemmatise import lemmatiseQuery
sys.setdefaultencoding("utf-8")

#from forms import SearchForm



@app.route('/')
@app.route('/index')
def index():
    query = request.args.get('q')
    if not query:
        return render_template("index.html")
    else:

        lemmatised_query = lemmatiseQuery(query)
        pears = findBestPears.runScript(lemmatised_query)
        pear_names = []
        for p in pears:
            pear_names.append(p[0])
            print p
        pages = scorePages.runScript(pear_names, lemmatised_query)
        if len(pears) == 0:
            pears = [['nopear',
                      'Sorry... no pears found :(',
                      './static/pi-pic.png']]
            print pears

        #'''remove the following lines after testing'''
        #pages = [['http://test.com', 'test']]

        return render_template('results.html', pears=pears,
                               query=query, results=pages)
