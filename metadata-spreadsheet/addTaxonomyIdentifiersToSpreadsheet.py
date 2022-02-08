import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    metadata_file = args.file
else:
    metadata_file = input('Enter filename (including \'.csv\'): ')

path = os.getcwd()
dir = os.path.dirname(path)
directory = os.path.join(dir, 'items-matched/')

tax = os.path.join(dir, 'logs/')
filename2 = os.path.join(tax, 'logOfTaxonomyTermsAdded.csv')
df_2 = pd.read_csv(filename2, header=0)
pivoted = pd.pivot(df_2, index='fileIdentifier', columns='type', values='id')
df_2 = pd.DataFrame(pivoted)
df_2 = df_2.reset_index()

new_items = pd.read_csv(metadata_file)

newDF = pd.DataFrame()
for count, filename in enumerate(os.listdir(directory)):
    print(count)
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
        if count == 0:
            newDF = newDF.append(df, ignore_index=True, sort=True)
        else:
            newDF = pd.merge(newDF, df, how='outer', on=['fileIdentifier'])

newDF.to_csv('allTaxonomyIdentifiersByFileIdentifiers.csv', index=False)


updated = pd.merge(new_items, newDF, how='left', on=['fileIdentifier'], suffixes=('_1', '_2'))
print(updated.head)
metadata_file = '01_'+metadata_file
updated.to_csv(metadata_file, index=False)
