from noble_nlp import Noble
from prepare_input_noble import process_file_to_files
from note_highlight_to_pdf import output_highlight
import os

nlp = Noble()

# where the input/output directories
nlp.root = 'C:\Users\phil\.noble'

# where the NobleCoder.jar file is
nlp.bin = 'C:\Users\phil\.noble'

# remove input files and intermediate files created during highlighting
nlp.cleanup = True

# populate the input directory
raw_data = 'test_data/sample_note_output.txt'
process_file_to_files(raw_data, nlp._in_dir)

# run noble coder on all files in the input directory
nlp.run()

if nlp.cleanup:
    nlp.clean_input()

print "Run complete."

print "Processing data."

nlp.process_data()
nlp.get_index_data()

print "Finished processing data."

print "Producing a pdf."

output_highlight(
    raw_data,
    css_file='test_data/PDFKit CSS fix.css',
    index_file='%s' % os.path.join(nlp._out_dir, 'Index Data.txt'),
    output_directory=nlp._out_dir,
    # periodontal disease NCIT codes for example. or set mode='string' and codes=['acuteness'] for the test_data
    codes=['C63743', 'C34918'],
    cleanup=nlp.cleanup,
)