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
endpoint_type = 'jsonapi/paragraph/collection_item_image'

username = secret.username
password = secret.password

# Authenticate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(base_url+'user/login?_format=json', headers=header,
                 json=data).json()
token = session['csrf_token']
status = s.get(base_url+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

# Update headers for posting to Drupal
s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})


# Function grabs name and uris from collection_name.
def fetch_data(data):
    for count, term in enumerate(data):
        item_dict = {}
        attributes = term.get('attributes')
        term_id = term.get('id')
        restrict = attributes.get('field_restricted')
        parent_id = attributes.get('parent_id')
        item_dict['restrict'] = restrict
        item_dict['id'] = term_id
        item_dict['parent_id'] = parent_id
        if restrict is True:
            all_items.append(item_dict)


# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
more_links = True
next_page_list = []
while more_links:
    if not next_page_list:
        r = s.get(base_url+endpoint_type + '?page[limit=50]').json()
    else:
        next_page_link = next_page_list[0]
        r = s.get(next_page_link).json()
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
all_items.to_csv('allParagraphs_collection_item_image.csv', index=False)
