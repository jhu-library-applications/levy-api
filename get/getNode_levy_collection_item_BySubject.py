import requests
import pandas as pd
import secret
import argparse

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
        secret = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

base_url = secret.base_url
entity_type = 'jsonapi/node/levy_collection_item'
field_filter = '?filter[field_subjects.name][value]='

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
def fetch_data(subject, data):
    for count, term in enumerate(data):
        item_dict = {'subjectSearched': subject}
        attributes = term.get('attributes')
        relationships = term.get('relationships')
        for key, value in attributes.items():
            item_dict[key] = value
        for r_key, r_value in relationships.items():
            data = r_value.get('data')
            if isinstance(data, list):
                for v in data:
                    identifier = v.get('id')
                    existing_value = item_dict.get(r_key)
                    if existing_value:
                        item_dict[r_key] = existing_value + '|' + identifier
                    else:
                        item_dict[r_key] = identifier
        all_items.append(item_dict)


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, row in df.iterrows():
    subject = row.get('subject')
    totalItemCount = 0
    next_page_list = []
    while totalItemCount < 10000:
        if not next_page_list:
            url_api = base_url + entity_type + field_filter + subject
            print(url_api)
            r = s.get(url_api).json()
        else:
            next_page_linkLink = next_page_list[0]
            r = s.get(next_page_linkLink).json()
        data = r.get('data')
        item_count = (len(data))
        totalItemCount = item_count + totalItemCount
        fetch_data(subject, data)
        next_page_list.clear()
        links = r.get('links')
        next_page_linkDict = links.get('next_page_link_page_link')
        if next_page_linkDict:
            next_page_linkLink = next_page_linkDict.get('href')
            next_page_list.append(next_page_linkLink)
        else:
            break

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levy_collection_item_BySubject.csv', index=False)
