"""
Outputs event data contained in a plaso storage file into a JSON-LD
document following the CASE ontology.
"""

import argparse
import os
import rdflib

import case
from case_plaso import plaso_exporter, CASE


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

    document = case.Document()
    exporter = plaso_exporter.PlasoExporter(document)
    exporter.export_storage_file(options.storage_file)

    print document.serialize(format='turtle', destination='test.ttl')
