from urllib.request import urlopen
from bs4 import BeautifulSoup
from rake_nltk import Rake
from link_finder import LinkFinder
from domain import *
from general import *
import mysql.connector

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    crawledDict_file = ''
    queue = set()
    crawled = set()
    crawledDict = dict()
    db =  None

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.crawledDict_file = Spider.project_name + '/crawledDict.txt'
        Spider.db = mysql.connector.connect(user='root', database='testter')
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.crawledDict[page_url] = Spider.get_keywords(page_url)
            Spider.insert_to_database(str(Spider.crawledDict[page_url]), page_url)
            Spider.update_files()


    @staticmethod
    def get_keywords(page_url):
        html_string = ''
        keywords = set()
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")

            soup = BeautifulSoup(html_string, 'lxml')

            title = soup.title

            if (title != None):
                titleString = title.string.strip()
                if (len(titleString) > 0):
                    keywords.add(titleString)

            for i in soup.find_all('h1'):
                if (i != None):
                    keyword = i.string.strip()

                    if (len(keyword) > 0 and len(keywords) < 5):
                        keywords.add(keyword)

            for i in soup.find_all('h2'):
                if (i != None):
                    keyword = i.string.strip()

                    if (len(keyword) > 0 and len(keywords) < 5):
                        keywords.add(keyword)

            for i in soup.find_all('strong'):
                if (i != None):
                    keyword = i.string.strip()

                    if (len(keyword) > 0 and len(keywords) < 5):
                        keywords.add(keyword)

        except Exception as e:
            print(str(e))
            return set()
        return keywords

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
        dict_to_file(Spider.crawledDict, Spider.crawledDict_file)

    @staticmethod
    def insert_to_database(keywords, url):
        cursor = Spider.db.cursor(buffered=True)
        insert = ("INSERT INTO string_test3 (keywords, url) VALUES (%s, %s)")
        cursor.execute(insert, (keywords, url))
        Spider.db.commit()



