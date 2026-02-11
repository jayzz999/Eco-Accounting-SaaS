# Eco-Accounting SaaS

AI-powered environmental reporting platform that automates ESG compliance, carbon footprint calculation, and GRI report generation for enterprises.

Built with **Next.js 16**, **FastAPI**, **AWS** (Lambda, Textract, Bedrock, Cognito, S3, RDS), and **Claude AI**.

---

## Features

- **AI-Powered Bill Processing** -- Upload utility bills and extract data automatically using AWS Textract OCR + Claude AI via Bedrock
- **Carbon Footprint Tracking** -- Real-time Scope 1/2/3 emission calculations with location-aware factors for 40+ countries
- **Multi-Framework Reporting** -- Generate PDF reports compliant with GRI 302/303/305, CDP, and TCFD standards
- **Compliance Monitoring** -- Automated checks against regional ESG regulations with alerts and recommendations
- **Carbon Credit Marketplace** -- Estimate offset needs, browse verified projects, and track credit purchases
- **Dashboard & Analytics** -- Interactive charts for emissions trends, consumption breakdowns, and compliance status

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16 (App Router), TypeScript, Tailwind CSS 4, Radix UI, Recharts, React Hook Form + Zod |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy 2, Pydantic 2, ReportLab (PDF generation) |
| **Database** | PostgreSQL (AWS RDS) |
| **AI/ML** | AWS Textract (OCR), AWS Bedrock (Claude 3 Sonnet) |
| **Auth** | AWS Cognito (JWT, OAuth) |
| **Storage** | AWS S3 (documents & reports) |
| **Infra** | AWS Lambda, API Gateway, CloudFormation, Amplify |

## Architecture

```
                    +------------------+
                    |   Next.js 16     |
                    |   Frontend       |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
       AWS Cognito                  AWS API Gateway
       (Auth/JWT)                          |
                                    AWS Lambda
                                    (FastAPI)
                              +------+------+
                              |      |      |
                           S3    Textract  Bedrock
                        (files)  (OCR)    (Claude AI)
                              |
                        PostgreSQL
                        (AWS RDS)
```

## Project Structure

```
eco-accounting-saas/
├── frontend/                     # Next.js 16 application
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   └── dashboard/
│   │       ├── page.tsx          # Dashboard home
│   │       ├── bills/            # Bill upload & management
│   │       ├── emissions/        # Emissions tracking
│   │       ├── reports/          # Report generation
│   │       ├── compliance/       # Compliance monitoring
│   │       ├── carbon-credits/   # Carbon credit marketplace
│   │       └── settings/         # Organization settings
│   ├── components/               # React components
│   └── lib/                      # API client & utilities
│
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # Application entry point (31 endpoints)
│   ├── models/
│   │   ├── database.py           # SQLAlchemy ORM models
│   │   └── schemas.py            # Pydantic validation schemas
│   └── services/
│       ├── aws_services.py       # S3, Textract, Bedrock integration
│       ├── carbon_calculator.py  # Emission calculation engine
│       ├── auth.py               # Cognito authentication
│       └── report_generator.py   # GRI PDF report generation
│
├── data/
│   └── emission-factors/         # Emission factor databases
│       ├── electricity.json      # 40+ country/region grid factors
│       ├── fuel.json             # 8 fuel types
│       ├── water.json            # Supply, wastewater, desalination
│       └── waste.json            # Landfill, incineration, composting, recycling
│
├── infrastructure/               # AWS IaC
│   ├── cloudformation/           # CloudFormation templates
│   └── scripts/                  # Deployment automation
│
└── docs/                         # Extended documentation
    ├── PROJECT_OVERVIEW.md
    ├── SETUP.md
    └── AWS_DEPLOYMENT_GUIDE.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (local or remote)
- AWS account (for Textract/Bedrock/S3 -- optional for local dev with mock data)

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit with your config
python main.py
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # Edit with your config
npm run dev
```

Frontend runs at http://localhost:3000.

## API Endpoints

**31 RESTful endpoints** organized by domain:

| Group | Endpoints | Description |
|---|---|---|
| **Bills** | `POST /api/bills/upload`, `GET /api/bills`, `GET /api/bills/{id}`, `POST /api/bills/{id}/validate`, `GET /api/bills/{id}/download` | Upload, list, validate, download bills |
| **Emissions** | `POST /api/emissions/calculate`, `GET /api/emissions`, `GET /api/emissions/summary`, `GET /api/emissions/trends` | Calculate & track emissions |
| **Reports** | `POST /api/reports/generate`, `GET /api/reports`, `GET /api/reports/{id}`, `GET /api/reports/{id}/download` | Generate & download GRI/CDP/TCFD reports |
| **Compliance** | `GET /api/compliance/status`, `POST /api/compliance/check` | Check ESG compliance |
| **Carbon Credits** | `POST /api/carbon-credits/estimate`, `GET /api/carbon-credits`, `POST /api/carbon-credits/purchase`, `GET /api/carbon-credits/{id}` | Estimate, browse, purchase credits |
| **Auth** | `POST /api/auth/signup`, `POST /api/auth/confirm`, `POST /api/auth/signin`, `POST /api/auth/refresh`, `POST /api/auth/forgot-password` | Cognito-backed authentication |
| **Dashboard** | `GET /api/dashboard/stats`, `GET /api/analytics/trends` | Aggregated statistics & trends |
| **System** | `GET /health`, `GET /docs` | Health check & Swagger UI |

## Emission Factors Database

Location-aware emission factors covering:

- **Electricity**: Grid factors for 40+ countries/regions (e.g., UAE 0.427, USA 0.386, India 0.708, France 0.056 kg CO2e/kWh)
- **Fuel**: 8 types -- natural gas, diesel, gasoline, LPG, heating oil, kerosene, coal, propane
- **Water**: Supply (0.344), wastewater treatment (0.708), desalination RO (1.82) kg CO2e/m3
- **Waste**: Landfill, incineration, composting, recycling with negative offsets for recycled materials

## Deployment

### Local Development

See the [Quick Start](#quick-start) section above or [QUICKSTART.md](./QUICKSTART.md) for a detailed walkthrough.

### AWS Production

Follow the [AWS Deployment Guide](./docs/AWS_DEPLOYMENT_GUIDE.md) for full production setup including:

- Lambda + API Gateway (serverless backend)
- RDS PostgreSQL
- S3 with CORS
- Cognito user pools
- Amplify frontend hosting
- CloudWatch monitoring

**Estimated cost**: Within AWS Free Tier for 12 months; ~$110/month after.

## Documentation

| Document | Description |
|---|---|
| [QUICKSTART.md](./QUICKSTART.md) | 5-minute local setup guide |
| [docs/SETUP.md](./docs/SETUP.md) | Detailed development setup |
| [docs/PROJECT_OVERVIEW.md](./docs/PROJECT_OVERVIEW.md) | Architecture, business case, market analysis |
| [docs/AWS_DEPLOYMENT_GUIDE.md](./docs/AWS_DEPLOYMENT_GUIDE.md) | Production AWS deployment |
| [DEMO_GUIDE.md](./DEMO_GUIDE.md) | Step-by-step demo walkthrough |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | Feature implementation details |

## License

Proprietary.
