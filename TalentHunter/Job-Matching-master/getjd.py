from bs4 import BeautifulSoup
import json
import urllib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

with open('url.json', 'r') as f:
    url = json.load(f)
data = {}

i = 1
jd_df = pd.DataFrame()

driver = webdriver.Firefox(executable_path=r'E:\geckodriver.exe')

for u in url:
    driver.wait = WebDriverWait(driver, 5)
    driver.maximize_window()
    driver.get(u)
    #    r = urllib.urlopen(u).read()
    soup = BeautifulSoup(driver.page_source, "lxml")
    #    jd_df['position'] =
    # print (soup)
    header = soup.find("div", {"class": "cell tbl logoHeader"})
    # header = soup.find("div",{"class":"header cell info"})
    position = header.find('h2').get_text()
    print("*************************", position)
    company = header.find("span", {"class": "ib"}).get_text()
    location = header.find("span", {"class": "subtle ib"}).get_text()[2:]
    try:
        jd = soup.find("div", {"class": "jobDescriptionContent desc"}).get_text()
    except:
        jd = None
    #    website = soup.find("span",{"class":"value website"}).get_text()
    info = soup.find_all("div", {"class": "infoEntity"})
    try:
        headquaters = info[1].find("span", {"class": "value"}).get_text().strip().strip(r'\u')
        employees = info[2].find("span", {"class": "value"}).get_text().strip().strip(r'\u')
        founded = info[3].find("span", {"class": "value"}).get_text().strip().strip(r'\u')
        industry = info[5].find("span", {"class": "value"}).get_text().strip().strip(r'\u')
    except:
        headquaters = None
        employees = None
        founded = None
        industry = None
    #    revenue = info[6].find("span",{"class":"value"}).get_text().strip()
    #    competitors = info[7].find("span",{"class":"value"}).get_text().strip()
    data[i] = {
        'url': u,
        'company': company,
        'position': position,
        'location': location,
        #        'website':website,
        #        'revenue' :revenue,
        #        'competitors' :competitors,
        'Job Description': jd
    }
    print(i)
    i += 1

driver.quit()
jd_df = pd.DataFrame(data)
jd = jd_df.transpose()
# cols = jd.columns.tolist()
# print cols
jd = jd[['company', 'position', 'url', 'location', 'Job Description']]
jd.to_csv('data.csv', encoding="utf-8")
