
import os
import rdflib
from rdflib import RDF, OWL, BNode, Literal
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
        self._path_spec_traces = {}
        self._event_traces = {}
        self._event_exporters = {}

    def get_event_exporter(self, event):
        """Retrieves event exporter for given event."""
        data_type = event.data_type
        if data_type not in self._event_exporters:
            self._event_exporters[data_type] = EventExporter.from_data_type(
                data_type, self.document)
        return self._event_exporters[data_type]

    def export_path_spec(self, path_spec):
        """Exports the given DFVFS path spec into the graph.

        Returns: tuple containing URIRefs for Trace and File property bundle.
        """
        comparable = path_spec.comparable
        if comparable in self._path_spec_traces:
            # TODO: When filestat events call this, it will want to add more timestamps to the file pb.
            return self._path_spec_traces[comparable]

        trace = self.document.create_trace()
        file_pb = trace.create_property_bundle('File')

        self._path_spec_traces[comparable] = (trace, file_pb)

        # Add file path information.
        location = getattr(path_spec, 'location', None)
        if location:
            file_pb.add('filePath', location)
            file_name, extension = os.path.splitext(os.path.basename(location))
            file_pb.add('fileName', file_name)
            file_pb.add('extension', extension)

        file_pb.add(
            'fileSystemType', mappings.FileSystemType.get(path_spec.type_indicator, None))

        # If path spec has a parent, create the parent then create a relationship
        # object pointing to its parent.
        if path_spec.HasParent():
            parent_trace, _ = self.export_path_spec(path_spec.parent)
            relationship = self.document.create_relationship(
                source=trace,
                target=parent_trace,
                kindOfRelationship=mappings.kindOfRelationship.get(
                    path_spec.type_indicator, mappings.kindOfRelationship['_default']),
                # TODO: Not exactly sure what isDirectional means..
                isDirectional=True)

            # Add a property bundle to relationship if available.
            property_bundles.construct(path_spec.type_indicator, relationship)

        return trace, file_pb

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
        # Append extra file stat information to the "File" property bundle.
        if event.data_type == 'fs:stat':
            trace, file_pb = self.export_path_spec(event.pathspec)
            file_pb.add(
                'fileSystemType', mappings.FileSystemType.get(event.file_system_type, None))
            file_pb.add('isAllocated', event.is_allocated)
            file_pb.add('fileSize', getattr(event, 'file_size', None))

            # # Add extra file system specific property bundles. (eg. MFtRecord, Inode)
            # property_bundles.construct(event.data_type, trace, event)

        else:
            event_exporter = self.get_event_exporter(event)
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