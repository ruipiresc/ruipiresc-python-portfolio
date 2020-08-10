import os
import pickle
import email
import base64
from typing import Any, Iterable

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from . import exceptions

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service() -> Any:
    """Gets service for Gmail API.

    Returns:
        Any: service for gmail api

    """
    return build('gmail', 'v1', credentials=get_credentials())

def get_credentials() -> Any:
    """Gets credentials for Gmail API.

    Returns:
        Any: credentials for gmail api
    """

    if not os.path.exists('credentials.json'):
        raise exceptions.MissingGmailProjectCredentials()

    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials

def search_messages(service, user_id: str='me', query:str='') -> Iterable[str]:
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
        query: String used to filter messages returned. Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
        List of Messages that match the criteria of the query. Note that the returned list contains Message IDs, you must use get with the appropriate ID to get the details of a Message.
    """
    response = service.users().messages().list(userId=user_id, q=query).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
        messages.extend(response['messages'])
    
    message_ids = []
    for message in messages:
        message_ids.append(message['id'])

    return message_ids

def get_message(service, user_id: str='me', msg_id:str=None) -> email.message.EmailMessage:
    """Get a Message with given ID.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me" can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A Message.

    """
    message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
    return email.message_from_string(base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8"))
