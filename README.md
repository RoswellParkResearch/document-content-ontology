# Document Content Ontology

The purpose of the document content ontology is represent the contents with different kinds of documents. For example, if a pathology report mentions that the speciment was taken from the patient's lung, we want to represent that the report is about the patient, the string that reprenents the patient's lung, and link this to another ontology (such as the FMA or UBERON) that has a well structured representation of anatomical sites. Some parts of the ontology are based on the Information Artificact Ontology, but we also deviate from it.

[Document Content Ontology](./diagrams/document-content-ontology/diagrams/document%20content%20ontology.png)

Our driving use case is the processing the output of text documents passed through the Noble Coder NLP engine (http://noble-tools.dbmi.pitt.edu/). From this output, we then represent the relevant parts of the output, such as index where a particular string was found and its semantic type (i.e., the ontology class that specifies the meaning of the string). Output from other NLP (or text mining) programs can (of course) be used, and other annotations and data properties can be added as needed.

Raw Noble output for use with the scripts is located in the 'sample data' folder.

The raw output is run through scripts in the following order:
- NOBLE_output_processing
- ontologic_note_representation

This leaves you with a turtle (.ttl) file that can be loaded into a triple store along with the note_representation ontology.
