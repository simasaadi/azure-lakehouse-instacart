\# Azure deployment (optional)



This repo runs end-to-end without an Azure subscription using \*\*Azurite\*\* (local Azure Blob emulator).



If you \*do\* have an Azure subscription, the Terraform in `infra/azure/terraform/` will create:

\- Resource Group

\- ADLS Gen2 Storage Account (HNS enabled)

\- Private container `lakehouse/`



\## Terraform (requires Azure subscription)

From `infra/azure/terraform`:



```powershell

terraform init

terraform plan

terraform apply



