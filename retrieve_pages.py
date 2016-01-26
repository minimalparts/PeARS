
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import platform
import re
import requests
import sqlite3
import sys
from urllib2 import HTTPError
from create_history_db import create_history_db

HISTORY_DB = ''

print platform.system(), platform.release()
home_directory = os.path.expanduser('~')
print home_directory


def get_firefox_history_db(in_dir):
    """Given a home directory it will search it for the places.sqlite file
    in Mozilla Firefox and return the path. This should work on Windows/Linux"""

    firefox_directory = in_dir + "/.mozilla/firefox"
    print firefox_directory
    for files in os.walk(firefox_directory):
        # Build the filename
        if re.search('places.sqlite', str(os.path.join(files))):
            history_db = str(os.path.realpath(files[0])+'/places.sqlite')
            print history_db
            return history_db

    return None

print HISTORY_DB


def retrieve_pages():
    con = sqlite3.connect('history.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM History;")
    rows = cur.fetchall()

    for row in rows:
        id = row["Id"]
        url = str(row['URL'])
        # url = str('http://www.ubuntu.com')

        if url.endswith(('.gz', '.zip', '.exe', '.pdf', '.jpeg', '.jpg', '.7z', '.iso', '.img', '.png', '.svg',
                         'mp4', '.mp3', 'ogg', '.avi', '.wma', '.wmv', '.gif', '.rpm', '.deb', '.mkv', '.rar',
                         '.m4a', '.tgz', '.tar', '.webm')):
            print url + ' is a binary - omitted from database'
            continue

        try:
            r = requests.get(url, allow_redirects=False)
            r.encoding = 'utf-8'
            print str(r.status_code) + ' - ' + str(r.url)
            if r.status_code is not 200:
                print str(r.url) + ' has a status code of: ' + str(r.status_code) + ' omitted from database.'
                continue
        except:
            e = sys.exc_info()[0]
            print "Error - %s" % e
            continue

        bs_obj = BeautifulSoup(r.text)
        if hasattr(bs_obj.title, 'string') & (r.status_code == requests.codes.ok):
            try:
                title = unicode(bs_obj.title.string)
                if url.startswith('http'):

                    if title is None:
                        title = u'Untitled'
                    for x in bs_obj.find_all(['script', 'style', 'meta', '<!--', ]):
                        x.extract()
                    body = bs_obj.get_text()
                    title_str = title
                    body_str = body.strip()
                    print body_str
                    cur.execute("UPDATE History SET title=?, body=? WHERE ID=?", (title_str, body_str, id), )
                    con.commit()
                    print str(r.status_code) + ' - ' + title + ' - Committed.'

                if title is None:
                    title = u'Untitled'
            except HTTPError as e:
                title = u'Untitled'
            except None:
                title = u'Untitled'
                continue
        else:
            continue

    con.close()


if __name__ == '__main__':

    HISTORY_DB = get_firefox_history_db(home_directory)
    if HISTORY_DB is None:
        print 'Error - Cannot find the Firefox history database.\n\nExiting...'
        sys.exit(1)

    # If the firefox history db exists we then want to create our own version from it, minus the domains specified in
    # the user's ~/.pearsignore.
    #
    if not HISTORY_DB:
        create_history_db(HISTORY_DB)

    retrieve_pages()
