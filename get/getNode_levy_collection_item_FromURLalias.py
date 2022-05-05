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
type = 'jsonapi/node/levy_collection_item'
filter1 = '?filter[field_box]='
filter2 = '&filter[field_item_id]='

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
        relationships = term.get('relationships')
        for key, value in attributes.items():
            itemDict[key] = value
        for r_key, r_value in relationships.items():
            data = r_value.get('data')
            if isinstance(data, list):
                for v in data:
                    id = v.get('id')
                    existingValue = itemDict.get(r_key)
                    if existingValue:
                        itemDict[r_key] = existingValue+'|'+id
                    else:
                        itemDict[r_key] = id
        allItems.append(itemDict)


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
for index, row in df.iterrows():
    url_alias = row.get('url_alias')
    url_alias = url_alias.split('/')
    box = url_alias[-2]
    item_id = url_alias[-1]
    url_api = baseURL+type+filter1+box+filter2+item_id
    print(url_api)
    try:
        r = s.get(url_api).json()
        data = r.get('data')
        print(len(data))
        fetchData(data)
    except simplejson.errors.JSONDecodeError:
        itemDict = {}
        itemDict = {'url_alias': url_alias}
        allItems.append(itemDict)

all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levy_item_item_FromURLalias.csv', index=False)
