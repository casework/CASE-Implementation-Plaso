
import rdflib
from rdflib import RDF

# Store CASE binding in here, because it needs to be used in many modules.
CASE = rdflib.Namespace('http://case.example.org/core#')

# Store custom properties and objects not defined in CASE as the PLASO prefix.
PLASO = rdflib.Namespace('http://plaso.example.org/core#')