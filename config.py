#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# db configurations - not using now
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_BINDS = {
    'wikiwoods':      'sqlite:///' + os.path.join(basedir, 'wikiwoods.db')
}
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
CSRF_ENABLED = True
SECRET_KEY='parayan-manasilla'
