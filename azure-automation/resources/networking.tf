module "azure-networking" {
  # Source Need to be replaced with the remote repo URL
  # source = "/Users/soumilk/Documents/LambdaTest/terraform/hyperexecute/hye-azure-automation-modules/azure-shared-modules/networking"
   source                      = "git::ssh://git@github.com/soumilk-LT/hype-azure-automation-modules.git//azure-shared-modules/networking?ref=main"
  #source                      = "git@github.com:soumilk-LT/hype-azure-automation-modules.git//azure-shared-modules/networking?ref=main"
  subscription_id             = var.subscription_id
  virtual_machine_name        = var.vm_name
  resource_group_name         = var.resource_group_name
  virtual_network_name        = var.virtual_network_name
  virtual_network_subnet_name = var.virtual_network_subnet_name
  enable_public_ip_address    = var.enable_public_ip_address
  tags                        = var.tags
}
