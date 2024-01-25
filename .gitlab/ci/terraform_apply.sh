echo $GCP_KEY | base64 -d >> gcp_creds.json
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/gcp_creds.json

# Install terraform
apt-get install wget
wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor > /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" > /etc/apt/sources.list.d/hashicorp.list
apt update
apt-get install terraform

gcloud auth activate-service-account --key-file gcp_creds.json
gcloud config set project ds-internal-db-ally

cd infra/terraform
terraform init
terraform apply \
    -var "project=$(gcloud config get project)" \
    -auto-approve