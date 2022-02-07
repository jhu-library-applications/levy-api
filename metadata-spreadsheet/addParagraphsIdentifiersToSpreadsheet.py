import pandas as pd
import os

path = os.getcwd()
dir = os.path.dirname(path)
logs = os.path.join(dir, 'logs/')

filename = os.path.join(logs, 'logOfParagraphCollectionName.csv')
df = pd.read_csv(filename, header=0)

filename2 = '01_GottesmanFinalMetadata_test.csv'
new_items = pd.read_csv(filename2, header=0)

df.drop(['link', 'creator_role_id', 'levy_collection_names_id'], axis=1, inplace=True)
pivoted = pd.pivot_table(df, index=['fileIdentifier'], values=['paragraph_id'],
                         aggfunc=lambda x: '|'.join(str(v) for v in x if pd.notna(v)))
df = pd.DataFrame(pivoted)
df = df.reset_index()


updated = pd.merge(new_items, df, how='left', on=['fileIdentifier'], suffixes=('_1', '_2'))
print(updated.head)
filename2 = filename2[3:]
filename2 = '02_'+filename2
updated.to_csv(filename2, index=False)
