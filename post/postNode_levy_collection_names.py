import requests
import secrets
import json

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
type = 'jsonapi/node/levy_collection_names/'

s = requests.Session()
header = {'Content-type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL+'user/login?_format=json', headers=header,
                 json=data).json()
token = session['csrf_token']
status = s.get(baseURL+'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')
s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                  'application/vnd.api+json', 'X-CSRF-Token': token})

metadata = json.load(open('/Users/michelle/Documents/GitHub/levy-api/post/nameTest.json'))
metadata = json.dumps(metadata)
post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
print(post.get('errors'))
data = post.get('data')
id = data.get('id')
title = data['attributes']['title']
print(id, title)
