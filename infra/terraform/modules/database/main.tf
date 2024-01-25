variable "region" {}
variable "project" {}
variable "db_name" {}
variable "database_names" {}

resource "google_sql_database_instance" "postgres" {
  name  = var.db_name
  region = var.region
  project = var.project

  database_version = "POSTGRES_15"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name = "IPv4 default route"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
        name  = "max_connections"
        value = "250"
    }
  }
}

resource "google_sql_database" "database" {
  for_each = toset(var.database_names)
  name = each.key
  instance = google_sql_database_instance.postgres.name
  charset = "UTF8"
  project = var.project
}

resource "google_sql_user" "user" {
  name = "developer"
  instance = google_sql_database_instance.postgres.name
  password = random_password.password.result
  project = var.project
}

resource "random_password" "password" {
  length = 16
  special = true
  override_special = "#$%^&*()"
}

resource "google_project_service" "cloud_sql_admin" {
  project = var.project
  service = "sqladmin.googleapis.com"
}

output "conn_string_prefix" {
  description = "PostgreSQL connection string without database name at the end."
  value = "postgresql://${google_sql_user.user.name}:${google_sql_user.user.password}@localhost:5432"
}
