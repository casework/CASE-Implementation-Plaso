# CASE/UCO Plaso implementation

*Note: This POC is not ontology-correct! The Volatility example is more up to date.*

This is an implementation of exporting [plaso](https://github.com/log2timeline/plaso) storage files into an
RDF graph following the [CASE/UCO](https://github.com/ucoProject/CASE) ontology.


## Install

Install the case API
```
git clone https://github.com/ucoProject/CASE-Python-API.git
pip install CASE-Python-API
```

Then clone and install requirements.txt
```
git clone https://github.com/ucoProject/CASE-Plaso-Implementation.git
cd CASE-Plaso-Implementation
pip install -r requirements.txt
```


## Usage
Pass the storage file created by the log2timeline tool into the "case_plaso" tool:
```
python case_plaso_export.py myimage.bin.plaso output.json --format json-ld
```
