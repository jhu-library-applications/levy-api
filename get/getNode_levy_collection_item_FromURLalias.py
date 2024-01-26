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
        secret = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

base_url = secret.base_url
endpoint_type = 'jsonapi/node/levy_collection_item'
filter1 = '?filter[field_box]='
filter2 = '&filter[field_item_id]='

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


# Function grabs filename and uris from file object.
def fetch_data(data):
    for count, term in enumerate(data):
        item_dict = {}
        item_identifier = term.get('id')
        item_dict['item_identifier'] = item_identifier
        attributes = term.get('attributes')
        relationships = term.get('relationships')
        for key, value in attributes.items():
            item_dict[key] = value
        for r_key, r_value in relationships.items():
            data = r_value.get('data')
            if isinstance(data, list):
                for v in data:
                    id = v.get('id')
                    existing_value = item_dict.get(r_key)
                    if existing_value:
                        item_dict[r_key] = existing_value+'|'+id
                    else:
                        item_dict[r_key] = id
        all_items.append(item_dict)


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, row in df.iterrows():
    url_alias = row.get('link')
    url_alias = url_alias.split('/')
    box = url_alias[-2]
    item_id = url_alias[-1]
    url_api = base_url+endpoint_type+filter1+box+filter2+item_id
    print(url_api)
    try:
        r = s.get(url_api).json()
        data = r.get('data')
        print(len(data))
        fetch_data(data)
    except simplejson.error.JSONDecodeError:
        item_dict = {}
        item_dict = {'url_alias': url_alias}
        all_items.append(item_dict)

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levy_item_item_FromURLalias.csv', index=False)
