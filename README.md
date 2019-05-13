# Cyber-investigation Analysis Standard Expression (CASE)

_Read the [CASE Wiki tab](https://github.com/casework/CASE/wiki) to learn **everything** you need to know about the Cyber-investigation Analysis Standard Expression (CASE) ontology._
_For learning about the Unified Cyber Ontology, CASE's parent, see [UCO](https://github.com/ucoProject/UCO)._

# CASE Plaso implementation

*Note: This POC is not ontology-correct!*

This is an implementation of exporting [plaso](https://github.com/log2timeline/plaso) storage files into an
RDF graph following the [CASE](https://github.com/casework/CASE) ontology.


### Install

Install the case API
```
git clone https://github.com/casework/CASE-Python-API.git
pip install CASE-Python-API
```

Then clone and install requirements.txt
```
git clone https://github.com/casework/CASE-Plaso-Implementation.git
cd CASE-Plaso-Implementation
pip install -r requirements.txt
```


### Usage
Pass the storage file created by the log2timeline tool into the "case_plaso" tool:
```
python case_plaso_export.py myimage.bin.plaso output.json --format json-ld
```

# I have a question!

Before you post a Github issue or send an email ensure you've done this checklist:

1. [Determined scope](https://caseontology.org/ontology/start.html#scope) of your task. It is not necessary for most parties to understand all aspects of the ontology, mapping methods, and supporting tools.

2. Familiarize yourself with the [labels](https://github.com/casework/CASE-Implementation-Plaso/labels) and search the [Issues tab](https://github.com/casework/CASE-Implementation-Plaso/issues). Typically, only light-blue and red labels should be used by non-admin Github users while the others should be used by CASE Github admins.
*All but the red `Project` labels are found in every [`casework`](https://github.com/casework) repository.*
