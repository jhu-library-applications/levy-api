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
type = 'jsonapi/node/levy_collection_names/'

startTime = time.time()

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

# Open levy_collection_names CSV as DataFrame
filename = 'levy_collection_namesToCreate.csv'
df = pd.read_csv(filename)

# Loop through DataFrame and create JSON for each row
all_items = []
for index, row in df.iterrows():
    print(index)
    tax_item = {}
    tax_dict = {}
    full_type = 'node--levy_collection_names'
    title = row['title']
    tax_dict['type'] = full_type
    tax_dict['attributes'] = {'title': title, 'status': True}
    tax_item['data'] = tax_dict
    metadata = json.dumps(tax_item)

# Post levy_collection_name JSON to Drupal site and save results in dictonary
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    data = post.get('data')
    id = data.get('id')
    title = data['attributes']['title']
    link = data['links']['self']['href']
    results = {}
    results['title'] = title
    results['id'] = id
    results['link'] = link
    print(results)
    print('')
    all_items.append(results)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(all_items)
dt = datetime.now().strftime('%Y-%m-%d')
newFile = 'logOfNodeCollectionNamesAdded_'+dt+'.csv'
fullname = os.path.join(directory, newFile)
log.to_csv(fullname, index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
