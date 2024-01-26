import requests
import pandas as pd
import secret

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
ext = '?page[limit=50]?include=field_people.field_name,field_people.field_roles,field_people.paragraph_type'

# List of single value fields
relation_dict = ['node_type', 'field_pdf', 'field_publisher']
# List of repeatable fields
relation_list = ['field_subjects', 'field_people',
                 'field_instrumentation_metadata', 'field_images',
                 'field_duplicates', 'field_composition_metadata']
# List of fields not to record
skip_fields = ['body', 'revision_timestamp', 'revision_log', 'path',
               'revision_translation_affected', 'drupal_internal__vid',
               'promote', 'sticky', 'default_langcode']


def fetch_data(data):
    for entry in data:
        item = {}
        item_type = entry.get('type')
        item_id = entry.get('id')
        item['type'] = item_type
        item['id'] = item_id
        attributes = entry.get('attributes')
        relationships = entry.get('relationships')
        for key, value in attributes.items():
            if key in skip_fields:
                pass
            else:
                item[key] = value
        for relation in relation_dict:
            data = relationships[relation]['data']
            if data:
                rel_type = relationships[relation]['data']['type']
                rel_id = relationships[relation]['data']['id']
                item[relation] = rel_type+':::'+rel_id
        for relation in relation_list:
            rel_list = relationships[relation]['data']
            if rel_list:
                for x in rel_list:
                    rel_type = x.get('type')
                    rel_id = x.get('id')
                    if rel_id:
                        existing = item.get(relation)
                        if existing:
                            item[relation] = existing+'|'+rel_type+':::'+rel_id
                        else:
                            item[relation] = rel_type+':::'+rel_id
                if relation == 'field_people':
                    print(relationships[relation])
                    print(id)
        all_items.append(item)


# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
totalItemCount = 0
next_page_list = []
while totalItemCount < 200:
    if not next_page_list:
        r = requests.get(base_url+endpoint_type+ext).json()
    else:
        next_page_link = next_page_list[0]
        r = requests.get(next_page_link).json()
    data = r.get('data')
    item_count = (len(data))
    totalItemCount = item_count + totalItemCount
    fetch_data(data)
    next_page_list.clear()
    links = r.get('links')
    next_page_linkDict = links.get('next_page_link_page_link')
    if next_page_linkDict:
        next_page_link = next_page_linkDict.get('href')
        next_page_list.append(next_page_link)
    else:
        break
print('')


all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levyCollectionItems.csv', index=False)
