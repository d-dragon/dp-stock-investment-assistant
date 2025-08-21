variable "project_name" { type = string default = "dp-stock" }
variable "location" { type = string default = "eastus" }
variable "resource_group_name" { type = string default = "rg-dp-stock" }
variable "aks_node_count" { type = number default = 1 }
variable "aks_node_size" { type = string default = "Standard_B4ms" }