import requests
import pandas as pd
import secret

secretsVersion = input('To edit production server, enter secrets file: ')
if secretsVersion != '':
    try:
        secret = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

base_url = secret.base_url
endpoint_type = 'jsonapi/node/levy_collection_names'


# Function grabs name and uris from levy_collection_items.
def fetch_data(data):
    for count, term in enumerate(data):
        item_dict = {}
        attributes = term.get('attributes')
        term_id = term.get('id')
        title = attributes.get('title')
        item_dict['title'] = title
        item_dict['id'] = term_id
        all_items.append(item_dict)


# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
more_links = True
next_page_list = []
while more_links:
    if not next_page_list:
        r = requests.get(base_url+endpoint_type+'?page[limit=50]').json()
    else:
        next_page_link = next_page_list[0]
        r = requests.get(next_page_link).json()
    data = r.get('data')
    print(len(data))
    fetch_data(data)
    next_page_list.clear()
    links = r.get('links')
    next_page_linkDict = links.get('next_page_link_page_link')
    if next_page_linkDict:
        next_page_link = next_page_linkDict.get('href')
        next_page_list.append(next_page_link)
    else:
        break
print('')


all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('allCollectionNames.csv', index=False)
