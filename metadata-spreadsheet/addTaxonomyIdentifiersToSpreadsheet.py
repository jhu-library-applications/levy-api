import pandas as pd
import os


path = os.getcwd()
dir = os.path.dirname(path)
directory = os.path.join(dir, 'items-matched/')

filename2 = 'logOfTaxonomyTermsAdded.csv'
df_2 = pd.read_csv(filename2, header=0)
pivoted = pd.pivot(df_2, index='fileIdentifier', columns='type', values='id')
df_2 = pd.DataFrame(pivoted)
df_2 = df_2.reset_index()

filename3 = 'GottesmanFinalMetadata_2021-12-03.csv'
new_items = pd.read_csv(filename3)

newDF = pd.DataFrame()
for count, filename in enumerate(os.listdir(directory)):
    filename = directory + "/" + filename
    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
        field = filename[:-4].replace(directory+'/matched_', '')
        field = field+'_id'
        df.rename(columns={'id': field}, inplace=True)
        df = df.combine_first(df_2)
        df['fileIdentifier'] = df['fileIdentifier'].str.split('|')
        df.reset_index()
        df = df.explode('fileIdentifier')
        pivoted = pd.pivot_table(df, index=['fileIdentifier'], values=[field],
                                 aggfunc=lambda x: '|'.join(str(v) for v in x if pd.notna(v)))
        df = pd.DataFrame(pivoted)
        df = df.reset_index()
        new_filename = 'completed_'+field+'.csv'
        df.to_csv(new_filename, index=False)
        if count == 1:
            newDF = newDF.append(df, ignore_index=True, sort=True)
        else:
            newDF = pd.merge(newDF, df, how='outer', on=['fileIdentifier'])

newDF.to_csv('allTaxonomyIdentifiersByFileIdentifiers.csv', index=False)


updated = pd.merge(new_items, newDF, how='left', on=['fileIdentifier'], suffixes=('_1', '_2'))
print(updated.head)
filename3 = '01_'+filename3
updated.to_csv(filename3, index=False)
