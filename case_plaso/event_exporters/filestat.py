
import os

from dfvfs.lib import definitions as dfvfs_definitions

from case_plaso import lib, mappings, file_relationships
from case_plaso.event_exporter import EventExporter


@EventExporter.register('fs:stat')
class FileStatExporter(EventExporter):

    TIMESTAMP_MAP = {
        'atime': 'accessedTime',
        'ctime': 'metadataChangedTime',
        'crtime': 'createdTime',
        'mtime': 'modifiedTime'}

    # List of dfvfs type indicators that should have their location attribute ignored
    # when trying to create a PathRelation property bundle.
    # TODO: Populate this.
    _IGNORE_PATH_TYPE_INDICATORS = [
        dfvfs_definitions.TYPE_INDICATOR_LVM,
        dfvfs_definitions.TYPE_INDICATOR_TSK_PARTITION]

    def __init__(self, document):
        super(FileStatExporter, self).__init__(document)
        self._path_spec_traces = {}
        self._content_data_pbs = {}
        self._processed_hashes = set()

    # TODO: Clean up this function.
    def export_path_spec(self, path_spec):
        """Exports the given DFVFS path spec into the graph.

        Returns: tuple containing URIRefs for Trace and File property bundle.
        """
        comparable = path_spec.comparable
        if comparable in self._path_spec_traces:
            return self._path_spec_traces[comparable]

        # If we have an Image file type flatten it into the parent.
        if path_spec.type_indicator in dfvfs_definitions.STORAGE_MEDIA_IMAGE_TYPE_INDICATORS:
            assert path_spec.HasParent()
            parent_trace, parent_file_pb = self.export_path_spec(path_spec.parent)
            parent_trace.create_property_bundle(
                'Image',
                imageType=mappings.ImageType[path_spec.type_indicator])
            self._path_spec_traces[comparable] = (parent_trace, parent_file_pb)
            return parent_trace, parent_file_pb

        trace = self.document.create_trace()
        file_pb = trace.create_property_bundle('File')
        self._path_spec_traces[comparable] = (trace, file_pb)

        file_pb.add(
            'fileSystemType', mappings.FileSystemType.get(path_spec.type_indicator, None))

        # Add file path information.
        location = getattr(path_spec, 'location', None)
        if location:
            file_pb.add('filePath', location)
            file_name, extension = os.path.splitext(os.path.basename(location))
            file_pb.add('fileName', file_name)
            if extension:
                file_pb.add('extension', extension)

        # If path spec has a parent, create the parent then create a relationship
        # object pointing to its parent.
        # TODO: CASE should rethink the approach of putting this information in Relationships.
        if path_spec.HasParent():
            parent_trace, _ = self.export_path_spec(path_spec.parent)
            relationship = self.document.create_uco_object(
                'Relationship',
                source=trace,
                target=parent_trace,
                kindOfRelationship=mappings.kindOfRelationship.get(
                    path_spec.type_indicator, mappings.kindOfRelationship['_default']),
                isDirectional=True)

            if location and path_spec.type_indicator not in self._IGNORE_PATH_TYPE_INDICATORS:
                relationship.create_property_bundle('PathRelation', path=location)

            # Add an extra property bundle to relationship if available.
            file_relationships.construct(path_spec.type_indicator, relationship, path_spec)

        # We then want to REPEAT the same information in the trace, because reasons.
        # However, I guess we don't have to do it for all types, but I'm not sure which ones
        # to not do it for, so I'm going to do it for all of them.
        # TODO: We should not be repeating the information like this. We should rethink this.
        file_relationships.construct(path_spec.type_indicator, trace, path_spec)

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

        # Add hash data into content_data property bundle.
        # NOTE: This is were we could technically add the dataPayload of the
        # file as well... although that would make the file HUGE!
        # TODO: Don't add ContentData if hash is missing.
        if event.pathspec not in self._content_data_pbs:
            self._content_data_pbs[event.pathspec] = trace.create_property_bundle('ContentData')
        content_data = self._content_data_pbs[event.pathspec]
        for name, value in event.GetAttributes():
            if name in mappings.HashMethod and (content_data, name, value) not in self._processed_hashes:
                # Keep track of processed hashes, so we don't add the same hash twice.
                # TODO: Refactor this out when github.com/log2timeline/plaso/issues/910 is solved.
                self._processed_hashes.add((content_data, name, value))
                hash = self.document.create_hash(
                    hashMethod=mappings.HashMethod[name], hashValue=value)
                content_data.add('hash', hash)
