import csv

import parameters
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from parsel import Selector

# defining new variable passing two paramaters
writer = csv.writer(open(parameters.file_name, 'w'))

# writerow() method to the write to the file object
writer.writerow(['Name','Job Title','Company','College', 'Location','URL', 'Description'])
driver = webdriver.Firefox(executable_path=r'E:\geckodriver.exe')
driver.get('https://www.linkedin.com')

username = driver.find_element_by_class_name('login-email')
username.send_keys(parameters.linkedin_username)
sleep(0.5)

password = driver.find_element_by_class_name('login-password')
password.send_keys(parameters.linkedin_password)
sleep(0.5)

sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')
sign_in_button.click()
sleep(0.5)

driver.get('https://www.google.com')
sleep(3)

search_query = driver.find_element_by_name("q")
search_query.send_keys(parameters.search_query)
sleep(0.5)

search_query.send_keys(Keys.RETURN)
sleep(3)

linkedin_urls = driver.find_elements_by_class_name('iUh30')

linkedin_urls = [url.text for url in linkedin_urls]
sleep(0.5)
for linkedin_url in linkedin_urls:

   # get the profile URL
   driver.get(linkedin_url)

   # add a 5 second pause loading each URL
   sleep(5)

   # assigning the source code for the webpage to variable sel
   sel = Selector(text=driver.page_source)

   # xpath to extract the text from the class containing the name
   name = sel.xpath('//*[starts-with(@class,"pv-top-card-section__name")] / span / text()').extract_first()

   if name:
       name = name.strip()

   Description = sel.xpath('//*[starts-with(@class,"pv-skill-category-list__skills_list list-style-none")] / ol / text()').extract_first()
   #if Description:
       #Description = Description.strip()
   print(Description, "BBBBBBBBBBBBBBBBBBBBBBBBBBBB")

   # xpath to extract the text from the class containing the job title
   job_title = sel.xpath('//*[starts-with(@class,"pv-top-card-section__headline")] / text()').extract_first()

   if job_title:
       job_title = job_title.strip()

   # xpath to extract the text from the class containing the company
   #company = sel.xpath('//*[starts-with(@class,"pv-top-card-v2-section__entity-name pv-top-card-v2-section__company-name")] / text()').extract_first()
   company = sel.xpath('//*[starts-with(@class,"pv-top-card-v2-section__entity-name pv-top-card-v2-section__company-name")] / span / text()').extract_first()
   if company:
       company = company.strip()
       print(company,"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")

   # xpath to extract the text from the class containing the college
   college = sel.xpath('//*[starts-with(@class,"pv-top-card-v2-section__entity-name pv-top-card-v2-section__school-name")] / span / text()').extract_first()

   if college:
       college = college.strip()

   # xpath to extract the text from the class containing the location
   location = sel.xpath('//*[starts-with(@class,"pv-top-card-section__location")] / text()').extract_first()

   if location:
       location = location.strip()



   linkedin_url = driver.current_url
   writer.writerow([name,
                    job_title,
                    company,
                    college,
                    location,
                    linkedin_url,
                    Description])


driver.quit()

