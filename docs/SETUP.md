# Setup Guide - Eco-Accounting SaaS

Complete guide to set up the Eco-Accounting SaaS platform for local development or production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [AWS Services Configuration](#aws-services-configuration)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)

## Prerequisites

### Required Software

- **Node.js**: Version 18.x or higher
- **Python**: Version 3.11 or higher
- **PostgreSQL**: Version 15.x or higher (for local development)
- **Git**: For version control
- **AWS CLI**: For AWS service interaction
- **pip**: Python package manager
- **npm**: Node package manager

### AWS Account Requirements

- Active AWS account (free tier eligible)
- AWS access credentials (Access Key ID and Secret Access Key)
- Enabled services:
  - AWS Bedrock (with Claude model access)
  - AWS Textract
  - AWS S3
  - AWS RDS (for production)
  - AWS Cognito (for authentication)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd eco-accounting-saas
```

### 2. Project Structure

```
eco-accounting-saas/
├── frontend/              # Next.js application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── public/           # Static assets
├── backend/              # Python FastAPI application
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   ├── lambda/           # Lambda handlers
│   └── main.py           # FastAPI app
├── data/                 # Emission factors data
│   └── emission-factors/
├── infrastructure/       # AWS infrastructure code
├── docs/                 # Documentation
└── README.md
```

## Backend Setup

### 1. Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Local Database

```bash
# Install PostgreSQL (if not installed)
# macOS:
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb eco_accounting

# Set up database schema
python -c "from models.database import init_db, get_database_url; \
from pydantic_settings import BaseSettings; \
class Config(BaseSettings): \
    DB_USER='postgres'; \
    DB_PASSWORD='postgres'; \
    DB_HOST='localhost'; \
    DB_PORT=5432; \
    DB_NAME='eco_accounting'; \
config = Config(); \
init_db(get_database_url(config))"
```

### 4. Configure Environment Variables

```bash
cp .env.example .env

# Edit .env file
nano .env
```

Update with your values:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# S3 Configuration
S3_BUCKET_NAME=eco-accounting-bills

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eco_accounting
DB_USER=postgres
DB_PASSWORD=postgres

# Bedrock Configuration
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Application Configuration
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### 5. Test Backend

```bash
# Run FastAPI development server
python main.py

# Server should start on http://localhost:8000
# Visit http://localhost:8000/docs for API documentation
```

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

```bash
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

Update with your values:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# AWS Configuration
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_S3_BUCKET=eco-accounting-bills

# AWS Cognito (optional for local dev)
NEXT_PUBLIC_COGNITO_USER_POOL_ID=your-user-pool-id
NEXT_PUBLIC_COGNITO_CLIENT_ID=your-client-id
NEXT_PUBLIC_COGNITO_DOMAIN=your-cognito-domain
```

### 4. Run Development Server

```bash
npm run dev

# Frontend should start on http://localhost:3000
```

## AWS Services Configuration

### 1. Configure AWS CLI

```bash
aws configure

# Enter:
# AWS Access Key ID: your-access-key
# AWS Secret Access Key: your-secret-key
# Default region: us-east-1
# Output format: json
```

### 2. Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://eco-accounting-bills-YOUR-NAME

# Configure CORS
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:3000"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"]
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket eco-accounting-bills-YOUR-NAME \
  --cors-configuration file://cors.json
```

### 3. Enable Bedrock Model Access

1. Log in to AWS Console
2. Navigate to AWS Bedrock
3. Go to "Model access" in the left sidebar
4. Click "Request model access"
5. Select "Anthropic Claude 3 Sonnet"
6. Submit request (usually approved instantly)

### 4. Test AWS Services

```bash
# Test S3 access
aws s3 ls

# Test Bedrock access (from Python)
python -c "
import boto3
bedrock = boto3.client('bedrock', region_name='us-east-1')
print(bedrock.list_foundation_models())
"

# Test Textract access
python -c "
import boto3
textract = boto3.client('textract', region_name='us-east-1')
print('Textract client initialized successfully')
"
```

## Running the Application

### Development Mode

#### Terminal 1 - Backend:

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py
```

Backend will run on http://localhost:8000

#### Terminal 2 - Frontend:

```bash
cd frontend
npm run dev
```

Frontend will run on http://localhost:3000

### Access the Application

1. Open browser to http://localhost:3000
2. You should see the landing page
3. Click "Dashboard" to access the main application
4. Try uploading a sample bill

## Testing

### Backend Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run E2E tests (if configured)
npm run test:e2e
```

### Manual Testing Checklist

- [ ] Health check endpoint responds: http://localhost:8000/health
- [ ] API documentation loads: http://localhost:8000/docs
- [ ] Frontend loads without errors
- [ ] Dashboard displays mock data
- [ ] File upload interface works
- [ ] Carbon calculator returns results

## Common Issues and Solutions

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Database connection fails
**Solution**: Check PostgreSQL is running and credentials are correct
```bash
brew services start postgresql@15
psql -U postgres -d eco_accounting
```

**Issue**: AWS credentials not found
**Solution**: Configure AWS CLI or set environment variables
```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

### Frontend Issues

**Issue**: `Module not found` errors
**Solution**: Delete node_modules and reinstall
```bash
rm -rf node_modules package-lock.json
npm install
```

**Issue**: API connection refused
**Solution**: Ensure backend is running on port 8000
```bash
curl http://localhost:8000/health
```

**Issue**: Environment variables not loading
**Solution**: Restart Next.js dev server after changing .env.local
```bash
# Stop server (Ctrl+C)
npm run dev
```

## Next Steps

1. **Production Deployment**: See [AWS_DEPLOYMENT_GUIDE.md](./AWS_DEPLOYMENT_GUIDE.md)
2. **Add Authentication**: Integrate AWS Cognito
3. **Database Migrations**: Set up Alembic for schema changes
4. **CI/CD Pipeline**: Configure GitHub Actions
5. **Monitoring**: Set up CloudWatch dashboards

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Textract Documentation](https://docs.aws.amazon.com/textract/)
- [GRI Standards](https://www.globalreporting.org/standards/)

## Support

For questions or issues:
- Check the documentation in the `docs/` directory
- Review API documentation at http://localhost:8000/docs
- Check AWS service status at https://status.aws.amazon.com/

---

**Ready to start?** Follow the steps above to get your local development environment running!
