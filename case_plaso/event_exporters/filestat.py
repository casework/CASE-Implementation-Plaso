
import os

from case import CASE
from case_plaso import event_exporter, lib, mappings, property_bundles


@event_exporter.register
class FileStatExporter(event_exporter.EventExporter):

    DATA_TYPE = 'fs:stat'

    TIMESTAMP_MAP = {
        'atime': 'accessedTime',
        'ctime': 'metadataChangedTime',
        'crtime': 'createdTime',
        'mtime': 'modifiedTime'}

    def __init__(self, document):
        super(FileStatExporter, self).__init__(document)
        self._path_spec_traces = {}

    def export_path_spec(self, path_spec):
        """Exports the given DFVFS path spec into the graph.

        Returns: tuple containing URIRefs for Trace and File property bundle.
        """
        comparable = path_spec.comparable
        if comparable in self._path_spec_traces:
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
            if extension:
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

    def export_event(self, event):
        trace, file_pb = self.export_path_spec(event.pathspec)
        # NOTE: Re-adding the same property is fine. Duplicate triples will be removed.
        file_pb.add(
            'fileSystemType', mappings.FileSystemType.get(event.file_system_type, None))
        file_pb.add('isAllocated', event.is_allocated)
        file_pb.add('fileSize', getattr(event, 'file_size', None))
        # TODO: What is file_entry_type?

        # Add timestamps.
        if event.timestamp_desc in self.TIMESTAMP_MAP:
            file_pb.add(
                self.TIMESTAMP_MAP[event.timestamp_desc],
                lib.convert_timestamp(event.timestamp))

        # Add file system specific property bundles.
        # TODO: Is there anyway to get more information?
        elif event.timestamp_desc == 'bkup_time':
            trace.create_property_bundle(
                'HFSFileSystem',
                hfsBackupTime=lib.convert_timestamp(event.timestamp))
        elif event.timestamp_desc == 'dtime':
            trace.create_property_bundle(
                'ExtInode',
                extDeletionTime=lib.convert_timestamp(event.timestamp))