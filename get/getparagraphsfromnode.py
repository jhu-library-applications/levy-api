import requests
import pandas as pd
import secrets

secretsVersion = input('To edit production server, enter secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL

type = 'jsonapi/node/levy_collection_item'
ext = '&include=field_images.field_item_image.uid'
filter1 = '?filter[field_box]='
filter2 = '&filter[field_item_id]='


df = pd.read_csv('fileIdentifiers_2022-03-11.csv')
# Loop through item and grabs metadata, chuck into DataFrame.
allItems = []
for index, row in df.iterrows():
    fileId = row.get('fileIdentifier')
    box = fileId[5:8]
    item = fileId[-3:]
    url = baseURL+type+filter1+box+filter2+item+ext
    print(url)
    r = requests.get(url).json()
    data = r.get('data')
    included = r.get('included')
    if len(included) > 0:
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
                        r = requests.get(baseURL+'jsonapi/file/file/'+file_id).json()
                        attributes = r['data']['attributes']
                        filename = attributes.get('filename')
                        filesize = attributes.get('filesize')
                        newRow['filename'] = filename
                        newRow['filesize'] = filesize
                        print(filename)
                        allItems.append(newRow)
    else:
        print(included)

all_items = pd.DataFrame.from_dict(allItems)
print(all_items.head)

# Create CSV for new DataFrame.
all_items.to_csv('levyCollectionItems.csv', index=False)
