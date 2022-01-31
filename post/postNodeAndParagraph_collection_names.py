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

startTime = time.time()

path = os.getcwd()
dir = os.path.dirname(path)
termsToCreate = os.path.join(dir, 'termsToCreate')
directory = os.path.join(dir, 'logs')
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
fullname = os.path.join(termsToCreate, filename)
df = pd.read_csv(fullname)

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
    type = 'jsonapi/node/levy_collection_names/'
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

# Create Paragraph collection_name spreadsheet
filename1 = 'matched_CollectionNames.csv'
filename2 = fullname

df_1 = pd.read_csv(filename1, header=0)
print(df_1.columns)
df_2 = pd.read_csv(filename2, header=0)
print(df_2.columns)

df_1.set_index('title', inplace=True)
df_2.set_index('title', inplace=True)

frame = df_1.combine_first(df_2)
frame.reset_index(inplace=True)
frame.rename(columns={'id': 'levy_collection_names_id'}, inplace=True)
frame.drop(['count', 'role', 'taxonomy', 'title', 'link'], axis=1, inplace=True)

frame['fileIdentifier'] = frame['fileIdentifier'].str.split('|')
frame.reset_index()
frame = frame.explode('fileIdentifier')
frame.sort_values(by=['fileIdentifier'], inplace=True)
dt = datetime.now().strftime('%Y-%m-%d')
newFile = 'logOfparagraph_collection_namesToAdd_'+dt+'.csv'
fullname3 = os.path.join(directory, newFile)
frame.to_csv(fullname3, index=False)

# Post Paragraph collection_name
endpoint = 'jsonapi/paragraph/collection_name/'
df_3 = pd.read_csv(fullname3)

allItems = []
for index, row in df_3.iterrows():
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
    paragraph_type = {'data': {'type': 'paragraphs_type--paragraphs_type',
                      'id': '36170ce3-1d71-462d-95d0-01167a11e679'}}
    relationships = {'paragraph_type': paragraph_type, 'field_name': field_name,
                     'field_roles': field_roles}
    data = {'data': {'type': 'paragraph--collection_name',
            'attributes': attributes, 'relationships': relationships}}
    metadata = json.dumps(data)
    post = s.post(baseURL+endpoint, data=metadata, cookies=s.cookies).json()
    data = post.get('data')
    if data:
        id = data.get('id')
        link = data['links']['self']['href']
        print(id, link)
        row['paragraph_id'] = id
        row['link'] = link
    else:
        row['link'] = 'error'
    allItems.append(row)


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
newFile = 'logOfParagraphCollectionName.csv'
fullname = os.path.join(directory, newFile)
log.to_csv(fullname, index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
