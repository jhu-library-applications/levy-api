import requests
import pandas as pd
from datetime import datetime
import os
import secret

path = os.getcwd()
dir = os.path.dirname(path)
directory = os.path.join(dir, 'existing-taxonomies')
print(directory)
if not os.path.exists(directory):
    os.mkdir(directory)

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
endpoint_type = '/jsonapi/taxonomy_term/'

# Machine names of taxonomies for your Drupal instance.
taxonomies = ['composition_metadata', 'c', 'creator_r', 'duplicat',
              'instrumentation_metadata', 'publishers', 'subjects']


# Function grabs name and uris from taxonomy terms.
def fetch_data(data):
    for count, term in enumerate(data):
        tax_dict = {}
        attributes = term.get('attributes')
        term_id = term.get('id')
        name = attributes.get('name')
        tax_dict['taxonomy'] = taxonomy
        tax_dict['name'] = name
        tax_dict['id'] = term_id
        all_tax.append(tax_dict)


# Loop through taxonomies and grab all taxonomy terms, chuck into DataFrame.
all_tax = []
for taxonomy in taxonomies:
    print(taxonomy)
    more_links = True
    next_page_list = []
    while more_links:
        if not next_page_list:
            r = requests.get(base_url+endpoint_type+taxonomy+'?page[limit=50]').json()
        else:
            next_page_link = next_page_list[0]
            r = requests.get(next_page_link).json()
        data = r.get('data')
        print(len(data))
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

existingTax = pd.DataFrame.from_records(all_tax)
print(existingTax.head)

# Create CSV for DataFrame containing all taxonomy terms.
dt = datetime.now().strftime('%Y-%m-%d%H.%M.%S')
filename = 'allExistingTaxonomies_'+dt+'.csv'
fullname = os.path.join(directory, filename)
existingTax.to_csv(fullname, index=False)

# Creates CSV for each different taxonomy (subject, person, etc).
df = pd.read_csv(fullname)
unique = df['taxonomy'].unique()
print(unique)
for value in unique:
    newDF = df.loc[df['taxonomy'] == value]
    newDF = newDF.dropna(axis=1, how='all')  # Deletes blank columns.
    newFile = value+'.csv'
    fullname = os.path.join(directory, newFile)
    newDF.to_csv(fullname, index=False)
