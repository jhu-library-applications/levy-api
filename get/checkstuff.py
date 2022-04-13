import requests
import secrets
import time
import pandas as pd
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

# Save terminal output to file.
# python3 replaceImage.py -f somefile.csv | tee output.txt
# Output stream will be copied to txt file and still be visible in terminal.
# If txt file already exists, it gets overwritten.

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


# Function grabs data from file metadata object.
def checkIfDeleted(url):
    r = s.get(url)
    print(r)
    if r.status_code == 404:
        itemDict['deleted'] = True
    else:
        itemDict['deleted'] = True


def fetchData(new_url):
    r = s.get(new_url).json()
    data = r.get('data')
    new_id = data.get('id')
    attributes = data.get('attributes')
    filename = attributes.get('filename')
    uri = attributes.get('uri')
    filesize = attributes.get('filesize')
    itemDict['new_id'] = new_id
    itemDict['new_filename'] = filename
    itemDict['new_uri'] = uri['url']
    itemDict['new_filesize'] = filesize
    itemDict['upload_new_file'] = True


def getCollectionItemImage(old_id, paragraph_id):
    # Get collection_item_image metadata.
    type = 'jsonapi/paragraph/collection_item_image/'
    r = s.get(baseURL+type+paragraph_id, cookies=s.cookies).json()
    data = r.get('data')
    para_image_id = data.get('id')
    new_id = data['relationships']['field_item_image']['data']['id']
    if new_id == old_id:
        patch_results = False
    else:
        patch_results = True
    # Records data for log.
    itemDict['patch_posted'] = patch_results
    itemDict['para_image_id'] = para_image_id
    itemDict['new_id'] = new_id
    return patch_results


# Open file CSV as DataFrame.
df = pd.read_csv(filename)

type = '/jsonapi/file/file/'
filter = '?filter[filename]='

allItems = []
for index, row in df.iterrows():
    itemDict = row
    print('Replacing file {}'.format(index+1))
    fileIdentifier = row.get('fileIdentifier')
    filename = row.get('filename')
    paragraph_id = row.get('paragraph_id')
    old_id = row.get('old_id')
    filename = filename.strip()
    old_url = baseURL+type+old_id
    checkIfDeleted(old_url)
    patch_results = getCollectionItemImage(old_id, paragraph_id)
    if patch_results:
        new_id = itemDict['new_id']
        new_url = baseURL+type+new_id
        fetchData(new_url)
    else:
        pass

    allItems.append(itemDict)


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
log.to_csv('logReplacingImages.csv', index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
