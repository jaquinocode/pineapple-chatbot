
import spacy
from spacy.gold import GoldParse
from spacy.util import minibatch
import random
from pathlib import Path


LABEL = 'PHONE'
LABEL2 = 'ROOM'
LABEL3 = 'EMAIL'
 
# Code Source: https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting

revision_data = []

nlp = spacy.load('en_core_web_sm')

print()

revision_texts = [u'Raj S. Pamula, Ph.D., Chair, Advisor', 
                  u'Russell J. Abbott, Ph.D.', 
                  u'Vladimir N. Akis, Ph.D.',
                  u'Eun-Young (Elaine) Kang, Ph.D., Undergraduate Advisor']

# Apply the initial model to raw examples. You'll want to experiment
# with finding a good number of revision texts. It can also help to
# filter out some data.
for doc in nlp.pipe(revision_texts):
    tags = [w.tag_ for w in doc]
    heads = [w.head.i for w in doc]
    deps = [w.dep_ for w in doc]
    entities = [(e.start_char, e.end_char, e.label_) for e in doc.ents]
    revision_data.append((doc, GoldParse(doc, tags=tags, heads=heads,
                                         deps=deps, entities=entities)))


if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner)

# otherwise, get it, so we can add labels to it
else:
    ner = nlp.get_pipe('ner')

ner.add_label(LABEL)   # add new entity label to entity recognizer
ner.add_label(LABEL2)
ner.add_label(LABEL3)

fine_tune_data = [
    ("E&T A-322", {
        'entities': [(0, 9, 'ROOM')]
    }),

    ("Behzad Parvis, Ph.D., Chair, Advisor", {
        'entities': [(0, 20, 'PERSON')]
    }),

    ("Phone: (342) 093-4325", {
        'entities': [(7, 21, 'PHONE')]
    }),

    ("Phone: 342-093-4325", {
        'entities': [(7, 19, 'PHONE')]
    }),

    (": 917-093-4315", {
        'entities': [(2, 14, 'PHONE')]
    }),
    
    ("Raj S. Pamula, Ph.D., Chair, Advisor", {
        'entities': [(0, 22, 'PERSON')]
    }),

    ("Eun-Young (Elaine) Kang, Ph.D., Undergraduate Advisor", {
        'entities': [(0, 30, 'PERSON')]
    }),

    ("E&T A-329", {
        'entities': [(0, 9, 'ROOM')]
    }),

    ("Office: E&T A-329", {
        'entities': [(8, 17, 'ROOM')]
    }),

    ("Distributed Computing", {
        'entities': []
    }),

    ("Office", {
        'entities': []
    }),

    ("Student Outcomes", {
        'entities': []
    }),

    ("Integrated B.S./M.S ", {
        'entities': []
    }),

    ("       D", {
        'entities': []
    }),


    ("(342) 093-4325", {
        'entities': [(0, 14, 'PHONE')]
    }),

    ("(917) 343-0393", {
        'entities': [(0, 14, 'PHONE')]
    }),

    ("name123@calstatela.edu", {
        'entities': [(0, 22, 'EMAIL')]
    }), 

    ("namelastname@calstatela.edu", {
        'entities': [(0, 27, 'EMAIL')]
    }),

    ("hpguo@calstatela.edu", {
        'entities': [(0, 20, 'EMAIL')]
    }),

    ("Shannon.Dobson@calstatela.edu", {
        'entities': [(0, 29, 'EMAIL')]
    }),

    ("josemasia@gmail.com", {
        'entities': [(0, 19, 'EMAIL')]
    })

]

# Now shuffle the previous behaviour into the new fine-tuning data, and
# update with them together. You might want to upsample the fine-tuning
# examples (e.g. include 5 copies of it). This lets you use a better
# variety of revision data without changing the ratio of revision : tuning
# data.
n_epoch = 5
batch_size = 32
for i in range(n_epoch):
    examples = revision_data + fine_tune_data + fine_tune_data + fine_tune_data + fine_tune_data + fine_tune_data
    losses = {}
    random.shuffle(examples)
    for batch in minibatch(examples, batch_size):
        docs, golds = zip(*batch)
        nlp.update(docs, golds, losses=losses)
    print('Losses', losses)

test_text = ['Office' ,'E&T A-420', 'Phone' ,'(323) 343-6699', 'Zilong Ye']

docs = [nlp(t) for t in test_text] 

for doc in docs:
    for ent in doc.ents:
        print(ent.label_, ent.text)

output_dir = Path('/home/superman/spaCyStuff/new-model')

nlp.meta['name'] = 'pineapple_v3'  # rename model
nlp.to_disk(output_dir)
print("Saved model to", output_dir)
