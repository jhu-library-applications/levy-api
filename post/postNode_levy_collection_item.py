import requests
import secret
import json
import time
import os
from datetime import datetime
import pandas as pd
import argparse

path = os.getcwd()
dir = os.path.dirname(path)
meta = os.path.join(dir, 'metadata-spreadsheet/')


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    metadata_file = args.file
else:
    metadata_file = input('Enter filename (including \'.csv\'): ')

secretsVersion = input('To edit production server, enter secrets file: ')
if secretsVersion != '':
    try:
        secret = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secret.baseURL
username = secret.username
password = secret.password

type = 'jsonapi/node/levy_collection_item/'

startTime = time.time()

# Authenticate to Drupal site, get token
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
    value = row.get(value)
    if pd.notna(value):
        attributes[field] = value
    else:
        pass

def createAttributeInteger(field, value):
    value = row.get(value)
    if pd.notna(value):
        value = str(value)
        value = value.strip()
        value = value.zfill(3)
        print(value)
        attributes[field] = value
    else:
        pass


def createRelation(field, type, value):
    multipleData = []
    value = row.get(value)
    if pd.notna(value):
        value = value.strip()
        if '|' in value:
            values = value.split('|')
            for v in values:
                entry = {'type': type, 'id': v}
                multipleData.append(entry)
            relationships[field] = {'data': multipleData}
        else:
            data = {'type': type, 'id': value}
            relationships[field] = {'data': data}
    else:
        pass


# Open file CSV as DataFrame
metadata_file = os.path.join(meta, metadata_file)
df = pd.read_csv(metadata_file)
index = df.index
total = len(index)

# Loop through DataFrame.
all_items = []
for i, row in df.iterrows():
    row = row
    logDict = {}
    attributes = {}
    relationships = {}
    paragraph_ids = row['paragraph_id']
    item_image_ids = row['image_id']
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
    createAttributeInteger('field_box', 'field_box')
    createAttribute('field_dedicatee', 'field_dedicatee')
    createAttribute('field_first_line', 'field_first_line')
    createAttribute('field_first_line_of_chorus', 'field_first_line_of_chorus')
    createAttribute('field_form_of_composition', 'field_form_of_composition')
    createAttribute('field_full_title', 'field_full_title')
    createAttribute('field_instrumentation', 'field_instrumentation')
    createAttribute('field_item_author', 'field_item_author')
    createAttributeInteger('field_item_id', 'field_item_id')
    createAttribute('field_plate_number', 'field_plate_number')
    createAttribute('field_publish_date_text', 'field_publish_date_text')
    createAttribute('field_publish_date_year', 'field_publish_date_year')
    relationships['node_type'] = {'data': {'type': 'node_type--node_type', 'id': '6e078db8-0496-441e-b636-e85d6855ec6a'}}
    createRelation('field_instrumentation_metadata',
                   'taxonomy_term--instrumentation_metadata',
                   'field_instrumentation_metadata_id')
    createRelation('field_publisher', 'taxonomy_term--publishers',
                   'field_publisher_id')
    createRelation('field_subjects', 'taxonomy_term--subjects',
                   'field_subjects_id')
    createRelation('field_pdf', 'file--file', 'pdf_id')
    metadata = {'data': {'type': 'node--levy_collection_item', 'attributes':
                attributes, 'relationships': relationships}}
    metadata = json.dumps(metadata)
    # Post levy_collection_item and get data.
    post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
    errors = post.get('errors')
    if errors:
        for error in errors:
            error = error['detail']
            print('Item patch errors: {}'.format(error))
    rdata = post.get('data')
    id = rdata.get('id')
    nid = rdata['attributes']['drupal_internal__nid']
    path = rdata['attributes']['path']
    title = rdata['attributes']['title']
    link = rdata['links']['self']['href']
    print('Item id {}, item nid {}'.format(id, nid))
    print('Item path {}'.format(path))
    logDict['title'] = title
    logDict['item_id'] = id
    logDict['item_nid'] = nid
    logDict['api_link'] = link

    # Update item's collection_name paragraphs.
    if pd.notna(paragraph_ids):
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
            post = s.patch(para_link, data=metadata, cookies=s.cookies).json()
            drupal_internal__id = post['data']['attributes']['drupal_internal__id']
            result = 'Paragraph {} patch results: {}.'.format(paragraph_id, drupal_internal__id)
            print('Paragraph {} of {}. {}'.format(count+1, total_para, result))
            errors = post.get('errors')
            if errors:
                for error in errors:
                    error = error['detail']
                    print('Item post errors: {}'.format(error))
            patches = logDict.get('para_patches')
            if patches is None:
                logDict['para_patches'] = result
            else:
                patches = patches+'|'+result
                logDict['para_patches'] = patches
            p_field = {"type": "paragraph--collection_name",
                       "id": paragraph_id,
                       "meta": {"target_revision_id": revisionID}}
            people_data.append(p_field)
        field_people = {'data': people_data}
    else:
        pass
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
        post = s.patch(image_link, data=metadata, cookies=s.cookies).json()
        drupal_internal__id = post['data']['attributes']['drupal_internal__id']
        errors = post.get('errors')
        if errors is None:
            result = 'Collection item image {} patch results: {}.'.format(image_id, drupal_internal__id)
        else:
            for error in errors:
                error = error['detail']
                print('Item post errors: {}'.format(error))
        print('Image {} of {}. {}'.format(count+1, total_images, result))
        patches = logDict.get('image_patches')
        if patches is None:
            logDict['image_patches'] = result
        else:
            patches = patches+'|'+result
            logDict['image_patches'] = patches
        i_field = {"type": "paragraph--collection_item_image",
                   "id": image_id,
                   "meta": {"target_revision_id": revisionID}}
        image_data.append(i_field)
    field_images = {'data': image_data}

    # Update field_people and field_images in levy_collection_item
    # with information from paragraphs.
    rdata['relationships']['field_people'] = field_people
    rdata['relationships']['field_images'] = field_images
    rdata['attributes']['revision_translation_affected'] = True
    metadata = {'data': rdata}
    metadata = json.dumps(metadata)
    patch = s.patch(baseURL+type+id, data=metadata, cookies=s.cookies).json()
    errors = patch.get('errors')
    if errors is None:
        print('Successful item patch')
        updatedPeople = patch['data']['relationships']['field_people']['data']
        updatedImages = patch['data']['relationships']['field_images']['data']
        logDict['itemPatch_people'] = updatedPeople
        logDict['itemPatch_people_total'] = len(updatedPeople)
        logDict['itemPatch_images'] = updatedImages
        logDict['itemPatch_images_total'] = len(updatedImages)
        print('')
    else:
        for error in errors:
            error = error['detail']
            print('Item patch errors: {}'.format(error))
    all_items.append(logDict)

# Convert log results to DataFrame, export as CSV.
log = pd.DataFrame.from_dict(all_items)
dt = datetime.now().strftime('%Y-%m-%d')
log.to_csv('logofLevyCollectionItems_'+dt+'.csv', index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
