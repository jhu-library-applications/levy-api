import requests
import secrets
import json
import pandas as pd
import time
import os

secretsVersion = input('To edit production server, enter secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
username = secrets.username
password = secrets.password

fileLink = 'jsonapi/file/file/'


username = secrets.username
password = secrets.password

# Authenicate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data).json()
print(session)
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

# Update headers for posting to Drupal
s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})

filename = 'filesToDelete.csv'
df = pd.read_csv(filename)

# Loop through DataFrame and create JSON for each row
all_items = []
for index, row in df.iterrows():
    file_uuid = row['file_uuid']

# Post taxonomy JSON to Drupal site and save results in dictonary
    full_link = baseURL+fileLink+file_uuid
    delete = s.delete(full_link, cookies=s.cookies)
    print(delete)
