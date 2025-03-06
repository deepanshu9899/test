import os
import json
import argparse
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.monitor.query import MetricsQueryClient, MetricAggregationType
from azure.mgmt.subscription import SubscriptionClient
import requests

# Slack Webhook URL
slack_webhook_url = os.getenv("SLACK_AZURE_COST_WEBHOOK_URL")

# Retrieve the Slack user group ID from the environment variable
user_group_id = os.getenv("SLACK_USER_GROUP_ID")

# Azure authentication
credential = DefaultAzureCredential()

# Initialize Azure clients
metrics_client = MetricsQueryClient(credential)
subscription_client = SubscriptionClient(credential)

# Time range for metrics (last 7 days)
time_range = (datetime.now(timezone.utc) - timedelta(days=7), datetime.now(timezone.utc))

# Branch parser
parser = argparse.ArgumentParser(description="Script to check Unused Resources in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

branch_name = os.getenv('GITHUB_REF').split('/')[2]
if args.branch:
    branch_name = args.branch


def check_cpu_utilization(subscription_id):
    """
    Checks for VMs with 0% CPU utilization over the past 7 days in a given subscription.
    """
    compute_client = ComputeManagementClient(credential, subscription_id)
    zero_cpu_vms = []
    total_vms = 0

    for vm in compute_client.virtual_machines.list_all():
        total_vms += 1
        resource_id = vm.id

        try:
            # Query CPU utilization metrics
            response = metrics_client.query_resource(
                resource_uri=resource_id,
                metric_names=["Percentage CPU"],
                timespan=(time_range[0], time_range[1]),
                granularity=timedelta(hours=1),
                aggregations=[MetricAggregationType.AVERAGE]
            )
            # Check if all data points are 0% CPU
            if response.metrics:
                cpu_metric = response.metrics[0]
                if all(
                    data.average == 0 or data.average is None
                    for time_series in cpu_metric.timeseries
                    for data in time_series.data
                ):
                    zero_cpu_vms.append({
                        "VM Name": vm.name,
                        "Resource Group": vm.id.split('/')[4],
                        "Subscription ID": subscription_id,
                    })

        except Exception as e:
            print(f"Error fetching metrics for VM {vm.name}: {e}")

    return zero_cpu_vms, total_vms


def format_slack_message(zero_cpu_vms, total_vms_count):
    """
    Formats the message to be sent to Slack.
    """
    zero_cpu_vms_count = len(zero_cpu_vms)
    
    if zero_cpu_vms_count > 0:
        message = (
            f"*Here is the list of unused VMs:* Out of {total_vms_count} VMs analyzed, {zero_cpu_vms_count} VMs have 0% CPU utilization for the past 7 days in the Production Environment, Please Take the Necessary Action\n"
        )
        for vm in zero_cpu_vms:
            message += (
                f"```"
                f"VM Name: {vm['VM Name']}\n"
                f"Resource Group: {vm['Resource Group']}\n"
                f"Subscription ID: {vm['Subscription ID']}\n"
                f"```\n"
            )
    else:
        message = f"*Out of {total_vms_count} VMs analyzed, no VMs were found with 0% CPU utilization in the Production Environment.*"
    
    return message


def send_message_to_slack(message):
    """
    Sends a formatted message to a Slack channel using a webhook URL.
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
    Main function to check CPU utilization and send notifications.
    """
    all_zero_cpu_vms = []
    total_vms_count = 0

    for subscription in subscription_client.subscriptions.list():
        print(f"Processing subscription: {subscription.subscription_id}")
        zero_cpu_vms, total_vms = check_cpu_utilization(subscription.subscription_id)
        all_zero_cpu_vms.extend(zero_cpu_vms)
        total_vms_count += total_vms

    # Format and send Slack message
    slack_message = format_slack_message(all_zero_cpu_vms, total_vms_count)
    send_message_to_slack(slack_message)


if __name__ == "__main__":
    main()
