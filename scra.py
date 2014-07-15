import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

first = True

while True:
	client = MongoClient('localhost', 3001)
	db = client.meteor
	meldungen = db.meldungen

	opener = urllib2.build_opener()

	url = ('http://www.polizei.mvnet.de/cms2/Polizei_prod/Polizei/de/oeff/Pressemitteilungen/Aktuelle_Pressemitteilungen/index.jsp')
	ourUrl = opener.open(url).read()

	soup = BeautifulSoup(ourUrl)

	results = soup.find_all( 'a' , class_ = 'weiter')

	pidList = []
	for hrefs in results:
		suppe = BeautifulSoup(str(hrefs))
		pidList.append(suppe.a['href'])

	if first:
		pidList.reverse()

	for meldung in pidList:
		url = ('http://www.polizei.mvnet.de/cms2/Polizei_prod/Polizei/de/oeff/Pressemitteilungen/Aktuelle_Pressemitteilungen/index.jsp' + meldung)
		ourUrl = opener.open(url).read()

		soup = BeautifulSoup(ourUrl)
		title = soup.find('h2')
		subTitle = soup.find('em')
		suppe = BeautifulSoup(str(subTitle))
		revier = suppe.find('strong')

		indexChar = str(subTitle).index('.2')
		date = str(subTitle)[indexChar-5:indexChar+5]

		text = soup.find('div', class_ = 'freitext')

		if meldungen.find({'subTitle' : subTitle.text}).count() == 0:
			post = {"title": title.text, "date" : date, "subTitle": subTitle.text, "revier": revier.text, "text": text.prettify(formatter="html"), "time": time.strftime('%Y%m%d%H%M%S')}
			result = meldungen.insert(post)
			print 'Neue Meldung'
		time.sleep(10)

	first = False

	print 'done'
	#time.sleep(60)