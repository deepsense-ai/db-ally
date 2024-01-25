terraform {
  backend "gcs" {
    bucket = "db-ally-tfstate"
  }
}

locals {
  region = "europe-west1"

  database_name = "db-ally-postgres"
  zone          = "${local.region}-d"
}

module "database" {
  source  = "./modules/database"
  db_name = local.database_name
  region  = local.region
  project = var.project
  database_names = var.database_names
}

output "conn_string_prefix" {
  description = "PostgreSQL connection string without /<database-name> at the end."
  value       = module.database.conn_string_prefix
  sensitive   = true
}