import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
import requests
import argparse

# Slack Webhook URL
slack_webhook_url = os.getenv("SLACK_AZURE_COST_WEBHOOK_URL")

# Retrieve the Slack user group ID from the environment variable
user_group_id = os.getenv("SLACK_USER_GROUP_ID")

# Authenticate using default credentials
credential = DefaultAzureCredential()

# Initialize subscription client
subscription_client = SubscriptionClient(credential)

# Branch parser
parser = argparse.ArgumentParser(description="Script to check Unused Resources in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

branch_name = os.getenv('GITHUB_REF').split('/')[2]
if args.branch:
    branch_name = args.branch


def is_attached_to_nat_or_load_balancer(public_ip, network_client):
    """
    Check if the public IP is attached to a NAT gateway or load balancer.
    """
    try:
        # Check if the public IP is linked to a NAT Gateway
        nat_gateways = network_client.nat_gateways.list_all()
        for nat_gateway in nat_gateways:
            if nat_gateway.public_ip_addresses:
                for assoc_public_ip in nat_gateway.public_ip_addresses:
                    if assoc_public_ip.id == public_ip.id:
                        return True  # NAT Gateway association found

        # Check if the public IP is linked to a Load Balancer
        load_balancers = network_client.load_balancers.list_all()
        for lb in load_balancers:
            for frontend_ip_config in lb.frontend_ip_configurations:
                if frontend_ip_config.public_ip_address and frontend_ip_config.public_ip_address.id == public_ip.id:
                    return True  # Load Balancer association found

        # If no association is found, return False
        return False
    except Exception as e:
        print(f"Error while checking associations for IP {public_ip.name}: {e}")
        return True  # Default to considering it associated in case of error


def get_completely_unassociated_public_ips(subscription_id, subscription_name):
    """
    Get public IPs in a subscription that are completely unassociated (not attached to any resource).
    """
    network_client = NetworkManagementClient(credential, subscription_id)
    public_ips = network_client.public_ip_addresses.list_all()
    unassociated_public_ips = []

    for public_ip in public_ips:
        # Skip IPs that are associated with any configuration
        if public_ip.ip_configuration:
            continue

        # Check if the public IP is attached to a NAT Gateway or Load Balancer
        if is_attached_to_nat_or_load_balancer(public_ip, network_client):
            continue

        # If it's not attached to anything, consider it unassociated
        unassociated_public_ips.append({
            'IP Address': public_ip.ip_address,
            'IP Name': public_ip.name,
            'Resource Group': public_ip.id.split('/')[4],
            'Subscription Name': subscription_name
        })

    return unassociated_public_ips


def format_unassociated_ips_message(unassociated_ips):
    """
    Format unassociated IP information for a Slack message.
    """
    ip_count = len(unassociated_ips)
    slack_message = (
        "*Production AZURE Unused Resources Alerts*\n\n"
        f"*Here is the list of {ip_count} completely unassociated public IPs in the Production Environment, Please Take the Necessary Action*\n"
    )

    for ip_info in unassociated_ips:
        slack_message += (
            f"```"
            f"IP Address: {ip_info['IP Address']}\n"
            f"IP Name: {ip_info['IP Name']}\n"
            f"Resource Group: {ip_info['Resource Group']}\n"
            f"Subscription Name: {ip_info['Subscription Name']}\n"
            f"```\n"
        )
    return slack_message


def send_message_to_slack(message):
    """
    Send a formatted message to Slack using a webhook URL.
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
    Main function to fetch and report unassociated public IPs across all subscriptions.
    """
    all_unassociated_public_ips = []

    for subscription in subscription_client.subscriptions.list():
        print(f"Processing subscription: {subscription.subscription_id}")
        unassociated_ips = get_completely_unassociated_public_ips(subscription.subscription_id, subscription.display_name)
        all_unassociated_public_ips.extend(unassociated_ips)

    if all_unassociated_public_ips:
        # Prepare and send Slack message with unassociated IPs
        slack_message = format_unassociated_ips_message(all_unassociated_public_ips)
    else:
        # Send a message if no unassociated public IPs are found
        slack_message = f"*No completely unassociated public IPs found in the Production Environment.*\n"

    # Send the message to Slack
    send_message_to_slack(slack_message)


if __name__ == "__main__":
    main()
