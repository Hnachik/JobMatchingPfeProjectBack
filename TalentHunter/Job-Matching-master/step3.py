from __future__ import unicode_literals
import gensim
import logging
from gensim.summarization import keywords
import pandas as pd

import nltk
import string
import matplotlib.pyplot as plt
from nltk.stem.porter import PorterStemmer
from nltk import wordpunct_tokenize
import CleaningGlassdoor
from nltk.corpus import stopwords

language = CleaningGlassdoor.language
df = pd.read_csv('Cleaningdata.csv')
jd = df['Job Description'].tolist()
companies = df['company'].tolist()
positions = df['position'].tolist()
print("OKKKKKKK", language)


# Classes CountVectorizer and TfidfVectorizer
class MyCountVectorizer:
    def __init__(self, docs):
        self.corpus = self.normalize_corpus(docs)
        self.make_features()
        self.make_matrix()

    def normalize_corpus(self, docs):
        table = str.maketrans(string.punctuation,
                              len(string.punctuation) * ' ')
        norm_docs = []
        for doc_raw in docs:
            doc = filter(lambda x: x in string.printable, str(doc_raw))
            doc = str(doc).translate(table).lower()
            norm_docs.append(doc)
        return norm_docs

    def make_features(self):
        ''' create vocabulary set from the corpus '''
        stopwords = nltk.corpus.stopwords.words(language)
        self.features = set()
        for doc in self.corpus:
            for word in doc.split():
                if word not in stopwords:
                    self.features.add(word)
        self.features = sorted(list(self.features))

    def make_matrix(self):
        self.matrix = []
        for doc in self.corpus:
            doc_vec = []
            for word in self.features:
                tf = self.term_freq(word, doc)
                doc_vec.append(tf)
            self.matrix.append(doc_vec)

    def term_freq(self, term, document):
        words = document.split()
        count = 0
        for word in words:
            if word == term:
                count += 1
        return count

    def print_matrix(self):
        for vec in self.matrix:
            print(vec)

    def get_matrix(self):
        return self.matrix

    def get_features(self):
        return self.features

    def get_density(self):
        ''' get the density (non-zero elements / all elements )'''
        counter = 0
        total = 0
        for row in self.matrix:
            for item in row:
                if item != 0:
                    counter += 1
                total += 1
        return 1.0 * counter / total


import math


class MyTfIdfVectorizer(MyCountVectorizer):
    ''' inherits from MyCountVectorizer'''

    def make_matrix(self):
        'overriding method'
        self.matrix = []
        i = 0
        for doc in self.corpus:
            doc_vec = []
            for word in self.features:
                tf = self.term_freq(word, doc)
                idf = self.inverse_document_freq(word)
                i = i + 1
                doc_vec.append(tf * idf)
            # self.matrix.append(doc_vec)
            total = sum(doc_vec)
            doc_vec_norm = [i / total for i in doc_vec]
            self.matrix.append(doc_vec_norm)

    def inverse_document_freq(self, term):
        doc_count = 0
        for document in self.corpus:
            term_count = self.term_freq(term, document)
            if term_count > 0:
                doc_count += 1
        return math.log(1.0 * len(self.corpus) / doc_count)


with open('resumeconverted.txt', 'r') as f:
    # with open('res.txt', 'r') as f:
    resume = f.read()
jd.append(resume)
myvec = MyTfIdfVectorizer(jd)

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

model = gensim.models.KeyedVectors.load_word2vec_format(
    r'C:\Users\Administrator\PycharmProjects\Resume-Job-Description-Matching-master\GoogleNews-vectors-negative300.bin',
    binary=True, limit=500000)
MotClé = ["java", "python", "C++", "C"]
vec = []
for j in jd:
    print(type(j))
    jd_vector = []
    i = 0
    for word in str(j).split():
        if word not in MotClé:
            try:
                x = model[word]
                idx = myvec.get_features().index(word)
                z = myvec.get_matrix()[i][idx]
                lst = [a * z for a in x]
                jd_vector.append(lst)
            except:
                continue
        else:
            try:
                x = model[word]
                lst = [a * 10 for a in x]
                jd_vector.append(lst)
            except:
                continue
    i += 1
    vec.append(jd_vector)
# vec= list of lists of the vectors of the words of chaque job description
mean_vec = []
for j in vec:
    # j= list of word's vectors
    mean = []
    for i in range(300):
        accum = 0
        for word in j:
            accum += word[i]
        mean.append(1.0 * accum / len(word))
    mean_vec.append(mean)
    # mean_vec= list of job description's vector
data = mean_vec

# plot_mds(mean_vec)
# plot_pca(mean_vec)

from sklearn.metrics.pairwise import cosine_distances, cosine_similarity

cos_sim = []

import numpy as np

for vec in data[:-1]:
    vec = np.asarray(vec)
    d = np.asarray(data[-1])
    # cos_dist.append(float(cosine_distances(vec.reshape(1,-1),d.reshape(1,-1))))
    cos_sim.append(float(cosine_similarity(vec.reshape(1, -1), d.reshape(1, -1))))

ps = PorterStemmer()
key_list = []

for j in jd[:-1]:
    key = ''
    w = set()
    for word in keywords(str(j)).split('\n'):
        w.add(word)
    for x in w:
        key += '{} '.format(x)
    key_list.append(key)

summary = pd.DataFrame({
    'Company': companies,
    'Postition': positions,
    'Cosine Distances': cos_sim,
    'Keywords': key_list,
    'Job Description': jd[:-1]
})
z = summary.sort_values('Cosine Distances', ascending=False)
z.to_csv('Summaryimproved.csv', encoding="utf-8")
