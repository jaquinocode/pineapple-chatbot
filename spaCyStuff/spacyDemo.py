from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import spacy


URL = 'http://www.calstatela.edu/ecst/ce/faculty'

URL2 = 'http://www.calstatela.edu/faculty/zilong-ye'

URL3 = 'http://www.calstatela.edu/ecst/cs/faculty'

URL4 = 'http://www.calstatela.edu/faculty/mark-tufenkjian-phd-pe-professor-and-chair'

MODEL_PATH = '/home/superman/spaCyStuff/new-model'

test = 'Office E&T 420 Phone (323) 343-669 Address 5151 State University Drive, Los Angeles, CA 90032 Web cs.calstatela.edu or www.calstatela.edu/cs'


raw_html = urlopen(URL4).read().decode('utf-8')

soup = BeautifulSoup(raw_html, 'html.parser')

body = soup.body

body_contents = ''

relevant_labels = ['PERSON', 'ROOM', 'PHONE', 'EMAIL']

nlp = spacy.load(MODEL_PATH)

for i in body.find(id='content').strings:
	text = str(re.sub('(\n|\r|\t|\xa0|\u200b)', '', i))
	
	if len(text) > 1:
		text = text[1:] if text[0] == ' ' else text

	i = 0
	while i < len(text):
		text = text[1:] if text[0] == ' ' else text
		i += 1

	if not text:
		continue

	if not re.search('[a-zA-Z0-9]', text):
		continue
	
	doc = nlp(text)
	print(text)
	for ent in doc.ents:
		if str(ent.label_) in relevant_labels:

			if str(ent.label_) in ['ROOM', 'PHONE']:
				if not re.search('[0-9]', ent.text):
					continue
			
			if str(ent.label_) == 'EMAIL':
				if re.search('www', ent.text) or not re.search('@', ent.text):
					continue

			print(ent.label_, ent.text, '\n')
	



