# -*- encoding: utf-8 -*-
import re
from io import open
import string

from pyvi import ViTokenizer


class PreProcessing:

    PATH_STOPWORDS = 'data/stopwords.txt'

    def __init__(self):
        pass

    @staticmethod
    def solve(s):
        s = PreProcessing.remove_links_content(s)
        s = PreProcessing.remove_emails(s)
        s = PreProcessing.remove_numeric(s)
        s = PreProcessing.remove_datetime(s)
        s = PreProcessing.remove_punctuation(s)
        s = s.lower()
        s = PreProcessing.remove_newline_characters(s)
        s = PreProcessing.remove_multiple_space(s)
        s = ViTokenizer.tokenize(s)
        s = PreProcessing.remove_stopwords(s)
        return s

    @staticmethod
    def remove_emails(text):
        return re.compile(u'[^@|\s]+@[^@|\s]+').sub('', text)

    @staticmethod
    def remove_newline_characters(text):
        return re.compile(u'\n+').sub(' ', text)

    @staticmethod
    def remove_links_content(text):
        return re.compile(u'(https|http|ftp|ssh)://[^\s\[\]\(\)\{\}]+', re.I).sub('', text)

    @staticmethod
    def remove_multiple_space(text):
        return re.compile(u" +").sub(' ', text)

    @staticmethod
    def remove_punctuation(text):
        """https://stackoverflow.com/questions/11066400"""
        return re.sub(ur'[,;\-\(\)\[\]\{\}\<\>“”\"\'/\$%–@#^&*+=?:!…\.]', '', text)

    @staticmethod
    def remove_datetime(text):
        return re.compile(u'\d+[\-/\.]\d+[\-/\.]*\d*').sub('', text)

    @staticmethod
    def remove_numeric(text):
        return re.compile(ur'(\d+\,\d+\w*)|(\d+\.\d+\w*)|(\w*\d+\w*)').sub('', text)

    @staticmethod
    def remove_stopwords(text):
        stopwords = PreProcessing.stopwords()
        return " ".join([word for word in text.split() if word not in stopwords])

    @staticmethod
    def stopwords(path=PATH_STOPWORDS):
        with open(path, 'r', encoding='utf-8') as f:
            stopwords = []
            for line in f:
                stopwords.append(line.strip())
        return stopwords
