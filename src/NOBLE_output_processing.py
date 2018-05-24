import sys
import os
import pandas as pds


reload(sys)
sys.setdefaultencoding('utf8')

path_in = os.path.expanduser('~') + '\\Note ontology\sample_NOBLE_data.txt'
path_out = os.path.expanduser('~') + '\\Note ontology\processed_sample_NOBLE_data.txt'

df = pds.read_csv(path_in, sep='\t')
df.columns = [column.lower().replace(' ', '_') for column in df.columns]

patient_ids = []
note_types = []
note_dates = []
note_ids = []
for row in df.itertuples():
    row = row.__dict__

    # note metadata for match. input files for NOBLE are named with patient ID, note type, note date, note ID
    # this filename is stored in the 'document' column of the output
    # e.g. 123456-Clinic Notes-2012 12 31 00 00 00-1234567891011121.txt
    record_meta = str(row["document"]).split('-')
    patient_id = record_meta[0]
    note_type = record_meta[1]

    raw_date = str(record_meta[2]).split(' ')
    date_out = '{0}/{1}/{2}'.format(raw_date[1], raw_date[2], raw_date[0])

    note_id = str(record_meta[3]).replace('.txt', '')
    code = str(row['code'])

    # create a series to append to dataframe
    patient_ids.append(patient_id)
    note_types.append(note_type)
    note_dates.append(date_out)
    note_ids.append(note_id)

# append data series to the dataframe
df["patient_id"] = patient_ids
df["note_type"] = note_types
df["note_date"] = note_dates
df["note_id"] = note_ids

# reorder rows
df = df[['patient_id', 'note_type', 'note_date', 'note_id', 'document', 'matched_term', 'code', 'concept_name',
         'semantic_type', 'annotations']]

pds.DataFrame.to_csv(df, path_out, sep='\t', index=False)
