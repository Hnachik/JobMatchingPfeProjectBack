import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from nltk import wordpunct_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
from nltk.stem.snowball import FrenchStemmer
from nltk.stem.snowball import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import re
import csv

# set the font size of plots
plt.rcParams['font.size'] = 14
np.set_printoptions(precision=3)

df = pd.read_csv(r"E:\Workspace\pfe-backend-project\TalentHunter\Job-Matching-master\data.csv",
                 encoding='utf-8-sig')
'''df = df.drop(columns="headquaters")
df = df.drop(columns="employees")
df = df.drop(columns="founded")
df = df.drop(columns="industry")'''
Q1_corpus = df.iloc[:, 5].tolist()
tokenizer = RegexpTokenizer('[^_\W]+')
corpus = [tokenizer.tokenize((str(doc)).lower()) for doc in Q1_corpus]
# identify language:
languages_ratios = {}
tokens = wordpunct_tokenize(str(corpus))
words = [word.lower() for word in tokens]
for language in stopwords.fileids():
    stopwords_set = set(stopwords.words(language))
    words_set = set(words)
    common_elements = words_set.intersection(stopwords_set)

    languages_ratios[language] = len(common_elements)  # language "score"
language = max(languages_ratios, key=languages_ratios.get)

print("OKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK", language)
