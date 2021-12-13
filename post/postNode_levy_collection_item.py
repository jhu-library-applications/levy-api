import requests
import secrets
import json
import time
from datetime import datetime
import pandas as pd

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
type = 'jsonapi/node/levy_collection_item/'

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


def createAttribute(field, value):
    value = row[value].strip()
    if value != '':
        attributes[field] = value
    else:
        pass


def createRelation(field, type, value):
    multipleData = []
    value = row[value].strip()
    if value != '':
        if '|' in value:
            values = value.split('|')
            for v in values:
                entry = {'type': type, 'id': value}
                multipleData.append(entry)
            relationships[field] = {'data': multipleData}
        else:
            data = {'type': type, 'id': value}
            relationships[field] = {'data': data}
    else:
        pass


# Open file CSV as DataFrame
filename = 'filenames.csv'
df = pd.read_csv(filename)

allItems = []
for index, row in df.iterrows():
    row = row
    attributes = {}
    relationships = {}
    paragraph_ids = row['paragraph_ids']
    item_image_ids = row['item_image_ids']
    fileIdentifier = row['fileIdentifier']
    attributes['langcode'] = 'en'
    attributes['status'] = True
    createAttribute('title', 'title')
    createAttribute('field_advertisement', 'field_advertisement')
    createAttribute('field_artist', 'field_artist')
    createAttribute('field_box', 'field_box')
    createAttribute('field_dedicatee', 'field_dedicatee')
    createAttribute('field_first_line', 'field_first_line')
    createAttribute('field_first_line_of_chorus', 'field_first_line_of_chorus')
    createAttribute('field_form_of_composition', 'field_form_of_composition')
    createAttribute('field_full_title', 'field_full_title')
    createAttribute('field_instrumentation', 'field_instrumentation')
    createAttribute('field_item_author', 'field_item_author')
    createAttribute('field_item_id', 'field_item_id')
    createAttribute('field_plate_number', 'field_plate_number')
    createAttribute('field_publish_date_text', 'field_publish_date_text')
    createAttribute('field_publish_date_year', 'field_publish_date_year')
    createRelation('node_type', 'node_type--node_type', '')
    createRelation('field_instrumentation_metadata',
                   'taxonomy_term--instrumentation_metadata',
                   'field_instrumentation_metadata')
    createRelation('field_publisher', 'taxonomy_term--publishers',
                   'field_publisher')
    createRelation('field_subjects', 'taxonomy_term--subjects',
                   'field_subjects')
    metadata = {'data': {'type': 'node--levy_collection_item', 'attributes':
                attributes, 'relationships': relationships}}
    metadata = json.dumps(metadata)
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    print(post.get('errors'))
    rdata = post.get('data')
    id = rdata.get('id')
    nid = rdata['attributes']['drupal_internal__nid']
    print(nid)
    link = rdata['links']['self']['href']
    print(rdata['relationships']['field_people'])
    print(id, link)

    paragraph_ids = paragraph_ids.split('|')
    people_data = []
    for paragraph_id in paragraph_ids:
        ptype = 'jsonapi/paragraph/collection_name/'
        para = s.get(baseURL+ptype+paragraph_id, cookies=s.cookies).json()
        paradata = para.get('data')
        attributes = paradata['attributes']
        attributes['parent_id'] = nid
        revisionID = attributes["drupal_internal__revision_id"]
        metadata = json.dumps(para)
        post = s.patch(baseURL+ptype+paragraph_id, data=metadata, cookies=s.cookies).json()
        data = post.get('data')
        print(post)
        print(data['attributes']['parent_id'])
        print('')
        p_field = {"type": "paragraph--collection_name",
                   "id": paragraph_id,
                   "meta": {"target_revision_id": revisionID}}
        people_data.append(p_field)
    field_people = {'data': people_data}

    item_image_ids = item_image_ids.split('|')
    image_data = []
    for image_id in item_image_ids:
        itype = 'jsonapi/paragraph/collection_item_image/'
        image = s.get(baseURL+itype+image_id, cookies=s.cookies).json()
        imagedata = image.get('data')
        attributes = imagedata['attributes']
        attributes['parent_id'] = nid
        revisionID = attributes["drupal_internal__revision_id"]
        metadata = json.dumps(image)
        post = s.patch(baseURL+itype+image_id, data=metadata, cookies=s.cookies).json()
        data = post.get('data')
        print(post)
        print(data['attributes']['parent_id'])
        print('')
        i_field = {"type": "paragraph--collection_item_image",
                   "id": paragraph_id,
                   "meta": {"target_revision_id": revisionID}}
        image_data.append(i_field)
    field_images = {'data': people_data}

    rdata['relationships']['field_people'] = field_people
    rdata['relationships']['field_images'] = field_images
    rdata['attributes']['revision_translation_affected'] = True
    metadata = {'data': rdata}
    metadata = json.dumps(metadata)
    patch = s.patch(baseURL+type+id, data=metadata, cookies=s.cookies).json()
    errors = patch.get('errors')
    print(errors)
    if errors is None:
        print(patch['data']['relationships']['field_people'])
        print(patch['data']['attributes']['revision_translation_affected'])


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
dt = datetime.now().strftime('%Y-%m-%d')
log.to_csv('logofParagraphCollectionName_'+dt+'.csv')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
