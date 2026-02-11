# Quick Start Guide - Eco-Accounting SaaS

Get the application running in under 10 minutes!

## Prerequisites Check

```bash
# Check Node.js version (should be 18+)
node --version

# Check Python version (should be 3.11+)
python3 --version

# Check if AWS CLI is installed
aws --version
```

If any are missing, install them first (see [SETUP.md](./docs/SETUP.md)).

## 5-Minute Local Setup

### Step 1: Configure AWS Credentials

```bash
# Set up AWS credentials for Textract and Bedrock access
aws configure

# Enter your AWS Access Key ID and Secret Access Key
# Region: us-east-1
# Output format: json
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies (this may take 2-3 minutes)
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Start the backend server
python main.py
```

The backend should now be running on **http://localhost:8000**

✅ Test it: Open http://localhost:8000/health in your browser

### Step 3: Frontend Setup (in a new terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (this may take 2-3 minutes)
npm install

# Create environment file
cp .env.example .env.local

# Start the development server
npm run dev
```

The frontend should now be running on **http://localhost:3000**

✅ Test it: Open http://localhost:3000 in your browser

## Using the Application

### 1. Explore the Landing Page

- Open http://localhost:3000
- See the features overview
- Click "Get Started" or "Dashboard"

### 2. View the Dashboard

- Navigate to the Dashboard
- See mock emissions data and charts
- Explore different sections via the sidebar

### 3. Upload a Bill (Demo Mode)

- Click "Upload Bills" in the sidebar
- Try the drag-and-drop interface
- Select a PDF or image file
- (Note: Without AWS setup, this will work in demo mode)

### 4. Explore API Documentation

- Open http://localhost:8000/docs
- See all available endpoints
- Try the interactive API testing

## Next Steps

### For Demo/Presentation

You're all set! The application is running with:
- ✅ Beautiful UI with dashboard
- ✅ Bill upload interface
- ✅ Mock data visualization
- ✅ API documentation

### For Full Functionality

To enable AI processing and real calculations:

1. **Set up AWS S3**:
   ```bash
   aws s3 mb s3://eco-accounting-bills-YOUR-NAME
   ```

2. **Enable Bedrock Access**:
   - Go to AWS Console → Bedrock
   - Request access to Claude 3 Sonnet
   - Update `.env` with model ID

3. **Update Environment Variables**:
   ```bash
   # backend/.env
   S3_BUCKET_NAME=eco-accounting-bills-YOUR-NAME
   AWS_REGION=us-east-1
   ```

4. **Restart both servers**

### For Production Deployment

Follow the comprehensive guide:
- [AWS Deployment Guide](./docs/AWS_DEPLOYMENT_GUIDE.md)

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # You should see (venv) in your prompt
pip install -r requirements.txt
```

### Frontend shows errors

**Error**: `Module not found: Can't resolve 'lucide-react'`

**Fix**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use

**Error**: `Address already in use: 8000` or `3000`

**Fix**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### AWS credentials not working

**Error**: `Unable to locate credentials`

**Fix**:
```bash
# Reconfigure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

## Common Commands

```bash
# Backend
cd backend
source venv/bin/activate
python main.py

# Frontend
cd frontend
npm run dev

# Stop servers
# Press Ctrl+C in each terminal

# View logs
# Backend: Check terminal output
# Frontend: Check terminal output or browser console (F12)

# API docs
# http://localhost:8000/docs
```

## Project Structure at a Glance

```
eco-accounting-saas/
├── frontend/              ← Next.js app
│   ├── app/              ← Pages (landing, dashboard, etc.)
│   ├── components/       ← React components
│   └── lib/              ← API client, utilities
├── backend/              ← Python FastAPI
│   ├── main.py          ← Start here!
│   ├── models/          ← Database schemas
│   └── services/        ← Business logic (carbon calc, AWS)
├── data/                ← Emission factors (JSON)
└── docs/                ← Documentation
```

## Key Files to Understand

1. **backend/main.py**: All API endpoints
2. **backend/services/carbon_calculator.py**: Carbon emission calculations
3. **backend/services/aws_services.py**: Textract and Bedrock integration
4. **frontend/app/dashboard/page.tsx**: Main dashboard UI
5. **frontend/lib/api.ts**: Frontend API client
6. **data/emission-factors/**: Carbon calculation data sources

## Demo Flow for Presentation

1. **Show Landing Page**: http://localhost:3000
   - Highlight AI-powered features
   - Professional design

2. **Open Dashboard**: http://localhost:3000/dashboard
   - Show emissions overview
   - Demonstrate visualizations
   - Explain mock data

3. **Upload Interface**: Dashboard → Upload Bills
   - Show drag-and-drop
   - Explain AI processing flow
   - Discuss validation workflow

4. **API Documentation**: http://localhost:8000/docs
   - Show available endpoints
   - Demonstrate API testing
   - Explain integration possibilities

5. **Architecture Diagram**: Show docs/PROJECT_OVERVIEW.md
   - Explain AWS services
   - Discuss scalability
   - Highlight AI components

## Testing the Carbon Calculator

```python
# In backend directory, with venv activated
python

# Then in Python shell:
from services.carbon_calculator import get_calculator

calc = get_calculator()

# Test electricity calculation
result = calc.calculate_electricity_emissions(
    consumption_kwh=1000,
    country="UAE",
    region="Dubai"
)

print(result)
# Should show CO2e calculation with emission factor
```

## What's Working vs. What Needs AWS

### ✅ Working Without AWS
- Landing page and UI
- Dashboard with mock data
- Navigation and routing
- Form interactions
- Local carbon calculations
- API endpoints structure

### ⚠️ Needs AWS Setup
- Real bill upload to S3
- OCR text extraction (Textract)
- AI data parsing (Bedrock)
- Document storage
- Report PDF downloads

For a demo, the working parts are sufficient to show the concept!

## Getting Help

- **Setup Issues**: See [SETUP.md](./docs/SETUP.md)
- **AWS Deployment**: See [AWS_DEPLOYMENT_GUIDE.md](./docs/AWS_DEPLOYMENT_GUIDE.md)
- **Architecture Details**: See [PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md)
- **API Reference**: http://localhost:8000/docs

---

**You're all set!** The application should now be running locally. 🎉

For any questions or issues, check the documentation files in the `docs/` directory.
