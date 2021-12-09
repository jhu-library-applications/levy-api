import csv
import argparse
import pandas as pd
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

captureWords = [' and', 'Symbols', 'Names', ' for', ' of', 'chords', 'Chords',
                'solfege', 'Solfege', 'Dance', 'dance', 'figures', 'concert',
                'Concert', 'band']
itemList = []
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for count, row in enumerate(itemMetadata):
        row = row
        fileIdentifier = row['fileIdentifier']
        publish_date = row['field_publish_date_text']
        box = fileIdentifier[5:8]
        row['field_box'] = box.zfill(3)
        id = fileIdentifier[-3:]
        row['field_item_id'] = id.zfill(3)
        title = row['dc.title']
        authors = row['field_item_author']
        authors = authors.split('|')
        fullTitle = '{}.{} - {}'.format(str(box), str(id), title)
        row['field_full_title'] = fullTitle
        for author in authors:
            if "(" in author:
                role = author[author.find("(")+1:author.find(")")]
                author = author.replace('('+role+')', '')
                author = author.strip()
                if '&' in role:
                    roles = role.split(' & ')
                    for r in roles:
                        existing = row.get(r)
                        if existing:
                            row[r] = existing+'|'+author
                        else:
                            row[r] = author
                elif 'and' in role:
                    roles = role.split(' and ')
                    for r in roles:
                        existing = row.get(r)
                        if existing:
                            row[r] = existing+'|'+author
                        else:
                            row[r] = author
                else:
                    existing = row.get(role)
                    if existing:
                        row[role] = existing+'|'+author
                    else:
                        row[role] = author
            else:
                author = author
                existing = row.get('no_role')
                if existing:
                    row['no_role'] = existing+'|'+author
                else:
                    row['no_role'] = author
        description = row['dc.description']
        description = description.split("|")
        for x in description:
            if "Plate identifier: " in x:
                x = x.replace('Plate identifier: ', '')
                x = x.strip()
                row['field_plate_number'] = x
            elif "ad on" in x:
                row['field_advertisement'] = x
            elif "ads on" in x:
                row['field_advertisement'] = x
            elif "back cover" in x:
                row['field_advertisement'] = x
            elif "Johns Hopkins University, Levy Sheet Music Collection" in x:
                row['boxitem'] = x
            else:
                x = x.strip()
                x = x.rstrip('.')
                x = x.split('.')
                for component in x:
                    component = component.strip()
                    if '.' in component:
                        component = component.capitalize()
                    else:
                        component = component.capitalize()
                        component = component+'.'
                    existing = row.get('field_instrumentation')
                    if existing:
                        combined = existing+" "+component
                        row['field_instrumentation'] = combined
                    else:
                        row['field_instrumentation'] = component
        field_dedicatee = row['field_dedicatee']
        row['field_dedicatee'] = field_dedicatee.replace('|', ' ')
        instrumentation = row.get('field_instrumentation')
        if instrumentation is not None:
            for word in captureWords:
                if word in instrumentation:
                    instrumentation = instrumentation.replace(word, '')
            instrumentation = instrumentation.lower()
            instrumentation = instrumentation.strip()
            instrumentation = instrumentation.replace('.', '')
            instrumentation = instrumentation.replace(',', '')
            instrumentation = instrumentation.split()
            instrumentation = set(instrumentation)
            instrumentation = list(instrumentation)
            instrumentation = sorted(instrumentation)
            instrumentation = "|".join(instrumentation)
            row['field_instrumentation_metadata'] = instrumentation

        alternative = row['dc.title.alternative']
        alternative = alternative.split('|')
        for x in alternative:
            if "[first line]" in x:
                x = x.replace('[first line]', '')
                x = x.strip()
                row['field_first_line'] = x
            else:
                x = x.replace('[first line of chorus]', '')
                x = x.strip()
                row['field_first_line_of_chorus'] = x
        try:
            publish_date = int(publish_date)
            row['field_publish_date_year'] = str(publish_date)
        except (TypeError, ValueError):
            pass
        itemList.append(row)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df_1 = pd.DataFrame.from_records(itemList)
filename = filename[:-4]
df_1.to_csv(filename+'_1.csv', index=False, quoting=csv.QUOTE_ALL)
