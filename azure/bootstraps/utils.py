from yaml import safe_load
from azure.bootstraps.common import Config
from typing import Sequence

def ConfigParser(config_file_path: str) -> Sequence[Config]:
    with open(config_file_path, "r") as config_file:
        configs = []
        for i in safe_load(config_file):
            config = Config()
            config.resource_group = i["resource_group"]
            config.vm_name = i["vm_name"]
            config.admin_user = i["admin_user"]
            config.admin_password = i["admin_password"]
            config.ports = i["ports"]
            config.image = i["image"]
            config.vm_size = i["vm_size"]
            configs.append(config)
        return configs