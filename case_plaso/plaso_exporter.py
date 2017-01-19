
import os
from dfvfs.lib import definitions as dfvfs_definitions
from plaso.storage import zip_file

import case
from case import CASE
from case_plaso import PLASO, mappings, property_bundles
from case_plaso.event_exporter import EventExporter

# Import event exporters to get them registered.
from case_plaso import event_exporters as _


class PlasoExporter(object):
    """Exports plaso data into a RDF graph using the CASE ontology."""

    def __init__(self, document):
        """Initializes PlasoExporter.

        Args:
            document: CASE document to export plaso objects to.
        """
        self.document = document
        # Add 'plaso' prefix used by custom property bundles to internal graph.
        self.document.graph.namespace_manager.bind('plaso', PLASO)
        self._event_exporters = {}

    def get_event_exporter(self, data_type):
        """Retrieves event exporter for given event data_type."""
        if data_type not in self._event_exporters:
            self._event_exporters[data_type] = EventExporter.from_data_type(
                data_type, self.document)
        return self._event_exporters[data_type]

    def export_path_spec(self, path_spec):
        """Exports the given DFVFS path spec into the graph.

        Returns: tuple containing URIRefs for Trace and File property bundle.
        """
        # The event exporter for 'fs:stat' contains functionality to export
        # path_specs.
        file_stat_exporter = self.get_event_exporter('fs:stat')
        return file_stat_exporter.export_path_spec(path_spec)

    def export_event_source(self, event_source):
        if event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_DEVICE:
            # TODO
            pass
        elif event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_DIRECTORY:
            _, file_pb = self.export_path_spec(event_source.path_spec)
            file_pb.add('isDirectory', True)
        elif event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_FILE:
            _, file_pb = self.export_path_spec(event_source.path_spec)
            file_pb.add('isDirectory', False)
        else:
            # TODO: The rest are things like pipes, links, and sockets.
            pass

    def export_event(self, event):
        """Exports the given plaso EventObject into the graph."""
        event_exporter = self.get_event_exporter(event.data_type)
        event_exporter.export_event(event)

    def export_storage_file(self, storage_file):
        """Extracts and exports plaso event data and sources into the graph."""
        with zip_file.ZIPStorageFileReader(storage_file) as storage_reader:
            # TODO: Do stuff with metadata

            # Convert path specs into CASE Traces containgin file-type property bundles.
            for source in storage_reader.GetEventSources():
                self.export_event_source(source)

            for event in storage_reader.GetEvents():
                self.export_event(event)