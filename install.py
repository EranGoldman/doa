from os import remove
from sys import argv
import sqlite3
import string
from random import *
import hashlib

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


conn = sqlite3.connect('db/database.db')
characters = string.ascii_letters + string.punctuation + string.digits

print('Initializing DB ... ', end='')
with open('db/schema.sql', mode='r') as f:
    conn.cursor().executescript(f.read())
conn.commit()
print(bcolors.OKGREEN + ('OK'))
asciil = string.ascii_letters
user = "".join(choice(asciil) for x in range(randint(8, 12))).lower() \
        + "@yopmail.com"
adminUser = input("Admin email ("+user+") : ")
password = "".join(choice(characters) for x in range(randint(16, 24)))
adminPass = input("Admin password (default: "+password+") : ")
if adminUser == "":
    adminUser = user
if adminPass == "":
    adminPass = password
hash = hashlib.sha512()
hash.update(('%s' % adminPass).encode('utf-8'))
adminPass = hash.hexdigest()

query = "INSERT INTO zx_users (EMAIL,PASSWORD,ROLE) "
query += "VALUES ('"
query += adminUser
query += "','"
query += adminPass
query += "','admin');"
conn.execute(query)
conn.commit()

useMailgun = input("Do you want to use mailgun (N) ?")
if (useMailgun == 'Y' or useMailgun == 'y' or useMailgun.lower() == 'yes'):
    mailgunurl = input("Your mailgun domain : ")
    mailgunapi = input("Your mailgun api : ")
    query = "INSERT INTO mailgunCred (domain, apikey) "
    query += "VALUES ('https://api.mailgun.net/v2/"
    query += mailgunurl
    query += "/messages','" + mailgunapi + "')"
    conn.execute(query)
    conn.commit()

conn.close()
print('It is a good practice to delete the installation script.')
deleteSelf = input('Do you agree (Y) ? ')
if (deleteSelf == 'Y' or deleteSelf == 'y'):
    remove(argv[0])
