from configparser import SectionProxy
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder
from msgraph.generated.users.item.mail_folders.item.messages.messages_request_builder import MessagesRequestBuilder
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.users.item.calendar.events.events_request_builder import EventsRequestBuilder
from msgraph.generated.sites.sites_request_builder import SitesRequestBuilder

class Graph:
    settings: SectionProxy
    client_credential: ClientSecretCredential
    app_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        client_secret = self.settings['clientSecret']

        self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        self.app_client = GraphServiceClient(self.client_credential) # type: ignore

        # Hard-coded user ID
        self.user_id = '7e00cad8-6276-4c23-89f7-d3ea1c5fd1b8'

    async def get_app_only_token(self):
        graph_scope = 'https://graph.microsoft.com/.default'
        access_token = await self.client_credential.get_token(graph_scope)
        return access_token.token

    async def get_user(self):
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.app_client.users.by_user_id(self.user_id).get(request_configuration=request_config)
        return user

    async def get_inbox(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            top=25,
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        messages = await self.app_client.users.by_user_id(self.user_id).mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages

    async def send_mail(self, subject: str, body: str, recipient: str):
        message = Message()
        message.subject = subject

        message.body = ItemBody()
        message.body.content_type = BodyType.Text
        message.body.content = body

        to_recipient = Recipient()
        to_recipient.email_address = EmailAddress()
        to_recipient.email_address.address = recipient
        message.to_recipients = []
        message.to_recipients.append(to_recipient)

        request_body = SendMailPostRequestBody()
        request_body.message = message

        await self.app_client.users.by_user_id(self.user_id).send_mail.post(body=request_body)

    async def extract_inference_data(self):
        await self.extract_email_metadata()
        await self.extract_calendar_events()
        await self.extract_contacts_and_network()
        await self.extract_sharepoint_usage()

    async def extract_email_metadata(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            select=['from', 'isRead', 'receivedDateTime', 'subject', 'toRecipients', 'ccRecipients', 'importance', 'hasAttachments', 'categories'],
            top=25,
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        messages = await self.app_client.users.by_user_id(self.user_id).mail_folders.by_mail_folder_id('inbox').messages.get(
            request_configuration=request_config)

        email_metadata = []
        for message in messages.value:
            metadata = {
                "subject": message.subject,
                "from": message.from_.email_address.address if message.from_ and message.from_.email_address else "N/A",
                "received_date_time": message.received_date_time.strftime('%Y-%m-%d %H:%M:%S%z'),
                "is_read": message.is_read,
                "to_recipients": [recipient.email_address.address for recipient in message.to_recipients] if message.to_recipients else [],
                "cc_recipients": [recipient.email_address.address for recipient in message.cc_recipients] if message.cc_recipients else [],
                "importance": message.importance.value if message.importance else "normal",
                "has_attachments": message.has_attachments,
                "categories": message.categories if message.categories else []
            }
            email_metadata.append(metadata)

        # Print the enriched metadata
        for metadata in email_metadata:
            print(f"Subject: {metadata['subject']}")
            print(f"From: {metadata['from']}")
            print(f"Received: {metadata['received_date_time']}")
            print(f"Read: {'Yes' if metadata['is_read'] else 'No'}")
            print(f"To Recipients: {', '.join(metadata['to_recipients'])}")
            print(f"CC Recipients: {', '.join(metadata['cc_recipients'])}")
            print(f"Importance: {metadata['importance']}")
            print(f"Has Attachments: {'Yes' if metadata['has_attachments'] else 'No'}")
            print(f"Categories: {', '.join(metadata['categories'])}")
            print("-" * 40)
        
        # Return the enriched metadata
        return email_metadata

    async def extract_calendar_events(self):
        query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
            select=['subject', 'start', 'end', 'location'],
            top=25,
            orderby=['start/dateTime DESC']
        )
        request_config = EventsRequestBuilder.EventsRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        events = await self.app_client.users.by_user_id(self.user_id).calendar.events.get(request_configuration=request_config)
        for event in events.value:
            print(f"Subject: {event.subject}, Start: {event.start.date_time}, End: {event.end.date_time}, Location: {event.location.display_name}")
        # Return the calendar events
        return events

    async def extract_contacts_and_network(self):
        contacts = await self.app_client.users.by_user_id(self.user_id).contacts.get()
        if contacts.value:
            for contact in contacts.value:
                print(f"Name: {contact.display_name}, Email: {contact.email_addresses[0].address if contact.email_addresses else 'N/A'}")
        else:
            print("No contacts found.")

        # Return the contacts
        return contacts

    async def extract_sharepoint_usage(self, search_term=None):
        try:
            if search_term:
                sites = await self.app_client.sites.get(
                    request_configuration=SitesRequestBuilder.SitesRequestBuilderGetRequestConfiguration(
                        query_parameters=SitesRequestBuilder.SitesRequestBuilderGetQueryParameters(search=search_term)
                    )
                )
            else:
                sites = await self.app_client.sites.get()

            if sites and sites.value:
                for site in sites.value:
                    print(f"Site: {site.display_name or site.web_url}")
                    lists = await self.app_client.sites.by_site_id(site.id).lists.get()
                    if lists and lists.value:
                        for lst in lists.value:
                            print(f"  List: {lst.display_name}")
                            items = await self.app_client.sites.by_site_id(site.id).lists.by_list_id(lst.id).items.get()
                            if items and items.value:
                                for item in items.value:
                                    if item.fields:
                                        print(f"    Item: {item.fields.additional_data}")
                            else:
                                print("    No items found in this list.")
                    else:
                        print("  No lists found in this site.")
                # Return the SharePoint sites
                return sites
            else:
                print(f"No SharePoint sites found for search term '{search_term or ''}'")
        except Exception as e:
            print(f"Error extracting SharePoint usage: {e}")