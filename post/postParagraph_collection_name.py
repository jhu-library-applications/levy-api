import requests
import secrets
import json
import pandas as pd
import time
from datetime import datetime

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
type = 'jsonapi/paragraph/collection_name/'

startTime = time.time()

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


# Open file CSV as DataFrame
filename = 'filenames.csv'
df = pd.read_csv(filename)

allItems = []
for index, row in df.iterrows():
    row = row
    creator_role = row['creator_role_id']
    names_id = row['levy_collection_names_id']
    fileIdentifier = row['fileIdentifier']
    attributes = {'langcode': 'en', 'status': True,
                  'parent_type': 'node', 'parent_field_name': 'field_people'}
    field_name = {'data': {'type': 'node--levy_collection_names',
                  'id': names_id}}
    field_roles = {'data': {'type': 'taxonomy_term--creator_r',
                   'id': creator_role}}
    paragraph_type = {'data': {'type':'paragraphs_type--paragraphs_type',
                    'id':'36170ce3-1d71-462d-95d0-01167a11e679'}
    relationships = {'paragraph_type': paragraph_type, 'field_name': field_name,
                     'field_roles': field_roles}
    data = {'data': {'type': 'paragraph--collection_name',
            'attributes': attributes, 'relationships': relationships}}
    metadata = json.dumps(data)
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    data = post.get('data')
    id = data.get('id')
    link = data['links']['self']['href']
    print(id, link)
    row['paragraph_id'] = id
    row['link'] = link
    allItems.append(row)


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
dt = datetime.now().strftime('%Y-%m-%d')
log.to_csv('logofParagraphCollectionName_'+dt+'.csv')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
