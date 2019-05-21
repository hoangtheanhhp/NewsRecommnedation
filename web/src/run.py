# -*- encoding: utf-8 -*-
import utils
from models import LDAModel
from preprocessing import PreProcessing

PATH_DATA_SET = '/home/anh/Project/ML/LDA_Recommender_System/web/src/crawl/result/2019-04-09/'


def main():
    # utils.mkdir('models')
    # utils.mkdir(PATH_DATA_SET)
    # data = utils.load_data_set(PATH_DATA_SET)
    # sentences = [PreProcessing.solve(text) for text in data]
    # for sentence in sentences:
    #     print sentence
    lda = LDAModel()
    # lda.fit(sentences, num_topics=10)
    a = lda.doc_topic_dist
    for i in range(0,10):
        print "Topic #%d: " %(i+1) + lda.models.print_topic(i, 10)
if __name__ == '__main__':
    main()