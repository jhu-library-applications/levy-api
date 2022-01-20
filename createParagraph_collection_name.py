import pandas as pd

filename = 'matched_CollectionNames.csv'
filename2 = 'logOfNodeCollectionNamesAdded.csv'

df_1 = pd.read_csv(filename, header=0)
print(df_1.columns)
df_2 = pd.read_csv(filename2, header=0)
print(df_2.columns)

df_1.set_index('title', inplace=True)
df_2.set_index('title', inplace=True)

frame = df_1.combine_first(df_2)
frame.reset_index(inplace=True)
frame.rename(columns={'id': 'levy_collection_names_id'}, inplace=True)
frame.drop(['count', 'role', 'taxonomy', 'title', 'link'], axis=1, inplace=True)

frame['fileIdentifier'] = frame['fileIdentifier'].str.split('|')
frame.reset_index()
frame = frame.explode('fileIdentifier')
frame.sort_values(by=['fileIdentifier'], inplace=True)
frame.to_csv('paragraph_collection_namesToAdd.csv', index=False)
