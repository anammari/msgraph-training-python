# app.py
from flask import Flask, request, jsonify
import asyncio
import configparser
from graph import Graph
import nest_asyncio

# Apply nest_asyncio to fix event loop issues
nest_asyncio.apply()

app = Flask(__name__)

# Load settings
config = configparser.ConfigParser()
config.read(['config.cfg', 'config.dev.cfg'])
azure_settings = config['azure']

@app.route('/options', methods=['GET'])
def options():
    options_list = [
        {'id': 0, 'name': 'Exit'},
        {'id': 1, 'name': 'Display access token'},
        {'id': 2, 'name': 'List my inbox'},
        {'id': 3, 'name': 'Send mail'},
        {'id': 4, 'name': 'Extract email metadata'},
        {'id': 5, 'name': 'Extract calendar events'},
        {'id': 6, 'name': 'Extract contacts and network'},
        {'id': 7, 'name': 'Extract SharePoint usage'}
    ]
    return jsonify(options_list)

@app.route('/interact', methods=['POST'])
def interact():
    try:
        data = request.get_json()
        if not data or 'option' not in data:
            return jsonify({'error': 'Missing option in request'}), 400

        option = data['option']
        if not isinstance(option, int):
            return jsonify({'error': 'Option must be an integer'}), 400
        # Get search_term from the request data
        search_term = data.get('search_term', '')
        
        # Process the selected option
        result = asyncio.run(process_option(option, search_term))
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def process_option(option, search_term=''):
    # Initialize Graph object inside the async function to ensure it uses the same event loop
    graph_instance = Graph(azure_settings)

    if option == 0:
        return {'message': 'Goodbye...'}
    elif option == 1:
        token = await graph_instance.get_app_only_token()
        return {'app_only_token': token}
    elif option == 2:
        messages = await graph_instance.get_inbox()
        if messages and messages.value:
            message_list = []
            for message in messages.value:
                msg = {
                    'subject': message.subject,
                    'from': message.from_.email_address.name if message.from_ and message.from_.email_address else 'NONE',
                    'is_read': message.is_read,
                    'received_date_time': str(message.received_date_time)
                }
                message_list.append(msg)
            return {'messages': message_list, 'more_available': bool(messages.odata_next_link)}
        else:
            return {'messages': [], 'more_available': False}
    elif option == 3:
        # Send mail to the signed-in user
        user = await graph_instance.get_user()
        if user:
            user_email = user.mail or user.user_principal_name
            await graph_instance.send_mail('Testing Microsoft Graph', 'Hello world!', user_email or '')
            return {'message': 'Mail sent.'}
        else:
            return {'error': 'User not found.'}, 500
    elif option == 4:
        # Call the enriched extract_email_metadata function
        metadata = await graph_instance.extract_email_metadata()
        if metadata:
            return {'email_metadata': metadata}
        else:
            return {'email_metadata': []}
    elif option == 5:
        events = await graph_instance.extract_calendar_events()
        if events and events.value:
            event_list = []
            for event in events.value:
                evt = {
                    'subject': event.subject,
                    'start': str(event.start.date_time) if event.start else 'N/A',
                    'end': str(event.end.date_time) if event.end else 'N/A',
                    'location': event.location.display_name if event.location else 'N/A'
                }
                event_list.append(evt)
            return {'calendar_events': event_list}
        else:
            return {'calendar_events': []}
    elif option == 6:
        contacts = await graph_instance.extract_contacts_and_network()
        if contacts and contacts.value:
            contact_list = []
            for contact in contacts.value:
                cnt = {
                    'display_name': contact.display_name,
                    'email': contact.email_addresses[0].address if contact.email_addresses else 'N/A'
                }
                contact_list.append(cnt)
            return {'contacts': contact_list}
        else:
            return {'contacts': []}
    elif option == 7:
        sites = await graph_instance.extract_sharepoint_usage(search_term)
        if sites and sites.value:
            site_list = []
            for site in sites.value:
                sit = {
                    'display_name': site.display_name,
                    'web_url': site.web_url
                }
                site_list.append(sit)
            return {'sharepoint_sites': site_list}
        else:
            return {'sharepoint_sites': []}
    else:
        return {'error': 'Invalid option.'}, 400

if __name__ == '__main__':
    app.run(debug=True)