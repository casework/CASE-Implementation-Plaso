
from case_plaso import lib

# Register functions based on indicators.
registry = {}


def register(cls):
    """Registers EventExporter classes into registry."""
    registry[cls.DATA_TYPE] = cls
    return cls


class EventExporter(object):
    """Base class for an event exporter."""

    # Defines data types this exporter works with.
    # (The data_types should be unique from all other event exporters.)
    DATA_TYPE = None

    def __init__(self, document):
        """Initializes PlasoExporter.

        Args:
            document: CASE document to export plaso objects to.
        """
        self.document = document
        self._cached_elements = {}

    def export_timestamp(self, event, cached_element):
        """Exports the timestamp information from the element.

        Args:
            event: The plaso EventObject to export timestamp info from.
            cached_element: The cached element returned from export_event_data()
        """
        raise NotImplementedError()

    def export_event_data(self, event):
        """Export the event, only pertaining to the event data, not the timestamp
        information.

        Returns:
            cached element to be passed back to export_timestamp().
            (usually this is a property bundle you created here)
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
        if event_data_hash not in self._cached_elements:
            self._cached_elements[event_data_hash] = self.export_event_data(event)

        self.export_timestamp(event, self._cached_elements[event_data_hash])

    @classmethod
    def from_data_type(cls, data_type, document):
        """Factory for creating a EventExporter class based on data_type."""
        try:
            return registry[data_type](document)
        except KeyError:
            return DefaultEventExporter(document)


class DefaultEventExporter(EventExporter):

    def export_event(self, event):
        # TODO: Do something with events without an explicit exporter.
        pass
