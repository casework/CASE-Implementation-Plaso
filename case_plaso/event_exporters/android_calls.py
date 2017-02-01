
from case_plaso.event_exporter import EventExporter


@EventExporter.register('android:event:call')
class AndroidCallExporter(EventExporter):
    """Exporter for android call events."""

    TIMESTAMP_MAP = {
        'Call Ended': 'endTime',
        'Call Started': 'startTime'}

    def export_event_data(self, event):
        phone_call_pb = self.document.create_trace().create_property_bundle(
            'PhoneCall',
            duration=event.duration,
            callType=event.call_type)

        contact = self.export_contact(contactName=event.name, phoneNumber=event.number)

        if event.call_type in ('INCOMING', 'MISSED'):
            phone_call_pb.add('from', contact)
        elif event.call_type == 'OUTGOING':
            phone_call_pb.add('to', contact)
        else:
            phone_call_pb.add('participant', contact)

        return phone_call_pb
