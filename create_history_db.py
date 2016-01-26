# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
from os.path import exists
from urlparse import urlparse


def create_history_db(input_db):

    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    home_directory = os.path.expanduser('~')
    os.walk(home_directory)
    pearsignore = str(home_directory) + '/.pearsignore'
    f = open(pearsignore, 'r')

    firefox_history_db = input_db
    if firefox_history_db is None:
        print 'Cannot find Firefox history database...\n\nExiting...'
        sys.exit(2)

    # Connect to the firefox history database
    firefox_con = sqlite3.connect(firefox_history_db)

    # Create the history.db file if it does not exist
    if not exists('history.db'):
        new_db = os.open('history.db', flags)
        os.close(new_db)

    history_con = sqlite3.connect('history.db')

    with firefox_con:
        firefox_con.row_factory = sqlite3.Row
        cur = firefox_con.cursor()
        cur.execute("SELECT * FROM moz_places")
        rows = cur.fetchall()

        history_cur = history_con.cursor()
        history_cur.execute("DROP TABLE IF EXISTS History")
        history_cur.execute("CREATE TABLE History(Id INTEGER PRIMARY KEY, URL TEXT, TITLE TEXT, BODY TEXT)")

        # Get a list of the values from the .pearsignore file in the home directory
        exclude_list = f.readline().split(',')
        print exclude_list

        for row in rows:
            exclude_flag = False
            url = row['url']
            # Check to make sure input is a valid url
            u = urlparse(url)
            if u.scheme == 'https' or 'http':
                # Check the exclude list to see if contained in the url
                for excludes in exclude_list:
                    if excludes in u.netloc:
                        exclude_flag = True
                        print url + ' OMITTED FROM DATABASE'
                        continue
                # Commit valid url
                if exclude_flag is False:
                    history_cur.execute("INSERT INTO History(URL) VALUES (?)", (url, ))
                    history_con.commit()

    history_con.close()
    firefox_con.close()






