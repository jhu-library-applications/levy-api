import requests
import pandas as pd
from datetime import datetime
import os

path = os.getcwd()
dir = os.path.dirname(path)
directory = os.path.join(dir, 'existing-taxonomies')
print(directory)
if not os.path.exists(directory):
    os.mkdir(directory)

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
type = '/jsonapi/taxonomy_term/'

# Machine names of taxonomies for your Drupal instance.
taxonomies = ['composition_metadata', 'c', 'creator_r', 'duplicat',
              'instrumentation_metadata', 'publishers', 'subjects']

# Function grabs name and uris from taxonomy terms.
def fetchData(data):
    for count, term in enumerate(data):
        taxDict = {}
        attributes = term.get('attributes')
        id = term.get('id')
        name = attributes.get('name')
        taxDict['taxonomy'] = taxonomy
        taxDict['name'] = name
        taxDict['id'] = id
        allTax.append(taxDict)


# Loop through taxonomies and grab all taxonomy terms, chuck into DataFrame.
allTax = []
for taxonomy in taxonomies:
    print(taxonomy)
    more_links = True
    nextList = []
    while more_links:
        if not nextList:
            r = requests.get(baseURL+type+taxonomy+'?page[limit=50]').json()
        else:
            next = nextList[0]
            r = requests.get(next).json()
        data = r.get('data')
        print(len(data))
        fetchData(data)
        nextList.clear()
        links = r.get('links')
        nextDict = links.get('next')
        if nextDict:
            next = nextDict.get('href')
            nextList.append(next)
        else:
            break
    print('')

existingTax = pd.DataFrame.from_dict(allTax)
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
