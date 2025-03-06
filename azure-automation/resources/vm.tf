module "azure-vm-creation" {
  # Source Need to be replaced with the remote repo URL
  # source                      = "/Users/soumilk/Documents/LambdaTest/terraform/hyperexecute/hye-azure-automation-modules/azure-shared-modules/vm"
  source = "git::ssh://git@github.com/soumilk-LT/hype-azure-automation-modules.git//azure-shared-modules/vm?ref=main"
  #source                      = "git@github.com:soumilk-LT/hype-azure-automation-modules.git//azure-shared-modules/vm?ref=main"
  subscription_id             = var.subscription_id
  virtual_machine_name        = var.vm_name
  resource_group_name         = var.resource_group_name
  os_flavor                   = var.os_flavor
  admin_username              = var.admin_username
  admin_password              = var.admin_password
  virtual_machine_size        = var.virtual_machine_size
  source_image_reference      = var.source_image_reference
  source_image_id             = var.source_image_id
  compute_gallary_image       = var.compute_gallary_image
  virtual_network_name        = var.virtual_network_name
  virtual_network_subnet_name = var.virtual_network_subnet_name
  enable_public_ip_address    = var.enable_public_ip_address
  public_ip_address_id        = module.azure-networking.public_ip_address_id
  vm_nic_id                   = module.azure-networking.vm_nic_id
  auto_shut_down_scheduler    = var.auto_shut_down_scheduler
  priority                    = var.priority
  tags                        = var.tags
}
