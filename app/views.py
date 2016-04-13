#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request
from app import app, db
import findBestPears
import scorePages
import os
import sys
reload(sys)
from .utils import readPears, mkQueryDist, loadEntropies
#from lemmatise import lemmatiseQuery
#from forms import SearchForm
sys.setdefaultencoding("utf-8")


@app.route('/')
@app.route('/index')
def index():
    pages = []
    entropies_dict=loadEntropies()
    query = request.args.get('q')
    if not query:
        return render_template("index.html")
    else:
        #lemmatised_query = lemmatiseQuery(query)
	query_dist=mkQueryDist(query,entropies_dict)
	pears_ids = readPears()
        pears = findBestPears.runScript(query_dist,pears_ids)
        if len(pears) == 0:
            pears = [['nopear',
                      'Sorry... no pears found :(',
                      './static/pi-pic.png']]
            print pears
	else:
		pear_names = []
		for p in pears:
		    	pear_names.append(p[0])
		    	print p
			pages = scorePages.runScript(query,query_dist,pear_names)


        #'''remove the following lines after testing'''
        #pages = [['http://test.com', 'test']]

        return render_template('results.html', pears=pears,
                               query=query, results=pages)
