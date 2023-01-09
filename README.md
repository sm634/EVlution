# EVlution
Repo for EVlution hackathon team, Capgemini Invent

## Setup

1. Download Anaconda package, which will already have some required Data Science python libraries as well as bring in the Anaconda Prompt for Conda. You can download from here: https://www.anaconda.com/products/distribution

2. Clone the EVlution Repo into you local.

3. Navigate to the EVlutioin repo parent directory:
  ```cd ...\EVlution_ABM```
  
4. Open up the Anaconda Prompt (should be available through search after Anaconda has been successfully installed). 

5. Run the following command:
   ```conda env create -f environment.yml```
   
   This should create the environment will all the packages you need to run all of the programmes in the EVlution codebase/pipeline.

6. Using your preferred IDE, make sure you configure it to use the new environment (which will be called 'evlution_env' by default). 

7. To extract the data from S3, you will need the aws_access_key and aws_secret_access_key. Please email safal.mukhia@capgemini.com to be provided with the required keys.

#### Access to AWS Data Sources

1. To pull in the data used by the ABM model, the pipeline connects to AWS S3 bucket. Please request the AWS_ACCESS_KEY and AWS_SECRET_KEY from safal.mukhia@capgemini.com. You will need an AWS user account.

2. From the parent directory of the repo, run the following command:

```cp .env.example .env```

3. In the new .env file that should be created, you will need to add in the aws_access_key and aws_secret_access_key.

4. To make use of the credentials, you will need to create a .env file in the root EVlution directory. In the file, you should save: 
```
EVLUTION_AWS_ACCESS_KEY_ID=[access_key you were provided]
EVLUTION_AWS_SECRET_ACCESS_KEY=[secret access key you were provided]
EVLUTION_AWS_REGION_NAME=eu-west-2
EVLUTION_BUCKET_NAME=evlution-data
```
