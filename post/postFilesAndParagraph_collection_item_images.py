import requests
import json
import simplejson
import time
import pandas as pd
import os
import argparse
import secret

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

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


image_type = 'jsonapi/paragraph/collection_item_image'

startTime = time.time()

# Finds directory levy-api/logs
path = os.getcwd()
dir = os.path.dirname(path)
directory = os.path.join(dir, 'logs')
if not os.path.exists(directory):
    os.mkdir(directory)

# Authenticate to Drupal site, get token
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


def postFile(file, endpoint, file_type, fileIdentifier):
    # Create log for posting file.
    fileLog = {'filename': file, 'fileIdentifier': fileIdentifier}

    # Create Content-Disposition value using filename for header.
    cd_value = 'file; filename="{}"'.format(file)
    print(cd_value)
    # Read file as binary.
    data = open(file, 'rb')

    # Update headers for posting file to Drupal, updated for each file.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/octet-stream',
                      'Content-Disposition': cd_value, 'X-CSRF-Token': token})
    # Post file.
    try:
        post = s.post(baseURL+endpoint, data=data, cookies=s.cookies).json()
        print(post)
        file_id = post['data']['id']
        fileLog['postType'] = 'file'
        fileLog[file_type] = file_id
    except simplejson.errors.JSONDecodeError:
        fileLog['postType'] = 'file'
        fileLog[file_type] = 'UPLOAD FAILED'
        file_id = False
    all_items.append(fileLog)
    return file_id


# Create JSON for collection_item_image.
def createCollectionItemImage(file_id):
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
    return metadata


def postCollectionItemImage(metadata, fileIdentifier, file_id, file):
    # Creates log for posting paragraph collection_item_image.
    fileLog = {'fileIdentifier': fileIdentifier, 'file_id': file_id,
               'filename': file}

    # Updates header for posting paragraph.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/vnd.api+json', 'X-CSRF-Token': token})

    # Try to post new paragraph collection_item_image.
    try:
        post = s.post(baseURL+image_type, data=metadata, cookies=s.cookies).json()
        print(post)
        # Gets paragraph data for log
        data = post.get('data')
        image_id = data.get('id')
        revision_id = data['attributes']['drupal_internal__revision_id']

        # Records data for log.
        fileLog['postType'] = 'collection_item_image'
        fileLog['image_id'] = image_id
        fileLog['revision_id'] = revision_id
    except json.decoder.JSONDecodeError:
        fileLog['postType'] = 'collection_item_image'
        fileLog['image_id'] = 'UPLOAD FAILED'
        fileLog['revision_id'] = 'UPLOAD FAILED'
    all_items.append(fileLog)


# Open file CSV as DataFrame.
df = pd.read_csv(filename)

all_items = []
for index, row in df.iterrows():
    print('Posting files for item {}'.format(index))
    fileIdentifier = row['fileIdentifier']
    image = row.get('image')
    images = image.split('|')
    image_directory = row.get('image_directory')
    copyright = row.get('copyright')

    # Only post PDF files if item has no copyright.
    if copyright == 'noCopyright':
        pdf = row.get('pdf')
        pdf_directory = row.get('pdf_directory')
        file = os.path.join(pdf_directory, pdf)
        file_type = 'pdf_id'
        endpoint = 'jsonapi/node/levy_collection_item/field_pdf'
        file_id = postFile(file, endpoint, file_type, fileIdentifier)
        print(file_id)
        for image in images:
            file = os.path.join(image_directory, image)
            file_type = 'file_id'
            endpoint = 'jsonapi/paragraph/collection_item_image/field_item_image'
            file_id = postFile(file, endpoint, file_type, fileIdentifier)
            print(file_id)
            if file_id:
                metadata = createCollectionItemImage(file_id)
                postCollectionItemImage(metadata, fileIdentifier, file_id, file)
    else:
        for image in images:
            file = os.path.join(image_directory, image)
            file_type = 'file_id'
            endpoint = 'jsonapi/paragraph/collection_item_image/field_item_image'
            file_id = postFile(file, endpoint, file_type, fileIdentifier)
            print(file_id)
            if file_id:
                metadata = createCollectionItemImage(file_id)
                postCollectionItemImage(metadata, fileIdentifier, file_id, file)


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_records(all_items)
newFile = 'logOfImagesAndPDFs.csv'
fullname = os.path.join(directory, newFile)
log.to_csv(fullname, index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
