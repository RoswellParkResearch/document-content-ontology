# Document Content Ontology

The purpose of the document content ontology is represent the contents with different kinds of documents. For example, if a pathology report mentions that the speciment was taken from the patient's lung, we want to represent that the report is about the patient, the term that reprenents the patient's lung, and link the term to another ontology (such as the FMA or UBERON) that has a well structured representation of anatomical sites. Parts of the ontology are inspired by the Information Artificact Ontology and Semanticscience Integrated Ontology, but we prefer not to carry the metaphysical commits (such as a document being a kind of generically dependent continuant) that come along with these ontologies.

![](https://github.com/RoswellParkResearch/document-content-ontology/blob/master/diagrams/document_content_ontology-v2.png)

Our driving use case is the processing the output of text documents passed through the Noble Coder Named Entity Recognition engine (http://noble-tools.dbmi.pitt.edu/). From this output, we represent the relevant parts, such as index where a particular term was found and its semantic type (i.e., the ontology class that specifies the meaning of the term). Output from other NLP (or text mining) programs can (of course) be used, and other annotations and data properties can be added as needed.

Raw Noble output for use with the scripts is located in the 'sample data' folder.

The raw output is run through scripts in the following order:
- NOBLE_output_processing
- ontologic_note_representation

This leaves you with a turtle (.ttl) file that can be loaded into a triple store along with the note_representation ontology.
