from django.core.management.base import BaseCommand, CommandError

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import gensim
from gensim.models import LdaModel
from gensim import models, corpora, similarities
import re
import csv
from nltk.stem.porter import PorterStemmer
import time
from nltk import FreqDist
from collections import defaultdict
from scipy.stats import entropy
import matplotlib.pyplot as plt
import seaborn as sns

from accounts.models import Recruiter
from jobMatchingApi.models import Resume, JobPost, WorkHistory, Education, MatchedPosts
from jobMatchingApi.serializers import ResumeListSerializer, ResumeSerializer, JobPostCleanSerializer

sns.set_style("darkgrid")


def initial_clean(text):
    """
    Function to clean text of websites, email addresses and any punctuation
    We also lower case the text
    """
    text = re.sub("[\r?\n]", " ", text)
    text = re.sub("[\xa0]", " ", text)
    text = re.sub("[éêè]", "e", text)
    text = re.sub("[ô]", "o", text)
    text = re.sub("[ç]", "c", text)
    text = re.sub("[û]", "u", text)
    text = re.sub("[a-z]’", " ", text)
    text = re.sub("[^a-zA-Z ]", "", text)
    text = text.lower()  # lower case the text
    text = nltk.word_tokenize(text)
    return text


french_stop_words = stopwords.words('french')
extension = ['ete', 'etee', 'etees', 'etes', 'etant', 'etante', 'etants', 'etantes', 'etes',
             'etais', 'etait', 'etions', 'etiez', 'etaient', 'fumes', 'futes', 'fut', 'eumes', 'eutes', 'meme']
french_stop_words = french_stop_words + extension
english_stop_words = stopwords.words('english')
stop_words = french_stop_words + english_stop_words


def remove_stop_words(text):
    """
    Function that removes all stopwords from text
    """
    try:
        text = [word for word in text if word not in stop_words]
        text = [word for word in text if len(word) > 1]  # make sure we have no 1 letter words
    except IndexError:  # the word "oed" broke this, so needed try except
        pass
    return text


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


def apply_all(text):
    """
    This function applies all the functions above into one
    """
    return remove_stop_words(initial_clean(text))


def train_lda(data):
    """
    This function trains the lda model
    We setup parameters like number of topics, the chunksize to use in Hoffman method
    We also do 2 passes of the data since this is a small dataset, so we want the distributions to stabilize
    """
    num_topics = 23
    chunk_size = 150
    dictionary = corpora.Dictionary(data['job_dict'])
    corpus = [dictionary.doc2bow(doc) for doc in data['job_dict']]
    # low alpha means each document is only represented by a small number of topics, and vice versa
    # low eta means each topic is only represented by a small number of words, and vice versa
    lda = LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary,
                   alpha=1e-2, eta=0.5e-2, chunksize=chunk_size, minimum_probability=0.0, passes=2)
    return dictionary, corpus, lda


def jensen_shannon(query, matrix):
    """
    This function implements a Jensen-Shannon similarity
    between the input query (an LDA topic distribution for a document)
    and the entire corpus of topic distributions.
    It returns an array of length M where M is the number of documents in the corpus
    """
    # lets keep with the p,q notation above
    p = query[None, :].T  # take transpose
    q = matrix.T  # transpose matrix
    m = 0.5 * (p + q)
    return np.sqrt(0.5 * (entropy(p, m) + entropy(q, m)))


def get_most_similar_documents(query, matrix, k=20):
    """
    This function implements the Jensen-Shannon distance above
    and returns the top k indices of the smallest jensen shannon distances
    """
    sims = jensen_shannon(query, matrix)  # list of jensen shannon distances
    return sims.argsort()[:k]  # the top k positional index of the smallest Jensen Shannon distances


class Command(BaseCommand):
    help = 'LDA Model for Job Matching'

    def add_arguments(self, parser):
        parser.add_argument('seeker', type=int)

    def handle(self, **options):
        posts = JobPost.objects.all()
        job_data = JobPostCleanSerializer(posts, many=True).data
        with open('posts.csv', 'w', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, ['id', 'recruiter', 'post_url', 'job_title', 'job_type',
                                                       'publication_date', 'expiration_date', 'job_description',
                                                       'job_requirements', 'location'])
            dict_writer.writeheader()
            dict_writer.writerows(job_data)

        df = pd.read_csv('posts.csv',
                         usecols=['recruiter', 'job_title', 'job_type', 'job_description', 'job_requirements',
                                  'publication_date', 'expiration_date', 'location', 'post_url', 'id'], encoding='utf-8')
        df = df[df['job_description'].map(type) == str]
        df = df[df['job_requirements'].map(type) == str]
        df['job_title'].fillna(value="", inplace=True)
        df.dropna(axis=0, inplace=True, subset=['job_description'])
        df.dropna(axis=0, inplace=True, subset=['job_requirements'])
        # shuffle the data
        df = df.sample(frac=1.0)
        df.reset_index(drop=True, inplace=True)

        df['job_dict'] = df['job_title'].apply(apply_all) + df['job_description'].apply(apply_all) + df[
            'job_requirements'].apply(apply_all)

        all_words = [word for item in list(df['job_dict']) for word in item]
        # use FreqDist to get a frequency distribution of all words
        fDist = FreqDist(all_words)
        print(len(fDist))  # number of unique words
        k = 4000
        top_k_words = fDist.most_common(k)

        # define a function only to keep words in the top k words
        top_k_words, _ = zip(*fDist.most_common(k))
        top_k_words = set(top_k_words)

        def keep_top_k_words(text):
            return [word for word in text if word in top_k_words]

        df['job_dict'] = df['job_dict'].apply(keep_top_k_words)
        # document length
        df['doc_len'] = df['job_dict'].apply(lambda word: len(word))
        df.drop(labels='doc_len', axis=1, inplace=True)

        df = df[df['job_dict'].map(len) >= 40]
        # make sure all job_dict items are lists
        df = df[df['job_dict'].map(type) == list]
        df.reset_index(drop=True, inplace=True)

        msk = np.random.rand(len(df)) < 0.999

        train_df = df[msk]
        train_df.reset_index(drop=True, inplace=True)

        test_df = df[~msk]
        test_df.reset_index(drop=True, inplace=True)
        dictionary, corpus, lda = train_lda(train_df)

        MatchedPosts.objects.filter(seeker=options['seeker']).delete()
        resume = Resume.objects.get(seeker=options['seeker'])
        serializer = ResumeSerializer(resume)
        print(resume.seeker)
        flatted_resume = flatten_json(serializer.data)
        with open('cv.txt', 'w', encoding='utf-8') as f:
            for key in flatted_resume.keys():
                f.write("%s\r\n" % flatted_resume[key])

        # with open('cv.txt', 'r') as f:
        #     myResume = f.read()

        with open('cv.txt', 'r', encoding='utf-8') as f:
            # with open('res.txt', 'r') as f:
            cv = f.read()
        job_dict_resume = apply_all(cv)

        new_bow = dictionary.doc2bow(job_dict_resume)
        new_doc_distribution = np.array([tup[1] for tup in lda.get_document_topics(bow=new_bow)])

        # we need to use nested list comprehension here
        # this may take 1-2 minutes...
        doc_topic_dist = np.array([[tup[1] for tup in lst] for lst in lda[corpus]])

        # this is surprisingly fast
        most_sim_ids = get_most_similar_documents(new_doc_distribution, doc_topic_dist)
        most_similar_df = train_df[train_df.index.isin(most_sim_ids)]

        for i in most_similar_df.index:
            print(Recruiter.objects.get(id=most_similar_df.loc[i, 'recruiter']))
            matchedPost = MatchedPosts()
            matchedPost.seeker = resume.seeker
            matchedPost.recruiter = Recruiter.objects.get(id=most_similar_df.loc[i, 'recruiter'])
            matchedPost.job_title = most_similar_df.loc[i, 'job_title']
            matchedPost.post_url = most_similar_df.loc[i, 'post_url']
            matchedPost.publication_date = most_similar_df.loc[i, 'publication_date']
            matchedPost.expiration_date = most_similar_df.loc[i, 'expiration_date']
            matchedPost.location = most_similar_df.loc[i, 'location']
            matchedPost.job_type = most_similar_df.loc[i, 'job_type']
            matchedPost.job_description = most_similar_df.loc[i, 'job_description']
            matchedPost.job_requirements = most_similar_df.loc[i, 'job_requirements']
            matchedPost.save()
