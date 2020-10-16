from urllib.request import urlopen
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import re
import spacy

class DataExtractor:
    MODEL_PATH = '/home/superman/spaCyStuff/new-model'

    def __init__(self):
        self.nlp = spacy.load(DataExtractor.MODEL_PATH)

        self.intent_dict = {'GetEmails':'EMAIL', 'GetOfficeRoom':'ROOM', 'GetPhoneNum':'PHONE'}

    def remove_leading_spaces(self, text):
        while text[0] == ' ':
            text = text[1:]

        return text

    def get_entities(self, doc, intent):
        out = []

        for ent in doc.ents:

            if str(ent.label_) == self.intent_dict[intent]:

                if str(ent.label_) in ['ROOM', 'PHONE']:
                    if not re.search('[0-9]', ent.text):
                        continue
            
                if str(ent.label_) == 'EMAIL':
                    if not re.search('@', ent.text):
                        continue
                
                print(f" Answer found: {ent.text}")

                out.append(ent.text)
        
        return out

    def get_direct_answer(self, url, intent, slot):
        print(f" Opening {url} ...")
        raw_html = urlopen(url).read().decode('utf-8')
        soup = BeautifulSoup(raw_html, 'html.parser')
        body = soup.body

        found = False
        entities_found = []

        print(f" Searching {url} ...")

        content = body.find(id='content')

        if not content:
            return []

        n = 0

        for i in content.strings:
            text = str(re.sub('(\n|\r|\t|\xa0|\u200b)', '', i))
            
            if not text:
                continue

            if not re.search('[a-zA-Z0-9]', text):
                continue

            if n > 300:
                return []

           
            
            n += 1

            text = self.remove_leading_spaces(text)

            doc = self.nlp(text)

            if not found:
                found = self.find_name(text, slot) 
                count = 0

            if count >= 10:
                found = False

            if found:
                entities_found += self.get_entities(doc, intent)
                count += 1     

            if entities_found:
                return entities_found

        return entities_found

    def find_name(self, text, slot):
        texts = text.split(' ')

        for t in texts:
            t = re.sub('[^a-zA-Z0-9]', '',t)

            if self.compare(t, slot) > 0.95:
                return True

        return False

    def compare(self, a, b):
        if not a or not b:
            return 0

        a = a.lower()
        b = b.lower()

        similarity = SequenceMatcher(None, a, b)

        # Calculate a decimal percent of the similarity
        percent = round(similarity.ratio(), 2)

        return percent
        

           





