import requests
import pandas as pd
import secret
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

baseURL = secret.baseURL
type = 'jsonapi/node/levy_collection_item'
filter1 = '?filter[field_subjects.name][value]='

username = secret.username
password = secret.password

# Authenticate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data, verify=False).json()
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')


# Function grabs filename and uris from file object.
def fetchData(subject, data):
    for count, term in enumerate(data):
        itemDict = {'subjectSearched': subject}
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
    subject = row.get('subject')
    totalItemCount = 0
    nextList = []
    while totalItemCount < 10000:
        if not nextList:
            url_api = baseURL+type+filter1+subject
            print(url_api)
            r = s.get(url_api).json()
        else:
            nextLink = nextList[0]
            r = s.get(nextLink).json()
        data = r.get('data')
        item_count = (len(data))
        totalItemCount = item_count + totalItemCount
        fetchData(subject, data)
        nextList.clear()
        links = r.get('links')
        nextDict = links.get('next')
        if nextDict:
            nextLink = nextDict.get('href')
            nextList.append(nextLink)
        else:
            break

all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levy_collection_item_BySubject.csv', index=False)