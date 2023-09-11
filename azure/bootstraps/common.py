class Config:
    def __init__(self):
        self.resource_group = ""
        self.vm_name = ""
        self.admin_user = ""
        self.admin_password = ""
        self.ports = ""
        self.image = ""
        self.vm_size = ""

    def __dir__(self):
        return {
            "resource_group": self.resource_group,
            "vm_name": self.vm_name,
            "admin_user": self.admin_user,
            "admin_password": self.admin_password,
            "ports": self.ports,
            "image": self.image,
            "vm_size": self.vm_size
        }