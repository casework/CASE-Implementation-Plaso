
from case_plaso import event_exporter, lib


@event_exporter.register
class AndroidSMSExporter(event_exporter.EventExporter):
    """Exporter for android sms events."""

    DATA_TYPE = 'android:messaging:sms'

    def __init__(self, document):
        super(AndroidSMSExporter, self).__init__(document)
        self._contacts = {}

    def export_event(self, event):
        contact = self._contacts.get(event.address, None)
        if not contact:
            contact = self.document.create_trace()
            contact.create_property_bundle(
                'Contact',
                phoneNumber=event.address)
            self._contacts[event.address] = contact

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
