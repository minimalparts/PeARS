# PeARS

##What is PeARS?


PeARS (Peer-to-peer Agent for Reciprocated Search) is a lightweight, distributed search engine. It relies on people going about their normal business and browsing the web. While they do so, the pages they visit are indexed in the background, and assigned a ‘meaning’ (is this page about cats, fashion, ancient history, Python programming?, etc). From time to time, they can choose to share some or all of these meanings with others, providing the building stones of a giant search engine network, distributed across people. By linking page meanings with real people doing real browsing, PeARS ensures that the nodes in the network are topically coherent: an individual interested in architecture will probably have indexed a lot of web pages on associated topics, providing a potentially relevant cluster for someone with a query on, say, the German ‘Bauhaus’ movement.


To know more head over to: <a href="http://aurelieherbelot.net/pears/">http://aurelieherbelot.net/pears/</a>

##Set up
>This is mostly a development setup since we not really production ready yet. You can find a demo of PeARS running over here: http://pearsearch.herokuapp.com/

###Clone this repo

`git clone -b development git@github.com:minimalparts/PeARS.git`

`cd PeARS`


###Set up the development environment

1. <b>Set up virtualenv</b>
    >We recommend using virtualenv for the development. If you are just here for test it out, skip to the next section.

    **Install pip using easy_install**

    `sudo easy_install pip`

    or some other way your distribution supports like:

    `sudo yum install python-pip`


    **Install virtualenv using pip**


    `sudo pip install virtualenv`


    **Create a new virtualenv for PeARS and activate it**


    `virtualenv pears_env && source pears_env/bin/activate`


2. <b>Install the build dependencies</b>

    >We recommend using pip for installation. In case you don't have this, look inside requirements.txt and install dependencies manually.

    `pip install -r requirements.txt`

    Run the following in case you are having any issues while running

    `python -m textblob.download_corpora lite`


###Running the PeARS search engine


In the root directory of the repo, run

`python run.py`

Go to the browser and type localhost:5000. You should find PeARS running there.




####That's it, folks!

Please [report](https://github.com/minimalparts/PeARS/issues) to us any issues that you face.


###More links:

[Code Overview](https://github.com/minimalparts/PeARS/wiki/Code-overview)
