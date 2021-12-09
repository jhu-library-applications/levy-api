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
                  'application/vnd.api+json', 'X-CSRF-Token': token})

metadata = json.load(open('/Users/michelle/Documents/GitHub/levy-api/test.json'))
metadata = json.dumps(metadata)
post = s.post(baseURL+type, data=metadata, cookies=s.cookies).json()
print(post.get('errors'))
rdata = post.get('data')
id = rdata.get('id')
nid = rdata['attributes']['drupal_internal__nid']
print(nid)
link = rdata['links']['self']['href']
print(rdata['relationships']['field_people'])
print(id, link)

ptype = 'jsonapi/paragraph/collection_name/'
para = s.get(baseURL+ptype+'9ebc1895-8285-445e-bb20-b7042999b3d8', cookies=s.cookies).json()
paradata = para.get('data')
attributes = paradata['attributes']
attributes['parent_id'] = nid
revisionID = attributes["drupal_internal__revision_id"]
metadata = json.dumps(para)
post = s.patch(baseURL+ptype+'9ebc1895-8285-445e-bb20-b7042999b3d8', data=metadata, cookies=s.cookies).json()
data = post.get('data')
print(post)
print(data['attributes']['parent_id'])
print('')


field_people = {"data": [{"type": "paragraph--collection_name",
                          "id": "9ebc1895-8285-445e-bb20-b7042999b3d8",
                          "meta": {"target_revision_id": revisionID}}]}
rdata['relationships']['field_people'] = field_people
rdata['attributes']['revision_translation_affected'] = True
metadata = {'data': rdata}
metadata = json.dumps(metadata)
patch = s.patch(baseURL+type+id, data=metadata, cookies=s.cookies).json()
errors = patch.get('errors')
print(errors)
if errors is None:
    print(patch['data']['relationships']['field_people'])
    print(patch['data']['attributes']['revision_translation_affected'])
