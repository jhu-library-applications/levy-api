import requests
import secrets
import json
import simplejson
import time
import pandas as pd
import os
import argparse

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

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

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


# Function grabs name and uris from collection_name.
def fetchData(data):
    attributes = data.get('attributes')
    id = data.get('id')
    filename = attributes.get('filename')
    uri = attributes.get('uri')
    filesize = attributes.get('filesize')
    itemDict['id'] = id
    print('Successfully retrieved file metadata for {}'.format(id))
    itemDict['filename'] = filename
    itemDict['uri'] = uri
    itemDict['filesize'] = filesize


def postFile(file, endpoint):
    # Create Content-Disposition value using filename for header.
    cd_value = 'file; filename="{}"'.format(file)

    # Read file as binary.
    data = open(file, 'rb')

    # Update headers for posting file to Drupal, updated for each file.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/octet-stream',
                      'Content-Disposition': cd_value, 'X-CSRF-Token': token})
    # Post file.
    try:
        post = s.post(baseURL+endpoint, data=data, cookies=s.cookies).json()
        data = post.get('data')
        id = data.get('id')
        attributes = data.get('attributes')
        filename = attributes.get('filename')
        uri = attributes.get('uri')
        filesize = attributes.get('filesize')
        itemDict['new_id'] = id
        itemDict['new_filename'] = filename
        itemDict['new_uri'] = uri
        itemDict['new_filesize'] = filesize
        itemDict['upload'] = 'Success'
        print('Upload successful')
    except simplejson.errors.JSONDecodeError:
        itemDict['upload'] = 'Failure'
        print('Upload failure')
    allItems.append(itemDict)


# Open file CSV as DataFrame.
df = pd.read_csv(filename)

allItems = []
for index, row in df.iterrows():
    itemDict = {}
    print('Replacing file {}'.format(index))
    filename = row.get('filename')
    image_directory = row.get('image_directory')
    id = row['id']
    endpoint = 'jsonapi/file/file/'+id
    r = s.get(baseURL+endpoint).json()
    data = r.get('data')
    fetchData(data)
    file = os.path.join(image_directory, filename)
    postFile(file, endpoint)


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
log.to_csv('logReplacingImages.csv', index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
