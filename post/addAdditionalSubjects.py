import requests
import pandas as pd
import secret
import argparse
import urllib3
import time
import json

# This script adds 1 or more additional subjects if a Levy Collection Item already contains a certain subject.
# For instance, if Item contains "Rose" as a subject, add new subjects "Flowers" and "Gardens."
# CSV should contain two columns: "existingSubject" with existing subject term to search for
# and "subjectsToAdd" with terms to add to item. Separate multiple subjects with pipe ("|").
# All subject terms should already exist in taxonomy Subjects before running this script.

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    metadata_file = args.file
else:
    metadata_file = input('Enter filename (including \'.csv\'): ')

startTime = time.time()

secretsVersion = input('To edit production server, enter secrets file: ')
if secretsVersion != '':
    try:
        secret = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secret.baseURL
entity_type = 'jsonapi/node/levy_collection_item'
field_filter = '?filter[field_subjects.name][value]='
include = '?include=subjects'

username = secret.username
password = secret.password

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Authenticate to Drupal site, get token.
s = requests.Session()
header = {'Content-entity_type': 'application/json'}
data = {'name': username, 'pass': password}
session = s.post(baseURL + 'user/login?_format=json', headers=header,
                 json=data, verify=False).json()
token = session['csrf_token']
status = s.get(baseURL + 'user/login_status?_format=json').json()
if status == 1:
    print('authenticated')

# Get Drupal IDs for subject terms that we are adding.
df = pd.read_csv(metadata_file)
df['subjectsToAdd'] = df['subjectsToAdd'].str.split('|')
subjects_to_add = df['subjectsToAdd'].explode().unique()
subjects_to_add = list(subjects_to_add)
print(list(subjects_to_add))

subject_dictionary = {}
for subject_to_add in subjects_to_add:
    taxonomy_entity = 'jsonapi/taxonomy_term/subjects'
    taxonomy_filter = '?filter[name][value]='
    url_api = baseURL+taxonomy_entity+taxonomy_filter+subject_to_add
    r = s.get(url_api).json()
    data = r.get('data')
    for item in data:
        identifier = item.get('id')
        subject_dictionary[subject_to_add] = identifier
print(subject_dictionary)


log_dictionary = []
for count, row in df.iterrows():
    subject_to_search = row.get('existingSubject')
    subjects_to_add = row.get('subjectsToAdd')
    for number, subject_to_add in enumerate(subjects_to_add):
        identifier = subject_dictionary.get(subject_to_add)
        subjects_to_add[number] = identifier
    print(subjects_to_add)
    totalItemCount = 0
    nextList = []
    while totalItemCount < 10000:
        if not nextList:
            # Get list of Levy Collection Items containing query subject (subject_to_search).
            url_api = baseURL + entity_type + field_filter + subject_to_search
            print(url_api)
            r = s.get(url_api).json()
        else:
            nextLink = nextList[0]
            r = s.get(nextLink).json()
        data = r.get('data')
        item_count = (len(data))
        totalItemCount = item_count + totalItemCount
        all_json_subjects = []

        # Get information for Levy Collection Items from JSON response.
        for item in data:
            item_id = item.get('id')
            title = item['attributes']['title']
            url = item['attributes']['path']['alias']

            # Create list of subjects that already exist in Levy Collection Item.
            existing_subject_ids = []
            item_subjects = item['relationships']['field_subjects']['data']
            for item_subject in item_subjects:
                subject_id = item_subject.get('id')
                existing_subject_ids.append(subject_id)
            existing_subjects_count = len(existing_subject_ids)
            print('Existing subject count: {}'.format(existing_subjects_count))
            existing_subject_ids = list(set(existing_subject_ids))
            no_duplicates_existing_subjects_count = len(existing_subject_ids)
            print('Existing subject count without duplicates: {}'.format(no_duplicates_existing_subjects_count))

            # Add information to log.
            little_log = {'subject_to_search': subject_to_search,
                          'existing_subjects_count': existing_subjects_count,
                          'no_duplicates_existing_subjects_count': no_duplicates_existing_subjects_count,
                          'title': title,
                          'item_id': item_id, 'url': url}

            # Create complete list of subjects that will exist in Levy Collection Item once this script is complete.
            new_subject_ids = existing_subject_ids+subjects_to_add
            new_subject_ids = list(set(new_subject_ids))

            # Get list of subjects to add to Levy Collection Item by comparing new_subject_ids and existing_subjects_id.
            to_add = list(set(new_subject_ids) - set(existing_subject_ids))

            # If to_add list is not empty, add subjects to 'field_subjects' data.
            if to_add:
                subjects_to_add_count = len(to_add)
                print('Subjects to add: {}'.format(subjects_to_add_count))
                little_log['subjects_to_add'] = '|'.join(to_add)
                little_log['subjects_to_add_count'] = subjects_to_add_count
                for subject_to_add in to_add:
                    item_subjects.append({'type': 'taxonomy_term--subjects', 'id': identifier})

                # Create metadata for PATCH and covert to JSON.
                relationships = {'field_subjects': {'data': item_subjects}}
                patch_metadata = {'type': 'node--levy_collection_item', 'id': item_id,
                                  'relationships': relationships}
                metadata = {'data': patch_metadata}
                metadata = json.dumps(metadata)

                # Use item_id of Levy Collection Item to create URL for item PATCH.
                update_url = baseURL+entity_type+'/'+item_id
                print(update_url)

                # PATCH Levy Collection Item with updated JSON for 'field_subjects'.
                # Update headers for posting to Drupal.
                s.headers.update({'Accept': 'application/vnd.api+json', 'Content-Type':
                                  'application/vnd.api+json', 'X-CSRF-Token': token})
                patch = s.patch(update_url, data=metadata, headers=s.headers, cookies=s.cookies).json()

                # Try getting subject information from PATCH post; if unsuccessful, check for error message in JSON.
                try:
                    item_subjects = patch['data']['relationships']['field_subjects']['data']
                    new_subjects_count = len(item_subjects)
                    little_log['new_subjects_count'] = new_subjects_count
                    print('New subject count: {}'.format(new_subjects_count))
                    no_duplicates_new_subject_count = len(list(set(item_subjects)))
                    little_log['no_duplicates_new_subject_count'] = no_duplicates_new_subject_count
                    print('New subject count without duplicates: {}'.format(no_duplicates_new_subject_count))
                except KeyError:
                    errors = patch.get('errors')
                    if errors:
                        for error in errors:
                            error = error['detail']
                            little_log['error'] = error
                            print('Item patch errors: {}'.format(error))
            else:
                print('Subjects already exists')
                little_log['subjects_already_existed'] = True
            log_dictionary.append(little_log)
            print('')


# Convert results to DataFrame, export as CSV
log = pd.DataFrame.from_dict(log_dictionary)
fullname = 'log_AddingAdditionalSubjects.csv'
log.to_csv(fullname, index=False)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))