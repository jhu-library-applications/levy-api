import requests
import secrets
import json
import pandas as pd
import time
from datetime import datetime
import os

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
taxonomyLink = 'jsonapi/taxonomy_term/'

startTime = time.time()

termsToCreate = '/Users/michelle/Documents/GitHub/levy-api/termsToCreate'
directory = '/Users/michelle/Documents/GitHub/levy-api/logs'
if not os.path.exists(directory):
    os.mkdir(directory)

# Authenicate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data).json()
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

# Update headers for posting to Drupal
s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                  'application/vnd.api+json', 'X-CSRF-Token': token})

# Open taxonomy CSV as DataFrame
filename = 'taxonomyTermsToCreate.csv'
fullname = os.path.join(termsToCreate, filename)
df = pd.read_csv(fullname)

# Loop through DataFrame and create JSON for each row
all_items = []
for index, row in df.iterrows():
    row = row
    print(index)
    tax_item = {}
    tax_dict = {}
    tax_type = row['taxonomy']
    full_type = 'taxonomy_term--'+tax_type
    name = row['name']
    tax_dict['type'] = full_type
    tax_dict['attributes'] = {'name': name, 'status': True}
    tax_item['data'] = tax_dict
    metadata = json.dumps(tax_item)

# Post taxonomy JSON to Drupal site and save results in dictonary
    full_link = baseURL+taxonomyLink+tax_type
    post = s.post(full_link, data=metadata, cookies=s.cookies).json()
    data = post.get('data')
    id = data.get('id')
    link = data['links']['self']['href']
    row['name'] = name
    row['id'] = id
    row['link'] = link
    print('name')
    print('')
    all_items.append(row)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(all_items)
dt = datetime.now().strftime('%Y-%m-%d')
newFile = 'logOfTaxonomyTermsAdded_'+dt+'.csv'
fullname = os.path.join(directory, newFile)
log.to_csv(fullname, index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
