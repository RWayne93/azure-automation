from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.bootstraps.utils import load_env

class BaseAzureStorage:
    def __init__(self, subscription_id, resource_group_name, storage_account_name, location='eastus'):
        self.subscription_id = subscription_id
        self.resource_group_name = resource_group_name
        self.storage_account_name = storage_account_name
        self.location = location

        self.credential = DefaultAzureCredential()
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)
        self.storage_client = StorageManagementClient(self.credential, self.subscription_id)

    def create_resource_group(self):
        self.resource_client.resource_groups.create_or_update(self.resource_group_name, {"location": self.location})

    def create_storage_account(self):
        self.storage_client.storage_accounts.begin_create(
            self.resource_group_name,
            self.storage_account_name,
            {
                "sku": {"name": "Standard_GRS"},
                "kind": "StorageV2",
                "location": self.location,
                "encryption": {
                    "services": {
                        "file": {"key_type": "Account", "enabled": True},
                        "blob": {"key_type": "Account", "enabled": True}
                    },
                    "key_source": "Microsoft.Storage"
                },
                "tags": {"key1": "value1", "key2": "value2"}
            }
        ).result()

    def delete_resource_group(self):
        self.resource_client.resource_groups.begin_delete(self.resource_group_name).result()

class AzureFileShareStorage(BaseAzureStorage):
    def __init__(self, subscription_id, resource_group_name, storage_account_name, file_share_name, location='eastus'):
        super().__init__(subscription_id, resource_group_name, storage_account_name, location)
        self.file_share_name = file_share_name

    def create_file_share(self):
        return self.storage_client.file_shares.create(self.resource_group_name, self.storage_account_name, self.file_share_name, {})

    def get_file_share(self):
        return self.storage_client.file_shares.get(self.resource_group_name, self.storage_account_name, self.file_share_name)

    def update_file_share(self, metadata_type):
        return self.storage_client.file_shares.update(
            self.resource_group_name,
            self.storage_account_name,
            self.file_share_name,
            {"properties": {"metadata": {"type": metadata_type}}}
        )

    def delete_file_share(self):
        self.storage_client.file_shares.delete(self.resource_group_name, self.storage_account_name, self.file_share_name)

    def delete_resource_group(self):
        self.resource_client.resource_groups.begin_delete(self.resource_group_name).result()

    def setup_and_test_file_share(self):
        self.create_resource_group()
        self.create_storage_account()
        self.create_file_share()
        print("File share created:", self.get_file_share())
        self.update_file_share(metadata_type="image")
        print("File share updated:", self.get_file_share())
        self.delete_file_share()
        print("File share deleted.")
        self.delete_resource_group()
        # ... [rest of the file share specific methods from the original AzureStorageType]

class AzureBlobStorage(BaseAzureStorage):
    def __init__(self, subscription_id, resource_group_name, storage_account_name, blob_container_name, location='eastus'):
        super().__init__(subscription_id, resource_group_name, storage_account_name, location)
        self.blob_container_name = blob_container_name

    def create_blob_container(self):
        return self.storage_client.blob_containers.create(self.resource_group_name, self.storage_account_name, self.blob_container_name, {})

    def get_blob_container(self):
        return self.storage_client.blob_containers.get(self.resource_group_name, self.storage_account_name, self.blob_container_name)

    def update_blob_container(self, public_access="Container", metadata_value="true"):
        return self.storage_client.blob_containers.update(
            self.resource_group_name,
            self.storage_account_name,
            self.blob_container_name,
            {
                "public_access": public_access,
                "metadata": {
                    "metadata": metadata_value
                }
            }
        )

    def delete_blob_container(self):
        self.storage_client.blob_containers.delete(self.resource_group_name, self.storage_account_name, self.blob_container_name)

    def setup_and_test_blob_container(self):
        self.create_resource_group()
        self.create_storage_account()
        self.create_blob_container()
        print("Blob container created:", self.get_blob_container())
        self.update_blob_container()
        print("Blob container updated:", self.get_blob_container())
        self.delete_blob_container()
        print("Blob container deleted.")
        self.delete_resource_group()


if __name__ == "__main__":
    SUBSCRIPTION_ID = load_env()
    GROUP_NAME = "testgroupx"
    STORAGE_ACCOUNT = "storageaccountxxy"
    FILE_SHARE = "filesharexxyyzz"

    file_share_storage = AzureFileShareStorage(SUBSCRIPTION_ID, GROUP_NAME, STORAGE_ACCOUNT, FILE_SHARE)
    file_share_storage.setup_and_test_file_share()
    
    # Similarly, you can create a blob container, update it, and test it using the AzureBlobStorage class.
