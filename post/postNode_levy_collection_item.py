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
index = df.index
total = len(index)

# Loop through DataFrame.
allItems = []
for i, row in df.iterrows():
    row = row
    logDict = {}
    attributes = {}
    relationships = {}
    paragraph_ids = row['paragraph_ids']
    item_image_ids = row['item_image_ids']
    fileIdentifier = row['fileIdentifier']
    logDict['fileIdentifier'] = fileIdentifier
    statement = 'Item {}, number {} of {}'.format(fileIdentifier, i+1, total)
    print(statement)
    # Create JSON for levy_collection_item
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
    relationships['node_type'] = {'data': {'type': 'node_type--node_type', 'id': '6e078db8-0496-441e-b636-e85d6855ec6a'}}
    createRelation('field_instrumentation_metadata',
                   'taxonomy_term--instrumentation_metadata',
                   'field_instrumentation_metadata')
    createRelation('field_publisher', 'taxonomy_term--publishers',
                   'field_publisher')
    createRelation('field_subjects', 'taxonomy_term--subjects',
                   'field_subjects')
    createRelation('field_pdf', 'file--file', 'field_pdf')
    metadata = {'data': {'type': 'node--levy_collection_item', 'attributes':
                attributes, 'relationships': relationships}}
    metadata = json.dumps(metadata)
    # Post levy_collection_item and get data.
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    errors = post.get('errors')
    print('Item post errors: {}'.format(errors))
    rdata = post.get('data')
    id = rdata.get('id')
    nid = rdata['attributes']['drupal_internal__nid']
    path = rdata['attributes']['path']
    link = rdata['links']['self']['href']
    print('Item id {}, item nid {}'.format(id, nid))
    print('Item path {}'.format(path))
    logDict['item_id'] = id
    logDict['item_nid'] = nid
    logDict['item_link'] = link

    # Update item's collection_name paragraphs.
    paragraph_ids = paragraph_ids.split('|')
    total_para = len(paragraph_ids)
    logDict['total_para'] = total_para
    people_data = []
    for count, paragraph_id in enumerate(paragraph_ids):
        ptype = 'jsonapi/paragraph/collection_name/'
        para_link = baseURL+ptype+paragraph_id
        para = s.get(para_link, cookies=s.cookies).json()
        paradata = para.get('data')
        attributes = paradata['attributes']
        attributes['parent_id'] = nid
        revisionID = attributes["drupal_internal__revision_id"]
        metadata = json.dumps(para)
        post = s.patch(para_link, data=metadata, cookies=s.cookies)
        result = 'Paragraph {} patch results: {}.'.format(image_id, post)
        print('Paragraph {} of {}. {}'.format(count, total_para, result))
        patches = logDict.get('para_patches')
        if patches is None:
            logDict['para_patches'] = result
        else:
            patches = patches+'|'+result
            logDict['para_patches'] = result
        p_field = {"type": "paragraph--collection_name",
                   "id": paragraph_id,
                   "meta": {"target_revision_id": revisionID}}
        people_data.append(p_field)
    field_people = {'data': people_data}

    # Update item's collection_item_image paragraphs.
    item_image_ids = item_image_ids.split('|')
    total_images = len(item_image_ids)
    logDict['total_images'] = total_images
    image_data = []
    for count, image_id in enumerate(item_image_ids):
        itype = 'jsonapi/paragraph/collection_item_image/'
        image_link = baseURL+itype+image_id
        image = s.get(image_link, cookies=s.cookies).json()
        imagedata = image.get('data')
        attributes = imagedata['attributes']
        attributes['parent_id'] = nid
        revisionID = attributes["drupal_internal__revision_id"]
        metadata = json.dumps(image)
        post = s.patch(image_link, data=metadata, cookies=s.cookies)
        result = 'Image {} patch results: {}'.format(image_id, post)
        print('Image {} of {}. {}'.format(count, total_images, result))
        patches = logDict.get('image_patches')
        if patches is None:
            logDict['image_patches'] = result
        else:
            patches = patches+'|'+result
            logDict['image_patches'] = result
        i_field = {"type": "paragraph--collection_item_image",
                   "id": image_id,
                   "meta": {"target_revision_id": revisionID}}
        image_data.append(i_field)
    field_images = {'data': people_data}

    # Update field_people and field_images in levy_collection_item
    # with information from paragraphs.
    rdata['relationships']['field_people'] = field_people
    rdata['relationships']['field_images'] = field_images
    rdata['attributes']['revision_translation_affected'] = True
    metadata = {'data': rdata}
    metadata = json.dumps(metadata)
    patch = s.patch(baseURL+type+id, data=metadata, cookies=s.cookies).json()
    errors = patch.get('errors')
    print('Item patch errors: {}'.format(errors))
    if errors is None:
        print('Successful item patch')
        updatedPeople = patch['data']['relationships']['field_people'])
        updatedImages = patch['data']['relationships']['field_images'])
        logDict['itemPatch_people'] = updatedPeople
        logDict['itemPatch_images'] = updatedImages
        print('')
    allItems.append(logDict)

# Convert log results to DataFrame, export as CSV.
log = pd.DataFrame.from_dict(allItems)
dt = datetime.now().strftime('%Y-%m-%d')
log.to_csv('logofParagraphCollectionName_'+dt+'.csv')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
