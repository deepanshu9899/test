# module "azure-automation" {
#   # source                  = "git::ssh://git@github.com:LambdatestIncPrivate/hye-azure-automation-modules.git//azure-shared-modules/automation-account?ref=main"
#   source                  = "/Users/soumilk/Documents/LambdaTest/terraform/hyperexecute/hye-azure-automation-modules/azure-shared-modules/automation-account"
#   virtual_machine_name    = var.vm_name
#   subscription_id         = var.subscription_id
#   resource_group_name     = var.resource_group_name
#   tags                    = var.tags
#   automation_account_name = var.automation_account_name
#   runbook_name            = var.runbook_name
#   python_packages         = var.python_packages
#   schedule_name           = var.schedule_name
# }
