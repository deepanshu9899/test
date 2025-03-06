import requests
import argparse
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import pandas as pd
from slack_sdk import WebClient
import os

slack_token = os.environ.get('SLACK_TOKEN')
channel_id = '#azure-alert'
connection_string = os.environ.get('CONNECTION_STRING')
container_name = "service-principle"
local_file_path = blob_name = "prod.xlsx"

parser = argparse.ArgumentParser(description="Script to check unused VMs in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

branch_name = os.getenv('GITHUB_REF').split('/')[2]
if args.branch:
        branch_name = args.branch

def send_slack_message(message_text):
    client = WebClient(token=slack_token)
    formatted_message = f"*```{message_text}```*"
    response =client.chat_postMessage(
        channel=channel_id,
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

    if response["ok"]:
        print(f"Message sent successfully to {channel_id}: {message_text}")
        return True
    else:
        print(f"Message sending failed: {response['error']}")
        return False

def key_expiry_time(input_date,name,key):
    input_date = datetime.strptime(input_date, '%Y-%m-%d')
    current_date = datetime.now()

    
    time_difference = input_date - current_date
    days_remaining = time_difference.days
 
    if days_remaining <= 60:
        if days_remaining == 60:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 2 month remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining == 50:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 50 days remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining == 40:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 40 days remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining == 30:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 1 month remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining == 21:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 21 days remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining == 14:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | 14 days remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif 0 <= days_remaining <= 7:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | {days_remaining} day(s) remaining to key expiry."
            print(message)
            send_slack_message(message)
        elif days_remaining < 0:
            message = f"[{branch_name}]Service Principle: {name} | Key: {key} | Key expired {abs(days_remaining)} day(s) ago."
            print(message)
            send_slack_message(message)

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

access_token = credential.get_token('https://graph.microsoft.com/.default').token
graph_api_endpoint = f'https://graph.microsoft.com/v1.0/applications'
headers = {
    'Authorization': 'Bearer ' + access_token,
}
response = requests.get(graph_api_endpoint, headers=headers)

i = 0
current_date = datetime.now().date()

SP_Name = []
SP_Id = []
Key_Name = []
Key_Expiry = []
Key_Status = []
Key_Count = [] 

service_principals = response.json().get('value', [])

if response.status_code == 200:
    for sp in service_principals:

        if not sp['passwordCredentials'] and not sp['keyCredentials']:
            SP_Name.append(sp['displayName'])
            SP_Id.append(sp['id'])
            Key_Name.append("No keys Found")
            Key_Expiry.append('--')
            Key_Status.append('--')
            Key_Count.append(0)  

        else:
            for key in ['passwordCredentials', 'keyCredentials']:
                key_count = len(sp[key])
                for j in sp[key]:
                    SP_Name.append(sp['displayName'])
                    SP_Id.append(sp['id'])
                    Key_Name.append(j['displayName'])

                    expiry_date = j['endDateTime'].split('T')[0]
                    expiry_date_obj = datetime.strptime(expiry_date, "%Y-%m-%d").date()

                    key_expiry_time(expiry_date,sp['displayName'],j['displayName'])

                    Key_Expiry.append(expiry_date_obj)

                    if expiry_date_obj <= current_date:
                        Key_Status.append('Expired')
                    else:
                        Key_Status.append('Not Expired')

                    Key_Count.append(key_count)

    data = {
        'Service Principle': SP_Name,
        'Service Principle ID': SP_Id,
        'No of Keys': Key_Count,
        'Key Name': Key_Name,
        'Key Expiry (YYYY-MM-DD)': Key_Expiry,
        'Key Status': Key_Status,
        'Environment': branch_name
    }

    df = pd.DataFrame(data)
    df = df.sort_values("Key Status").reset_index(drop=True)
    print(df)
    df.to_excel(local_file_path, index=False)

    with open(local_file_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

    print(f"Uploaded {blob_name} to {container_name} container.")
else:
    print(f"Failed to list service principals. Status code: {response.status_code}")
    print(response.text)