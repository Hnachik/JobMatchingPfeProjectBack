from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import json
from bs4 import BeautifulSoup

driver = webdriver.Firefox(executable_path=r'C:\Users\Amin\Downloads\geckodriver-v0.24.0-win64_2\geckodriver.exe')


# driver.get('http://inventwithpython.com')

# driver = webdriver.Firefox()
def openbrowser(locid=236, key='java'):
    driver.wait = WebDriverWait(driver, 5)
    driver.maximize_window()
    words = key.split()
    txt = ''
    for w in words:
        txt += (w + '+')
    #    print txt
    driver.get(
        "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=true&clickSource=searchBtn&typedKeyword"
        "={}&sc.keyword={}&locT=N&locId={}&jobType=".format(
            txt[:-1], txt[:-1], locid))
    return driver


# s = urllib.urlopen('file:///C:/UTA/Data%20Science/Project2/pokemon_5378/data/{}/{}'.format(folder,files)).read()
def geturl(driver):
    trouve = 0
    url = set()
    while True:
        print("trouve= ", trouve)
        trouve = trouve + 1
        # while (trouve==1):
        soup1 = BeautifulSoup(driver.page_source, "lxml")

        main = soup1.find_all("li", {"class": "jl"})

        for m in main:
            url.add('https://www.glassdoor.com{}'.format(m.find('a')['href']))
            print(len(url))

        #    print url
        next_element = soup1.find("li", {"class": "next"})
        if next_element is not None:
            next_exist = next_element.find('a')
            print("nexttt:", next_exist)
            if next_exist is not None:
                print("yess")
                driver.find_element_by_class_name("next").click()
                print("okkkk")
                time.sleep(10)
            else:
                trouve = 0
                driver.quit()
            break
            print("okkkk")
        else:
            print("okk")
            trouve = 0
            driver.quit()
        break
        print("trouve=", trouve)
    return list(url)


x = openbrowser(key='java')
with open('url.json', 'w') as f:
    json.dump(geturl(driver), f, indent=4)
