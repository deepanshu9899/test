include "root" {
  path = find_in_parent_folders()
}

remote_state {
  backend = "azurerm"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite"
  }
  config = {
    subscription_id      = "6d191c3d-e7e4-448d-ae59-6b3e3d69eb8b"
    key                  = "browserupdatewin/terraform.tfstate"
    resource_group_name  = "Hypertest-Production"
    storage_account_name = "terraformstatefilesprodu"
    container_name       = "terraform-state-files"
  }
}
inputs = {
  subscription_id = "6d191c3d-e7e4-448d-ae59-6b3e3d69eb8b"
  
  ## -- Network Variables -- #
  virtual_network_name        = "Hypertest-Production-vnet"
  virtual_network_subnet_name = "hypertestProductionVmssSubnet6"
  enable_public_ip_address    = true
  public_ip_allocation_method = "Dynamic"
  
  ## -- Virtual Machine -- #
  os_flavor            = "windows"
  vm_name              = "basevm_windows10-28022024"
  priority             = "Spot"
  virtual_machine_size = "Standard_F2s_v2"
  resource_group_name  = "Hypertest-Production"

  source_image_id = "/subscriptions/6d191c3d-e7e4-448d-ae59-6b3e3d69eb8b/resourceGroups/Hypertest-Production/providers/Microsoft.Compute/galleries/hypertest_prod_images/images/hypertest-prod/versions/1.0.720240130"
  tags = {
    Environment  = "prod"
    Product      = "hyperexecute"
    Creator      = "shivams0702"
    Created_with = "terraform"
    Created_on   = "28-02-2024"
    Jira         = "HYP-8686"
  }
}
