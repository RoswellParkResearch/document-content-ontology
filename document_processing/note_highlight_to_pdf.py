import pandas as pds
import sys
import pdfkit as pdf
import os
from textwrap import dedent

reload(sys)
sys.setdefaultencoding('utf8')

def save_html(
        input_filepath,
        output_filepath,
        search_terms,
        polarities,
        sep='\t',
        tag_terms_flag=True,
        tag_field_name='NoteText',
        tag_field_index=-1,
        tag_font='bold',
        tag_color='red',
        tag_highlight=False,
        tag_font_size=''
        ):

    # coloring for polarity based tagging
    colors = {
        "positive": "green",
        "negative": "red"
    }

    def build_tag(term, color):
        tag = '<font color="' + color + '">' + term + '</font>'

        if tag_highlight:
            tag = '<span style="background-color: #FFFF00">' + tag + '</span>'

        # determine font
        if tag_font == 'bold':
            tag = '<b>' + tag + '</b>'
        elif tag_font == 'italics':
            tag ='<i>' + tag + '</i>'
        elif tag_font == 'bold and italics':
            tag = '<b><i>' + tag + '</i></b>'
        else:
            pass

        # determine font size
        if len(tag_font_size) > 0:
            tag = '<font size="' + tag_font_size + '">' + tag + '</font>'

        return tag

    def replace_str_index(text, index=0, replacement=''):
        return '%s %s ' % (text[:index-1], replacement)

    def replace_values(text, polarities, note_id):
        if not type(text) == type(""): return ""  # make sure that there is text to tag

        text_out = ""
        for i, tpl in enumerate(polarities[note_id]):
            period = False
            if i == 0:
                start = tpl[1]
                end = start+len(tpl[0])

                prev_start = tpl[1]
                prev_end = prev_start+len(tpl[0])
            else:
                # have to do this calculation off of the original difference between end and new start
                start = tpl[1]-prev_end
                end = start+len(tpl[0])

                prev_start = tpl[1]
                prev_end = prev_start+len(tpl[0])

            replacement = build_tag(tpl[0], colors[tpl[2]])
            if str(text[start - 1:end]).endswith('.'):
                period = True

            proc_text = replace_str_index(text, start, replacement)
            text = text[end:]

            if period:
                text += '.'

            if proc_text not in text_out:
                text_out += proc_text

        if len(text) > 0:
            text_out += text

        return text_out

    # read contents into data frame
    df = pds.read_csv(input_filepath, sep=sep, index_col=False, engine='python')

    with open(output_filepath, "w") as f:
        if tag_terms_flag:
            replaced_values = []
            for row in df.itertuples():
                row = row.__dict__

                # polarities is a key, val store with note id as the key and the vals as tuples: (term, start idx, polarity)
                text = replace_values(str(row['NoteText']), polarities, row['NoteID'])
                replaced_values.append(text)

            df['NoteText'] = replaced_values

        df = df[['MRN', 'AuthoredDtm', 'DocumentName', 'NoteID', 'NoteText']]
        df = df.sort_values(by=['MRN', 'NoteID', 'AuthoredDtm'])

        f.write('<html> <body>')
        # loop dataframe, write header row, add space, write note entirely. Look at the output html from previous runs to build this
        for row in df.itertuples():
            row = row.__dict__
            html = dedent("""
      <table border="1" class="dataframe">
        <thead>
            <tr style="text-align: left;" height="10">
                <th>MRN</th>
                <th>AuthoredDtm</th>
                <th>DocumentName</th>
                <th>NoteID</th>
            </tr>
        </thead>
        <tbody>
            <tr>
              <td>{0}</td>
              <td>{1}</td>
              <td>{2}</td>
              <td>{3}</td>
            </tr>
      </table>
      <br>
      <table width="1000" border="1" frame="box">
      <td>{4}</td>
      </table>
      <br>
      <br>
      <hr align="left" width="50%">
                          """.format(row['MRN'], row['AuthoredDtm'], row['DocumentName'], row['NoteID'], row['NoteText']))
            f.write(html)
        f.write('</body> </html>')
        f.close()
        return df

def word_window(text, window_size, indexes):

    # -1 in window size as default to use the entire note
    if window_size == -1:
        window_size = len(text)+1

    # find start and end of matches in the text
    positions = indexes

    # no match, don't need to keep the note
    if len(positions) < 1:
        return ""

    # calculate where to start the window, walk backwards until we're not in the middle of a word
    start_pos = min(positions) - window_size - 20
    if start_pos < 0: start_pos = 0
    while True:
        if start_pos == 0:
            break
        if text[start_pos] != ' ':
            start_pos -= 1
        else:
            break

    # calculate where the to end the window, walk forwards until we're not in the middle of a word
    end_pos = max(positions) + window_size + 20
    if end_pos > len(text): end_pos = len(text) - 1
    while True:
        if end_pos >= len(text):
            break
        if text[end_pos] != ' ':
            end_pos += 1
        else:
            break

    # return the word window around the start/end positions
    return text[start_pos:end_pos]


def word_window_df(df, window_size, needles, indexes, mode='string'):
    index_dict = {}
    for row in indexes.itertuples():
        row = row.__dict__
        if row['note_id'] not in index_dict:
            index_dict[row['note_id']] = {}
        if mode == 'ncit':
            if row['code'] in needles:
                index_dict[row['note_id']][row['term']] = int(row['index_start'])
        else:
            if row['term'] in needles:
                index_dict[row['note_id']][row['term']] = int(row['index_start'])

    indexed_windows = []
    for row in df.itertuples():
        row = row.__dict__
        note_indexes = {}
        if row['NoteID'] in index_dict:
            note_indexes = index_dict[row['NoteID']]
        positions = [index for term, index in note_indexes.items()]
        if len(positions) > 0:
            first_pos = min(positions)
            last_pos = max(positions)
            positions = [first_pos, last_pos]
        else:
            positions = []

        window = word_window(str(row['NoteText']), window_size, positions)
        indexed_windows.append(window)

    df['NoteText'] = indexed_windows

    df.drop_duplicates()
    pds.set_option('display.width', window_size*2)

    # only return the rows where NoteText had a match within the text
    return df.loc[df['NoteText'] != ""]

def get_terms_for_codes(indexes, codes, mode):
    df = indexes

    terms = []
    for row in df.itertuples():
        row = row.__dict__
        if mode == 'ncit':
            if row['code'] not in codes:
                continue
            else:
                if row['term'] not in terms:
                    terms.append(row['term'])
        else:
            if row['term'] not in codes:
                continue
            else:
                if row['term'] not in terms:
                    terms.append(row['term'])

    return terms

def get_term_polarities(indexes, codes, mode):
    df = indexes

    # convert the noble output of polarity column into single words
    polarity = {
        "Positive_Polarity": "positive",
        "Negative_Polarity": "negative"
    }

    # polarities is a key, val store with note id as the key and the vals as tuples: (term, start idx, polarity)
    polarities = {}

    df = df.sort_values(by=['mrn', 'note_id', 'index_start'])

    for row in df.itertuples():
        row = row.__dict__
        if row['note_id'] not in polarities:
            polarities[row['note_id']] = []
        if mode == 'ncit':
            if row['code'] not in codes:
                continue
            else:
                if (str(row['term']).strip(), row['index_start'], polarity[row['polarity']]) not in polarities[row['note_id']]:
                    polarities[row['note_id']].append((str(row['term']).strip(), row['index_start'], polarity[row['polarity']]))
        else:
            if row['term'] not in codes:
                continue
            else:
                if (str(row['term']).strip(), row['index_start'], polarity[row['polarity']]) not in polarities[row['note_id']]:
                    polarities[row['note_id']].append((str(row['term']).strip(), row['index_start'], polarity[row['polarity']]))

    return polarities

def output_highlight(raw_data_file,
                     css_file,
                     index_file,
                     output_directory,
                     codes,
                     window_size=-1,
                     cleanup=False,
                     mode='ncit'
                     ):
    # data in
    indexes_df = pds.read_csv(index_file, sep='\t')
    raw_data_df = pds.read_csv(raw_data_file, sep='\t')

    # data out
    html_out = os.path.join(output_directory, 'Noble HTML out.html')
    pdf_out = os.path.join(output_directory, 'Noble PDF out.pdf')
    windows_out = os.path.join(output_directory, 'Word windows out.txt')

    results = word_window_df(raw_data_df, window_size, codes, indexes_df, mode=mode)

    pds.DataFrame.to_csv(results, windows_out, sep='\t', index=False)

    # get all terms matched in text that were tagged with our ncit codes of interest
    terms = get_terms_for_codes(indexes_df, codes, mode)

    # get all polarities for terms matched in text that were tagged with our ncit codes of interest
    polarities = get_term_polarities(indexes_df, codes, mode)

    # pass terms if running NCIT codes, needles if strings
    save_html(windows_out, html_out,
              terms, polarities, tag_highlight=True)

    # path to the wkhtmltopdf.exe needs to be passed as kwarg or setting it in $PATH
    config = pdf.configuration(wkhtmltopdf=os.path.expanduser('~') +'\\wkhtmltopdf\\bin\wkhtmltopdf.exe')

    # pdf specifications and css. This css file fixes page breaks, repeating headers, and headers overlapping with data

    # the css file is simply:
    # thead, tfoot { display: table-row-group }
    # tr { page-break-inside: avoid }

    pdf_options = {
        'page-size': 'Letter',
        'margin-top': '0.1in',
        'margin-right': '0.1in',
        'margin-bottom': '0.1in',
        'margin-left': '0.1in',
        'encoding': "UTF-8",
        'user-style-sheet': css_file,
        'no-outline': None
    }
    pdf.from_file(html_out, pdf_out, configuration=config, options=pdf_options)

    if cleanup:
        os.remove(html_out)
        os.remove(windows_out)