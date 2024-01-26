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
endpoint_type = '/jsonapi/file/file/'
endpoint_filter = '?filter[filename]='

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
        attributes = term.get('attributes')
        term_id = term.get('id')
        file_name = attributes.get('filename')
        url = attributes['uri']['url']
        item_dict['id'] = term_id
        item_dict['filename'] = file_name
        item_dict['url'] = url
        print(id)
        all_items.append(item_dict)


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, row in df.iterrows():
    filename = row.get('filename')
    filename = filename.strip()
    try:
        r = s.get(base_url+endpoint_type+endpoint_filter+filename).json()
        data = r.get('data')
        fetch_data(data)
    except simplejson.errors.JSONDecodeError:
        item_dict = {}
        item_dict = {'filename': filename, 'id': 'not found'}
        all_items.append(item_dict)

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('allParagraphs_collection_item_image.csv', index=False)
