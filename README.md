# Serverless Django Postgres with Neon

## Prerequisites

1. Familiarity with Django, Docker, Postgres, Serverless Framework, and AWS (CLI, ECR, Lambda, S3)
1. Neon Account with a Project
1. AWS Account
1. AWS CLI configured with your keys

## Preamble

To try out Neon "locally" all you need is a Neon account and a project. You can clone this repo, change a few postgres related variables and it will just work. Nothing fancy, not even a Polls model, but enough for Django Admin login.

You'll also be able to deploy Django to AWS Lambda using a docker image via Serverless Framework (sls).

### Local Setup

1. Clone this repo
1. `cd src/backend`
1. Copy .env.sample to .env
   1. Update to use your Neon connection details. (I have a `main` and `dev` Postgres branch, hence two sections)
   1. AWS credentials will be used in the next section, so feel free to add them now.
1. In a terminal, `docker compose up`
1. In another terminal, bash into the running container e.g. `docker exec -it django-neon-api-1 bash`
   1. Migrate your database `./manage.py migrate`
   1. Create a super user `./manage.py createsuperuser`
1. Open http://localhost:9000/admin

### AWS Deployment

For these steps we will use the AWS CLI.

The Secrets created in SSM will be used via sls to create a deployment bucket and a static bucket.

The remaining are for access to Neon Postgres.

#### Define some local env vars

1. export AWS_PROFILE=`<default or other>`
1. export AWS_ACCOUNT_ID=`<your account ID>`
1. export AWS_REGION=`<your preferred region>`
1. export AWS_KMS_KEY_ID=`<your kms key id>`
   1. You can also remove all the `--key-id` options from below to use the default aws/ssm key
1. export AWS_ECR_REPO_NAME=`<your ecr repository name>`

#### Add Secrets via SSM

1.  Define and create your deployment bucket name

    ```
       aws ssm put-parameter \
       --name "/SLS_DEPLOYMENT_BUCKET" \
       --value "<your-globally-unique-bucket-name>" \
       --type "SecureString" \
       --key-id "${AWS_KMS_KEY_ID}" \
       --overwrite
    ```

1.  Define and create your static assets bucket name

    ```
      aws ssm put-parameter \
      --name "/django/STATIC_BUCKET" \
      --value "<your-globally-unique-bucket-name>" \
      --type "SecureString" \
      --key-id "${AWS_KMS_KEY_ID}" \
      --overwrite
    ```

1.  Neon Postgres (Dev Branch)

    1. Hostname

       ```
         aws ssm put-parameter \
         --name "/dev/neon/POSTGRES_HOST" \
         --value "<your hostname>" \
         --type "SecureString" \
         --key-id "${AWS_KMS_KEY_ID}" \
         --overwrite
       ```

    1. DB

       ```

         aws ssm put-parameter \
         --name "/dev/neon/POSTGRES_DB" \
         --value "<your db name>" \
         --type "SecureString" \
         --key-id "${AWS_KMS_KEY_ID}" \
         --overwrite

       ```

    1. Password

       ```
         aws ssm put-parameter \
         --name "/dev/neon/POSTGRES_PASSWORD" \
         --value "<your password>" \
         --type "SecureString" \
         --key-id "${AWS_KMS_KEY_ID}" \
         --overwrite

       ```

    1. User

       ```
         aws ssm put-parameter \
         --name "/dev/neon/POSTGRES_USER" \
         --value "<your user>" \
         --type "SecureString" \
         --key-id "${AWS_KMS_KEY_ID}" \
         --overwrite
       ```

#### Login to ECR

```
    aws ecr get-login-password | \
        docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com'
```

#### Build and Push Image

1. Create (if it doesn't exist) an ECR repository
   1. `aws ecr describe-repositories --repository-names ${AWS_ECR_REPO_NAME} || aws ecr create-repository --repository-name ${AWS_ECR_REPO_NAME}`
1. `docker build -t django-neon .`
1. `docker tag django-neon ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${AWS_ECR_REPO_NAME}:latest`
1. `docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${AWS_ECR_REPO_NAME}:latest`

#### Deploy

1. `serverless deploy --stage dev --region ${AWS_REGION}`

   Note: AWS_ECR_REPO_NAME is used in serverless.yml for the image name

   https://github.com/mqarty/serverless-django-postgres/blob/73f6c1f9e69c2bacf331b9fbd0792894f0cd0d03/src/backend/serverless.yml#L69-L72

1. Copy the endpoint, a.k.a function url, from the output e.g. https://blahblahblah.lambda-url.us-west-1.on.aws/.

#### Login to Admin

If you go to that endpoint and append `/admin` you won't see a very pretty admin. To fix that we need to run Django's collect static function from the lambda. To do that make sure you are in `./src/backend`.

1. Run `./scripts/invoke_manage.py dev api collectstatic -p "--no-input --clear"`

   This will execute collectstatic on the Lambda in AWS and print out the response locally. e.g.

   ```
      django-neon-dev-api$ ./manage.py collectstatic --no-input --clear
      {
         "ExecutedVersion": "$LATEST",
         "Payload": "<botocore.response.StreamingBody object at 0x7f8f60115ea0>",
         "ResponseMetadata": {
            "HTTPHeaders": {
                  "connection": "keep-alive",
                  "content-length": "3",
                  "content-type": "application/json",
                  "date": "Mon, 12 Feb 2024 19:56:46 GMT",
                  "x-amz-executed-version": "$LATEST",
                  "x-amzn-remapped-content-length": "0",
                  "x-amzn-requestid": "7f94c25d-fddc-467b-932d-f2fa459ea095",
                  "x-amzn-trace-id": "root=1-65ca77f3-1ea3eb4d46b8201f48aec17f;sampled=1;lineage=131737ad:0"
            },
            "HTTPStatusCode": 200,
            "RequestId": "7f94c25d-fddc-467b-932d-f2fa459ea095",
            "RetryAttempts": 0
         },
         "StatusCode": 200
      }
      [0]
   ```

1. Once that is successful, you can log into the admin with the super user you created earlier.

### Where is everything?

Coming Soon
