import requests
import secret
import json
import simplejson
import time
import pandas as pd
import os
import argparse

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

startTime = time.time()

# Save terminal output to file.
# python3 replaceImage.py -f somefile.csv | tee output.txt
# Output stream will be copied to txt file and still be visible in terminal.
# If txt file already exists, it gets overwritten.

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


# Function grabs data from file metadata object.
def fetch_data(url):
    try:
        r = s.get(url).json()
        data = r.get('data')
        attributes = data.get('attributes')
        old_id = data.get('id')
        filename = attributes.get('filename')
        uri = attributes.get('uri')
        filesize = attributes.get('filesize')
        print('Successfully retrieved file metadata for {}'.format(old_id))
        item_dict['old_filename'] = filename
        item_dict['old_uri'] = uri['url']
        item_dict['old_filesize'] = filesize
    except simplejson.errors.JSONDecodeError:
        old_id = False
    except AttributeError:
        old_id = False
    return old_id


def deleteFile(url):
    s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})
    delete = s.delete(url, cookies=s.cookies)
    status = delete.status_code
    print(status)
    if status == 204:
        results = True
    else:
        results = False
    item_dict['old_file_deleted'] = results
    return results


def postFile(file):
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
        endpoint = 'jsonapi/paragraph/collection_item_image/field_item_image'
        post = s.post(baseURL+endpoint, data=data, cookies=s.cookies).json()
        data = post.get('data')
        new_id = data.get('id')
        attributes = data.get('attributes')
        filename = attributes.get('filename')
        uri = attributes.get('uri')
        filesize = attributes.get('filesize')
        item_dict['new_id'] = new_id
        item_dict['new_filename'] = filename
        item_dict['new_uri'] = uri['url']
        item_dict['new_filesize'] = filesize
        item_dict['upload_new_file'] = True
        print('Upload successful')
    except simplejson.errors.JSONDecodeError:
        item_dict['upload_new_file'] = False
        new_id = False
        print('Upload failure')
    return new_id


def patchCollectionItemImage(old_id, new_id, paragraph_id):

    # Get collection_item_image metadata.
    type = 'jsonapi/paragraph/collection_item_image/'
    r = s.get(baseURL+type+paragraph_id, cookies=s.cookies).json()
    data = r.get('data')
    image = data['relationships']['field_item_image']['data']
    # Update file id in metadata.
    image['id'] = new_id
    del data['relationships']['field_item_image']['data']['meta']
    metadata = {"data": data}
    metadata = json.dumps(metadata)

    # Updates header for posting paragraph.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/vnd.api+json', 'X-CSRF-Token': token})
    # Try to patch new paragraph collection_item_image.
    try:
        patch = s.patch(baseURL+type+paragraph_id, data=metadata,
                        cookies=s.cookies).json()
        # Gets paragraph data for log
        data = patch.get('data')
        para_image_id = data.get('id')
        file_id = data['relationships']['field_item_image']['data']['id']
        patch_results = True
        # Records data for log.
        item_dict['patch_posted'] = patch_results
        item_dict['para_image_id'] = para_image_id
        item_dict['file_id'] = file_id
    except json.decoder.JSONDecodeError:
        patch_results = False
        item_dict['patchSuccessful'] = patch_results
    return patch_results


# Open file CSV as DataFrame.
df = pd.read_csv(filename)

all_items = []
for index, row in df.iterrows():
    print('Replacing file {}'.format(index+1))
    fileIdentifier = row.get('fileIdentifier')
    filename = row.get('filename')
    paragraph_id = row.get('paragraph_id')
    old_id = row.get('file_id')
    filesize = row.get('filesize')
    image_directory = 'H:\Lester S. Levy Sheet Music Collection\9. Gottesman Images Output\LevyImageFilesForSam72DPI_1000pxMAX'
    item_dict = {'fileIdentifier': fileIdentifier, 'filename': filename,
                 'paragraph_id': paragraph_id, 'old_filesize': filesize}
    file = os.path.join(image_directory, filename)
    endpoint = 'jsonapi/file/file/'+old_id
    url = baseURL+endpoint
    old_id = fetch_data(url)
    if old_id:
        # Delete old file.
        results = deleteFile(url)
        if results:
            new_id = postFile(file)
            if new_id:
                # Replace old_id with new_id in field_item_image.
                patch_results = patchCollectionItemImage(old_id, new_id, paragraph_id)
    else:
        pass
    for key, value in item_dict.items():
        print("{}: {}".format(key, value))
    print("")
    all_items.append(item_dict)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(all_items)
log.to_csv('logReplacingImages.csv', index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
