from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError

import logging
import math
import string
import json
import re
import gensim
import nltk
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize

from gensim.summarization import keywords
from nltk.stem.porter import PorterStemmer
from jobMatchingApi.views import CleaningGlassdoor
from jobMatchingApi.models import Resume, JobPost, WorkHistory, Education, MatchedPosts
from jobMatchingApi.serializers import ResumeListSerializer, ResumeSerializer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_corpus(docs):
    table = str.maketrans(string.punctuation,
                          len(string.punctuation) * ' ')
    norm_docs = []
    for doc_raw in docs:
        doc = filter(lambda raw: raw in string.printable, doc_raw)

        doc = str(doc).translate(table).lower()
        norm_docs.append(doc)
    # self.corpus = norm_docs
    return norm_docs


def term_freq(term, document):
    words = document.split()
    count = 0
    for _word in words:
        if _word == term:
            count += 1
    return count


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[str(name[:-1])] = str(x)

    flatten(y)
    return out


def text_cleaner(text_temp):
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words("french"))
    text = re.sub("[\r?\n]", " ", text_temp)
    text = re.sub("[\xa0]", " ", text)
    text = re.sub("[éêè]", "e", text)
    text = re.sub("[ô]", "o", text)
    text = re.sub("[ç]", "c", text)
    text = re.sub("[û]", "u", text)
    text = re.sub("[a-z]’", " ", text)  # break into lines
    text = re.sub("[^a-zA-Z.+3]", " ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)
    # Also include + for C++
    text = text.lower()  # Go to lower case
    text = nltk.word_tokenize(text)  # and split them apart
    try:
        text = [word for word in text if word not in stop_words]
        text = [word for word in text if len(word) > 1]  # make sure we have no 1 letter words
    except IndexError:  # the word "oed" broke this, so needed try except
        pass
    return text


class MyCountVector:
    def __init__(self, docs):
        self.corpus = normalize_corpus(docs)
        self.features = set()
        self.matrix = []
        self.make_features()
        self.make_matrix()

    def make_features(self):
        """ create vocabulary set from the corpus """
        stopWords = nltk.corpus.stopwords.words('french')
        for doc in self.corpus:
            for _word in doc.split():
                if _word not in stopWords:
                    self.features.add(_word)
        # self.features = set([word for doc in self.corpus for word in doc.split() if word not in stopwords])
        self.features = sorted(list(self.features))

    def make_matrix(self):
        for doc in self.corpus:
            doc_vec = []
            for _word in self.features:
                tf = term_freq(_word, doc)
                doc_vec.append(tf)
            self.matrix.append(doc_vec)

    def get_matrix(self):
        return self.matrix

    def get_features(self):
        return self.features

    def get_density(self):
        """ get the density (# of non-zero elements / # all elements )"""
        counter = 0
        total = 0
        for row in self.matrix:
            for item in row:
                if item != 0:
                    counter += 1
                total += 1
        return 1.0 * counter / total


class MyTfIdfVector(MyCountVector):
    """ inherits from MyCountVector"""

    def make_matrix(self):
        """overriding method"""
        self.matrix = []
        for doc in self.corpus:
            doc_vec = []
            for _word in self.features:
                tf = term_freq(_word, doc)
                idf = self.inverse_document_freq(_word)
                doc_vec.append(tf * idf)
            # self.matrix.append(doc_vec)
            total = sum(doc_vec)
            doc_vec_norm = [j / total for j in doc_vec]
            self.matrix.append(doc_vec_norm)

    def inverse_document_freq(self, term):
        doc_count = 0
        for document in self.corpus:
            term_count = term_freq(term, document)
            if term_count > 0:
                doc_count += 1
        return math.log(1.0 * len(self.corpus) / doc_count)


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('seeker', type=int)

    def handle(self, *args, **options):

        # df = pd.read_csv('data.csv')
        # jd = df['job_description'].tolist()
        # companies = df['company_name'].tolist()
        # positions = df['job_title'].tolist()

        resume = Resume.objects.get(seeker=options['seeker'])
        serializer = ResumeSerializer(resume)

        flat2 = flatten_json(serializer.data)
        with open('cv.txt', 'w') as f:
            for key in flat2.keys():
                f.write("%s\r\n" % flat2[key])

        with open('cv.txt', 'r') as f:
            myResume = f.read()

        MatchedPosts.objects.filter(seeker=options['seeker']).delete()
        posts = JobPost.objects.all()
        jobD = []
        company = []
        jobTitles = []

        for post in posts:
            jobD.append(post.job_description)
            company.append(post.recruiter)
            jobTitles.append(post.job_title)

        skills = []
        for item in resume.skills:
            skills.append(item['name'])
        jobD.append(myResume)
        myVec = MyTfIdfVector(jobD)

        # Logging code taken from http://rare-technologies.com/word2vec-tutorial/
        logging.basicConfig(
            format='%(asctime)s : %(levelname)s : %(message)s',
            level=logging.INFO)

        model = gensim.models.KeyedVectors.load_word2vec_format(
            r'E:\GoogleNews-vectors-negative300.bin',
            binary=True, limit=500000)
        language = CleaningGlassdoor.language
        stopwords = nltk.corpus.stopwords.words(language)

        p = string.punctuation
        d = string.digits
        table_p = str.maketrans(p, len(p) * " ")
        table_d = str.maketrans(d, len(d) * " ")
        vec = []
        for j in jobD:
            x = j.translate(table_p)
            y = x.translate(table_d)
            jd_vector = []
            i = 0
            for word in y.split():
                if word.lower() not in stopwords and len(word) > 1 and word not in skills:
                    try:
                        x = model[word]
                        idx = myVec.get_features().index(word)
                        z = myVec.get_matrix()[i][idx]
                        lst = [a * z for a in x]
                        jd_vector.append(lst)
                    except:
                        continue
                else:
                    try:
                        x = model[word]
                        lst = [a * 2 for a in x]
                        jd_vector.append(lst)
                    except:
                        continue
            i += 1
            vec.append(jd_vector)

        mean_vec = []
        for j in vec:
            mean = []
            for i in range(300):
                accum = 0
                for word in j:
                    accum += word[i]
                mean.append(1.0 * accum / len(word))
            mean_vec.append(mean)
        data = mean_vec

        cos_dist = []

        for vec in data[:-1]:
            vec = np.asarray(vec)
            d = np.asarray(data[-1])
            # cos_dist.append(float(cosine_distances(vec.reshape(1,-1),d.reshape(1,-1))))
            cos_dist.append(float(cosine_similarity(vec.reshape(1, -1), d.reshape(1, -1))))

        ps = PorterStemmer()
        key_list = []

        for j in jobD[:-1]:
            key = ''
            w = set()
            for word in keywords(j).split('\n'):
                w.add(ps.stem(word))
            for x in w:
                key += '{} '.format(x)
            key_list.append(key)

        summary = pd.DataFrame({
            # 'Company': jobTitles,
            'job_title': jobTitles,
            'cosine_distance': cos_dist,
            'job_description': jobD[:-1]
        }).sort_values('cosine_distance', ascending=False)
        for i in summary.index:
            matchedPost = MatchedPosts()
            matchedPost.seeker = resume.seeker
            matchedPost.job_title = summary.loc[i, 'job_title']
            matchedPost.job_description = summary.loc[i, 'job_description']
            matchedPost.cosine_distance = summary.loc[i, 'cosine_distance']
            matchedPost.save()

