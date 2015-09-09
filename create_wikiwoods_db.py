#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app.models import WikiWoods
from app import db

def create_wikiwoods_db():
    db.drop_all(bind='wikiwoods')
    db.create_all(bind='wikiwoods')
    with open(os.path.join(os.path.dirname(__file__), "wikiwoods.dm")) as f:
        dmlines = f.readlines()
        f.close()

    for l in dmlines:
        wikiwoods = WikiWoods()
        items = l.rstrip('\n').split('\t')
        wikiwoods.word = unicode(items[0], "utf-8")
        wikiwoods.vector = ",".join(items[1:])
        db.session.add(wikiwoods)
        db.session.commit()

    print "Successfully created db"


if __name__ == '__main__':
    create_wikiwoods_db()


