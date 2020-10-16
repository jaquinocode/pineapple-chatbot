import mysql.connector as mc
from Chatbot.mysqlstorage import MySQLStorage
from Chatbot.dataExtractor import DataExtractor
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

try:
    from Levenshtein.StringMatcher import StringMatcher as SequenceMatcher
except ImportError:
    from difflib import SequenceMatcher


class SimpleChatBot:

    def __init__(self, name, **kwargs):

        self.name = name

        self.storage = MySQLStorage(**kwargs)

        self.dataExtractor = DataExtractor()

        self.stopWords = set(stopwords.words('english'))

        self.greetings = {'hello', 'hi', 'hey'}

    def get_intent(self, intent):
        intent_dict = {'GetEmails':'email', 'GetOfficeRoom':'office', 'GetPhoneNum':'phone'}

        return intent_dict[intent]

    def get_link(self, input):
        tokens = [i for i in word_tokenize(input) if i.lower() not in self.stopWords]

        for t in tokens:
            if t.lower() in self.greetings:
                return "Hello!"

        response_set = self.storage.get_urls2(tokens)

        print(str(tokens))

        if len(response_set) > 1:
            best_match = self.jaccard_sim_comparison(tokens, response_set)
        elif len(response_set) == 1:
            best_match = response_set[0][0]
        else:
            return  "I didn't quite get that. Please try again."

        return f"#Here is what I found using keywords: {str(tokens)}^{best_match}"

    def get_response(self, input, intent, slot):
    
        if slot == 'None':
            return f"Cannot distinguish subject for intent <{intent}>"

        intent_str = self.get_intent(intent)

        slots = slot.split(" ")

        title = "Prof."
       
        if len(slots) > 1:
            slot = slots[-1]
            title = slots[0]

        response_set = self.storage.get_urls(intent_str, slot)

        if not response_set:
             return "Sorry, I can't help you with that."

        tokens = [i for i in word_tokenize(input) if i not in self.stopWords]

        def jaccard_sim_val(elem):
            keywords = set(word_tokenize(
                elem[1].replace('\'', '').replace(',', '')))

            return len(tokens) / len(keywords)

        sorted_responses = sorted(response_set, key=jaccard_sim_val)

        possible_anwers = []

        urls = []

        for r in list(sorted_responses)[:3]:
            url = r[0]

            urls.append(url)

            possible_anwers += self.dataExtractor.get_direct_answer(url, intent, slot)

            if len(possible_anwers) > 0:
                return f"{title} {slot}'s {intent_str} is {possible_anwers[0]}"

        if not possible_anwers:
            return f"$Could not get {self.get_intent(intent)} for {slot}. Link(s) that might help: {str(urls[:3])}"

        

    def compare(self, first_statement, second_statement):

        statement = first_statement.lower()

        other_statement = second_statement.lower()

        similarity = SequenceMatcher(None, statement, other_statement)

        return round(similarity.ratio(), 10)

    def shortest_link(self, response_set):

        def url_len(tup):
            return len(tup[0])

        return min(response_set, key=url_len)[0]

    def jaccard_sim_comparison(self, filtered_tokens, response_set):
        best_val = -1
        best_match = None

        for r in response_set:

            keywords = set(word_tokenize(
                r[1].replace('\'', '').replace(',', '')))

            tokens = set(filtered_tokens)

            val = len(tokens) / float(len(keywords))

            if val > best_val:
                best_val = val
                best_match = r[0]

        return best_match

    def closes_match2(self, filtered_tokens, response_set):
        best_val = -1
        best_match = None

        for r in response_set:
            val = 0

            path_start = r[0].find('.edu/') + 5
            path = r[0][path_start:]
            subdirs = path.split('/')

            for f in filtered_tokens:
                i = 1
                for s in subdirs:
                    val += self.compare(f, r[0]) * i
                    i *= 0.25

            val /= len(subdirs)

            if val > best_val:
                best_val = val
                best_match = r[0]

        return best_match

    def closest_match(self, filtered_tokens, response_list):
        best_val = 0
        best_match = None

        for r in response_list:
            keywords = r[1].replace('\"', '\'').split(',')

            path = r[2][r[2].find('.edu/')+5:]

            subdirs = path.split('/')

            kval = 0
            uval = 0
            sval = 0

            for f in filtered_tokens:
                for k in keywords:
                    kval += self.compare(f, k)

                for u in subdirs:
                    uval += self.compare(f, u)

            filtered_sent = ' '.join(filtered_tokens)

            for k in keywords:
                sval += self.compare(filtered_sent, k)

            kval /= len(keywords) * len(filtered_tokens)
            uval /= len(subdirs) * len(filtered_tokens)
            sval /= len(keywords)

            val = kval*0.25 + uval*0.25 + sval*0.5

            if val > best_val:
                best_val = val
                best_match = r[2]

        return best_match
