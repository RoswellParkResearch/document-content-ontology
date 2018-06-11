from subprocess import call
from bds_nlp.nlp_base import NLPProcessing
import os
import pandas as pds

class Noble(NLPProcessing):
    """ Handling of running Noble Coder."""

    def __init__(self):
        super(Noble, self).__init__()
        self.name = 'noble'
        self.terminology = 'NCI_Thesaurus'

    @property
    def _in_dir(self):
        return os.path.join(self.root, 'input')

    @property
    def _out_dir(self):
        return os.path.join(self.root, 'output')

    def _create_directories_if_needed(self):
        in_dir = self._in_dir
        out_dir = self._out_dir
        if not os.path.exists(in_dir):
            os.mkdir(in_dir)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

    def _run(self):
        if call(['java', '-jar', '%s\NobleCoder-1.0.jar' % self.root,
                 '-terminology', '%s' % self.terminology,
                 '-input', '%s' % self._in_dir,
                 '-output', '%s' % self._out_dir,
                 '-search best-match',
                 '-stripDigits',
                 '-stripSmallWords',
                 '-stripCommonWords',
                 '-selectBestCandidates',
                 '-ignoreUsedWords',
                 '-subsumptionMode',
                 '-acronymExpansion',
                 '-scoreConcepts',
                 '-negationDetection',
                ]) > 0:
            raise Exception('Error running Noble')

    def clean_input(self):
        input_files = [f for f in os.listdir(self._in_dir) if os.path.isfile(os.path.join(self._in_dir, f))]
        for file in input_files:
            os.remove('%s\%s'% (self._in_dir, file))
        print 'Input directory cleaned.'

    def process_data(self, save_df=True):

        df = pds.read_csv('%s' % os.path.join(self._out_dir, 'RESULTS.tsv'), sep='\t')
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
                 'semantic_type', 'annotations', 'polarity']]
        if save_df:
            pds.DataFrame.to_csv(df, '%s' % os.path.join(self._out_dir, 'Processed Data.txt'), sep='\t', index=False)

        return df

    def get_index_data(self, save_df=True):

        index_data = []

        df = pds.read_csv('%s' % os.path.join(self._out_dir, 'Processed Data.txt'), sep='\t')
        df.columns = [column.lower().replace(' ', '_') for column in df.columns]

        for row in df.itertuples():
            row = row.__dict__

            # note metadata for match
            record_meta = str(row["document"]).split('-')
            patient_id = record_meta[0]
            note_id = str(record_meta[3]).replace('.txt', '')
            code = str(row['code'])

            # note indexes for matched terms
            index_raw = str(row["annotations"]).split(',')
            polarity = str(row['polarity'])
            index_proc = [str(i).split('/') for i in index_raw if "/" in str(i)]
            for item in index_proc:
                index_data.append((patient_id, note_id, code, item[0], item[1], polarity))

        indexes = pds.DataFrame([result for result in index_data],
                                columns=['mrn', 'note_id', 'code', 'term', 'index_start', 'polarity'])

        if save_df:
            pds.DataFrame.to_csv(indexes, '%s' % os.path.join(self._out_dir, 'Index Data.txt'), sep='\t', index=False)

        return indexes

# example usage
if __name__ == "__main__":
    nlp = Noble()

    # where the input/output directories
    nlp.root = 'C:\Users\ph37399\.noble'

    # where the NobleCoder.jar file is
    nlp.bin = 'C:\Users\ph37399\.noble'
    nlp.cleanup = False

    nlp.run()

    if nlp.cleanup:
        nlp.clean_input()

    print "Run complete."
    
    # do processing on self.root\output\RESULTS.tsv here
    print "Processing data."

    nlp.process_data()
    nlp.get_index_data()

    print "Finished processing data."
    