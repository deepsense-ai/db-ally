terraform {
  required_providers {
    google = {
      source  = "hashicorp/google",
      version = "~> 4.80.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = local.region
  zone    = local.zone
}