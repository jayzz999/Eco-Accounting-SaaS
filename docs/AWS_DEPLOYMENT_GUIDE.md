# AWS Deployment Guide - Eco-Accounting SaaS

This guide walks you through deploying the complete Eco-Accounting SaaS platform on AWS infrastructure using your free tier account.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                               │
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │  CloudFront  │────────▶│   Amplify    │  (Frontend)        │
│  └──────────────┘         │   Hosting    │                    │
│                           └──────────────┘                    │
│                                                                 │
│  ┌──────────────┐         ┌──────────────┐                    │
│  │  API Gateway │────────▶│    Lambda    │  (Backend)         │
│  └──────────────┘         │  Functions   │                    │
│                           └──────────────┘                    │
│                                    │                            │
│         ┌──────────────────────────┼──────────────────┐        │
│         │                          │                  │        │
│    ┌────▼────┐              ┌─────▼─────┐      ┌────▼────┐   │
│    │   RDS   │              │  Textract │      │ Bedrock │   │
│    │Postgres │              └───────────┘      │(Claude) │   │
│    └─────────┘                                 └─────────┘   │
│                                                                 │
│    ┌──────────┐              ┌───────────┐                    │
│    │    S3    │              │  Cognito  │                    │
│    │  Bills   │              │   Auth    │                    │
│    └──────────┘              └───────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

1. AWS Account (Free Tier eligible)
2. AWS CLI installed and configured
3. Node.js 18+ and Python 3.11+
4. Basic knowledge of AWS services

## Step 1: Configure AWS CLI

```bash
# Install AWS CLI if not already installed
# macOS
brew install awscli

# Configure with your credentials
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (us-east-1 recommended)
# - Output format (json)
```

## Step 2: Create S3 Bucket for Bills

```bash
# Create S3 bucket
aws s3 mb s3://eco-accounting-bills-YOUR-NAME --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket eco-accounting-bills-YOUR-NAME \
  --versioning-configuration Status=Enabled

# Configure CORS for frontend access
cat > cors-config.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket eco-accounting-bills-YOUR-NAME \
  --cors-configuration file://cors-config.json
```

## Step 3: Set Up RDS PostgreSQL Database

### Using AWS Console:

1. Go to RDS Dashboard
2. Click "Create database"
3. Choose:
   - **Engine**: PostgreSQL
   - **Version**: PostgreSQL 15.x
   - **Template**: Free tier
   - **DB instance identifier**: eco-accounting-db
   - **Master username**: postgres
   - **Master password**: (create a strong password)
   - **DB instance class**: db.t3.micro (free tier eligible)
   - **Storage**: 20 GB
   - **Public access**: Yes (for initial setup, secure later)
   - **VPC security group**: Create new, allow PostgreSQL (5432)

4. Wait for database to be created (5-10 minutes)
5. Note the endpoint URL

### Initialize Database:

```bash
# Install psql client if not installed
brew install postgresql

# Connect to RDS
psql -h YOUR-RDS-ENDPOINT.rds.amazonaws.com -U postgres -d postgres

# Run database initialization
# You'll need to create tables based on backend/models/database.py
```

## Step 4: Set Up AWS Cognito (User Authentication)

### Using AWS Console:

1. Go to AWS Cognito
2. Click "Create user pool"
3. Configure:
   - **Cognito user pool sign-in options**: Email
   - **Password policy**: Cognito defaults
   - **MFA**: Optional (None for demo)
   - **User account recovery**: Email only
   - **Required attributes**: email, name
   - **Email provider**: Amazon SES
   - **User pool name**: eco-accounting-users
   - **App client name**: eco-accounting-web-client
   - **Authentication flows**: ALLOW_USER_PASSWORD_AUTH

4. Note:
   - User Pool ID
   - App Client ID
   - Cognito Domain

## Step 5: Configure IAM Roles for Lambda

Create an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::eco-accounting-bills-YOUR-NAME/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "textract:AnalyzeDocument",
        "textract:DetectDocumentText"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 6: Enable AWS Bedrock Model Access

1. Go to AWS Bedrock console
2. Navigate to "Model access"
3. Click "Manage model access"
4. Select:
   - Anthropic Claude 3 Sonnet
   - Anthropic Claude 3 Haiku (optional, for cost savings)
5. Request access (usually instant approval)

## Step 7: Deploy Backend (Lambda + API Gateway)

### Package Lambda Function:

```bash
cd backend

# Create deployment package
mkdir -p lambda_package
pip install -r requirements.txt -t lambda_package/
cp -r *.py lambda_package/
cp -r models/ services/ lambda_package/

cd lambda_package
zip -r ../lambda_function.zip .
cd ..
```

### Deploy Lambda:

```bash
# Create Lambda function
aws lambda create-function \
  --function-name eco-accounting-api \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR-ACCOUNT-ID:role/lambda-execution-role \
  --handler main.handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{
    S3_BUCKET_NAME=eco-accounting-bills-YOUR-NAME,
    DB_HOST=YOUR-RDS-ENDPOINT,
    DB_NAME=eco_accounting,
    DB_USER=postgres,
    DB_PASSWORD=YOUR-PASSWORD,
    AWS_REGION=us-east-1
  }"
```

### Create API Gateway:

1. Go to API Gateway console
2. Create new "HTTP API"
3. Add integration:
   - Type: Lambda
   - Function: eco-accounting-api
4. Add routes:
   - ANY /{proxy+}
5. Deploy to stage "prod"
6. Note the API endpoint URL

## Step 8: Deploy Frontend (AWS Amplify)

### Using AWS Amplify Console:

1. Go to AWS Amplify console
2. Click "New app" > "Host web app"
3. Choose:
   - **Repository**: Connect your GitHub (or upload code)
   - **Branch**: main
   - **Framework**: Next.js
   - **Build settings**: Auto-detected

4. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR-API-GATEWAY-URL
   NEXT_PUBLIC_AWS_REGION=us-east-1
   NEXT_PUBLIC_S3_BUCKET=eco-accounting-bills-YOUR-NAME
   NEXT_PUBLIC_COGNITO_USER_POOL_ID=your-user-pool-id
   NEXT_PUBLIC_COGNITO_CLIENT_ID=your-client-id
   ```

5. Deploy (takes 5-10 minutes)

### Alternative: Manual Deployment

```bash
cd frontend

# Create production build
npm run build

# Deploy to S3 + CloudFront
aws s3 sync out/ s3://eco-accounting-frontend-YOUR-NAME --delete

# Configure CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name eco-accounting-frontend-YOUR-NAME.s3.amazonaws.com \
  --default-root-object index.html
```

## Step 9: Configure Environment Variables

### Backend (.env):

```bash
cd backend
cp .env.example .env

# Edit .env with your values
nano .env
```

Update with:
- Your RDS endpoint
- S3 bucket name
- AWS credentials (if running locally)

### Frontend (.env.local):

```bash
cd frontend
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

Update with:
- API Gateway URL
- Cognito details
- S3 bucket name

## Step 10: Test the Deployment

### Test Backend:

```bash
# Health check
curl https://YOUR-API-GATEWAY-URL/health

# Should return:
# {"status":"healthy","timestamp":"..."}
```

### Test Frontend:

1. Visit your Amplify URL or CloudFront distribution
2. Navigate to Dashboard
3. Try uploading a sample bill

## Cost Optimization for Free Tier

### Services that Stay Free:
- **S3**: First 5GB storage, 20,000 GET requests, 2,000 PUT requests/month
- **Lambda**: 1M requests, 400,000 GB-seconds compute/month
- **RDS**: 750 hours of db.t3.micro, 20GB storage/month (12 months only)
- **CloudFront**: 1TB data transfer out, 10M HTTP requests/month
- **API Gateway**: 1M API calls/month (12 months only)

### Services with Pay-As-You-Go:
- **Textract**: $1.50 per 1,000 pages (FORMS/TABLES)
- **Bedrock Claude**: ~$3 per 1M input tokens, ~$15 per 1M output tokens

### Tips to Stay Within Free Tier:
1. Use RDS only during testing (stop when not in use)
2. Implement bill caching to reduce Textract calls
3. Use Claude Haiku for simple extractions (cheaper)
4. Set up billing alerts at $5, $10

## Step 11: Set Up Monitoring

### CloudWatch Alarms:

```bash
# Lambda errors alarm
aws cloudwatch put-metric-alarm \
  --alarm-name eco-accounting-lambda-errors \
  --alarm-description "Alert on Lambda errors" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold

# Budget alert
aws budgets create-budget \
  --account-id YOUR-ACCOUNT-ID \
  --budget file://budget.json
```

## Step 12: Security Best Practices

1. **Enable MFA** on AWS root account
2. **Use IAM roles** instead of access keys where possible
3. **Restrict S3 bucket** access with bucket policies
4. **Enable RDS encryption** at rest
5. **Use AWS Secrets Manager** for sensitive credentials
6. **Enable CloudTrail** for audit logging
7. **Set up WAF** on API Gateway to prevent abuse

## Troubleshooting

### Lambda Function Times Out:
- Increase timeout in Lambda configuration
- Check RDS security group allows Lambda VPC access
- Verify database connection string

### Textract Fails:
- Verify IAM role has Textract permissions
- Check file is valid PDF/image
- Ensure file is under 5MB for synchronous calls

### Frontend Can't Reach API:
- Check CORS configuration on API Gateway
- Verify API Gateway URL in frontend .env
- Check CloudWatch logs for errors

### RDS Connection Fails:
- Verify security group allows inbound on port 5432
- Check RDS publicly accessible setting
- Confirm endpoint and credentials

## Next Steps

1. **Set up CI/CD**: Use GitHub Actions to auto-deploy on push
2. **Add more features**: Implement remaining endpoints
3. **Improve error handling**: Add retry logic and better error messages
4. **Add tests**: Unit tests for backend, E2E tests for frontend
5. **Performance optimization**: Add caching layer (ElastiCache)
6. **Scale**: Move to Lambda@Edge for global distribution

## Support

For issues or questions:
- AWS Support (free tier includes basic support)
- AWS Documentation: https://docs.aws.amazon.com
- Project GitHub Issues

---

**Congratulations!** Your Eco-Accounting SaaS is now deployed on AWS. 🎉
