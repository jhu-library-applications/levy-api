import requests
import pandas as pd
import secret
import argparse

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

endpoint_type = 'jsonapi/node/levy_collection_item/'
ext = '?include=field_pdf,field_images.field_item_image'

df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, row in df.iterrows():
    item_uuid = row['drupal_id']
    url = base_url+endpoint_type+item_uuid+ext
    print(index, url)
    r = requests.get(url).json()
    data = r.get('data')
    included = r.get('included')
    if included:
        for item in included:
            new_row = row.copy()
            drupal_id = item['id']
            drupal_type = item['type']
            if drupal_type == 'paragraph--collection_item_image':
                new_row['paragraph_id'] = drupal_id
                relationships = item.get('relationships')
                if relationships:
                    field_item_image = relationships.get('field_item_image')
                    if field_item_image:
                        if field_item_image['data']:
                            file_id = field_item_image['data']['id']
                            print(file_id)
                            new_row['file_id'] = file_id
                        if file_id != 'missing':
                            file_url = base_url+'jsonapi/file/file/'+file_id
                            r = requests.get(file_url).json()
                            attributes = r['data']['attributes']
                            filename = attributes.get('filename')
                            filesize = attributes.get('filesize')
                            new_row['filename'] = filename
                            new_row['filesize'] = filesize
                            print(filename)
            elif drupal_type == 'file--file':
                new_row['file_id'] = drupal_id
                print(drupal_id)
                filename = item['attributes']['filename']
                new_row['filename'] = filename
            all_items.append(new_row)
    else:
        print(included)

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levyCollectionItems.csv', index=False)
