from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure_utils import load_env

def list_all_resource_groups_and_resources(subscription_id):
    # Use the default credential (e.g., from environment variable or local development environment)
    credential = DefaultAzureCredential()

    # Initialize a Resource Management client
    resource_client = ResourceManagementClient(credential, subscription_id)

    # List all resource groups
    for rg in resource_client.resource_groups.list():
        print(f"Resource Group: {rg.name}")
        
        # List all resources in the current resource group
        resources = resource_client.resources.list_by_resource_group(rg.name)
        for resource in resources:
            print(f"Resource Name: {resource.name}, Type: {resource.type}")
        print()

def delete_resource_groups_except_excluded(subscription_id, excluded_rg_list):
    # Use the default credential (e.g., from environment variable or local development environment)
    credential = DefaultAzureCredential()

    # Initialize a Resource Management client
    resource_client = ResourceManagementClient(credential, subscription_id)

    # List all resource groups
    for rg in resource_client.resource_groups.list():
        if rg.name not in excluded_rg_list:
            print(f"Deleting Resource Group: {rg.name}")
            resource_client.resource_groups.begin_delete(rg.name)
        else:
            print(f"Skipping deletion of Resource Group: {rg.name} as it's in the exclusion list")


if __name__ == '__main__':
    # Replace with your Azure subscription ID
    excluded_resource_groups = ["myResourceGroup", "NetworkWatcherRG", 'cloud-shell-storage-westus']
    subscription_id = load_env()
    
    print('Listing all resource groups and resources')
    list_all_resource_groups_and_resources(subscription_id)
    print('Deleting all resource groups except those in the exclusion list')
    delete_resource_groups_except_excluded(subscription_id, excluded_resource_groups)

    print('done')
