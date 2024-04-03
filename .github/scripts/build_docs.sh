#!/bin/bash

pip install --upgrade pip
pip install --quiet wheel==0.41.3
pip install --quiet -r requirements-dev.txt

echo $GCP_KEY | base64 -d >> gcp_creds.json
gcloud auth activate-service-account --key-file gcp_creds.json
gcloud config set project ds-internal-db-ally

# Build the documentation
mkdocs build

# Upload built docs to a bucket
gcloud storage cp -r site/* gs://db-ally-documentation

# Invalidate cached content in the CDN
gcloud compute url-maps invalidate-cdn-cache db-ally-documentation-lb \
    --path "/*" --async
