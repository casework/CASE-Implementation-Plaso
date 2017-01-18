
from case_plaso import event_exporter, lib


@event_exporter.register
class AndroidCallExporter(event_exporter.EventExporter):
    """Exporter for android call events."""

    DATA_TYPE = 'android:event:call'

    TIMESTAMP_MAP = {
        'Call Ended': 'endTime',
        'Call Started': 'startTime'}

    def __init__(self, document):
        super(AndroidCallExporter, self).__init__(document)
        self._contacts = {}

    def export_event_data(self, event):
        phone_call_pb = self.document.create_trace().create_property_bundle(
            'PhoneCall',
            duration=event.duration,
            callType=event.call_type)

        contact = self._contacts.get((event.name, event.number), None)
        if not contact:
            contact = self.document.create_trace()
            contact.create_property_bundle(
                'Contact',
                contactName=event.name,
                phoneNumber=event.number)
            self._contacts[(event.name, event.number)] = contact

        if event.call_type in ('INCOMING', 'MISSED'):
            phone_call_pb.add('from', contact)
        elif event.call_type == 'OUTGOING':
            phone_call_pb.add('to', contact)
        else:
            phone_call_pb.add('participant', contact)

        return phone_call_pb

    def export_timestamp(self, event, pb):
        try:
            pb.add(self.TIMESTAMP_MAP[event.timestamp_desc], lib.convert_timestamp(event.timestamp))
        except KeyError:
            pass
