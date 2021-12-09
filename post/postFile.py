import requests
import secrets
import json

username = secrets.username
password = secrets.password

# Your Drupal baseURL: https://example.com/
baseURL = 'https://levy-test.mse.jhu.edu/'
type = 'jsonapi/node/levy_collection_item/'

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
                  'application/octet-stream', 'Content-Disposition': 'file',
                  'X-CSRF-Token': token})

id = 'bbc8e1d0-9dbc-4f2a-a363-e52b32b2b243'
filename = 'jhu_coll-0002_09280.jpg'
cd_value = 'file; filename="{}"'.format(filename)
data = open('jhu_coll-0002_09280.jpg', 'rb')
s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                  'application/octet-stream', 'Content-Disposition': cd_value,
                  'X-CSRF-Token': token})
post = s.post(baseURL+'jsonapi/node/article/field_image', data=data, cookies=s.cookies)
print(post)
