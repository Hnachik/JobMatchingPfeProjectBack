import pymysql
import csv

f = open(r"Cleaningdata.csv", "r", encoding="utf-8-sig")
fString = f.read()

fList = []
for line in fString.split("\n"):
    fList.append(line.split(','))
print(fList[0][0])
print("okkkkkkk")
# connect to database
db = pymysql.connect("localhost", "samar", "samar", "TalentHunter")

# prepare cursos object
cursor = db.cursor()

# drop table if it already exist
cursor.execute("DROP TABLE IF EXISTS JOB")

# create column names from the first line in the file
company = fList[0][0];
position = fList[0][1];
url = fList[0][2];
location = fList[0][3];
jobDescription = fList[0][4]

# create student table

jobs = """CREATE TABLE JOB(
       {} varchar(255) NOT NULL,
       {} varchar(255) not null,
       {} varchar(255) not null,
       {} varchar(255) not null,
       {} varchar(65000)
        )""".format(company, position, url, location, jobDescription)
cursor.execute(jobs)
db.close()
