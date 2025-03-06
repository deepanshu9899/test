from slack_sdk import WebClient
import sys
import os

slack_token = os.environ.get('SLACK_TOKEN')
# channel_id = '#azure-alert'
channel_id = '#browser-updates'

def send_slack_message(message_text):
    client = WebClient(token=slack_token)
    formatted_message = f"*{message_text}*"
    # formatted_message = message_text
    response = client.chat_postMessage(
        channel=channel_id,
        text=formatted_message,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": formatted_message
                }
            }
        ]
    )
    ts = response.data['ts']

    if response["ok"]:
        print(ts) 
        return ts  
    else:
        print(f"Message sending failed: {response['error']}")
        return None

ts_value = send_slack_message(sys.argv[1])
