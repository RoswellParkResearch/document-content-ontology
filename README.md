# note-ontology

The purpose of code in this repo is to use the output of text documents passed through the Noble Coder NLP engine (http://noble-tools.dbmi.pitt.edu/) to develop an ontology capable of being loaded into and queried using a triple store.

Raw Noble output for use with the scripts is located in the 'sample data' folder.

The raw output is run through scripts in the following order:
- NOBLE_output_processing
- ontologic_note_representation

This leaves you with a turtle (.ttl) file that can be loaded into a triple store along with the note_representation ontology.