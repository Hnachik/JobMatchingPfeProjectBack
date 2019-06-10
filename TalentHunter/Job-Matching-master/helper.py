import csv
import json
import pandas as pd
import numpy as np
import pickle
import re
from time import sleep  # So we don't request too much from the server
from collections import Counter  # Keep track of counts
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.common.exceptions import NoSuchElementException
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

data = []
with open('data.csv') as csvFile:
    csvReader = csv.DictReader(csvFile)
    for csvRow in csvReader:
        data.append(csvRow)

job_dict = {}
desc_dict = {}

for item in data:
    pk = item['id']
    job_dict[pk] = [item['position'], item['company'], item['url'], item['location']]
    desc_dict[pk] = item['job_description']


def clean_job_text(job_title, words):
    for word in words:
        job_title = job_title.replace(word, "")
    return job_title


'''
Clean up text
Input: Description from desc_dict
Output: Cleaned text
'''


def text_cleaner(text_temp):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words("french"))
    text = text_temp.strip("\n")  # break into lines
    text = re.sub("[^a-zA-Z.+3]", " ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)
    # Also include + for C++
    text = text.lower()  # Go to lower case
    text = text.split()  # and split them apart
    text = [w for w in text if not w in stopwords]
    return text


from nltk.corpus import stopwords

cachedStopWords = stopwords.words("french")


def text_cleaner(text_temp):
    text = text_temp.lower()
    text = re.sub("[^a-zA-Z.+3]", " ", text)
    text = text.strip("\n")
    text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    return text


''' 
Input a cv and a job
Job_dict should be j_id key, then description
For key,value in job_dict.items():
    sim[key] = get_sim(cv, value, item) etc
Returns cosine tfid similarity
'''


def get_sim(cv, job_desc):
    sim_vec = TfidfVectorizer(min_df=1)
    tfidf = sim_vec.fit_transform([cv, job_desc])  # tfidf vectorization
    sim_array = (tfidf * tfidf.T).A  # cosine similarity
    sim = sim_array[0][1]
    return sim


'''
Input cv, and all jobs in the dictionary
Return a sorted list of tuples (job_id, similarity)
'''


def best_match(cv, d_dict):
    cv_cleaned = text_cleaner(cv)
    sim = {}
    new_desc_dict = clean_dict(d_dict)
    for key, value in new_desc_dict.items():
        sim[key] = get_sim(cv_cleaned, value)
    best_match_dict = sorted(sim.items(), key=lambda x: x[1], reverse=True)
    return best_match_dict


def clean_dict(d_dict):
    new_dict = {}
    for key, value in d_dict.items():
        new_dict[key] = text_cleaner(value)
    return new_dict


with open('res.txt', 'r') as f:
    # with open('res.txt', 'r') as f:
    cv = f.read()

match_list = best_match(cv, desc_dict)
print(match_list)
num_jobs = len(job_dict)
best_matches = {}
for i in range(num_jobs):
    j_id = match_list[i][0]
    best_matches[j_id] = job_dict[j_id]
best_match_df = pd.DataFrame.from_dict(best_matches, orient="index")
best_match_df.columns = ["Title", "Company", "Location", "Link"]
best_match_df['Title'] = best_match_df['Title'].apply(lambda x: clean_job_text(x, ["Apply", "Save", "Now", "Easy"]))
best_match_df.to_csv('best_match_df.csv', encoding="utf-8")

# with open('happy.json', 'w') as jsonFile:
#     jsonFile.write(json.dumps(data, indent=4))
