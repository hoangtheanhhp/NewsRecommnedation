# -*- encoding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import warnings


class crawler:
    def __init__(self):
        self.ids = {}
        self.new_stories = []
        self.domain = 'http://baomoi.com'
        warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

    def is_exist(self, doc_id):
        try:
            _ = self.ids[doc_id]
            return True
        except:
            self.ids.update({doc_id: True})
            return False

    def get_homepage(self):
        try:
            homepage = requests.get('https://baomoi.com/', timeout=(5, 30))
        except Exception as e:
            print(e.message)
            return None
        return homepage.content

    def parser_hompage(self, homepage):
        bs = BeautifulSoup(homepage)
        list_stories = bs.find_all('div', {'class': 'story__meta'})
        for story in list_stories:
            source = story.find_all('a', {'class': 'cache', 'target': '_blank'})
            self.parser_resultset(source)
            # get related stories
            relate = story.find_all('a', {'class': 'relate'})
            for r in relate:
                href = r.attrs['href']
                self.parser_related(href)

    def parser_related(self, relate):
        try:
            r = requests.get(self.domain + relate, timeout=(5, 30)).content
        except Exception as e:
            print(e.message)
            return
        bs = BeautifulSoup(r)
        list_related = bs.find_all('div', {'class': 'story__meta'})
        for story in list_related:
            source = story.find_all('a', {'class': 'cache', 'target': '_blank'})
            self.parser_resultset(source)

    def parser_resultset(self, source):
        for s in source:
            href = s.attrs['href']
            doc_id = self.get_id(href)
            if '/c/' not in href or self.is_exist(doc_id):
                continue
            content = self.get_content(href)
            if content.strip() == u'':
                continue
            self.new_stories.append(content)

    def get_id(self, href):
        name = os.path.basename(href)
        return os.path.splitext(name)[0]

    def get_content(self, href):
        url_href = self.domain + href
        try:
            source = requests.get(url_href, timeout=(5, 30)).content
        except Exception as e:
            print(e.message)
            return u''
        bs = BeautifulSoup(source)
        content = self.get_content_baomoi(bs)
        return content

    def get_content_baomoi(self, bs):
        article = []
        title = bs.find_all('h1', {'class': 'article__header'})
        article.append(u'\n'.join([t.text for t in title]).strip())
        print('title: %s' % (article[0]))
        description = bs.find_all('div', {'class': 'article__sapo'})
        article.append(u'\n'.join([t.text for t in description]).strip())
        body = bs.find_all('p', {'class': 'body-text'})
        tags_raw = bs.find_all('div', {'class': 'article__tag'})
        tags = []
        for tag in tags_raw:
            tag = tag.text.strip().split(u'/')
            tag = map(lambda x: x.strip(), tag)
            tags += tag
        tags = u'[tags] : ' + u' , '.join(tags)
        article.append(u'\n'.join([t.text for t in body]).strip())
        article.append(tags)
        return u'\n'.join(article)

    def remove_old_documents(self):
        del self.new_stories[:]
        self.ids.clear()

    def run(self):
        del self.new_stories[:]
        homepage = self.get_homepage()
        if homepage == None:
            return
        self.parser_hompage(homepage)
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print('[%s] - There are %d new documents' % (date, len(self.new_stories)))


if __name__ == '__main__':
    c = crawler()
    c.run()
