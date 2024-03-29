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

endpoint_type = 'jsonapi/node/levy_collection_item'
ext = '&include=field_images.field_item_image.uid'
filter1 = '?filter[field_box]='
filter2 = '&filter[field_item_id]='


df = pd.read_csv(metadata_file)
# Loop through item and grabs metadata, chuck into DataFrame.
all_items = []
for index, row in df.iterrows():
    fileId = row.get('fileIdentifier')
    box = fileId[5:8]
    item = fileId[-3:]
    url = base_url+endpoint_type+filter1+box+filter2+item+ext
    print(index, url)
    r = requests.get(url).json()
    data = r.get('data')
    included = r.get('included')
    if included:
        for item in included:
            newRow = {'fileIdentifier': fileId}
            paragraph_id = item['id']
            paragraph_type = item['type']
            if paragraph_type == 'paragraph--collection_item_image':
                newRow['paragraph_id'] = paragraph_id
                print(paragraph_id)
                relationships = item.get('relationships')
                if relationships:
                    field_item_image = relationships.get('field_item_image')
                    if field_item_image:
                        file_id = field_item_image['data']['id']
                        print(file_id)
                        newRow['file_id'] = file_id
                        file_url = base_url+'jsonapi/file/file/'+file_id
                        r = requests.get(file_url).json()
                        attributes = r['data']['attributes']
                        filename = attributes.get('filename')
                        filesize = attributes.get('filesize')
                        newRow['filename'] = filename
                        newRow['filesize'] = filesize
                        print(filename)
                        all_items.append(newRow)
    else:
        print(included)

all_items = pd.DataFrame.from_records(all_items)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levyCollectionItems.csv', index=False)
