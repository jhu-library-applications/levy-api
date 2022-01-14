import requests
import secrets
import json
import time
from datetime import datetime
import pandas as pd
import os

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
file = 'jsonapi/paragraph/collection_item_image/field_item_image'
type = 'jsonapi/paragraph/collection_item_image'

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

# Open file CSV as DataFrame
filename = 'filenames.csv'
df = pd.read_csv(filename)

allItems = []
for index, row in df.iterrows():
    row = row
    filename = row['filename']
    fileIdentifier = row['fileIdentifier']
    # Create Content-Disposition value using filename
    cd_value = 'file; filename="{}"'.format(filename)

    # Read file as binary
    data = open(filename, 'rb')

    # Update headers for posting file to Drupal, updated for each file
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/octet-stream',
                      'Content-Disposition': cd_value, 'X-CSRF-Token': token})
    # Post file
    post = s.post(baseURL+file, data=data, cookies=s.cookies).json()
    print(post)
    file_id = post['data']['id']
    row['file_id'] = file_id

    # Create JSON for collection_item_image
    attributes = {}
    attributes['parent_type'] = 'node'
    attributes['parent_field_name'] = 'field_images'
    attributes['field_restricted'] = False
    relationships = {}
    image_data = {'data': {'type': 'file--file', 'id': file_id,
                  'meta': {'alt': None, 'title': None}}}
    content_data = {'data': {'type': 'taxonomy_term--c',
                    'id': '5d6b9be2-46eb-4ef5-9697-ec52e06bcdc2'}}
    paragraph_data = {'data': {'type': 'paragraphs_type--paragraphs_type',
                      'id': '5caf7240-8349-415c-a858-e76b338dfa3f'}}
    relationships['field_item_image'] = image_data
    relationships['field_content_type'] = content_data
    relationships['paragraph_type'] = paragraph_data
    data = {'data': {'type': 'paragraph--collection_item_image',
            'attributes': attributes, 'relationships': relationships}}
    metadata = json.dumps(data)

    # Post collection_item_image to Drupal
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/vnd.api+json', 'X-CSRF-Token': token})
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    data = post.get('data')
    image_id = data.get('id')
    revision_id = data['attributes']['drupal_internal__revision_id']
    row['image_id'] = image_id
    row['revision_id'] = revision_id
    allItems.append(row)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
dt = datetime.now().strftime('%Y-%m-%d')
newFile = 'logOfParagraphCollectionItemImages_'+dt+'.csv'
fullname = os.path.join(directory, newFile)
log.to_csv(fullname)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
