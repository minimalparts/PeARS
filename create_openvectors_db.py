#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from app.models import OpenVectors
from app import db

def create_openvectors_db():
    db.drop_all(bind='openvectors')
    db.create_all(bind='openvectors')
    with open(os.path.join(os.path.dirname(__file__), "openvectors.dm")) as f:
        dmlines = f.readlines()
        f.close()

    for l in dmlines:
        openvectors = OpenVectors()
        items = l.rstrip('\n').split('\t')
        openvectors.word = unicode(items[0], "utf-8")
        openvectors.vector = ",".join(items[1:])
        db.session.add(openvectors)
        db.session.commit()

    print "Successfully created db"


if __name__ == '__main__':
    create_openvectors_db()


