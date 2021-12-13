import requests
import pandas as pd

# Your baseURL: https://example.com+//jsonapi/node/levy_collection_item'
baseURL = 'https://levy-test.mse.jhu.edu/'
type = 'jsonapi/node/levy_collection_names'


# Function grabs name and uris from levy_collection_items.
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
