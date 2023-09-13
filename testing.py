from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
import subprocess

credential = DefaultAzureCredential()
subscription_client = SubscriptionClient(credential)

tenants = list(subscription_client.tenants.list())

# List all tenants
print("Available Tenants:")
for idx, tenant in enumerate(tenants, start=1):
    print(f"{idx}. Tenant ID: {tenant.tenant_id}")
print(f"{len(tenants) + 1}. Continue with currently logged-in tenant")

selection = input("Enter the index, Tenant ID of the tenant you want to switch to, or choose to continue with the current tenant: ")

# Check if the user entered an index
if selection.isdigit():
    if 1 <= int(selection) <= len(tenants):
        chosen_tenant_id = tenants[int(selection) - 1].tenant_id
        subprocess.run(["az", "login", "--tenant", chosen_tenant_id])
    elif int(selection) == len(tenants) + 1:
        print("Continuing with the currently logged-in tenant...")
    else:
        print("Invalid index. Exiting.")
        exit()
else:
    chosen_tenant_id = selection
    subprocess.run(["az", "login", "--tenant", chosen_tenant_id])

cmd = [
    "az", "ad", "user", "list",
    "--query", "[].{DisplayName:displayName, UserPrincipalName:userPrincipalName}",
    "-o", "table"
]

output = subprocess.check_output(cmd, universal_newlines=True)

print(output)
