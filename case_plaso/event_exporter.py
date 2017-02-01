
import collections
from case_plaso import lib


class EventExporter(object):
    """Base class for an event exporter."""

    TIMESTAMP_MAP = {}

    # A knowledge base that will be shared among all instances of this class.
    # NOTE: This will obviously break in the future if/when we support multiprocessing
    # TODO: Make this more robust and harder for an event exporter to accidentally destroy everything.
    knowledge_base = {}

    _registry = {}

    def __init__(self, document):
        """Initializes PlasoExporter.

        Args:
            document: CASE document to export plaso objects to.
        """
        self.document = document
        self._cached_property_bundles = {}
        self._contacts = {}

    def export_contact(self, **properties):
        """Exports contact information from given properties.

        Args:
            properties: Dictionary of property names and values to export.

        Returns:
            The resulting trace.
        """
        contact_hash = lib.hash_dict(properties)
        contact = self._contacts.get(contact_hash, None)
        if not contact:
            contact = self.document.create_trace()
            contact.create_property_bundle('Contact', **properties)
            self._contacts[contact_hash] = contact
        return contact

    def export_timestamp(self, event, property_bundle):
        """Exports the timestamp information from the element.

        Args:
            event: The plaso EventObject to export timestamp info from.
            property_bundle: The cached property bundle to place timestamp on.
        """
        try:
            property_bundle.add(
                self.TIMESTAMP_MAP[event.timestamp_desc],
                lib.convert_timestamp(event.timestamp))
        except KeyError:
            pass

    def export_event_data(self, event):
        """Export the event, only pertaining to the event data, not the timestamp
        information.

        Returns:
            property bundle to be passed back to export_timestamp().
        """
        raise NotImplementedError()

    def export_event(self, event):
        """Exports a plaso event into the document."""
        # Usually there are duplicate events where only the timestamps is different.
        # Therefore, by default we are going to process event_data and timestamps
        # in separate processes.
        # If this is not the case, (single timestamp events) please overwrite this function.
        # TODO: Refactor this out when github.com/log2timeline/plaso/issues/910 is solved.

        event_data_hash = lib.hash_event_data(event)

        # Run export_event_data only on the first instance.
        if event_data_hash not in self._cached_property_bundles:
            self._cached_property_bundles[event_data_hash] = self.export_event_data(event)

        self.export_timestamp(event, self._cached_property_bundles[event_data_hash])

    @classmethod
    def register(cls, data_type):
        """Decorator for registering EventExporter classes into registry based on data_type."""
        def _register(_cls):
            cls._registry[data_type] = _cls
            return _cls
        return _register

    @classmethod
    def from_data_type(cls, data_type, document):
        """Factory for creating a EventExporter class based on data_type."""
        try:
            return cls._registry[data_type](document)
        except KeyError:
            return DefaultEventExporter(document)


class DefaultEventExporter(EventExporter):

    def export_event(self, event):
        # TODO: Do something with events without an explicit exporter.
        pass
