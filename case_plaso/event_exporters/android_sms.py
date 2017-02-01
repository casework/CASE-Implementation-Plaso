
from case_plaso import lib
from case_plaso.event_exporter import EventExporter


@EventExporter.register('android:messaging:sms')
class AndroidSMSExporter(EventExporter):
    """Exporter for android sms events."""

    def export_event(self, event):
        contact = self.export_contact(phoneNumber=event.address)

        trace = self.document.create_trace()
        pb = trace.create_property_bundle(
            'Message',
            # TODO: Confirm that this timestamp will always be 'sent' and not possibly 'received' or 'downloaded'.
            sentTime=lib.convert_timestamp(event.timestamp),
            messageText=event.body)

        if event.sms_read != 'UNKNOWN':
            pb.add('isRead', event.sms_read == 'READ')

        if event.sms_type == 'RECEIVED':
            pb.add('from', contact)
        elif event.sms_type == 'SENT':
            pb.add('to', contact)
        else:
            pb.add('participant', contact)
