import pandas as pds
from textwrap import dedent
import sys
import os


reload(sys)
sys.setdefaultencoding('utf8')

noble_file_in = os.path.expanduser('~') + '\\Note ontology\processed_sample_NOBLE_data.txt'
ttl_out = os.path.expanduser('~') + '\\Note ontology\clinic_notes_ontology_sample.ttl'

def ttl_prefixes(base="", ontology_uri=""):
    # specify the base uri
    if base.strip() == "":
        base = "http://example.com/note_representations.owl/"

    # create uri for ontology
    if ontology_uri.strip() == "":
        ontology_uri = "http://example.com/sample_note_output.owl"

    ttl = dedent("""\
        @prefix dc: <http://purl.org/dc/elements/1.1/> .
        @prefix obo: <http://purl.obolibrary.org/obo/> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix swrl: <http://www.w3.org/2003/11/swrl#> .
        @prefix swrla: <http://swrl.stanford.edu/ontologies/3.3/swrla.owl#> .
        @prefix swrlb: <http://www.w3.org/2003/11/swrlb#> .
        @prefix xml: <http://www.w3.org/XML/1998/namespace> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .  
        @prefix emr: <{0}> .
        @prefix op: <{0}object_property/> . 
        @prefix dp: <{0}data_property/> .
        @base <{0}> .
        
        op:hasPatientID rdf:type owl:ObjectProperty .
        op:hasNoteID rdf:type owl:ObjectProperty . 
        
        dp:isAboutPatient rdf:type owl:DatatypeProperty .
        
        emr:mentions rdf:type owl:AnnotationProperty .
        
        <{1}> rdf:type owl:Ontology .

        """.format(base, ontology_uri))
    return ttl

df = pds.read_csv(noble_file_in, sep='\t')
df.columns = [column.lower().replace(' ', '_') for column in df.columns]

file_out = open(ttl_out, 'w')

file_out.write(ttl_prefixes(base="http://purl.roswellpark.org/emr/note_representations.owl/",
                            ontology_uri="http://purl.roswellpark.org/emr/sample_note_output.owl"))

patients = []
notes = []
concepts = {}
for row in df.itertuples():
    row = row.__dict__
    note_id = str(row['note_id']).strip()
    if row['patient_id'] not in patients:
        patients.append(row['patient_id'])
    if (row['patient_id'], row['note_id']) not in notes:
        notes.append((row['patient_id'], row['note_id']))
    if note_id not in concepts:
        concepts[note_id] = []

    # can not do the below check if you want to quantify multi matches within a note
    if row['concept_name'] not in concepts[note_id]:
        concepts[note_id].append(row['concept_name'])

for patient in patients:
    ttl = dedent("""
                 emr:pt_{0} rdf:type owl:NamedIndividual ;
                        rdf:type emr:dental_patient ;
                        op:hasPatientID '{0}' .
                 """).format(patient)
    file_out.write(ttl)

for note in notes:
    note_id = note[1]
    patient_id = note[0]
    ttl = dedent("""
                 emr:note_{0} rdf:type emr:dental_clinic_note ;
                              op:hasNoteID '{0}' ;
                              dp:isAboutPatient emr:pt_{1} .
                 """).format(note_id, patient_id)
    file_out.write(ttl)

for note_id, concept in concepts.items():
    concept_list = []
    for item in concept:
        item = item.strip()
        concept_list.append('"%s"' % item)
    out = ', '.join(str(element) for element in concept_list)
    ttl = dedent("""
                 emr:note_{0} emr:mentions {1} .
                 """).format(note_id, out)
    file_out.write(ttl)

file_out.close()

print "Ontology file generated"
