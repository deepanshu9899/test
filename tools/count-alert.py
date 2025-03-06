from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from slack_sdk import WebClient
import os

slack_token = os.environ.get('SLACK_TOKEN')
channel_id = '#azure-cost'
subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
resource_group = os.environ.get('RESOURCE_GROUP')

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

credential = DefaultAzureCredential()
resource_client = ResourceManagementClient(credential, subscription_id)
resources = resource_client.resources.list_by_resource_group(resource_group)

for resource in resources:
    if resource.type == "Microsoft.Compute/virtualMachineScaleSets":
        if resource.sku.capacity > 10:
            message = f'{resource.name} | count greater than 10'
            print(message)
            send_slack_message(message_text=message)
        else:
            print(f'{resource.name} | instances count -> {resource.sku.capacity}')
        