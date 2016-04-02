### Produce demo users

* Make a new user

`mkdir users/ravi/`
`mkdir users/ravi/categories/`

* Get some Wikipedia categories in this user's pear:

`./getWikiCat ravi Environment`
`./getWikiCat ravi Environmentalism`
`cat users/raci/categories/*txt > users/ravi/ravi.txt`

* Run distributional semantics on the pages visited by this user:

`python ./runDistSemWeighted.py users/ravi/ravi.txt users/ravi/ravi.urls.dists.txt`
