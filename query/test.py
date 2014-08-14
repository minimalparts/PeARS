import urllib
page = urllib.urlopen('http://192.168.2.10/BBC/BBC.topic.keys')
for l in page:
	print l
