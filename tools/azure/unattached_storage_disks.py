import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import argparse

# Slack Webhook URL
slack_webhook_url = os.getenv("SLACK_AZURE_COST_WEBHOOK_URL")

# Retrieve the Slack user group ID from the environment variable
user_group_id = os.getenv("SLACK_USER_GROUP_ID")

# Authenticate using default credentials (requires Azure CLI login or managed identity)
credential = DefaultAzureCredential()

# Initialize the subscription client
subscription_client = SubscriptionClient(credential)

# Branch parser
parser = argparse.ArgumentParser(description="Script to check Unused Resources in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

branch_name = os.getenv('GITHUB_REF').split('/')[2]
if args.branch:
    branch_name = args.branch


# Function to list unattached disks for a specific subscription
def get_unattached_disks(subscription_id, subscription_name):
    compute_client = ComputeManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)

    # List all resource groups
    resource_groups = [rg.name for rg in resource_client.resource_groups.list()]

    # List all the disks in the subscription
    disks = compute_client.disks.list()

    # Get the list of VM IDs (those attached to VMs)
    attached_disks = set()

    # List all the VMs in the subscription to check their attached disks
    for vm in compute_client.virtual_machines.list_all():
        # Check the OS disk
        if vm.storage_profile.os_disk.managed_disk and vm.storage_profile.os_disk.managed_disk.id:
            attached_disks.add(vm.storage_profile.os_disk.managed_disk.id)

        # Check the data disks
        for disk in vm.storage_profile.data_disks:
            if disk.managed_disk and disk.managed_disk.id:
                attached_disks.add(disk.managed_disk.id)

    # Collect unattached disks
    unattached_disks = []
    for disk in disks:
        if disk.id not in attached_disks and disk.disk_state != 'Attached' and disk.disk_state != 'Reserved':
            resource_group = disk.id.split('/')[4]
            unattached_disks.append({
                'Disk Name': disk.name,
                'Disk Size (GB)': disk.disk_size_gb,
                'Resource Group': resource_group,
                'Subscription Name': subscription_name
            })

    return unattached_disks, resource_groups


# Function to send message to Slack
def send_message_to_slack(message):
    # Add user group tagging if the user group ID is provided
    if user_group_id:
        user_group_tag = f"<!subteam^{user_group_id}>"
        message_with_tag = f"{user_group_tag} {message}"
    else:
        message_with_tag = message

    payload = {"text": message_with_tag}
    try:
        response = requests.post(slack_webhook_url, json=payload)
        if response.status_code == 200:
            print("Message successfully sent to Slack.")
        else:
            print(f"Failed to send message to Slack: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending message to Slack: {e}")


# Loop through all subscriptions and get unattached disks and resource groups
all_unattached_disks = []
all_resource_groups = []

for subscription in subscription_client.subscriptions.list():
    print(f"Processing subscription: {subscription.subscription_id}")
    unattached_disks, resource_groups = get_unattached_disks(subscription.subscription_id, subscription.display_name)
    all_unattached_disks.extend(unattached_disks)
    all_resource_groups.extend(resource_groups)

# Calculate number of disks
disks_count = len(all_unattached_disks)

# If unattached disks are found, format them for Slack message
if all_unattached_disks:
    slack_message = f"*Here is the list of {disks_count} unattached disks in the Production Environment, Please Take the Necessary Action.*\n"

    # Send each disk's info in its own grey box
    for disk in all_unattached_disks:
        slack_message += "```"
        slack_message += f"Disk Name: {disk['Disk Name']}\n"
        slack_message += f"Disk Size (GB): {disk['Disk Size (GB)']} GB\n"
        slack_message += f"Resource Group: {disk['Resource Group']}\n"
        slack_message += f"Subscription Name: {disk['Subscription Name']}\n"
        slack_message += "```\n"

    # Send the formatted message to Slack
    send_message_to_slack(slack_message)
else:
    slack_message = f"*No unattached disks found across all subscriptions.*\n"
    send_message_to_slack(slack_message)

# Print all resource groups
print("Resource Groups across all subscriptions:")
for rg in all_resource_groups:
    print(rg)
