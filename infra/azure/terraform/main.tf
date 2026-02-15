terraform {
  required_version = ">= 1.5.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "random_integer" "suffix" {
  min = 1000
  max = 9999
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "adls" {
  name                     = "${var.storage_account_prefix}${random_integer.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  is_hns_enabled           = true  # ADLS Gen2
}

resource "azurerm_storage_container" "lakehouse" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.adls.name
  container_access_type = "private"
}

output "storage_account_name" {
  value = azurerm_storage_account.adls.name
}

output "container_name" {
  value = azurerm_storage_container.lakehouse.name
}
