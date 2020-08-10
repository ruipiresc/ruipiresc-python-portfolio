class MissingGmailProjectCredentials(Exception):
    def __init__(self) -> None:
        print('Missing credentials.json')
        print('You need to turn on Gmail API')
        print('Please do the step 1 of this quickstart tutorial')
        print('https://developers.google.com/gmail/api/quickstart/python')