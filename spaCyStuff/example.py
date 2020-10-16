import spacy

nlp = spacy.load('/home/superman/spaCyStuff/new-model')

test = ['Zilong Ye', 'Raj Pamula', 'Huiping Guo']

docs = [nlp(t) for t in test] 

for doc in docs:
    for ent in doc.ents:
        print(ent.label_, ent.text)