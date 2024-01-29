import requests
import pandas as pd
import secret
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
entity_type = 'jsonapi/node/levy_collection_item'
field_filter = '?filter[field_publish_date_text][operator]=CONTAINS&filter[field_publish_date_text][value]='

username = secret.username
password = secret.password

# Authenticate to Drupal site, get token
s = requests.Session()
header = {'Content-entity_type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(base_url + 'user/login?_format=json', headers=header,
                 json=data, verify=False).json()
token = session['csrf_token']
status = s.get(base_url + 'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')


# Function grabs filename and uris from file object.
def fetch_data(year_to_search, metadata):
    for count, term in enumerate(metadata):
        item_dict = {'year_searched': year_to_search}
        item_dict['id'] = term['id']
        attributes = term.get('attributes')
        relationships = term.get('relationships')
        for key, value in attributes.items():
            item_dict[key] = value
        for r_key, r_value in relationships.items():
            item_data = r_value.get('data')
            if isinstance(item_data, list):
                for v in item_data:
                    identifier = v.get('id')
                    existing_value = item_dict.get(r_key)
                    if existing_value:
                        item_dict[r_key] = existing_value + '|' + identifier
                    else:
                        item_dict[r_key] = identifier
        all_items.append(item_dict)


years_to_search = ['1924', '1925', '1926', '1927', '1928']
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, year in enumerate(years_to_search):
    total_item_count = 0
    next_page_list = []
    while total_item_count < 10000:
        if not next_page_list:
            url_api = base_url + entity_type + field_filter + year
            print(url_api)
            r = s.get(url_api).json()
        else:
            next_page_linkLink = next_page_list[0]
            r = s.get(next_page_linkLink).json()
        data = r.get('data')
        item_count = (len(data))
        total_item_count = item_count + total_item_count
        print(total_item_count)
        fetch_data(year, data)
        next_page_list.clear()
        links = r.get('links')
        next_page_link_dict = links.get('next')
        if next_page_link_dict:
            next_page_link = next_page_link_dict.get('href')
            next_page_list.append(next_page_link)
        else:
            break

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levy_collection_item_by_year.csv', index=False)
