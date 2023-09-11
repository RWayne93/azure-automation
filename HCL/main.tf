locals {
  vms = jsondecode(file("${path.module}/../vm_config.json"))
}

resource "azurerm_windows_virtual_machine" "main" {
  for_each = { for vm in local.vms : vm.vm_name => vm }

  name                  = each.value.vm_name
  admin_username        = each.value.admin_user
  admin_password        = each.value.admin_password
  location              = azurerm_resource_group.rg.location
  resource_group_name   = each.value.resource_group
  network_interface_ids = [azurerm_network_interface.my_terraform_nic.id]
  size                  = each.value.vm_size

  os_disk {
    name                 = "myOsDisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }

  source_image_reference {
    publisher = each.value.image.publisher
    offer     = each.value.image.offer
    sku       = each.value.image.sku
    version   = each.value.image.version
  }

  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.my_storage_account.primary_blob_endpoint
  }
}

resource "azurerm_network_security_group" "my_terraform_nsg" {
  for_each = { for vm in local.vms : vm.vm_name => vm }

  name                = "${random_pet.prefix.id}-${each.key}-nsg"
  location            = azurerm_resource_group.rg.location
  resource_group_name = each.value.resource_group

  dynamic "security_rule" {
    for_each = each.value.ports
    content {
      name                       = "rule-${security_rule.value}"
      priority                   = 1000 + security_rule.key
      direction                  = "Inbound"
      access                     = "Allow"
      protocol                   = "Tcp"
      source_port_range          = "*"
      destination_port_range     = security_rule.value
      source_address_prefix      = "*"
      destination_address_prefix = "*"
    }
  }
}
