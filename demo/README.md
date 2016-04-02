### Produce demo users

* Make a new user

`mkdir users/ravi/`
`mkdir users/ravi/categories/`

* Get some Wikipedia categories in this user's pear:

`./getWikiCat ravi Environment`
`./getWikiCat ravi Environmentalism`
`cat users/ravi/categories/*txt|sort -u > users/ravi/ravi.txt`

* Run distributional semantics on the pages visited by this user:

`python ./runDistSemWeighted.py users/ravi/ravi.txt users/ravi/urls.dists.txt`
`cat users/ravi/urls.dists.txt|sort -u > tmp; mv tmp users/ravi/urls.dists.txt`

* Make wordclouds for those pages:

`python ./mkWordClouds.py`

* Make profile for the user:

`python ./mkProfiles.py lea`
