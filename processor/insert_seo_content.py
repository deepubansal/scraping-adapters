from processor import ContentProcessor
from bs4 import BeautifulSoup
from random import randint


class InsertSeoContentProcessor(ContentProcessor):

    def __init__(self, append_text_file="/Users/dbansal/Work/MyCode/auto-poster-adapter/seo_append_texts"):
        ContentProcessor.__init__(self)
        with open(append_text_file, 'r') as f:
            self._seo_texts = [line for line in f.readlines()]

    def process(self, source_text):
        soup = BeautifulSoup(source_text, "html.parser")
        if randint(0,1):
            random_seo = BeautifulSoup("<blockquote>{}</blockquote>".format(self._get_random_seo_text()), "html.parser")
        else:
            random_seo = BeautifulSoup(self._get_random_seo_text(), "html.parser")

        for table in soup.select("table"):
            table.insert_after(BeautifulSoup("<blockquote>{}</blockquote>".format(self._get_random_seo_text()), "html.parser"))
        soup.append(random_seo)
        return str(soup)

    def _get_random_seo_text(self):
        return self._seo_texts[randint(0, len(self._seo_texts) - 1)]

if __name__ == "__main__":
    with open('/Users/dbansal/Work/MyCode/wp-auto-poster/posts/posts0012/files/file1') as f:
        print InsertSeoContentProcessor().process(source_text=(f.read()))
