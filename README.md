# CASE/UCO Plaso implemenation

This is an implementation of exporting [plaso](https://github.com/log2timeline/plaso) storage files into an
RDF graph following the [CASE/UCO](https://casework.github.io/case) ontology.


## Install

Install the case API
```
git clone https://github.com/casework/case-api-python.git
cd case-api-python
python setup.py install

```

Then clone and install requirements.txt
```
git clone https://github.com/casework/case-implementation-plaso.git
cd case-implementation-plaso
pip install -r requirements.txt
```


## Usage
Pass the storage file created by the log2timeline tool into the "case_plaso" tool:
```
python case_plaso_export.py myimage.bin.plaso output.json --format json-ld
```
