from azure.bootstraps.create_vm import AzureVM
from azure.bootstraps.utils import load_env, ConfigParser

def main():
    subscription_id = load_env()
    vm_creator = AzureVM(subscription_id)

    use_config_file = input('Do you have a config file to use? (yes/no): ').strip().lower()

    if use_config_file == 'yes':
        config_file_name = input('Enter the path to your config file: ')
        print('Creating Virtual Machines from config file...')
        ConfigParser(vm_creator, config_file_name)
    else:
        resource_group_name = input('Enter a name for your resource group: ')
        vm_name = input('Enter a name for your VM: ')
        admin_user = 'azureuser'
        admin_password = vm_creator.generate_password()
        ports = ['22', '80', '443']

        vm_creator.create_resource_group_if_none_exists(resource_group_name)
        vm_creator.create_virtual_machine(resource_group_name, vm_name, admin_user, admin_password, ports)

if __name__ == '__main__':
    main()