
from dfvfs.lib import definitions as dfvfs_definitions
from plaso.engine.knowledge_base import KnowledgeBase
from plaso.storage import zip_file

from case_plaso import PLASO, lib
from case_plaso.event_exporter import EventExporter

# Import event exporters to get them registered.
from case_plaso import event_exporters as _


class PlasoExporter(object):
    """Exports plaso data into a RDF graph using the CASE ontology."""

    # Configuration attributes stored in a plaso Session object.
    _CONFIGURATION_ATTRIBUTES = [
        'identifier',
        'command_line_arguments',
        'debug_mode',
        'enabled_parser_names',
        'filter_expression',
        'filter_file',
        'parser_filter_expression',
        'preferred_encoding',
        'preferred_year']

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
        # TODO: Extract parser chain information and other metadata (e.g. sqlite query used)
        event_exporter = self.get_event_exporter(event.data_type)
        event_exporter.export_event(event)

    def export_session(self, session):
        """Exports the given plaso storage Session into the graph."""
        instrument = self.document.create_uco_object(
            'Tool',
            name=session.product_name,
            version=session.product_version,
            toolType='parser?',
            creator='Joachim Metz')
        config = instrument.create_property_bundle('ToolConfiguration')
        for attribute in self._CONFIGURATION_ATTRIBUTES:
            if hasattr(session, attribute):
                value = getattr(session, attribute)
                if value is None:
                    # None is technically a configuration, but we don't want to print "None".
                    value = ''
                value = str(value)
                setting = self.document.create_node(
                    'ConfigurationSetting', bnode=True, itemName=attribute, itemValue=value)
                config.add('configurationSetting', setting)

        # TODO: How do we know who performed the Plaso action? That information
        # is not in the plaso storage file...
        performer = self.document.create_uco_object('Identity')
        performer.create_property_bundle(
            'SimpleName',
            givenName='John',
            familyName='Doe')

        action = self.document.create_uco_object(
            'ForensicAction',
            startTime=lib.convert_timestamp(session.start_time),
            endTime=lib.convert_timestamp(session.completion_time))
        action.create_property_bundle(
            'ActionReferences',
            performer=performer,
            instrument=instrument,
            result=None,   # TODO: We can't fill this in because we don't know what session created what event objects...
            location=None)  # TODO: How am I supposed to be able to get this information?

    def export_storage_file(self, storage_file):
        """Extracts and exports plaso event data and sources into the graph."""
        with zip_file.ZIPStorageFileReader(storage_file) as storage_reader:
            knowledge_base = KnowledgeBase()
            storage_reader.ReadPreprocessingInformation(knowledge_base)
            # TODO: Export knowledge base.

            for session in storage_reader._storage_file.GetSessions():
                self.export_session(session)

            for source in storage_reader.GetEventSources():
                self.export_event_source(source)

            for event in storage_reader.GetEvents():
                self.export_event(event)
