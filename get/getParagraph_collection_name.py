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
type = 'jsonapi/paragraph/collection_name'


# Function grabs name and uris from collection_name.
def fetchData(data):
    for count, term in enumerate(data):
        itemDict = {}
        attributes = term.get('attributes')
        id = term.get('id')
        title = attributes.get('title')
        itemDict['title'] = title
        itemDict['id'] = id
        allItems.append(itemDict)


# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
more_links = True
nextList = []
while more_links:
    if not nextList:
        r = requests.get(baseURL+type+'?page[limit=50]').json()
    else:
        next = nextList[0]
        r = requests.get(next).json()
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
all_items.to_csv('allCollectionNames.csv', index=False)