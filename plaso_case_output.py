"""
Outputs event data contained in a plaso storage file into a JSON-LD
document following the CASE ontology.
"""

import argparse
import os
import rdflib

from case_plaso import plaso_exporter, CASE


def get_context(graph):
  context = dict(
      (pfx, unicode(ns))
      for (pfx, ns) in graph.namespaces() if pfx and
      unicode(ns) != u"http://www.w3.org/XML/1998/namespace")
  context['@vocab'] = str(CASE)
  return context


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        'Plaso-CASE',
        description='Extracts plaso events from a plaso storage file and '
                    'outputs a CASE document.')
    parser.add_argument(
        'storage_file',
        help='A plaso storage file. (The resulting file from running '
                    'log2timeline.)')
    options = parser.parse_args()

    if not os.path.exists(options.storage_file):
        raise IOError('Missing plaso storage file.')

    exporter = plaso_exporter.PlasoExporter()
    exporter.export_storage_file(options.storage_file)

    print exporter.graph.serialize(format='turtle')

    # print graph.serialize(format='json-ld', context=get_context(graph))


    # trace1 = rdflib.BNode()
    # graph.add((trace1, RDF.type, CASE.Trace))
    #
    # content_data1 = rdflib.BNode()
    # graph.add((content_data1, RDF.type, CASE.ContentData))
    # graph.add((content_data1, CASE.byteOrder, CASE.BigEndian))
    # graph.add((content_data1, CASE.sizeInBytes, rdflib.Literal(17)))
    # graph.add((content_data1, CASE.data, rdflib.Literal("bmVsc29uQGNyeW53ci5jb20=")))
    #
    # hash1 = rdflib.BNode()
    # graph.add((hash1, RDF.type, CASE.Hash))
    # graph.add((hash1, CASE.hashMethod, CASE.SHA256))
    # graph.add((hash1, CASE.hashValue, rdflib.Literal("8fabebdaf41b54014f6c3507c44ae160547d05d31bd50d6a12234c5bc4bdb45c")))
    # graph.add((content_data1, CASE.hash, hash1))
    #
    # graph.add((trace1, CASE.propertyBundle, content_data1))
    #
    # content_data2 = rdflib.BNode()
    # graph.add((content_data2, RDF.type, CASE.ContentData))
    # graph.add((content_data2, CASE.byteOrder, CASE.LittleEndian))
    # graph.add((trace1, CASE.propertyBundle, content_data2))
    #
    # # context = Context()
