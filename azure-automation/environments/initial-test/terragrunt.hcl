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
    subscription_id      = "e4e753ea-67e1-40b6-af99-875a23dbc046"
    key                  = "${path_relative_to_include("root")}/terraform.tfstate"
    resource_group_name  = "playground-rg"
    storage_account_name = "tf1state"
    container_name       = "terraform-state-files"
  }
}

inputs = {
  subscription_id = "e4e753ea-67e1-40b6-af99-875a23dbc046"

  # -------- Virtual Machine -------- #
  vm_name              = "azure-vm-initial"
  os_flavor            = "windows"
  virtual_machine_size = "Standard_F2s_v2"
  resource_group_name  = "playground-rg"
  admin_username       = "ltuser"
  admin_password       = "#lambdapass123#"

  # When source_image_id is defined, the source_image_reference won't take effect
  source_image_id = "/subscriptions/e4e753ea-67e1-40b6-af99-875a23dbc046/resourceGroups/hypertest-stage/providers/Microsoft.Compute/galleries/hypertest_stage/images/hypertest_stage_specialized/versions/0.1.18"
  #compute_gallary_image = {
  #  name = "1.1.3"
  #  image_name = "hypertest_stage_specialized"
  #  gallery_name = "hypertest_stage"
  #}
  tags = {
    environment    = "test"
    billing_target = "hyperexecute"
    created_by     = "Soumil"
    created_with   = "terraform"
  }

  #source_image_reference = {
  #  publisher = "MicrosoftWindowsServer"
  #  offer     = "WindowsServer"
  #  sku       = "2016-Datacenter"
  #  version   = "latest"
  #}
  #auto_shut_down_scheduler = {
  #  enabled = true
  #  timezone = "India Standard Time"
  #  daily_recurrence_time = "2300"
  #}

  # -------- Networking --------- #
  virtual_network_name        = "demo-network"
  virtual_network_subnet_name = "internal"
  enable_public_ip_address    = true
  public_ip_allocation_method = "Dynamic"


  # -------- VM Image Creation --------- #
  capture_vm_image = true
  image_gallery_name = "hypertest_stage"
  shared_image_name = "hypertest_stage_specialized"
  shared_image_version_to_create = "0.1.33"
  vm_image_name = "test_image_creation"
  source_virtual_machine_id = "/subscriptions/e4e753ea-67e1-40b6-af99-875a23dbc046/resourceGroups/hypertest-stage/providers/Microsoft.Compute/virtualMachines/test-cleanup-script"
}
