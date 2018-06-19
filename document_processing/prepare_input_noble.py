import pandas as pds
import re
import string

def file_len(fname):
    # get line count of files. Using this method because enumerate doesn't hold entire contents of files in memory
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i

def prepare_file(path_in):
    with open(path_in, "r") as f:
        lines = f.readlines()
    f.close()
    return lines

def sanitize_punctuation(to_convert):
    pattern = re.compile('[%s]' % re.escape(string.punctuation))
    pattern_2 = re.compile('[^A-Za-z0-9]+')

    out = pattern.sub(' ', str(to_convert))
    out = pattern_2.sub(' ', str(out))

    return out

def read_file_to_df_batch(text, head, sep):
    # create data frame from parent file header and slice of text from parent file
    head = [item.strip() for item in head]

    out = []
    for line in text:
        split = line.split(sep)
        out.append(split)

    df = pds.DataFrame.from_records(out, columns=head)
    df = df.replace(r'\n', ' ', regex=True)

    return df

def split_note_file_to_files(dataframe, output_directory):

    for row in dataframe.itertuples(index=False):
        row = row.__dict__
        num = str(row['NoteID'])

        # creates files with file name structure below to store metadata:
        #   123456-Clinic Notes-12 25 2005 00 00 00-900008989856457.txt
        path_out = output_directory + '\\' + str(row['MRN']) + "-" + str(sanitize_punctuation(row['DocumentName'])) + "-" \
                   + str(sanitize_punctuation(row['AuthoredDtm'])) + "-" + num + ".txt"

        f = open(path_out, "w")
        f.write(str(row['NoteText']))
        f.close()

def process_file_to_files(raw_data_path_in, output_directory, batch_size=100, separator='\t'):

    print "Reading in lines"
    lines = prepare_file(raw_data_path_in)
    file_length = file_len(raw_data_path_in)

    print "Starting file creation"
    header = lines[0].split(separator)
    lines.pop(0)

    increment = 0
    # Crawl down the file and run the batcher on slices of the parent file
    while True:
        lines_in = lines[increment:increment+batch_size]

        df = read_file_to_df_batch(lines_in, head=header, sep=separator)

        # converts a slice of the larger data frame into separate files with one note per file
        split_note_file_to_files(df, output_directory)

        increment += batch_size
        if increment >= file_length:
            break

    print "File creation done"
