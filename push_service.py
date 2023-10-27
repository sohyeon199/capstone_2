token = ""
title = ""
message = ""

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("./app-push-test-11f73-firebase-adminsdk-9i5uf-37b4c43793.json")
default_app = firebase_admin.initialize_app(cred)

def send_pmsg(tokens: list, title: str, message: str):
    from firebase_admin import messaging

    # This registration token comes from the client FCM SDKs.
    registration_token = token

    # See documentation on defining a message payload.
    message = messaging.Message(
        data = {
            'score': '850',
            'time': '2:45',
        },
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)
    
    # # Create a list containing up to 500 registration tokens.
    # # These registration tokens come from the client FCM SDKs.
    # registration_tokens = [
    #     'YOUR_REGISTRATION_TOKEN_1',
    #     # ...
    #     'YOUR_REGISTRATION_TOKEN_N',
    # ]

    # message = messaging.MulticastMessage(
    #     data={'score': '850', 'time': '2:45'},
    #     tokens=registration_tokens,
    # )
    # response = messaging.send_multicast(message)
    # if response.failure_count > 0:
    #     responses = response.responses
    #     failed_tokens = []
    # for idx, resp in enumerate(responses):
    #     if not resp.success:
    #         # The order of responses corresponds to the order of the registration tokens.
    #         failed_tokens.append(registration_tokens[idx])
    # print('List of tokens that caused failures: {0}'.format(failed_tokens))

    # # See the BatchResponse reference documentation
    # # for the contents of response.
    # print('{0} messages were sent successfully'.format(response.success_count))