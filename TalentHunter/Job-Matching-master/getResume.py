import pandas as pd
import numpy as np


df =pd.read_csv('test.csv')
jd = df['jobDescription'].tolist()
skills=df['allSkills'].tolist()
Job=[]

for i in range(209):
    s=str(df['jobDescription'][i])+ "  "+str(df['allSkills'][i])
    Job.append(s)

print(len(Job))
print(Job[0])
