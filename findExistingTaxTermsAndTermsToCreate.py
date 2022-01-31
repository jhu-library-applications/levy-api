import pandas as pd
from datetime import datetime
import os

path = os.getcwd()
dir = os.path.dirname(path)
aggregated = os.path.join(dir, 'aggregated-taxonomies/')
taxonomies = os.path.join(dir, 'existing-taxonomies/')

directory = os.path.join(dir, 'items-matched/')
if not os.path.exists(directory):
    os.mkdir(directory)

termsDone = os.path.join(dir, 'termsDone/')
if not os.path.exists(termsDone):
    os.mkdir(termsDone)

termsToCreate = os.path.join(dir, 'termsToCreate/')
if not os.path.exists(termsToCreate):
    os.mkdir(termsToCreate)

matchDictionary = {'AggregatedByfield_publisher.csv': 'publishers.csv',
                   'AggregatedByfield_subjects.csv': 'subjects.csv',
                   'AggregatedByfield_instrumentation_metadata.csv':
                   'instrumentation_metadata.csv'}

for key, value in matchDictionary.items():
    df_1 = pd.read_csv(aggregated+key, header=0)
    df_2 = pd.read_csv(taxonomies+value, header=0)
    frame = pd.merge(df_1, df_2, how='left', on=['name'], suffixes=('_1', '_2'))

    frame.drop_duplicates(inplace=True)
    dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    renamedKey = key.replace('AggregatedBy', 'matched_')
    fullname = os.path.join(directory, renamedKey)
    print("Created new file: {}".format(renamedKey))
    print('')
    frame.to_csv(fullname, index=False)

newDF = pd.DataFrame()
for filename in os.listdir(directory):
    filename = directory + "/" + filename
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
        field = filename[:-4].replace(directory, '')
        field = field.replace('/matched_', '')
        df['type'] = field
        newDF = newDF.append(df, ignore_index=True, sort=True)

toCreate = []
done = []
for count, row in newDF.iterrows():
    id = row['id']
    taxonomy = row['type']
    if pd.isna(id):
        row['taxonomy'] = taxonomy.replace('field_', '')
        del row['id']
        toCreate.append(row)
    else:
        done.append(row)

toCreate = pd.DataFrame.from_dict(toCreate)
filename = 'taxonomyTermsToCreate.csv'
fullname = os.path.join(termsToCreate, filename)
toCreate.to_csv(fullname, index=False)

done = pd.DataFrame.from_dict(done)
filename2 = 'taxonomyTermsDone.csv'
fullname2 = os.path.join(termsDone, filename2)
done.to_csv(fullname2, index=False)
