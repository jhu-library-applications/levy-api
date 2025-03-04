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
# python3 replaceImage.py -f some_file.csv | tee output.txt
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
def fetch_data(file_url):
    try:
        r = s.get(file_url).json()
        metadata = r.get('data')
        attributes = metadata.get('attributes')
        retrieved_old_id = metadata.get('id')
        old_filename = attributes.get('filename')
        uri = attributes.get('uri')
        old_filesize = attributes.get('filesize')
        print('Successfully retrieved file metadata for {}'.format(retrieved_old_id))
        item_dict['old_filename'] = old_filename
        item_dict['old_uri'] = uri['url']
        item_dict['old_filesize'] = old_filesize
    except simplejson.errors.JSONDecodeError:
        retrieved_old_id = False
    except AttributeError:
        retrieved_old_id = False
    return retrieved_old_id


def delete_file(file_url):
    s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})
    delete = s.delete(file_url, cookies=s.cookies)
    file_status = delete.status_code
    print(file_status)
    if file_status == 204:
        delete_results = True
    else:
        delete_results = False
    item_dict['old_file_deleted'] = delete_results
    return delete_results


def post_file(file_path):
    # Create Content-Disposition value using filename for header.
    cd_value = 'file; filename="{}"'.format(file_path)

    # Read file as binary.
    file_data = open(file_path, 'rb')

    # Update headers for posting file to Drupal, updated for each file.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/octet-stream',
                      'Content-Disposition': cd_value, 'X-CSRF-Token': token})
    # Post file.
    try:
        image_endpoint = 'jsonapi/paragraph/collection_item_image/field_item_image'
        post = s.post(baseURL+image_endpoint, data=file_data, cookies=s.cookies).json()
        metadata = post.get('data')
        retrieved_new_id = metadata.get('id')
        attributes = metadata.get('attributes')
        new_filename = attributes.get('filename')
        uri = attributes.get('uri')
        new_filesize = attributes.get('filesize')
        item_dict['new_id'] = retrieved_new_id
        item_dict['new_filename'] = new_filename
        item_dict['new_uri'] = uri['url']
        item_dict['new_filesize'] = new_filesize
        item_dict['upload_new_file'] = True
        print('Upload successful')
    except simplejson.errors.JSONDecodeError:
        item_dict['upload_new_file'] = False
        retrieved_new_id = False
        print('Upload failure')
    return retrieved_new_id


def patch_collection_item_image(id_new, id_paragraph):

    # Get collection_item_image metadata.
    drupal_type = 'jsonapi/paragraph/collection_item_image/'
    r = s.get(baseURL+drupal_type+id_paragraph, cookies=s.cookies).json()
    image_data = r.get('data')
    image = image_data['relationships']['field_item_image']['data']
    # Update file id in metadata.
    image['id'] = id_new
    del image_data['relationships']['field_item_image']['data']['meta']
    metadata = {"data": image_data}
    metadata = json.dumps(metadata)

    # Updates header for posting paragraph.
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/vnd.api+json', 'X-CSRF-Token': token})
    # Try to patch new paragraph collection_item_image.
    try:
        patch = s.patch(baseURL+type+paragraph_id, data=metadata,
                        cookies=s.cookies).json()
        # Gets paragraph data for log
        patch_data = patch.get('data')
        para_image_id = patch_data.get('id')
        file_id = patch_data['relationships']['field_item_image']['data']['id']
        paragraph_patch_results = True
        # Records data for log.
        item_dict['patch_posted'] = paragraph_patch_results
        item_dict['para_image_id'] = para_image_id
        item_dict['file_id'] = file_id
    except json.decoder.JSONDecodeError:
        paragraph_patch_results = False
        item_dict['patchSuccessful'] = patch_results
    return paragraph_patch_results


# Open file CSV as DataFrame.
df = pd.read_csv(filename)

all_items = []
for index, row in df.iterrows():
    file_number = index+1
    print('Replacing file {}'.format(file_number))
    fileIdentifier = row.get('fileIdentifier')
    filename = row.get('filename')
    paragraph_id = row.get('paragraph_id')
    old_id = row.get('file_id')
    filesize = row.get('filesize')
    image_directory = '/Users/michelle/Desktop/folder'
    item_dict = {'fileIdentifier': fileIdentifier, 'filename': filename,
                 'paragraph_id': paragraph_id, 'old_filesize': filesize}
    file = os.path.join(image_directory, filename)
    endpoint = 'jsonapi/file/file/'+old_id
    url = baseURL+endpoint
    old_id = fetch_data(url)
    if old_id:
        # Delete old file.
        results = delete_file(url)
        if results:
            new_id = post_file(file)
            if new_id:
                # Replace old_id with new_id in field_item_image.
                patch_results = patch_collection_item_image(new_id, paragraph_id)
    else:
        pass
    for key, value in item_dict.items():
        print("{}: {}".format(key, value))
    print("")
    all_items.append(item_dict)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_records(all_items)
log.to_csv('logReplacingImages.csv', index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
