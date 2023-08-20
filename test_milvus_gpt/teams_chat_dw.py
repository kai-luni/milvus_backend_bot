from datetime import datetime
from dateutil.parser import parse
import os
import time
import openai
import requests

from chat_utils import ask, ask_direct_search, search_jsonl

import os
import requests
import openai

def initialize_openai():
    """
    Initialize the OpenAI settings using environment variables.

    This function configures the OpenAI SDK to use the "azure" type and sets up other necessary configurations
    using the environment variables. Make sure the required environment variables are set before calling this function.
    """
    openai.api_type = "azure"
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_base = os.getenv('OPENAI_API_BASE')
    openai.api_version = os.getenv('OPENAI_API_VERSION')

def request_device_code(tenant_id, client_id, scopes):
    """
    Request a device code for Microsoft's OAuth2.0 device flow.

    Args:
        tenant_id (str): The ID of the Azure AD tenant.
        client_id (str): The application's client ID.
        scopes (str): The space-separated list of scopes for which the token is requested.

    Returns:
        dict: A dictionary containing details about the device code.
    """
    device_code_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    payload = {'client_id': client_id, 'scope': scopes}
    response = requests.post(device_code_url, data=payload)
    device_code_data = response.json()

    # Display the user code and verification URL
    print(f"Please visit {device_code_data['verification_uri']} and enter the code: {device_code_data['user_code']}")

    return device_code_data

def poll_for_token(tenant_id, client_id, device_code_data):
    """
    Poll Microsoft's OAuth endpoint for an access token.

    This function keeps polling the token endpoint until an access token is received or an error occurs.

    Args:
        tenant_id (str): The ID of the Azure AD tenant.
        client_id (str): The application's client ID.
        device_code_data (dict): The device code data received from the request_device_code function.

    Returns:
        str: The received access token.
    """
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    while True:
        payload = {
            'client_id': client_id,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'device_code': device_code_data['device_code']
        }
        response = requests.post(token_url, data=payload)
        token_data = response.json()
        if 'access_token' in token_data:
            return token_data['access_token']
        time.sleep(device_code_data['interval'])  # Wait before polling again

def get_chats(access_token, tenant_id, client_id, scopes):
    """
    Retrieve the chats for the authenticated user.

    If the access token is invalid (e.g., expired), this function will re-run the process to get a new access token.

    Args:
        access_token (str): The access token to authenticate the request.
        tenant_id (str): The ID of the Azure AD tenant.
        client_id (str): The application's client ID.
        scopes (str): The space-separated list of scopes for which the token is requested.

    Returns:
        list: A list containing the chats for the authenticated user.
    """
    url = "https://graph.microsoft.com/v1.0/me/chats"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    
    # If forbidden, re-run the process to get a new access token
    if response.status_code == 401:
        device_code_data = request_device_code(tenant_id, client_id, scopes)
        access_token = poll_for_token(tenant_id, client_id, device_code_data)
        print(f"New Access Token is: {access_token}")
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
    
    response.raise_for_status()
    return response.json()['value'], access_token


def get_last_timestamp():
    """
    Retrieve the last timestamp from a file.

    This function reads the timestamp from a file named 'last_timestamp.txt'. 
    If the file does not exist, it returns None.

    Returns:
        datetime.datetime: The parsed datetime object from the file or None if the file does not exist.
    """
    try:
        with open('last_timestamp.txt', 'r') as file:
            return parse(file.read().strip())
    except FileNotFoundError:
        return None

def get_messages(access_token, chat_id):
    """
    Fetch the first 3 messages from a specific chat.

    Args:
        access_token (str): The access token to authenticate the request.
        chat_id (str): The ID of the chat from which messages need to be fetched.

    Returns:
        list: A list containing the first 3 messages from the specified chat.
    """
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    messages = response.json()['value']
    return messages[:3]  # Return only the first 3 messages

def get_messages_since(access_token, chat_id, last_timestamp):
    """
    Fetch messages from a chat that were created after a specified timestamp.

    Args:
        access_token (str): The access token to authenticate the request.
        chat_id (str): The ID of the chat from which messages need to be fetched.
        last_timestamp (datetime.datetime): The timestamp to filter messages.

    Returns:
        list: A list containing messages that were created after the specified timestamp.
    """
    messages = get_messages(access_token, chat_id)
    if last_timestamp:
        messages = [message for message in messages if parse(message['createdDateTime']) > last_timestamp]
    return messages

def send_message_to_chat(access_token, chat_id, message_content):
    """
    Send a message to a specific chat.

    Args:
        access_token (str): The access token to authenticate the request.
        chat_id (str): The ID of the chat to which the message needs to be sent.
        message_content (str): The content of the message to be sent.

    Returns:
        dict: A dictionary containing the response from the server after sending the message.
    """
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

def set_last_timestamp(timestamp):
    """
    Save the given timestamp to a file.

    This function writes the provided timestamp to a file named 'last_timestamp.txt'.

    Args:
        timestamp (datetime.datetime): The timestamp to be saved.
    """
    with open('last_timestamp.txt', 'w') as file:
        file.write(str(timestamp))


tenant_id = os.getenv("TEAMS_TENANT_ID")
client_id = os.getenv("TEAMS_CLIENT_ID")
scopes = 'https://graph.microsoft.com/.default'
access_token = os.getenv("TEAMS_TENANT_ACCESS_TOKEN")
##//TODO: make this check on access token better
chats, access_token = get_chats(access_token, tenant_id, client_id, scopes)
chat_gpt = next((chat for chat in chats if chat['topic'] == 'PhatGPT'), None)
if chat_gpt:
    chat_id = chat_gpt['id']
else:
    print("ChatGPT not found")
    exit()

messages = get_messages(access_token, chat_id)
for message in messages:
    if message['from']:
        print(f"From: {message['from']['user']['displayName']}")
    print(f"Content: {message['body']['content']}\n")

initialize_openai()

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
            answer_vector = ask(content, os.environ['BEARER_TOKEN'], os.environ["SERVER_IP"])
            send_message_to_chat(access_token, chat_id, f"answer vectorsearch: {answer_vector}")

            keywords = ask_direct_search(content)
            all_texts = search_jsonl("/mnt/c/git_linux/milvus_backend_bot/gpt/phat_sharepoint.jsonl", keywords)
            
            texts = []
            character_count = 0

            for entry in all_texts:
                if character_count + len(entry) < 16000:
                    texts.append(entry)
                    character_count += len(entry)
                else:
                    break

            answer = ask(content, None, None, 16000, source="direct_search")
            send_message_to_chat(access_token, chat_id, f"answer directsearch: {answer}")

        # Update the last timestamp
        last_timestamp = timestamp

    # Store the last timestamp in the file
    set_last_timestamp(last_timestamp)

    # Wait before polling again (adjust the sleep time as needed)
    time.sleep(3)

