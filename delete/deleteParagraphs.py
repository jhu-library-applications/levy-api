import requests
import secret
import pandas as pd

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
endpoint_paragraph = 'jsonapi/paragraph/collection_item_image/'
endpoint_item = 'jsonapi/node/levy_collection_item/'
username = secret.username
password = secret.password

# Authenticate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data).json()
print(session)
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

filename = 'paragraphsToDelete.csv'
df = pd.read_csv(filename)

# Loop through DataFrame
all_items = []
for index, row in df.iterrows():
    row = row.copy()
    print(index, filename)
    paragraph_uuids = row['paragraph_uuid']
    item_uuid = row['item_uuid']
    data = s.get(baseURL+endpoint_item+item_uuid)
    paragraph_images = data['data']['relationships']['field_images']['data']

    if paragraph_images:
        for image in paragraph_images:
            if image['id'] in paragraph_uuids:

    ]
    remove p
    # Update headers for DELETE requests in Drupal
    s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})

    full_link = baseURL+endpoint_paragraph+paragraph_uuid
    delete = s.delete(full_link, cookies=s.cookies)

    # HTTP 204 (No content) response means the fileLink is deleted.
    # HTTP 404 means not found.
    row['delete'] = delete
    print(delete)
    all_items.append(row)


all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('deletedFileLog.csv', index=False)
