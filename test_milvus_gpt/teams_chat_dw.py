from datetime import datetime
from dateutil.parser import parse
import os
import time
import requests

tenant_id = os.getenv("TEAMS_TENANT_ID")
client_id = os.getenv("TEAMS_CLIENT_ID")
scopes = 'https://graph.microsoft.com/.default'

# # Request a device code
# device_code_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
# payload = {'client_id': client_id, 'scope': scopes}
# response = requests.post(device_code_url, data=payload)
# device_code_data = response.json()

# # Display the user code and verification URL
# print(f"Please visit {device_code_data['verification_uri']} and enter the code: {device_code_data['user_code']}")

# # Poll for the token
# token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
# while True:
#     payload = {
#         'client_id': client_id,
#         'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
#         'device_code': device_code_data['device_code']
#     }
#     response = requests.post(token_url, data=payload)
#     token_data = response.json()
#     if 'access_token' in token_data:
#         access_token = token_data['access_token']
#         print(f"Access Token: {access_token}")
#         break
#     time.sleep(device_code_data['interval'])  # Wait before polling again

access_token = os.getenv("TEAMS_TENANT_ACCESS_TOKEN")

def get_chats(access_token):
    url = "https://graph.microsoft.com/v1.0/me/chats"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()['value']

chats = get_chats(access_token)
chat_gpt = next((chat for chat in chats if chat['topic'] == 'PhatGPT'), None)
if chat_gpt:
    chat_id = chat_gpt['id']
else:
    print("ChatGPT not found")
    exit()

def get_messages(access_token, chat_id):
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    messages = response.json()['value']
    return messages[:3]  # Return only the first 3 messages


messages = get_messages(access_token, chat_id)
for message in messages:
    if message['from']:
        print(f"From: {message['from']['user']['displayName']}")
    print(f"Content: {message['body']['content']}\n")

def send_message_to_chat(access_token, chat_id, message_content):
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {
        'body': {
            'contentType': 'text',
            'content': message_content
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()  # raise exception if any error
    return response.json()

# message_content = "Hello from PhatGPT!"
# send_message_to_chat(access_token, chat_id, message_content)

def get_last_timestamp():
    try:
        with open('last_timestamp.txt', 'r') as file:
            return parse(file.read().strip())
    except FileNotFoundError:
        return None

def set_last_timestamp(timestamp):
    with open('last_timestamp.txt', 'w') as file:
        file.write(str(timestamp))

def get_messages_since(access_token, chat_id, last_timestamp):
    messages = get_messages(access_token, chat_id)
    if last_timestamp:
        messages = [message for message in messages if parse(message['createdDateTime']) > last_timestamp]
    return messages

def mirror_message(access_token, chat_id, message_content):
    send_message_to_chat(access_token, chat_id, f"echo: {message_content}")

# Read the last timestamp from the file
last_timestamp = get_last_timestamp()

while True:
    # Get messages since the last timestamp
    messages = get_messages_since(access_token, chat_id, last_timestamp) if last_timestamp else get_messages(access_token, chat_id)

    # Process new messages
    for message in messages:
        content = message['body']['content'].replace("<p>", "").replace("</p>", "")
        timestamp = parse(message['createdDateTime'])

        # Check if the message starts with '<p>phatgpt' and mirror it if it does
        if content.lower().startswith('phatgpt'):
            mirror_message(access_token, chat_id, content)

        # Update the last timestamp
        last_timestamp = timestamp

    # Store the last timestamp in the file
    set_last_timestamp(last_timestamp)

    # Wait before polling again (adjust the sleep time as needed)
    time.sleep(5)

