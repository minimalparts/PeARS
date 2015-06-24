#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, request
from app import app, db
#from forms import SearchForm

@app.route('/')
@app.route('/index')
def index():
    return "Hrishi Loves Aiswarya"


