import requests
import pandas as pd
import secrets
import argparse
import simplejson

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
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
type = '/jsonapi/file/file/'
filter = '?filter[filename]='

username = secrets.username
password = secrets.password

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


# Function grabs filename and uris from file object.
def fetchData(data):
    for count, term in enumerate(data):
        itemDict = {}
        attributes = term.get('attributes')
        id = term.get('id')
        filename = attributes.get('filename')
        url = attributes['uri']['url']
        itemDict['id'] = id
        itemDict['filename'] = filename
        itemDict['url'] = url
        print(id)
        allItems.append(itemDict)


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
for index, row in df.iterrows():
    filename = row.get('filename')
    filename = filename.strip()
    try:
        r = s.get(baseURL+type+filter+filename).json()
        data = r.get('data')
        fetchData(data)
    except simplejson.errors.JSONDecodeError:
        itemDict = {}
        itemDict = {'filename': filename, 'id': 'not found'}
        allItems.append(itemDict)

all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('allParagraphs_collecction_item_image.csv', index=False)
