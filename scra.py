import HTMLParser
import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time
import re
import json

first = True
urlLen = None
parser = HTMLParser.HTMLParser()

while True:
	#connecting to meteor.js DB normale Port is 3001
	client = MongoClient('localhost', 3001)
	db = client.meteor
	meldungen = db.meldungen

	opener = urllib2.build_opener()

	#getting list of police-PM urls
	url = ('http://www.polizei.mvnet.de/cms2/Polizei_prod/Polizei/de/oeff/Pressemitteilungen/Aktuelle_Pressemitteilungen/index.jsp')
	ourUrl = opener.open(url).read()

	if urlLen != len(ourUrl):

		soup = BeautifulSoup(ourUrl)

		results = soup.find_all( 'a' , class_ = 'weiter')

		pidList = []
		for hrefs in results:
			suppe = BeautifulSoup(str(hrefs))
			pidList.append(suppe.a['href'])

		if first:
			pidList.reverse()

		#scraping police-PMs
		for meldung in pidList:
			url = ('http://www.polizei.mvnet.de/cms2/Polizei_prod/Polizei/de/oeff/Pressemitteilungen/Aktuelle_Pressemitteilungen/index.jsp' + meldung)
			ourUrl2 = opener.open(url).read()

			soup = BeautifulSoup(ourUrl2)
			title = soup.find('h2')
			subTitle = soup.find('em')
			suppe = BeautifulSoup(str(subTitle))
			revier = suppe.find('strong')

			indexChar = str(subTitle).index('.2')
			date = str(subTitle)[indexChar-5:indexChar+5]

			text = soup.find('div', class_ = 'freitext')
			text = text.prettify(formatter="html")

			#pushing PMs to meteor.js monogoDB
			if meldungen.find({'subTitle' : subTitle.text}).count() == 0:
				ort = 'none'
				lat = 'none'
				lng = 'none'

				if '(ots)' in text:
					start = text.find('<p>')
					end = text.find('(ots)')
					ort = text[start + 6:end]
					ort = ort.strip()
					ort = ort.replace(',', '')
					ort = ort.replace('/', '-')
					ort = ort.replace(' ', '-')
					print ort

					ort = parser.unescape(ort)

					googleGeocode = opener.open('https://maps.googleapis.com/maps/api/geocode/json?address=' 
						+ ort + '&components=country:DE|administrative_area:MV').read()
					content = json.loads(googleGeocode)
					lat = content['results'][0]['geometry']['location']['lat']
					lng = content['results'][0]['geometry']['location']['lng']


				post = {"title": title.text, "ort": ort, 'location': {'lat': lat, 'long': lng}, "date" : date, "subTitle": subTitle.text, "revier": revier.text, "text": text, "time": time.strftime('%Y%m%d%H%M%S')}
				result = meldungen.insert(post)
				print 'Neue Meldung'
			time.sleep(5)

		urlLen = len(ourUrl)
		print urlLen
	else:
		print 'keine neuen Meldungen'
		time.sleep(60)

	first = False

	print 'done'
	#time.sleep(60)