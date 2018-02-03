from rewriter import ContentProcessor
from wordai.turing import TuringWordAi as WordAi
import json
import os
from bs4 import BeautifulSoup
from bs4 import Comment
import time
from wordai.exceptions import SpinError
from wordai.exceptions import NetworkError

class WordAIProcessor(ContentProcessor):

    def __init__(self, username=None, api_key=None):
        ContentProcessor.__init__(self)
        if not username:
            with open(os.path.expanduser("~/.wordai/credentials.json")) as f:
                credentials = json.loads(f.read())
            username = credentials['username']
            api_key = credentials['api_key'].decode('base64')
        self.rewriter = WordAi(username, api_key)
        self.rewriter.TIMEOUT = 60

    def process(self, source_text):
        input_soup = BeautifulSoup(source_text, "html.parser")
        comments = input_soup.findAll(text=lambda text:isinstance(text, Comment))
        for comment in comments:
            comment.extract()
        replacement = """<table id="{id}">This is dummy text</table>"""
        tables = []
        for idx, table in enumerate(input_soup.select('table')):
            table.replace_with(BeautifulSoup(replacement.format(id="%02d" % idx),"html.parser"))
            tables.append(table)
        try:
            variation = self.get_variation(input_soup)
        except SpinError as e:
            print "Too many requests error. Sleeping for 10 seconds"
            time.sleep(10)
            variation = self.get_variation(input_soup)
        output_soup = BeautifulSoup(variation, 'html.parser')
        for table in output_soup.select('table'):
            table.replace_with(tables[int(table.get('id'))])
        print "Pausing for 10 seconds"
        time.sleep(10)
        return str(output_soup)

    def get_variation(self, input_soup):
        variation = self.rewriter.unique_variation(str(input_soup).decode('utf-8'))
        return variation

# with open('/Users/dbansal/Work/MyCode/scraping/mic/Output/articles/gst-rates-for-lic-policies-and-other-insurance-premiums') as f:
#     WordAIProcessor().process(source_text=(f.read()))
