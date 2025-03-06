import os
import argparse
import json
import requests
import yaml
from collections import defaultdict
from slack_sdk import WebClient
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient
# import mysql.connector
# from mysql.connector import Error

parser = argparse.ArgumentParser(description="Script to check unused VMs in Azure.")
parser.add_argument("--branch", type=str, help="The branch to process", required=False, default='')
args = parser.parse_args()

# Define the age threshold (24 hours ago) with UTC timezone
threshold_time = (datetime.utcnow() - timedelta(hours=24)).replace(tzinfo=timezone.utc)

# Get the list of subscription IDs from environment variables
subscription_ids = os.getenv("SUBSCRIPTION_IDS", "").split(",")

# Load exclusion dictionary and OpsGenie configuration from environment variables
exclusion_dict = json.loads(os.getenv("EXCLUSION_DICT", "{}"))
opsgenie_api_key = os.getenv("OPSGENIE_API_KEY")
opsgenie_api_url = "https://api.opsgenie.com/v2/alerts"

# MySQL database configuration
# mysql_config = {
#     "host": os.getenv("MYSQL_HOST"),
#     "user": os.getenv("MYSQL_USER"),
#     "password": os.getenv("MYSQL_PASSWORD"),
#     "database": os.getenv("MYSQL_DATABASE")
# }

def get_vms_in_vmss(compute_client, resource_group_name, subscription_id):
    vms_in_vmss = []
    vmss_list = compute_client.virtual_machine_scale_sets.list(resource_group_name)
    
    for vmss in vmss_list:
        vmss_name = vmss.name
        
        # Exclude VMSS if it is in the exclusion list or present in the MySQL database
        if is_vmss_excluded(subscription_id, resource_group_name, vmss_name):
            continue

        print(f"Checking VMSS: {vmss_name} in Resource Group: {resource_group_name}")
        vm_instances = compute_client.virtual_machine_scale_set_vms.list(resource_group_name, vmss_name)

        for vm in vm_instances:
            creation_time = vm.time_created  # Adjust field if necessary
            if creation_time and creation_time < threshold_time:
                vms_in_vmss.append({
                    "VM Name": vm.name,
                    "VMSS Name": vmss_name,
                    "Resource Group": resource_group_name,
                    "Creation Time": creation_time,
                    "Subscription ID": subscription_id
                })

    return vms_in_vmss

# Check if VMSS is in exclusion list
def is_vmss_excluded(subscription_id, resource_group, vmss_name):
    return (
        subscription_id in exclusion_dict and
        resource_group in exclusion_dict[subscription_id] and
        vmss_name in exclusion_dict[subscription_id][resource_group]
    )

# Check if VMSS exists in MySQL database
def is_vmss_in_database(vmss_name):
    try:
        connection = mysql.connector.connect(**mysql_config)
        if connection.is_connected():
            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM vmss_table WHERE vmss_name = %s"
            cursor.execute(query, (vmss_name,))
            result = cursor.fetchone()
            return result[0] > 0  # True if VMSS exists in the database
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return False

# Send alert to OpsGenie
def send_opsgenie_alert(subscription_id, resource_group, vmss_name, vm_count):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"GenieKey {opsgenie_api_key}"
    }

    alert_data = {
        "message": f"High VM Count Alert for {vmss_name} in {resource_group}",
        "alias": f"{subscription_id}-{resource_group}-{vmss_name}",
        "description": (
            f"The VM count for VMSS '{vmss_name}' in resource group '{resource_group}' "
            f"of subscription '{subscription_id}' is {vm_count}, which exceeds the threshold of 5."
        ),
        "priority": "P2",
        "tags": ["High VM Count", "Azure", "VMSS"],
        "details": {
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "vmss_name": vmss_name,
            "vm_count": vm_count
        }
    }

    response = requests.post(opsgenie_api_url, headers=headers, json=alert_data)
    if response.status_code == 202:
        print(f"Alert sent to OpsGenie for VMSS '{vmss_name}'")
    else:
        print(f"Failed to send alert to OpsGenie: {response.text}")

def send_slack_file(vms_list):
    if not vms_list:
        print("No unused VMs to notify.")
        return

    # Group data by subscription, resource group, and VMSS
    grouped_vms = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    total_vms_count = 0  # Track the total number of VMs
    for vm in vms_list:
        subscription_id = vm['Subscription ID']
        resource_group = vm['Resource Group']
        vmss_name = vm.get('VMSS Name', 'Unknown VMSS')
        grouped_vms[subscription_id][resource_group][vmss_name].append(vm)
        total_vms_count += 1  # Increment the total VM count

    # Create a formatted string for the text file and structure data for YAML
    
    git_env = os.getenv('GITHUB_REF').split('/')[2]
    if args.branch:
        git_env = args.branch
    structured_data = {}
    file_content = f"Summary of Unused VMSS(s)\n\nEnvironment: {git_env}\nTotal VMs: {total_vms_count}\n\n"
    blocks = [f"*Summary of Unused VMSS(s)*\n\n*Environment:* {git_env}\n*Total VMs:* {total_vms_count}\n\n"]
    
    for subscription_id, resource_groups in grouped_vms.items():
        file_content += f"Subscription ID: {subscription_id}\n\n"
        subscription_data = {"resource_groups": []}
        
        # Slack message block for subscription
        blocks.append(f"*Subscription ID:* {subscription_id}")
        
        for resource_group, vmss_groups in resource_groups.items():
            rg_vms_count = sum(len(vms) for vms in vmss_groups.values())
            file_content += f"  Resource Group: {resource_group} (Total VMs: {rg_vms_count})\n\n"
            rg_data = {"name": resource_group, "total_vms": rg_vms_count, "vmss": []}
            
            # Slack message block for resource group
            blocks.append(f"*Resource Group:* {resource_group} (Total VMs: {rg_vms_count})")
            
            for vmss_name, vms in vmss_groups.items():
                file_content += f"    VMSS Name: {vmss_name} (VM Count: {len(vms)})\n"
                vmss_data = {"name": vmss_name, "vm_count": len(vms), "vms": []}
                
                # Add VMSS details to Slack message
                vmss_block = f"- *VMSS Name:* {vmss_name} (VM Count: {len(vms)})"
                for vm in vms:
                    vm_name = vm['VM Name']
                    creation_time = vm['Creation Time']
                    file_content += f"      - VM Name: {vm_name} [{creation_time}]\n"
                    
                    # Append VM details to the VMSS data and Slack block
                    vmss_data["vms"].append({
                        "vm_name": vm_name,
                        "creation_time": creation_time
                    })
                    vmss_block += f"\n    • VM Name: {vm_name} [{creation_time}]"
                vmss_block += "\n"

                
                blocks.append(vmss_block)
                rg_data["vmss"].append(vmss_data)
                file_content += "\n"
            
            subscription_data["resource_groups"].append(rg_data)
            file_content += "\n"
        
        structured_data[subscription_id] = subscription_data
        file_content += "\n\n"

    # Write to a temporary text file
    today_date = datetime.now().strftime("%Y-%m-%d")
    temp_file_path = f"/tmp/unused_vms_{today_date}.txt"
    with open(temp_file_path, 'w') as file:
        file.write(file_content)

    # Write to a YAML file
    yaml_file_path = f"/tmp/unused_vms_{today_date}.yaml"
    with open(yaml_file_path, 'w') as yaml_file:
        yaml.dump(structured_data, yaml_file, default_flow_style=False)

    # Send the files and message to Slack
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
    slack_channel_id = os.getenv("SLACK_CHANNEL_ID")

    try:
        # Send message with red-colored attachment
        # attachment_text = "\n".join(blocks)
        # message_response = client.chat_postMessage(
        #     channel=slack_channel_id,
        #     text="",
        #     attachments=[{
        #         "color": "#FF0000",  # Red color for the attachment border
        #         "text": attachment_text
        #     }]
        # )

        #Upload text file
        response = client.files_upload_v2(
            channels=slack_channel_id,
            file=temp_file_path,
            filename=os.path.basename(temp_file_path),
            title=f"Unused VMs Text Report ({today_date})"
        )
        
        # # Upload YAML file
        # yaml_response = client.files_upload_v2(
        #     channels=slack_channel_id,
        #     file=yaml_file_path,
        #     filename=os.path.basename(yaml_file_path),
        #     title=f"Unused VMs YAML Report ({today_date})"
        # )

        # if not response['ok'] or not yaml_response['ok'] or not message_response['ok']:
        if not message_response['ok']:
            print("Failed to send files or message to Slack.")
        else:
            print("Files and message sent to Slack successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Initialize Azure SDK clients for each subscription and retrieve all resource groups
credential = DefaultAzureCredential()
all_vms = []

for subscription_id in subscription_ids:
    compute_client = ComputeManagementClient(credential, subscription_id)
    resource_client = ResourceManagementClient(credential, subscription_id)
    
    for rg in resource_client.resource_groups.list():
        resource_group_name = rg.name
        vms_in_rg = get_vms_in_vmss(compute_client, resource_group_name, subscription_id)
        all_vms.extend(vms_in_rg)

# Check if there are any VMs and send a Slack file if so
if all_vms:
    print("Unused VMs detected. Sending Slack file.")
    send_slack_file(all_vms)
else:
    print("No unused VMs found.")