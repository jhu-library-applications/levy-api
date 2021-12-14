import requests
import secrets
import time
from datetime import datetime
import pandas as pd

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
file = 'jsonapi/node/levy_collection_item/field_pdf'

startTime = time.time()

# Authenicate to Drupal site, get token
s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data).json()
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

# Open file CSV as DataFrame
filename = 'pdf_filenames.csv'
df = pd.read_csv(filename)

allItems = []
for index, row in df.iterrows():
    row = row
    filename = row['filename']
    fileIdentifier = row['fileIdentifier']
    # Create Content-Disposition value using filename
    cd_value = 'file; filename="{}"'.format(filename)

    # Read file as binary
    data = open(filename, 'rb')

    # Update headers for posting file to Drupal, updated for each file
    s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                      'application/octet-stream',
                      'Content-Disposition': cd_value, 'X-CSRF-Token': token})
    # Post file
    post = s.post(baseURL+file, data=data, cookies=s.cookies).json()
    print(post)
    file_id = post['data']['id']
    row['pdf_id'] = file_id
    allItems.append(row)

# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(allItems)
dt = datetime.now().strftime('%Y-%m-%d')
log.to_csv('logofPDFs_'+dt+'.csv')

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
