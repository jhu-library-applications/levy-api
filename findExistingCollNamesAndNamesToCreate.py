import pandas as pd
from datetime import datetime
import os

termsDone = '/Users/michelle/Documents/GitHub/levy-api/termsDone'
if not os.path.exists(termsDone):
    os.mkdir(termsDone)

termsToCreate = '/Users/michelle/Documents/GitHub/levy-api/termsToCreate'
if not os.path.exists(termsToCreate):
    os.mkdir(termsToCreate)

aggregatedRoles = '/Users/michelle/Documents/GitHub/levy-api/aggregated-roles/'
typeSheet = 'allCollectionNames.csv'
rolesSheet = '/Users/michelle/Documents/GitHub/levy-api/existing-taxonomies/creator_r.csv'

rolesList = ['AggregatedByarranger.csv', 'AggregatedBycomposer.csv',
             'AggregatedBylyricist.csv', 'AggregatedByno_role.csv',
             'AggregatedBypseudonym.csv']

rolesDF = pd.read_csv(rolesSheet)
rolesDF = rolesDF.rename(columns={'name': 'role', 'id': 'creator_role_id'})

newDF = pd.DataFrame()
for filename in rolesList:
    role = filename.replace('AggregatedBy', '')
    role = role[:-4]
    filename = aggregatedRoles + "/" + filename
    print(filename)
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
        df['role'] = role
        df = pd.merge(df, rolesDF, how='left', on=['role'])
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
renamedKey = typeSheet.replace('all', 'matched_')
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
filename = 'levy_collection_namesToCreate.csv'
fullname = os.path.join(termsToCreate, filename)
toCreate.to_csv(fullname, index=False)


done = pd.DataFrame.from_dict(done)
filename2 = 'levy_collection_namesDone.csv'
fullname2 = os.path.join(termsDone, filename2)
done.to_csv(fullname2, index=False)
