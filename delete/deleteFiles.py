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

fileLink = 'jsonapi/file/file/'


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

# Update headers for DELETE requests in Drupal
s.headers.update({'Accept': 'application/vnd.api+json', 'X-CSRF-Token': token})

filename = 'filesToDelete.csv'
df = pd.read_csv(filename)

# Loop through DataFrame
all_items = []
for index, row in df.iterrows():
    filename = row['filename']
    print(index, filename)
    file_uuid = row['file_uuid']
    file_uuid = file_uuid.strip()
    full_link = baseURL+fileLink+file_uuid
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
