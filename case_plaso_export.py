"""
Outputs event data contained in a plaso storage file into a JSON-LD
document following the CASE ontology.
"""

import argparse
import rdflib
import os

import case
from case_plaso import plaso_exporter


def main():
    parser = argparse.ArgumentParser(
        'Plaso-CASE',
        description='Extracts plaso events from a plaso storage file and '
                    'outputs a CASE document.')
    parser.add_argument(
        'storage_file',
        help='A plaso storage file. (The resulting file from running '
                    'log2timeline.)')
    parser.add_argument(
        'output_file',
        help='File path to export the resulting serialized file.')
    # TODO: Add specific choices
    parser.add_argument(
        '--format',
        choices=sorted([p.name for p in rdflib.plugin.plugins(kind=rdflib.serializer.Serializer)
                 if '/' not in p.name]),
        default='json-ld',
        help='The serialization format. (default: %(default)s)')
    options = parser.parse_args()

    if not os.path.exists(options.storage_file):
        raise IOError('Missing plaso storage file.')

    document = case.Document()
    exporter = plaso_exporter.PlasoExporter(document)
    print 'Exporting storage file...'
    exporter.export_storage_file(options.storage_file)
    print 'Serializing graph...'
    document.serialize(format=options.format, destination=options.output_file)


if __name__ == '__main__':
    main()
