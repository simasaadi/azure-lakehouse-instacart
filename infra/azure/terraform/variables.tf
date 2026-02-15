variable "location" {
  type    = string
  default = "canadacentral"
}

variable "resource_group_name" {
  type    = string
  default = "rg-instacart-lakehouse"
}

variable "storage_account_prefix" {
  type    = string
  default = "stinstacartlh"
  description = "Must be lowercase letters/numbers only; name will be suffixed for uniqueness."
}

variable "container_name" {
  type    = string
  default = "lakehouse"
}
