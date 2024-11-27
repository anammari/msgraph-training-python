# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# <UserAuthConfigSnippet>
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential
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
from msgraph.generated.users.item.contacts.contacts_request_builder import ContactsRequestBuilder
from msgraph.generated.users.item.todo.todo_request_builder import TodoRequestBuilder
from msgraph.generated.users.item.todo.lists.item.tasks.tasks_request_builder import TasksRequestBuilder
from msgraph.generated.users.item.planner.planner_request_builder import PlannerRequestBuilder
from msgraph.generated.users.item.drive.drive_request_builder import DriveRequestBuilder
from msgraph.generated.sites.item.lists.lists_request_builder import ListsRequestBuilder

class Graph:
    settings: SectionProxy
    device_code_credential: DeviceCodeCredential
    user_client: GraphServiceClient

    def __init__(self, config: SectionProxy):
        self.settings = config
        client_id = self.settings['clientId']
        tenant_id = self.settings['tenantId']
        graph_scopes = self.settings['graphUserScopes'].split(' ')

        self.device_code_credential = DeviceCodeCredential(client_id, tenant_id = tenant_id)
        self.user_client = GraphServiceClient(self.device_code_credential, graph_scopes)
# </UserAuthConfigSnippet>

    # <GetUserTokenSnippet>
    async def get_user_token(self):
        graph_scopes = self.settings['graphUserScopes']
        access_token = self.device_code_credential.get_token(graph_scopes)
        return access_token.token
    # </GetUserTokenSnippet>

    # <GetUserSnippet>
    async def get_user(self):
        # Only request specific properties using $select
        query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
            select=['displayName', 'mail', 'userPrincipalName']
        )

        request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )

        user = await self.user_client.me.get(request_configuration=request_config)
        return user
    # </GetUserSnippet>

    # <GetInboxSnippet>
    async def get_inbox(self):
        query_params = MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
            # Only request specific properties
            select=['from', 'isRead', 'receivedDateTime', 'subject'],
            # Get at most 25 results
            top=25,
            # Sort by received time, newest first
            orderby=['receivedDateTime DESC']
        )
        request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
            query_parameters= query_params
        )

        messages = await self.user_client.me.mail_folders.by_mail_folder_id('inbox').messages.get(
                request_configuration=request_config)
        return messages
    # </GetInboxSnippet>

    # <SendMailSnippet>
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

        await self.user_client.me.send_mail.post(body=request_body)
    # </SendMailSnippet>

    # <ExtractInferenceDataSnippet>
    async def extract_inference_data(self):
        await self.extract_email_metadata()
        await self.extract_calendar_events()
        await self.extract_contacts_and_network()
        await self.extract_task_management()
        await self.extract_onedrive_usage()
        await self.extract_sharepoint_usage()
    # </ExtractInferenceDataSnippet>

    # <ExtractEmailMetadataSnippet>
    async def extract_email_metadata(self):
        messages = await self.get_inbox()
        for message in messages.value:
            print(f"Subject: {message.subject}, From: {message.from_.email_address.address}, Received: {message.received_date_time}, Read: {message.is_read}")
    # </ExtractEmailMetadataSnippet>

    # <ExtractCalendarEventsSnippet>
    async def extract_calendar_events(self):
        query_params = EventsRequestBuilder.EventsRequestBuilderGetQueryParameters(
            select=['subject', 'start', 'end', 'location'],
            top=25,
            orderby=['start/dateTime DESC']
        )
        request_config = EventsRequestBuilder.EventsRequestBuilderGetRequestConfiguration(
            query_parameters=query_params
        )
        events = await self.user_client.me.calendar.events.get(request_configuration=request_config)
        for event in events.value:
            print(f"Subject: {event.subject}, Start: {event.start.date_time}, End: {event.end.date_time}, Location: {event.location.display_name}")
    # </ExtractCalendarEventsSnippet>

    # <ExtractContactsAndNetworkSnippet>
    async def extract_contacts_and_network(self):
        contacts = await self.user_client.me.contacts.get()
        if contacts.value:
            for contact in contacts.value:
                print(f"Name: {contact.display_name}, Email: {contact.email_addresses[0].address if contact.email_addresses else 'N/A'}")
        else:
            print("No contacts found.")
    # </ExtractContactsAndNetworkSnippet>

    # <ExtractTaskManagementSnippet>
    async def extract_task_management(self):
        todo_lists = await self.user_client.me.todo.lists.get()
        if todo_lists.value:
            for todo_list in todo_lists.value:
                print(f"Task List: {todo_list.display_name}")
                tasks = await self.user_client.me.todo.lists.by_list_id(todo_list.id).tasks.get()
                if tasks.value:
                    for task in tasks.value:
                        print(f"Task: {task.title}, Due: {task.due_date_time.date_time if task.due_date_time else 'N/A'}, Completed: {task.is_completed}")
                else:
                    print("No tasks found in this list.")
        else:
            print("No task lists found.")

        planner_plans = await self.user_client.me.planner.plans.get()
        if planner_plans.value:
            for plan in planner_plans.value:
                print(f"Planner Plan: {plan.title}")
                # Note: Further extraction of plan details requires more specific queries which are not covered here.
        else:
            print("No Planner plans found.")
    # </ExtractTaskManagementSnippet>

    # <ExtractOneDriveUsageSnippet>
    async def extract_onedrive_usage(self):
        drive = await self.user_client.me.drive.get()
        drive_items = await self.user_client.me.drive.root.children.get()
        for item in drive_items.value:
            print(f"Item: {item.name}, Size: {item.size}, Modified: {item.last_modified_date_time}")
    # </ExtractOneDriveUsageSnippet>

    # <ExtractSharePointUsageSnippet>
    async def extract_sharepoint_usage(self):
        try:
            sites = await self.user_client.sites.get()
            if sites.value:
                for site in sites.value:
                    print(f"Site: {site.display_name or site.web_url}")
                    lists = await self.user_client.sites.by_site_id(site.id).lists.get()
                    if lists.value:
                        for lst in lists.value:
                            print(f"  List: {lst.display_name}")
                            items = await self.user_client.sites.by_site_id(site.id).lists.by_list_id(lst.id).items.get()
                            if items.value:
                                for item in items.value:
                                    print(f"    Item: {item.fields.additional_data}")
                            else:
                                print("    No items found in this list.")
                    else:
                        print("  No lists found in this site.")
            else:
                print("No SharePoint sites found.")
        except Exception as e:
            print(f"Error extracting SharePoint usage: {e}")
    # </ExtractSharePointUsageSnippet>
