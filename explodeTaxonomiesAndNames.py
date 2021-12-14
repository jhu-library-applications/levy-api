import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

tax_dir = '/Users/michelle/Documents/GitHub/levy-api/aggregated/'
if not os.path.exists(tax_dir):
    os.mkdir(tax_dir)

roles_dir = '/Users/michelle/Documents/GitHub/levy-api/aggregated-roles/'
if not os.path.exists(roles_dir):
    os.mkdir(roles_dir)

df = pd.read_csv(filename, header=0)

fields = ['field_publisher', 'field_subjects', 'field_instrumentation_metadata']
field_roles = ['lyricist', 'composer', 'arranger', 'no_role', 'pseudonym']
id = 'fileIdentifier'
# Reshapes sheet indexed by id (field aggregated)
# --> sheet indexed by field (id aggregated)

# original
# id   field
# Smith, Ed    001|004|005
# Smith, Jane  004

# new
# field        id
# 001          Smith, Ed
# 004          Smith, Ed|Smith, Jane
# 005          Smith, Ed

for field in field_roles:
    df[field] = df[field].str.strip()
    df[field] = df[field].str.split('|')
    df.reset_index()
    df = df.explode(field)

    # Pivot table, aggregated values associated with field.
    pivoted = pd.pivot_table(df, index=[field], values=id,
                             aggfunc=lambda x: '|'.join(str(v) for v in x))

    # Create updated_df from pivot table.
    updated_df = pd.DataFrame(pivoted)
    updated_df = updated_df.reset_index()

    updated_df[id] = updated_df[id].str.split('|')
    updated_df[id] = updated_df[id].apply(set)
    updated_df[id] = updated_df[id].apply(sorted)
    updated_df['count'] = updated_df[id].str.len()
    updated_df[id] = updated_df[id].str.join('|')
    updated_df = updated_df.rename(columns={field: 'title'})

    # Create CSV for updated_df.
    print(updated_df.columns)
    print(updated_df.head)
    newFile = 'AggregatedBy'+field+'.csv'
    fullname = os.path.join(roles_dir, newFile)
    updated_df.to_csv(fullname, index=False)

for field in fields:
    df[field] = df[field].str.strip()
    df[field] = df[field].str.split('|')
    df.reset_index()
    df = df.explode(field)

    # Pivot table, aggregated values associated with field.
    pivoted = pd.pivot_table(df, index=[field], values=id,
                             aggfunc=lambda x: '|'.join(str(v) for v in x))

    # Create updated_df from pivot table.
    updated_df = pd.DataFrame(pivoted)
    updated_df = updated_df.reset_index()

    updated_df[id] = updated_df[id].str.split('|')
    updated_df[id] = updated_df[id].apply(set)
    updated_df[id] = updated_df[id].apply(sorted)
    updated_df['count'] = updated_df[id].str.len()
    updated_df[id] = updated_df[id].str.join('|')
    updated_df = updated_df.rename(columns={field: 'name'})

    # Create CSV for updated_df.
    print(updated_df.columns)
    print(updated_df.head)
    newFile = 'AggregatedBy'+field+'.csv'
    fullname = os.path.join(tax_dir, newFile)
    updated_df.to_csv(fullname, index=False)
