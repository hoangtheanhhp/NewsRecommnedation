# -*- encoding: utf-8 -*-
import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import gensim
from gensim.utils import simple_preprocess
from sklearn.externals import joblib
from distances import get_most_similar_documents

PATH_DICTIONARY = "models/id2word.dictionary"
PATH_CORPUS = "models/corpus.mm"
PATH_LDA_MODEL = "models/LDA.model"
PATH_DOC_TOPIC_DIST = "models/doc_topic_dist.dat"


def make_texts_corpus(sentences):
    for sentence in sentences:
        yield simple_preprocess(sentence)


class StreamCorpus(object):
    def __init__(self, sentences, dictionary):
        self.sentences = sentences
        self.dictionary = dictionary

    def __iter__(self):
        for tokens in make_texts_corpus(self.sentences):
            yield self.dictionary.doc2bow(tokens)

class LDAModel:

    def __init__(self):
        """
        :param sentences: list or iterable (recommend)
        """
        self.models = None
        self.dictionary = None
        self.corpus = None
        self.doc_topic_dist = None
        if os.path.exists(PATH_LDA_MODEL):
            self.models = gensim.models.LdaModel.load(PATH_LDA_MODEL)
        if os.path.exists(PATH_DICTIONARY):
            self.dictionary = gensim.corpora.Dictionary.load(PATH_DICTIONARY)
        if os.path.exists(PATH_CORPUS):
            self.corpus = gensim.corpora.MmCorpus(PATH_CORPUS)
        if os.path.exists(PATH_DOC_TOPIC_DIST):
            self.doc_topic_dist = joblib.load(PATH_DOC_TOPIC_DIST)

    def _make_corpus_bow(self, sentences):
        self.corpus = StreamCorpus(sentences, self.id2word)
        # save corpus
        gensim.corpora.MmCorpus.serialize(PATH_CORPUS, self.corpus)

    def _make_dictionary(self, sentences):
        self.texts_corpus = make_texts_corpus(sentences)
        self.id2word = gensim.corpora.Dictionary(self.texts_corpus)
        # self.id2word.filter_extremes(no_below=10, no_above=0.25)
        # self.id2word.compactify()
        self.id2word.save(PATH_DICTIONARY)

    def documents_topic_distribution(self):
        doc_topic_dist = np.array(
            [[tup[1] for tup in lst] for lst in self.lda_model[self.corpus]]
        )
        # save documents-topics matrix
        joblib.dump(doc_topic_dist, PATH_DOC_TOPIC_DIST)
        return doc_topic_dist

    def fit(self, sentences, num_topics=64, passes=5,
            chunksize=100, random_state=42, alpha=1e-2, eta=0.5e-2,
            minimum_probability=0.0, per_word_topics=False):
        self._make_dictionary(sentences)
        self._make_corpus_bow(sentences)
        self.lda_model = gensim.models.ldamodel.LdaModel(
            self.corpus, id2word=self.id2word, num_topics=num_topics, passes=passes,
            chunksize=chunksize, random_state=random_state, alpha=alpha, eta=eta,
            minimum_probability=minimum_probability, per_word_topics=per_word_topics
        )
        self.lda_model.save(PATH_LDA_MODEL)

    def transform(self, sentence):
        """
        :param document: preprocessed document
        """
        document_corpus = next(make_texts_corpus([sentence]))
        corpus = self.id2word.doc2bow(document_corpus)
        document_dist = np.array(
            [tup[1] for tup in self.lda_model.get_document_topics(bow=corpus)]
        )
        return corpus, document_dist

    def predict(self, document_dist):
        doc_topic_dist = self.documents_topic_distribution()
        return get_most_similar_documents(document_dist, doc_topic_dist)

    def update(self, new_corpus):  # TODO
        """
        Online Learning LDA
        https://radimrehurek.com/gensim/models/ldamodel.html#usage-examples
        https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation
        """
        self.lda_model.update(new_corpus)
        # get topic probability distribution for documents
        for corpus in new_corpus:
            yield self.lda_model[corpus]

    def coherence_score(self):
        self.coherence_model_lda = gensim.models.coherencemodel.CoherenceModel(
            model=self.lda_model, texts=self.corpus,
            dictionary=self.id2word, coherence='c_v'
        )
        logging.INFO(self.coherence_model_lda.get_coherence())

    def compute_coherence_values(self, mallet_path, dictionary, corpus,
                                 texts, end=40, start=2, step=3):
        """
        Compute c_v coherence for various number of topics

        Parameters:
        ----------
        dictionary : Gensim dictionary
        corpus : Gensim corpus
        texts : List of input texts
        end : Max num of topics

        Returns:
        -------
        model_list : List of LDA topic models
        coherence_values : Coherence values corresponding to the LDA model
                           with respective number of topics
        """
        coherence_values = []
        model_list = []
        for num_topics in range(start, end, step):
            model = gensim.models.wrappers.LdaMallet(
                mallet_path, corpus=self.corpus,
                num_topics=self.num_topics, id2word=self.id2word)
            model_list.append(model)
            coherencemodel = gensim.models.coherencemodel.CoherenceModel(
                model=model, texts=self.texts_corpus,
                dictionary=self.dictionary, coherence='c_v'
            )
            coherence_values.append(coherencemodel.get_coherence())

        return model_list, coherence_values

    def plot(self, coherence_values, end=40, start=2, step=3):
        x = range(start, end, step)
        plt.plot(x, coherence_values)
        plt.xlabel("Num Topics")
        plt.ylabel("Coherence score")
        plt.legend(("coherence_values"), loc='best')
        plt.show()

    def print_topics(self):
        pass