
import os
import rdflib
from rdflib import RDF, OWL, BNode, Literal
from dfvfs.lib import definitions as dfvfs_definitions
from plaso.storage import zip_file

import case
from case import CASE
from case_plaso import PLASO, mappings, property_bundles


# document = case.Document()
# trace = document.create_trace()
# pb = trace.create_property_bundle('File', filePath='this', extension='is')
# pb.add('fileName', 'test')
# print document.serialize(format='turtle')


class PlasoExporter(object):
    """Exports plaso data into a RDF graph using the CASE ontology."""

    def __init__(self, graph=None):
        if not graph:
            # TODO: For now we are going to store graph in memory, change to
            # a database store in the future.
            graph = rdflib.Graph()
            graph.namespace_manager.bind('case', CASE)
            graph.namespace_manager.bind('plaso', PLASO)
        self.graph = graph
        self._path_spec_traces = {}

    def export_path_spec(self, path_spec):
        """Exports the given DFVFS path spec into the graph.

        Returns: tuple containing URIRefs for Trace and File property bundle.
        """
        comparable = path_spec.comparable
        if comparable in self._path_spec_traces:
            # TODO: When filestat events call this, it will want to add more timestamps to the file pb.
            return self._path_spec_traces[comparable]

        trace = BNode()
        file_pb = BNode()
        self._path_spec_traces[comparable] = (trace, file_pb)

        self.graph.add((trace, RDF.type, CASE.Trace))
        self.graph.add((file_pb, RDF.type, CASE.File))
        self.graph.add((trace, CASE.propertyBundle, file_pb))

        # Add file path information.
        location = getattr(path_spec, 'location', None)
        if location:
            self.graph.add((file_pb, CASE.filePath, Literal(location)))
            file_name, extension = os.path.splitext(os.path.basename(location))
            self.graph.add((file_pb, CASE.fileName, Literal(file_name)))
            self.graph.add((file_pb, CASE.extension, Literal(extension)))

        # Add file system type.
        # TODO: I'm confused about the rules. Should I be adding a "fileSystemType"
        # property? or should I be creating a "FileSystem" property bundle?
        file_system_type = mappings.FileSystemType.get(path_spec.type_indicator, None)
        # if not file_system_type:
        #     # TODO: Figure out better way to handle this.
        #     # If we don't have a matching file system type, create a custom one.
        #     # (We must do this in order to stay lossless.)
        #     file_system_type = CASE[path_spec.type_indicator]
        #     self.graph.add((file_system_type, RDF.type, OWL.NamedIndividual))
        #     self.graph.add((file_system_type, RDF.type, CASE.FileSystemType))
        if file_system_type:
            self.graph.add((file_pb, CASE.fileSystemType, file_system_type))

        # If path spec has a parent, create the parent then create a relationship
        # object pointing to its parent.
        if path_spec.HasParent():
            parent_trace, _ = self.export_path_spec(path_spec.parent)
            relationship = rdflib.BNode()
            self.graph.add((relationship, RDF.type, CASE.Relationship))
            self.graph.add((relationship, CASE.source, trace))
            self.graph.add((relationship, CASE.target, parent_trace))
            kind_of_relationship = mappings.kindOfRelationship.get(
                path_spec.type_indicator, mappings.kindOfRelationship['_default'])
            self.graph.add((relationship, CASE.kindOfRelationship, Literal(kind_of_relationship)))
            # TODO: Not exactly sure what isDirectional means...
            self.graph.add((relationship, CASE.isDirectional, Literal(True)))

            # Add a property to relationship if available.
            pb = property_bundles.construct(
                path_spec.type_indicator, self.graph, path_spec)
            if pb:
                self.graph.add((relationship, CASE.propertyBundle, pb))

        return trace, file_pb

    def export_event_source(self, event_source):
        if event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_DEVICE:
            # TODO
            pass
        elif event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_DIRECTORY:
            _, file_pb = self.export_path_spec(event_source.path_spec)
            self.graph.add((file_pb, CASE.isDirectory, rdflib.Literal(True)))
        elif event_source.file_entry_type == dfvfs_definitions.FILE_ENTRY_TYPE_FILE:
            _, file_pb = self.export_path_spec(event_source.path_spec)
            self.graph.add((file_pb, CASE.isDirectory, rdflib.Literal(False)))
        else:
            # TODO: The rest are things like pipes, links, and sockets.
            pass

    def export_event(self, event):
        # Append extra file stat information to the "File" property bundle.
        if event.data_type in ('fs:stat', 'fs:stat:ntfs'):
            _, file_pb = self.export_path_spec(event.path_spec)
            file_system_type = mappings.FileSystemType.get(event.file_system_type, None)
            if file_system_type:
                self.graph.add((file_pb, CASE.fileSystemType, file_system_type))
            self.graph.add((file_pb, CASE.isAllocated, Literal(event.is_allocated)))
            file_size = getattr(event, 'file_size', None)
            if file_size is not None:
                self.graph.add((file_pb, CASE.fileSize, Literal(file_size)))




    def export_storage_file(self, storage_file):
        """Extracts and exports plaso event data and sources into the graph."""
        with zip_file.ZIPStorageFileReader(storage_file) as storage_reader:
            # TODO: Do stuff with metadata

            # Convert path specs into CASE Traces containgin file-type property bundles.
            for source in storage_reader.GetEventSources():
                self.export_event_source(source)

            for event in storage_reader.GetEvents():
                self.export_event(event)