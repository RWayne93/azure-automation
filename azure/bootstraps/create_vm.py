from azure.bootstraps.utils import load_env
from azure.bootstraps.images import AzureImageHandler
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
import string
import random
import json

class AzureVM:
    def __init__(self, subscription_id, location='eastus'):
        self.subscription_id = subscription_id
        self.location = location
        self.credential = DefaultAzureCredential()
        self.compute_client = ComputeManagementClient(self.credential, self.subscription_id)
        self.network_client = NetworkManagementClient(self.credential, self.subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    @staticmethod
    def generate_password(length:  int=12) -> str:
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for i in range(length))
        print(f"Your generated password is: {password} it has also been saved in a txt file called password.txt")
        with open('password.txt', 'w') as f:
            f.write(password)
        return password

    def create_resource_group_if_none_exists(self, resource_group_name):
        resource_group_exists = False
        for rg in self.resource_client.resource_groups.list():
            if rg.name == resource_group_name:
                resource_group_exists = True
                break

        if not resource_group_exists:
            self.resource_client.resource_groups.create_or_update(resource_group_name, {'location': self.location})
            print(f"Resource group {resource_group_name} created in {self.location}.")

    def create_virtual_machine(self, resource_group_name, vm_name, admin_user, admin_password, ports=[], image_data=None, vm_size=None):
        # Use the default credential
        
        credential = DefaultAzureCredential()

        if image_data:
            chosen_publisher = image_data['publisher']
            chosen_offer = image_data['offer']
            chosen_sku = image_data['sku']

            if vm_size:
                selected_vm_size = vm_size
            else:
                image_handler = AzureImageHandler(self.subscription_id)
                selected_vm_size = image_handler.select_vm_size(self.location)

        else:
            image_handler = AzureImageHandler(self.subscription_id)
            image_data = image_handler.list_available_images(self.location)
            chosen_publisher = image_data['publisher']
            chosen_offer = image_data['offer']
            chosen_sku = image_data['sku']
            selected_vm_size = image_handler.select_vm_size(self.location)

        # Create compute and network clients
        compute_client = ComputeManagementClient(credential, subscription_id)
        network_client = NetworkManagementClient(credential, subscription_id)
        
        # Create a VNet
        vnet_name = vm_name + '_vnet'
        subnet_name = vm_name + '_subnet'
        async_vnet_creation = network_client.virtual_networks.begin_create_or_update(
            resource_group_name,
            vnet_name,
            {
                'location': 'eastus',  # You can change this
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                },
                'subnets': [{
                    'name': subnet_name,
                    'address_prefix': '10.0.0.0/24'
                }]
            }
        )
        async_vnet_creation.result()

        # Create a public IP
        public_ip_name = vm_name + '_ip'
        async_ip_creation = network_client.public_ip_addresses.begin_create_or_update(
            resource_group_name,
            public_ip_name,
            {
                'location': 'eastus',  # You can change this
                'sku': {'name': 'Basic'},
                'public_ip_allocation_method': 'Dynamic',
                'public_ip_address_version': 'IPV4'
            }
        )
        public_ip_info = async_ip_creation.result()

        # Create a NIC
        nic_name = vm_name + '_nic'
        async_nic_creation = network_client.network_interfaces.begin_create_or_update(
            resource_group_name,
            nic_name,
            {
                'location': 'eastus',  # You can change this
                'ip_configurations': [{
                    'name': 'ip_config',
                    'public_ip_address': {'id': public_ip_info.id},
                    'subnet': {'id': async_vnet_creation.result().subnets[0].id}
                }]
            }
        )
        nic_info = async_nic_creation.result()

        # Specify ports
        if ports:
            security_group_name = vm_name + '_nsg'
            rule_list = []
            priority = 1000
            for port in ports:
                rule_name = f'rule_{port}'
                rule_list.append({
                    'name': rule_name,
                    'protocol': 'Tcp',
                    'direction': 'Inbound',
                    'source_address_prefix': '*',
                    'destination_address_prefix': '*',
                    'source_port_range': '*',
                    'destination_port_range': port,
                    'access': 'Allow',
                    'priority': priority
                })
                priority += 10
            async_nsg_creation = network_client.network_security_groups.begin_create_or_update(
                resource_group_name,
                security_group_name,
                {
                    'location': 'eastus',  # You can change this
                    'security_rules': rule_list
                }
            )
            nsg_info = async_nsg_creation.result()

            # Associate the NSG to the subnet
            subnet_info = network_client.subnets.get(resource_group_name, vnet_name, subnet_name)
            subnet_info.network_security_group = {'id': nsg_info.id}
            async_subnet_update = network_client.subnets.begin_create_or_update(
                resource_group_name, vnet_name, subnet_name, subnet_info)
            async_subnet_update.result()

        # Create VM
        async_vm_creation = compute_client.virtual_machines.begin_create_or_update(
            resource_group_name,
            vm_name,
            {
                'location': 'eastus',  # You can change this
                'os_profile': {
                    'computer_name': vm_name,
                    'admin_username': admin_user,
                    'admin_password': admin_password
                },
                'hardware_profile': {
                    'vm_size': selected_vm_size
                },
                'storage_profile': {
                    'image_reference': {
                        'publisher': chosen_publisher,
                        'offer': chosen_offer,
                        'sku': chosen_sku,
                        'version': 'latest'
                    }
                },
                'network_profile': {
                    'network_interfaces': [{
                        'id': nic_info.id
                    }]
                }
            }
        )
        vm_info = async_vm_creation.result()
        print(f"VM {vm_name} created with ID: {vm_info.id}")

def process_config_file(vm_creator, file_name):
    with open(file_name, 'r') as file:
        configs = json.load(file)
        for config in configs:
            #print(config)
            vm_creator.create_resource_group_if_none_exists(config['resource_group'])
            vm_creator.create_virtual_machine(
                config['resource_group'],
                config['vm_name'],
                config['admin_user'],
                config['admin_password'],
                config['ports'],  
                config.get('image', None),
                config.get('vm_size', None)
            )

if __name__ == '__main__':
    subscription_id = load_env()
    vm_creator = AzureVM(subscription_id)

    use_config_file = input('Do you have a config file to use? (yes/no): ').strip().lower()

    if use_config_file == 'yes':
        config_file_name = input('Enter the path to your config file: ')
        print('Creating Virtual Machines from config file...')
        process_config_file(vm_creator, config_file_name)
    else:
        resource_group_name = input('Enter a name for your resource group: ')
        vm_name = input('Enter a name for your VM: ')
        admin_user = 'azureuser'
        admin_password = vm_creator.generate_password()
        ports = ['22', '80', '443']

        vm_creator.create_resource_group_if_none_exists(resource_group_name)
        vm_creator.create_virtual_machine(resource_group_name, vm_name, admin_user, admin_password, ports)
