
from case import CASE

from case_plaso import lib, PLASO
from case_plaso.event_exporter import EventExporter


class SkypeExporter(EventExporter):

    def __init__(self, document):
        super(SkypeExporter, self).__init__(document)
        # Setup knowledge base.
        for topic in ('skype_accounts', 'skype_message_threads'):
            if topic not in self.knowledge_base:
                self.knowledge_base[topic] = {}

    def export_account(self, username, display_name=None):
        skype_accounts = self.knowledge_base['skype_accounts']
        account, pb = skype_accounts.get(username, (None, None))
        if not account:
            account = self.document.create_trace()
            account.create_property_bundle('Account', accountIssuer='Skype')
            pb = account.create_property_bundle(
                'DigitalAccount',
                accountLogin=username)
            skype_accounts[username] = (account, pb)

        # Add displayname if it has not already been added.
        if display_name and (pb, 'displayName', display_name) not in self.document:
            pb.add('displayName', display_name)

        return account


@EventExporter.register('skype:event:account')
class SkypeAccountExporter(SkypeExporter):
    """Exporter for skype account events."""

    TIMESTAMP_MAP = {
        'Profile Changed': PLASO.profileChangedTime,
        'Authenticate Request': PLASO.authenticateRequestTime,
        'Last Online': PLASO.lastOnlineTime,  # TODO: Not sure if this can constitute as CASE.lastLoginTime
        'Mood Event': PLASO.skypeMoodTime,  # What is this?!
        'Auth Request Sent': PLASO.authenticateRequestSentTime,
        'Last Used': PLASO.lastUsedTime,      # TODO: Again, could this constitute as CASE.lastLoginTime?
    }

    def export_event_data(self, event):
        trace = self.document.create_trace()

        # TODO: Ugh.. the Skype parser did not query for the "skypename" column which contains the username.
        # TODO: In the future, when we can get usernames, add account to knowledge_base.
        trace.create_property_bundle('Account', accountIssuer='Skype')
        # trace.create_property_bundle('DigitalAccount', displayName=event.display_name)

        # TODO: Should I be adding the account profile info on the same trace?
        # NOTE: This "username" is false. It's really: "{full_name} <{display_name}>"
        full_name, _, _ = event.username.rpartition(' ')
        first_name, _, last_name = full_name.partition(' ')
        trace.create_property_bundle('SimpleName', givenName=first_name, familyName=last_name)
        trace.create_property_bundle('SimpleAddress', country=event.country)

        # All the timestamps are unique, therefore we will appent them to an extended "SkypeAccount" pb.
        return trace.create_property_bundle(PLASO.SkypeAccount)


@EventExporter.register('skype:event:call')
class SkypeCallExporter(SkypeExporter):
    """Exporter for skype call events."""

    TIMESTAMP_MAP = {
        'WAITING': CASE.createdTime,
        'ACCEPTED': CASE.startTime,
        'FINISHED': CASE.endTime}

    def export_event_data(self, event):
        # TODO: Should video conferences be treated differently?
        trace = self.document.create_trace()
        pb = trace.create_property_bundle('PhoneCall')
        pb.add('callType', 'OUTGOING' if event.user_start_call else 'INCOMING')
        pb.add('to', self.export_account(event.dst_call))
        pb.add('from', self.export_account(event.src_call))
        trace.create_property_bundle(
            PLASO.SkypeCall,
            isVideo=event.video_conference)
        return pb

    def export_timestamp(self, event, property_bundle):
        # NOTE: The skype parser unconventionality sets the timestamp description as
        # the attribute "call_type".
        try:
            property_bundle.add(
                self.TIMESTAMP_MAP[event.call_type],
                lib.convert_timestamp(event.timestamp))
        except KeyError:
            pass


@EventExporter.register('skype:event:chat')
class SkypeChatExporter(SkypeExporter):
    """Exporter for skype chat events."""

    def export_message_thread(self, title):
        message_threads = self.knowledge_base['skype_message_threads']
        trace, pb = message_threads.get(title, (None, None))
        if not trace:
            trace = self.document.create_trace()
            pb = trace.create_property_bundle('MessageThread', displayName=title)
            message_threads[title] = trace, pb
        return trace, pb

    def export_event(self, event):
        trace = self.document.create_trace()
        pb = trace.create_property_bundle(
            'Message',
            unknownTime=lib.convert_timestamp(event.timestamp),  # This is probably sent time, but we can't be sure.
            messageText=getattr(event, 'text', None))


        # Add author.
        # The developer of this parser, connected the diplayname to the author username.
        display_name, _, username = event.from_account.rpartition(' ')
        username = username[1:-1]  # Remove surrounding < >
        author = self.export_account(username, display_name)
        pb.add('from', author)

        # Add recipients.
        for username in event.to_account.split(', '):
            if username:
                recipient = self.export_account(username)
                pb.add('to', recipient)

        # Add message thread.
        # TODO: I don't think the title is good enough for thread id.
        # The parser needs to be updated to use the "name" column from the "Chats" table.
        _, message_thread_pb = self.export_message_thread(event.title)
        message_thread_pb.add('message', trace)
        
        
@EventExporter.register('skype:event:transferfile')
class SkypeFileTransferExporter(SkypeExporter):
    """Exporter for skype file transfer events."""
    
    def export_event(self, event):
        # TODO: CASE needs to add support for file transfers.
        pass


@EventExporter.register('skype:event:sms')
class SkypeSMSExporter(SkypeExporter):
    """Exporter for skype sms events."""

    def export_event(self, event):
        # TODO: The parser could have potentially joined the "SMSes" table with the "Messages" table in order to grab
        # more information such as the username and direction... unfortunately it did not..
        contact = self.export_contact(phonenNumber=event.number)
        trace = self.document.create_trace()
        trace.create_property_bundle(
            'Message',
            participant=contact,
            unknownTime=lib.convert_timestamp(event.timestamp)  # TODO: Figure out meaning. (its probably created or sent time)
        )

