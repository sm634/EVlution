#!bin/bash
# A script to be used after the correct environment is set up for the EVlution repo codebase.
# This script will create a .env script to store environment variables used to access data sources like s3 in.

touch .env
echo "EVLUTION_AWS_ACCESS_KEY_ID=" >> .env
echo "EVLUTION_AWS_SECRET_ACCESS_KEY=" >> .env
echo "EVLUTION_AWS_REGION_NAME=eu-west-2" >> .env
echo "EVLUTION_BUCKET_NAME=evlution-data" >> .env