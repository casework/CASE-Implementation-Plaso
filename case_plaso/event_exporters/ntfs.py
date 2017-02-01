
from plaso.lib.eventdata import EventTimestamp

from case_plaso.event_exporter import EventExporter


@EventExporter.register('fs:stat:ntfs')
class NTFSExporter(EventExporter):

    TIMESTAMP_MAP = {
        EventTimestamp.CREATION_TIME: 'mftFileNameCreatedTime',
        EventTimestamp.MODIFICATION_TIME: 'mftFileNameModifiedTime',
        EventTimestamp.ACCESS_TIME: 'mftFileNameAccessedTime',
        EventTimestamp.ENTRY_MODIFICATION_TIME: 'mftFileNameRecordChangeTime'}

    def export_event_data(self, event):
        # TODO: Figure out how to associate MftRecord pb with the associated
        # File pb so we don't have to make separate traces.
        # (The path spec points to the $Mft file.)
        trace = self.document.create_trace()
        pb = trace.create_property_bundle(
            'MftRecord',
            mftFileID=getattr(event, 'file_reference', None),
            mftFlags=getattr(event, 'file_attribute_flags', None),
            mftParentID=getattr(event, 'parent_file_reference', None))
        return pb
