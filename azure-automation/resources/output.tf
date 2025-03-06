output "linux_vm_password" {
  description = "Password for the Linux VM"
  sensitive   = true
  value       = module.azure-vm-creation.linux_vm_password
}
