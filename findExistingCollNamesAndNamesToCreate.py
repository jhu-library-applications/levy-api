import pandas as pd
from datetime import datetime

aggregatedRoles = '/Users/michelle/Documents/GitHub/levy-api/aggregated-roles/'
typeSheet = 'allCollectionNames.csv'

rolesList = ['AggregatedByarranger.csv', 'AggregatedBycomposer.csv',
             'AggregatedBylyricist.csv', 'AggregatedByno_role.csv',
             'AggregatedBypseudonym.csv']


newDF = pd.DataFrame()
for filename in rolesList:
    role = filename.replace('AggregatedBy', '')
    role = role[:-4]
    filename = aggregatedRoles + "/" + filename
    print(filename)
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
        df['role'] = role
        newDF = newDF.append(df, ignore_index=True, sort=True)

newDF = newDF.drop_duplicates()
newDF['title'] = newDF['title'].str.strip()
print(newDF.head)

typeSheet = 'allCollectionNames.csv'
existing = pd.read_csv(typeSheet, header=0)
print(existing.head)
existing['title'] = existing['title'].str.strip()

frame = pd.merge(newDF, existing, how='left', on=['title'])
frame.drop_duplicates(inplace=True)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
renamedKey = typeSheet.replace('all', 'merged')
frame.to_csv(renamedKey, index=False)

newDF = pd.read_csv(renamedKey, header=0)

toCreate = []
done = []
for count, row in newDF.iterrows():
    id = row['id']
    title = row['title']
    role = row['role']
    if pd.isna(id):
        toCreate.append({'title': title})
    else:
        done.append(row)

toCreate = pd.DataFrame.from_dict(toCreate)
print(toCreate.head)
toCreate.drop_duplicates(inplace=True)
toCreate.to_csv('levy_collection_namesToCreate.csv', index=False)

done = pd.DataFrame.from_dict(done)
print(done.head)
done.to_csv('levy_collection_namesDone.csv', index=False)
