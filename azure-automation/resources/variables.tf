
## -------- Common Variables --------- #
variable "subscription_id" {
  type        = string
  description = "Subscription id of Azure"
  nullable    = false
}

## ---------- VM based variables ----------- #
variable "vm_name" {
  type        = string
  description = "Suffix for resource group name"
  default     = "lt-vm"
  nullable    = false
}

variable "os_flavor" {
  type        = string
  description = "Type of OS to spin up in the VM"
  default     = "windows"
  nullable    = false
}

variable "virtual_machine_size" {
  type        = string
  description = "VM machine type"
  default     = "Standard_f4s_v2"
  nullable    = false
}

variable "resource_group_name" {
  type        = string
  description = "The Azure Resource group name"
  default     = "playground-rg"
  nullable    = false
}

variable "admin_username" {
  type        = string
  description = "The VM admin user"
  default     = "ltuser"
  nullable    = false
}

variable "admin_password" {
  type        = string
  description = "The VM admin user password"
  default     = null
}

variable "source_image_reference" {
  type = object({
    publisher = string
    offer     = string
    sku       = string
    version   = string
  })
  description = "source_image_reference"
  default     = null
}

variable "source_image_id" {
  type        = string
  description = "Azure Source inage ID"
  default     = null
}

variable "compute_gallary_image" {
  type = object({
    name         = string
    image_name   = string
    gallery_name = string
  })
  description = "The parameters required for the compute image gallary image creation"
  default     = null
  nullable    = true
}

variable "tags" {
  type        = map(string)
  description = "Tags to be placed on the resources"
  default = {
    environment    = "test"
    billing_target = "hyperexecute"
    created_by     = "Soumil"
    created_with   = "terraform"
  }
  nullable = false
}

variable "auto_shut_down_scheduler" {
  type = object({
    enabled               = bool
    timezone              = string
    daily_recurrence_time = string
  })
  description = "Automated shutdown schedules for Azure VMs"
  default     = null
}

variable "priority" {
  type        = string
  description = "Specifies the priority of this Virtual Machine"
  default     = "Spot"
  validation {
    condition     = contains(["Regular", "Spot"], var.priority)
    error_message = "Valid values for priority are (Regular, Spot)"
  }
}

# variable "tenant_id" {
#   type        = string
#   description = "Tenant id of Azure"
#   nullable    = false
# }


## -------- Networking Variables --------- #

variable "virtual_network_name" {
  type        = string
  description = "Azure network interface name"
  default     = null
}
variable "virtual_network_subnet_name" {
  type        = string
  description = "Azure network interface name"
  default     = null
}

variable "enable_public_ip_address" {
  type        = bool
  description = "Enable public IP address on VM ?"
  default     = false
}

variable "public_ip_allocation_method" {
  type        = string
  description = "Defines the allocation method for this IP address. Possible values are Static or Dynamic"
  default     = "Dynamic"
  validation {
    condition     = contains(["Dynamic", "Static"], var.public_ip_allocation_method)
    error_message = "Valid values for allocation_method are (Dynamic, Static) and priority should be Spot"
  }
}

## -------- VM Compute Image Variables --------- #

variable "capture_vm_image" {
  type        = bool
  description = "The name of the Shared Image"
  default     = false
}

variable "shared_image_name" {
  type        = string
  description = "The name of the Shared Image"
  default     = null
}

variable "shared_image_version_to_create" {
  type        = string
  description = "The name of the Shared Image"
  default     = null
}

variable "image_gallery_name" {
  type        = string
  description = " The name of the Shared Image Gallery in which the Shared Image exists."
  default     = null
}

variable "vm_image_name" {
  type        = string
  description = "Specifies the name of the image."
  default     = null
}

variable "source_virtual_machine_id" {
  type        = string
  description = "The Virtual Machine ID from which to create the image."
  default     = null
}

variable "hyper_v_generation" {
  type        = string
  description = "The HyperVGenerationType of the VirtualMachine created from the image"
  default     = "V1"
}

variable "os_disk_os_state" {
  type        = string
  description = "Specifies the state of the operating system contained in the blob. Currently, the only value is Generalized"
  default     = "Specialized"
  validation {
    condition     = contains(["Specialized", "Generalized"], var.os_disk_os_state)
    error_message = "Valid values for os_disk_os_state are (Specialized, Generalized)"
  }
}

## -------- Automation Account Variables --------- # 
variable "automation_account_name" {
  type        = string
  description = "Automation Account Name"
  default     = "automation-terraform"
  nullable    = false
}

variable "runbook_name" {
  type        = string
  description = "Runbook Name"
  default     = "starts-vm"
  nullable    = false
}

variable "schedule_name"{
  type        = string
  description = "Schedule Name"
  default = "start-vm-schedule"
  nullable    = false
}

variable "python_packages" {
  type = list(object({
    name        = string
    content_uri = string
  }))
  default = [
    {
      name        = "identity"
      content_uri = "https://files.pythonhosted.org/packages/30/10/5dbf755b368d10a28d55b06ac1f12512a13e88874a23db82defdea9a8cd9/azure_identity-1.15.0-py3-none-any.whl"
    },
    {
      name        = "mgmtcompute"
      content_uri = "https://files.pythonhosted.org/packages/1d/28/468b2f3dc36367a81ca4158c0aac01b66eefb5f4076674c28666d7396776/azure_mgmt_compute-30.3.0-py3-none-any.whl"
    },
    {
      name        = "typing"
      content_uri = "https://files.pythonhosted.org/packages/24/21/7d397a4b7934ff4028987914ac1044d3b7d52712f30e2ac7a2ae5bc86dd0/typing_extensions-4.8.0-py3-none-any.whl"
    },
    {
      name        = "msal"
      content_uri = "https://files.pythonhosted.org/packages/35/33/0fd933b627879a9855d02a83a57929b45d0bdbeb050ddd63109cc404fbf6/msal-1.24.1-py2.py3-none-any.whl"
    },
    {
      name        = "mgmtcore"
      content_uri = "https://files.pythonhosted.org/packages/b1/5a/3a31578b840600dffb75f3ffb383cc4c5e8ea0d06a1085f86b17e18c3193/azure_mgmt_core-1.4.0-py3-none-any.whl"
    },
    {
      name        = "core"
      content_uri = "https://files.pythonhosted.org/packages/9c/f8/1cf23a75cb8c2755c539ac967f3a7f607887c4979d073808134803720f0f/azure_core-1.29.5-py3-none-any.whl"
    },
  ]
}