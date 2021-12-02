import requests
import pandas as pd

# Your baseURL: https://example.com+//jsonapi/node/levy_collection_item'
baseURL = 'https://levy-test.mse.jhu.edu//jsonapi/node/levy_collection_item/'


relation_dict = ['node_type', 'field_pdf', 'field_publisher']
relation_list = ['field_subjects', 'field_people',
                 'field_instrumentation_metadata', 'field_images',
                 'field_duplicates', 'field_composition_metadata']
skip_fields = ['body', 'revision_timestamp', 'revision_log', 'path',
               'revision_translation_affected', 'drupal_internal__nid',
               'drupal_internal__vid', 'promote', 'sticky', 'default_langcode']

# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
item_uuid = 'ccaac2b5-dbcf-4c8b-930c-850c36d69b9a'
r = requests.get(baseURL+item_uuid).json()
item = {}
data = r.get('data')
type = data.get('type')
id = data.get('id')
item['type'] = type
item['id'] = id
attributes = data.get('attributes')
relationships = data.get('relationships')
for key, value in attributes.items():
    if key in skip_fields:
        pass
    else:
        item[key] = value
for relation in relation_dict:
    rel_type = relationships[relation]['data']['type']
    rel_id = relationships[relation]['data']['id']
    item[relation] = rel_type+':::'+rel_id
for relation in relation_list:
    rel_list = relationships[relation]['data']
    print(rel_list)
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
allItems.append(item)


all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv(id+'.csv', index=False)
