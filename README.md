# PeARS


##Installation
>This is mostly a development setup since we not really production ready yet. You can find a demo of PeARS running over here: http://pearsearch.herokuapp.com/

1. Clone this repo

`git clone -b development git@github.com:minimalparts/PeARS.git`

`cd PeARS`


2. Set up the development environment

    1. Set up virtualenv
        >We recommend using virtualenv for the development. If you are just here for test it out, skip to the next section.

        Install pip using easy_install

        `sudo easy_install pip`

        or some other way your distribution supports like:

        `sudo yum install python-pip`


        Install virtualenv using pip


        `sudo pip install virtualenv`

        Create a new virtualenv for PeARS and activate it

        `virtualenv pears_env && source pears_env/bin/activate`


    2. Install the build dependencies

        >We recommend using pip for installations. In case you don't have this, looks inside requirements.txt and install dependencies manually.

        `pip install -r requirements.txt`

        Run the following in case you are having any issues while running

        `python -m textblob.download_corpora lite`


3. Running the PeARS search engine


    In the root directory of the repo, run

    `python run.py`

    Go to the browser and type localhost:5000. You should find PeARS running there.


That's it, folks! Please get back to us in case of any issues.
