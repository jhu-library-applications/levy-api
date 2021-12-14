import pandas as pd
from datetime import datetime
import os

aggregated = '/Users/michelle/Documents/GitHub/levy-api/aggregated/'
taxonomies = '/Users/michelle/Documents/GitHub/levy-api/taxonomies/'

directory = '/Users/michelle/Documents/GitHub/levy-api/merged'
if not os.path.exists(directory):
    os.mkdir(directory)

matchDictionary = {'AggregatedByfield_publisher.csv': 'publishers.csv',
                   'AggregatedByfield_subjects.csv': 'subjects.csv',
                   'AggregatedByfield_instrumentation_metadata.csv':
                   'instrumentation_metadata.csv'}

for key, value in matchDictionary.items():
    df_1 = pd.read_csv(aggregated+key, header=0)
    print(df_1.columns)
    df_2 = pd.read_csv(taxonomies+value, header=0)
    print(df_2.columns)
    frame = pd.merge(df_1, df_2, how='left', on=['name'], suffixes=('_1', '_2'))

    frame.drop_duplicates(inplace=True)
    print(frame.head)
    dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    renamedKey = key.replace('AggregatedBy', 'merged')
    fullname = os.path.join(directory, renamedKey)
    frame.to_csv(fullname, index=False)

newDF = pd.DataFrame()
for filename in os.listdir(directory):
    filename = directory + "/" + filename
    print(filename)
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
        field = filename[:-4].replace(directory, '')
        field = field.replace('/merged', '')
        df['type'] = field
        newDF = newDF.append(df, ignore_index=True, sort=True)

toCreate = []
done = {}
for count, row in newDF.iterrows():
    id = row['id']
    taxonomy = row['type']
    if pd.isna(id):
        toCreate.append(row)
    else:
        fileIdentifiers = row['fileIdentifier'].split("|")
        for identifier in fileIdentifiers:
            existing = done.get(identifier)
            if existing:
                fieldValue = existing.get(taxonomy)
                if fieldValue:
                    fieldValue = fieldValue+"|"+row['taxonomy']+':::'+row['id']
                    existing[taxonomy] = fieldValue
                else:
                    newValue = row['taxonomy']+':::'+row['id']
                    done[identifier] = {taxonomy: newValue}
            else:
                print(row)
                newValue = row['taxonomy']+':::'+row['id']
                done[identifier] = {taxonomy: newValue}
print(done)
toCreate = pd.DataFrame.from_dict(toCreate)
toCreate.to_csv('taxonomyTermsToCreate.csv', index=False)

done = pd.DataFrame.from_dict(done, orient='index')
done.sort_index(inplace=True)
done.reset_index(inplace=True)
done = done.rename(columns={'index': 'fileIdentifier'})
done.to_csv('taxonomyTermsDone.csv', index=False)
