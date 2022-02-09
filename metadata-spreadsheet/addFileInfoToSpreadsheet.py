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
logs = os.path.join(dir, 'logs/')

filename = os.path.join(logs, 'logOfImagesAndPDFs.csv')
df = pd.read_csv(filename, header=0)

new_items = pd.read_csv(metadata_file, header=0)

df.drop(['filename', 'postType', 'file_id', 'revision_id'], axis=1, inplace=True)
pivoted = pd.pivot_table(df, index=['fileIdentifier'], values=['image_id'],
                         aggfunc=lambda x: '|'.join(str(v) for v in x if pd.notna(v)))
pivoted2 = pd.pivot_table(df, index='fileIdentifier', values=['pdf_id'],
                          aggfunc=lambda x: '|'.join(str(v) for v in x if pd.notna(v)))
df2 = pd.DataFrame(pivoted)
df = pd.DataFrame(pivoted2)

updated = pd.merge(new_items, df, how='left', on=['fileIdentifier'], suffixes=('_1', '_2'))
updated = pd.merge(updated, df2, how='left', on=['fileIdentifier'], suffixes=('_1', '_2'))
print(updated.head)
metadata_file = metadata_file[3:]
metadata_file = '03_'+metadata_file
updated.to_csv(metadata_file, index=False)
