# -*- encoding: utf-8 -*-
import utils
from models import LDAModel
from preprocessing import PreProcessing

PATH_DATA_SET = '/home/anh/Project/ML/LDA_Recommender_System/src/crawl/result/2019-04-09/'


def main():
    # utils.mkdir('models')
    # utils.mkdir(PATH_DATA_SET)
    # data = utils.load_data_set(PATH_DATA_SET)
    # sentences = [PreProcessing.solve(text) for text in data]
    # for sentence in sentences:
    #     print sentence
    lda = LDAModel()
    # lda.fit(sentences)
    # model_list, coherence_values = lda.coherence_model_lda(dictionary=lda.id2word, corpus=lda.corpus, texts=data_lemmatized, start=2, limit=40, step=6)
    for i in range(0,64):
        print lda.models.print_topic(i)
if __name__ == '__main__':
    main()