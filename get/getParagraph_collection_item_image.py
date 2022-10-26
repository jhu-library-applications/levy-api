import requests
import pandas as pd
import secret

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
type = 'jsonapi/paragraph/collection_item_image'

username = secrets.username
password = secrets.password

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
s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})


# Function grabs name and uris from collection_name.
def fetchData(data):
    for count, term in enumerate(data):
        itemDict = {}
        attributes = term.get('attributes')
        id = term.get('id')
        restrict = attributes.get('field_restricted')
        parent_id = attributes.get('parent_id')
        itemDict['restrict'] = restrict
        itemDict['id'] = id
        itemDict['parent_id'] = parent_id
        if restrict is True:
            allItems.append(itemDict)


# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
more_links = True
nextList = []
while more_links:
    if not nextList:
        r = s.get(baseURL+type+'?page[limit=50]').json()
    else:
        next = nextList[0]
        r = s.get(next).json()
    data = r.get('data')
    print(len(data))
    fetchData(data)
    nextList.clear()
    links = r.get('links')
    nextDict = links.get('next')
    if nextDict:
        next = nextDict.get('href')
        nextList.append(next)
    else:
        break
print('')


all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('allParagraphs_collecction_item_image.csv', index=False)