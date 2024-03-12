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

resource "google_project_service" "compute_api" {
  project = var.project
  service = "compute.googleapis.com"
}

resource "google_storage_bucket" "docs_bucket" {
  name          = "db-ally-documentation"
  location      = "EU"
  storage_class = "STANDARD"

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

resource "google_storage_bucket_iam_member" "member" {
  provider = google
  bucket   = google_storage_bucket.docs_bucket.name
  role     = "roles/storage.objectViewer"
  member   = "allUsers"
}

output "conn_string_prefix" {
  description = "PostgreSQL connection string without /<database-name> at the end."
  value       = module.database.conn_string_prefix
  sensitive   = true
}