from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient
import requests
import os
import argparse

# Slack Webhook URL (ensure this is set as an environment variable)
slack_webhook_url = os.getenv("SLACK_AZURE_COST_WEBHOOK_URL")

# Retrieve the user group ID from the environment variable
user_group_id = os.getenv("SLACK_USER_GROUP_ID")

# Authenticate using default credentials
credential = DefaultAzureCredential()

# Initialize subscription client
subscription_client = SubscriptionClient(credential)

# Branch parser
parser = argparse.ArgumentParser(description="Script to check Unused Production Environment Resources in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

branch_name = os.getenv('GITHUB_REF').split('/')[2]
if args.branch:
    branch_name = args.branch


def get_unattached_snapshots(subscription_id, subscription_name):
    """
    Get unattached snapshots (snapshots not linked to any disk).
    """
    compute_client = ComputeManagementClient(credential, subscription_id)
    unattached_snapshots = []

    # List all snapshots in the subscription (handling pagination)
    snapshots = compute_client.snapshots.list()

    for snapshot in snapshots:
        try:
            # Check if the snapshot is associated with any disk or resource
            if not snapshot.disk_state or snapshot.disk_state.lower() == 'unattached':
                unattached_snapshots.append({
                    'Snapshot Name': snapshot.name,
                    'Resource Group': snapshot.id.split('/')[4],
                    'Subscription Name': subscription_name
                })
        except Exception as e:
            print(f"Error checking snapshot {snapshot.name}: {e}")

    return unattached_snapshots


def format_unattached_snapshots_message(unattached_snapshots):
    """
    Format unattached snapshot information for a Slack message.
    """
    snapshot_count = len(unattached_snapshots)

    if snapshot_count == 0:
        return f"*No unattached snapshots found in this subscription.*"

    slack_message = f"*Here is the list of {snapshot_count} unattached snapshots in the Production Environment, Please Take the Necessary Action.*\n"
    for snapshot_info in unattached_snapshots:
        slack_message += (
            f"```"
            f"Snapshot Name: {snapshot_info['Snapshot Name']}\n"
            f"Resource Group: {snapshot_info['Resource Group']}\n"
            f"Subscription Name: {snapshot_info['Subscription Name']}\n"
            f"```\n"
        )
    return slack_message


def send_message_to_slack(message):
    """
    Send a formatted message to Slack via a webhook URL.
    """
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


def main():
    """
    Main function to fetch and report unattached snapshots across all subscriptions.
    """
    all_unattached_snapshots = []

    for subscription in subscription_client.subscriptions.list():
        print(f"Processing subscription: {subscription.subscription_id}")
        unattached_snapshots = get_unattached_snapshots(subscription.subscription_id, subscription.display_name)
        all_unattached_snapshots.extend(unattached_snapshots)

    # Prepare Slack message based on results
    if all_unattached_snapshots:
        slack_message = format_unattached_snapshots_message(all_unattached_snapshots)
    else:
        slack_message = "*No unattached snapshots found across any subscriptions.*\n"

    # Send the message to Slack
    send_message_to_slack(slack_message)


if __name__ == "__main__":
    main()
