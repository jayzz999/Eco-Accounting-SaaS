"""
Main FastAPI application for Eco-Accounting SaaS
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum
from typing import List, Optional
import os
from datetime import datetime, timedelta

from models.schemas import (
    BillUploadRequest,
    BillResponse,
    EmissionResponse,
    ReportGenerationRequest,
    ReportResponse,
    DashboardStats,
    ComplianceStatusResponse,
    CarbonCreditResponse,
    SuccessResponse,
    ErrorResponse,
)
from services.carbon_calculator import get_calculator
from services.auth import get_cognito_auth, get_current_user, get_current_user_optional, CognitoAuth
from models.database import init_db, get_db_session, Organization, Bill, Emission
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# Initialize FastAPI app
app = FastAPI(
    title="Eco-Accounting SaaS API",
    description="AI-powered environmental reporting and carbon footprint tracking",
    version="1.0.0",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
        # Continue running even if DB init fails (for demo purposes)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Eco-Accounting SaaS API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Authentication request/response models
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class ConfirmSignUpRequest(BaseModel):
    email: EmailStr
    confirmation_code: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ConfirmForgotPasswordRequest(BaseModel):
    email: EmailStr
    confirmation_code: str
    new_password: str


# Authentication endpoints
@app.post("/api/auth/signup")
async def signup(request: SignUpRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Register a new user"""
    return auth.sign_up(request.email, request.password, request.full_name)


@app.post("/api/auth/confirm-signup")
async def confirm_signup(request: ConfirmSignUpRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Confirm user registration with verification code"""
    return auth.confirm_sign_up(request.email, request.confirmation_code)


@app.post("/api/auth/signin")
async def signin(request: SignInRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Sign in and get JWT tokens"""
    return auth.sign_in(request.email, request.password)


@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshTokenRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Refresh access token"""
    return auth.refresh_token(request.refresh_token)


@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@app.post("/api/auth/signout")
async def signout(current_user: dict = Depends(get_current_user), auth: CognitoAuth = Depends(get_cognito_auth)):
    """Sign out current user"""
    # Extract token from current_user (it's stored in token_claims)
    # For now, return success message
    return {"message": "Signed out successfully"}


@app.post("/api/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Request password reset"""
    return auth.forgot_password(request.email)


@app.post("/api/auth/confirm-forgot-password")
async def confirm_forgot_password(request: ConfirmForgotPasswordRequest, auth: CognitoAuth = Depends(get_cognito_auth)):
    """Confirm password reset with code"""
    return auth.confirm_forgot_password(request.email, request.confirmation_code, request.new_password)


# Bills endpoints
@app.post("/api/bills/upload", response_model=SuccessResponse)
async def upload_bill(
    file: UploadFile = File(...),
    bill_type: Optional[str] = Form(None),
    db: Session = Depends(get_db_session)
):
    """
    Upload a bill for processing with AI extraction
    """
    try:
        from services.aws_services import get_s3_service, get_bedrock_service
        from datetime import datetime as dt

        # Read file content
        file_content = await file.read()

        # Generate S3 key
        timestamp = dt.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"bills/{timestamp}_{file.filename}"

        # Upload to S3
        s3_service = get_s3_service()
        s3_url = s3_service.upload_file(
            file_content=file_content,
            key=s3_key,
            metadata={"bill_type": bill_type or "unknown"}
        )

        # Create bill record in database (initial)
        from models.database import BillStatus, BillType
        bill = Bill(
            organization_id=1,  # Default org for demo
            file_name=file.filename,
            file_path=s3_url,
            bill_type=BillType(bill_type) if bill_type else BillType.OTHER,
            status=BillStatus.PROCESSING
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)

        # Extract data using Claude Vision (async processing)
        bedrock_service = get_bedrock_service()
        extracted_data = bedrock_service.extract_bill_data_from_image(
            file_content,
            bill_type=bill_type
        )

        # Update bill with extracted data
        bill.extracted_data = extracted_data
        bill.status = BillStatus.EXTRACTED

        # Calculate emissions from extracted data
        if extracted_data.get('consumption_amount') and extracted_data.get('bill_type'):
            calculator = get_calculator()
            bill_type_extracted = extracted_data['bill_type']

            if bill_type_extracted == 'electricity':
                emission_result = calculator.calculate_electricity_emissions(
                    consumption_kwh=float(extracted_data['consumption_amount']),
                    country="UAE",  # Default for demo
                    region="Dubai"
                )

                # Store emission record
                from models.database import BillType as BT
                emission = Emission(
                    bill_id=bill.id,
                    organization_id=1,
                    source_type=BT.ELECTRICITY,
                    category="Scope 2",
                    consumption_amount=emission_result['consumption_amount'],
                    consumption_unit="kWh",
                    emission_factor=emission_result['emission_factor'],
                    total_co2e=emission_result['total_co2e'],
                    period_start=dt.strptime(extracted_data.get('billing_period_start', dt.utcnow().isoformat()[:10]), "%Y-%m-%d") if extracted_data.get('billing_period_start') else dt.utcnow(),
                    period_end=dt.strptime(extracted_data.get('billing_period_end', dt.utcnow().isoformat()[:10]), "%Y-%m-%d") if extracted_data.get('billing_period_end') else dt.utcnow()
                )
                db.add(emission)
                bill.status = BillStatus.VALIDATED

        db.commit()
        db.refresh(bill)

        return SuccessResponse(
            success=True,
            message="Bill uploaded and processed successfully",
            data={
                "bill_id": bill.id,
                "file_name": file.filename,
                "bill_type": bill_type,
                "status": bill.status.value,
                "extracted_data": extracted_data
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bills", response_model=List[BillResponse])
async def list_bills(
    skip: int = 0,
    limit: int = 20,
    bill_type: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    List all bills for an organization
    """
    query = db.query(Bill).filter(Bill.organization_id == 1)  # Default org

    if bill_type:
        from models.database import BillType
        query = query.filter(Bill.bill_type == BillType(bill_type))

    bills = query.order_by(Bill.created_at.desc()).offset(skip).limit(limit).all()

    return [
        BillResponse(
            id=bill.id,
            organization_id=bill.organization_id,
            file_name=bill.file_name,
            bill_type=bill.bill_type.value,
            status=bill.status.value,
            extracted_data=bill.extracted_data or {},
            created_at=bill.created_at,
            processed_at=bill.created_at
        )
        for bill in bills
    ]


@app.get("/api/bills/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: int):
    """
    Get bill details by ID
    """
    # TODO: Implement database query
    raise HTTPException(status_code=404, detail="Bill not found")


@app.post("/api/bills/{bill_id}/validate", response_model=SuccessResponse)
async def validate_bill(bill_id: int, validated_data: dict):
    """
    Validate and confirm extracted bill data
    """
    # TODO: Implement validation logic
    return SuccessResponse(
        success=True,
        message="Bill validated successfully",
        data={"bill_id": bill_id}
    )


@app.get("/api/bills/{bill_id}/download")
async def download_bill(bill_id: int, db: Session = Depends(get_db_session)):
    """
    Download bill PDF from S3
    """
    from fastapi.responses import Response
    from services.aws_services import get_s3_service

    # Get bill from database
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Extract S3 key from file_path
    s3_service = get_s3_service()
    bucket_name = os.getenv('S3_BUCKET_NAME')

    # file_path format: s3://bucket-name/key
    s3_key = bill.file_path.replace(f"s3://{bucket_name}/", "")

    # Download from S3
    try:
        pdf_bytes = s3_service.download_file(s3_key)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={bill.file_name}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download bill: {str(e)}")


# Emissions endpoints
@app.post("/api/emissions/calculate", response_model=EmissionResponse)
async def calculate_emissions(
    bill_id: int,
    consumption_amount: float,
    consumption_unit: str,
    bill_type: str,
    country: str = "global",
    region: Optional[str] = None
):
    """
    Calculate carbon emissions for a bill
    """
    try:
        calculator = get_calculator()

        # Calculate emissions
        result = calculator.calculate_emissions(
            bill_type=bill_type,
            consumption_amount=consumption_amount,
            consumption_unit=consumption_unit,
            country=country,
            region=region
        )

        # TODO: Store emission record in database

        return EmissionResponse(
            id=0,  # TODO: Get from database
            organization_id=1,  # TODO: Get from auth
            bill_id=bill_id,
            category=result["category"],
            source_type=result["source_type"],
            consumption_amount=result["consumption_amount"],
            consumption_unit=result["consumption_unit"],
            emission_factor=result["emission_factor"],
            total_co2e=result["total_co2e"],
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/emissions")
async def list_emissions(
    skip: int = 0,
    limit: int = 50,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db_session)
):
    """
    List emissions for an organization
    """
    org_id = 1  # Default organization

    query = db.query(Emission).filter(Emission.organization_id == org_id)

    if start_date:
        query = query.filter(Emission.period_start >= start_date)
    if end_date:
        query = query.filter(Emission.period_end <= end_date)

    emissions = query.order_by(Emission.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": e.id,
            "bill_id": e.bill_id,
            "organization_id": e.organization_id,
            "category": e.category,
            "source_type": e.source_type.value if e.source_type else None,
            "consumption_amount": e.consumption_amount,
            "consumption_unit": e.consumption_unit,
            "emission_factor": e.emission_factor,
            "total_co2e": e.total_co2e,
            "period_start": e.period_start.isoformat() if e.period_start else None,
            "period_end": e.period_end.isoformat() if e.period_end else None,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in emissions
    ]


@app.get("/api/emissions/summary")
async def get_emissions_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Get emissions summary and statistics
    """
    # TODO: Implement aggregation logic
    return {
        "total_emissions": 0,
        "by_category": {},
        "by_source": {},
        "trend": "stable"
    }


# Reports endpoints
@app.post("/api/reports/generate")
async def generate_report(request: ReportGenerationRequest, db: Session = Depends(get_db_session)):
    """
    Generate an environmental report (GRI, CDP, TCFD)
    """
    try:
        from services.report_generator import get_report_generator
        from services.aws_services import get_s3_service
        from models.database import Report, ReportType as RT
        from datetime import datetime as dt

        org_id = 1  # Default organization

        # Get organization data
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get emissions data for the period
        emissions = db.query(Emission).filter(
            Emission.organization_id == org_id,
            Emission.period_start >= request.period_start,
            Emission.period_end <= request.period_end
        ).all()

        if not emissions:
            raise HTTPException(status_code=400, detail="No emissions data found for the specified period")

        # Prepare organization data
        org_data = {
            "name": org.name,
            "industry": org.industry,
            "country": org.country,
            "region": org.region
        }

        # Prepare emissions data
        emissions_data = [
            {
                "source_type": e.source_type.value if e.source_type else "unknown",
                "category": e.category,
                "consumption_amount": e.consumption_amount,
                "consumption_unit": e.consumption_unit,
                "emission_factor": e.emission_factor,
                "total_co2e": e.total_co2e,
                "period_start": e.period_start,
                "period_end": e.period_end
            }
            for e in emissions
        ]

        # Generate report PDF
        generator = get_report_generator()

        if request.report_type == "GRI-305":
            pdf_bytes = generator.generate_gri_305_report(
                org_data, emissions_data, request.period_start, request.period_end
            )
        else:
            raise HTTPException(status_code=400, detail=f"Report type {request.report_type} not yet supported")

        # Upload to S3
        s3_service = get_s3_service()
        timestamp = dt.utcnow().strftime("%Y%m%d_%H%M%S")
        s3_key = f"reports/{org_id}/{request.report_type}_{timestamp}.pdf"
        s3_url = s3_service.upload_file(
            file_content=pdf_bytes,
            key=s3_key,
            metadata={
                "report_type": request.report_type,
                "organization_id": str(org_id)
            }
        )

        # Prepare report data summary
        report_data = {
            "total_emissions": sum(e["total_co2e"] for e in emissions_data),
            "emissions_count": len(emissions_data),
            "emissions_by_scope": {
                "scope_1": sum(e["total_co2e"] for e in emissions_data if e.get("category") == "Scope 1"),
                "scope_2": sum(e["total_co2e"] for e in emissions_data if e.get("category") == "Scope 2"),
                "scope_3": sum(e["total_co2e"] for e in emissions_data if e.get("category") == "Scope 3")
            },
            "period": {
                "start": request.period_start.isoformat(),
                "end": request.period_end.isoformat()
            },
            "organization": org_data["name"]
        }

        # Store report record in database
        report = Report(
            organization_id=org_id,
            report_type=RT(request.report_type),
            title=f"{request.report_type} Report - {request.period_start.strftime('%Y-%m-%d')} to {request.period_end.strftime('%Y-%m-%d')}",
            description=request.description or f"Auto-generated {request.report_type} compliance report",
            report_data=report_data,
            file_path=s3_url,
            period_start=request.period_start,
            period_end=request.period_end,
            status="completed"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return {
            "id": report.id,
            "organization_id": report.organization_id,
            "report_type": report.report_type.value,
            "title": report.title,
            "file_path": report.file_path,
            "period_start": report.period_start.isoformat(),
            "period_end": report.period_end.isoformat(),
            "status": report.status,
            "created_at": report.created_at.isoformat()
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports")
async def list_reports(skip: int = 0, limit: int = 20, db: Session = Depends(get_db_session)):
    """
    List all reports for an organization
    """
    from models.database import Report
    org_id = 1  # Default organization

    reports = db.query(Report).filter(Report.organization_id == org_id)\
        .order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": r.id,
            "organization_id": r.organization_id,
            "report_type": r.report_type.value,
            "title": r.title,
            "file_path": r.file_path,
            "period_start": r.period_start.isoformat() if r.period_start else None,
            "period_end": r.period_end.isoformat() if r.period_end else None,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in reports
    ]


@app.get("/api/reports/{report_id}")
async def get_report(report_id: int, db: Session = Depends(get_db_session)):
    """
    Get report details by ID
    """
    from models.database import Report
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "organization_id": report.organization_id,
        "report_type": report.report_type.value,
        "title": report.title,
        "file_path": report.file_path,
        "period_start": report.period_start.isoformat() if report.period_start else None,
        "period_end": report.period_end.isoformat() if report.period_end else None,
        "status": report.status,
        "created_at": report.created_at.isoformat() if report.created_at else None
    }


@app.get("/api/reports/{report_id}/download")
async def download_report(report_id: int, db: Session = Depends(get_db_session)):
    """
    Download report PDF
    """
    from models.database import Report
    from services.aws_services import get_s3_service
    from fastapi.responses import Response

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Extract S3 key from file_path (s3://bucket/key format)
    s3_key = report.file_path.replace(f"s3://{os.getenv('S3_BUCKET_NAME', 'eco-accounting-bills-jayanthmuthina-2024')}/", "")

    try:
        s3_service = get_s3_service()
        pdf_bytes = s3_service.download_file(s3_key)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={report.title.replace(' ', '_')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")


# Dashboard endpoints
@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db_session)):
    """
    Get dashboard statistics and overview from database
    """
    from sqlalchemy import func, extract
    from datetime import datetime as dt

    org_id = 1  # Default organization

    # Total bills
    total_bills = db.query(func.count(Bill.id)).filter(Bill.organization_id == org_id).scalar() or 0

    # Total emissions
    total_emissions_result = db.query(func.sum(Emission.total_co2e)).filter(Emission.organization_id == org_id).scalar()
    total_emissions = float(total_emissions_result) if total_emissions_result else 0

    # Current month emissions
    current_month = dt.utcnow().month
    current_year = dt.utcnow().year
    current_month_emissions_result = db.query(func.sum(Emission.total_co2e)).filter(
        Emission.organization_id == org_id,
        extract('month', Emission.period_start) == current_month,
        extract('year', Emission.period_start) == current_year
    ).scalar()
    current_month_emissions = float(current_month_emissions_result) if current_month_emissions_result else 0

    # Previous month emissions
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    previous_month_emissions_result = db.query(func.sum(Emission.total_co2e)).filter(
        Emission.organization_id == org_id,
        extract('month', Emission.period_start) == prev_month,
        extract('year', Emission.period_start) == prev_year
    ).scalar()
    previous_month_emissions = float(previous_month_emissions_result) if previous_month_emissions_result else 0

    # Emissions change percentage
    if previous_month_emissions > 0:
        emissions_change = ((current_month_emissions - previous_month_emissions) / previous_month_emissions) * 100
    else:
        emissions_change = 0

    # Recent bills
    recent_bills_query = db.query(Bill).filter(Bill.organization_id == org_id).order_by(Bill.created_at.desc()).limit(5).all()
    recent_bills = [
        BillResponse(
            id=bill.id,
            organization_id=bill.organization_id,
            file_name=bill.file_name,
            bill_type=bill.bill_type.value,
            status=bill.status.value,
            extracted_data=bill.extracted_data or {},
            created_at=bill.created_at,
            processed_at=bill.created_at
        )
        for bill in recent_bills_query
    ]

    # Emissions by month (last 6 months)
    emissions_by_month = []
    for i in range(5, -1, -1):
        month_date = dt(current_year, current_month, 1) - timedelta(days=30 * i)
        month_emissions = db.query(func.sum(Emission.total_co2e)).filter(
            Emission.organization_id == org_id,
            extract('month', Emission.period_start) == month_date.month,
            extract('year', Emission.period_start) == month_date.year
        ).scalar()
        emissions_by_month.append({
            "month": month_date.strftime("%b %Y"),
            "emissions": float(month_emissions) if month_emissions else 0
        })

    return DashboardStats(
        total_bills=total_bills,
        total_emissions=total_emissions,
        current_month_emissions=current_month_emissions,
        previous_month_emissions=previous_month_emissions,
        emissions_change=emissions_change,
        compliance_status="compliant" if total_emissions < 100000 else "non_compliant",
        recent_bills=recent_bills,
        emissions_by_month=emissions_by_month
    )


# Compliance endpoints
@app.get("/api/compliance/status")
async def get_compliance_status(db: Session = Depends(get_db_session)):
    """
    Get current compliance status with automated checks
    """
    from sqlalchemy import func
    org_id = 1  # Default organization

    # Get total emissions
    total_emissions = db.query(func.sum(Emission.total_co2e)).filter(
        Emission.organization_id == org_id
    ).scalar() or 0

    # Get bills count
    bills_count = db.query(func.count(Bill.id)).filter(
        Bill.organization_id == org_id
    ).scalar() or 0

    # Define compliance rules and check them
    checks = []

    # GRI Standards - Check if we have emission data
    checks.append({
        "rule_name": "GRI 305 - Emissions Disclosure",
        "regulation": "GRI Standards",
        "is_compliant": total_emissions > 0 and bills_count > 0,
        "details": f"Organization has {bills_count} bills processed and {total_emissions:.2f} kg CO2e calculated",
        "checked_at": datetime.utcnow().isoformat()
    })

    # ISO 14064 - Greenhouse gas accounting
    has_scope2 = db.query(Emission).filter(
        Emission.organization_id == org_id,
        Emission.category == "Scope 2"
    ).first() is not None

    checks.append({
        "rule_name": "ISO 14064 - GHG Accounting",
        "regulation": "ISO 14064",
        "is_compliant": has_scope2,
        "details": "Scope 2 emissions are being tracked" if has_scope2 else "Need to track Scope 2 emissions",
        "checked_at": datetime.utcnow().isoformat()
    })

    # CDP Requirements - Check data completeness
    recent_bills = db.query(Bill).filter(
        Bill.organization_id == org_id,
        Bill.status == "validated"
    ).count()

    checks.append({
        "rule_name": "CDP - Data Completeness",
        "regulation": "Carbon Disclosure Project",
        "is_compliant": recent_bills >= 3,
        "details": f"{recent_bills} validated bills (minimum 3 required for quarterly reporting)",
        "checked_at": datetime.utcnow().isoformat()
    })

    # UAE Carbon Regulations - Emissions threshold
    emissions_tonnes = total_emissions / 1000
    checks.append({
        "rule_name": "UAE - Emissions Reporting Threshold",
        "regulation": "UAE Environmental",
        "is_compliant": True,  # Always compliant for demo
        "details": f"Current emissions: {emissions_tonnes:.3f} tonnes CO2e (below 100t threshold)",
        "checked_at": datetime.utcnow().isoformat()
    })

    # Calculate overall compliance
    compliant_checks = sum(1 for c in checks if c["is_compliant"])
    overall_compliant = compliant_checks == len(checks)

    return {
        "overall_compliant": overall_compliant,
        "checks": checks,
        "checked_at": datetime.utcnow().isoformat(),
        "summary": {
            "total_checks": len(checks),
            "compliant": compliant_checks,
            "non_compliant": len(checks) - compliant_checks
        }
    }


# Carbon credits endpoints
@app.post("/api/carbon-credits/estimate")
async def estimate_carbon_credits(
    period_start: datetime,
    period_end: datetime,
    project_type: str,
    offset_percentage: int = 50,
    db: Session = Depends(get_db_session)
):
    """
    Estimate potential carbon credits needed for offsetting emissions
    """
    org_id = 1  # TODO: Get from authentication

    # Query emissions for the specified period
    emissions = db.query(Emission).filter(
        Emission.organization_id == org_id,
        Emission.period_start >= period_start,
        Emission.period_end <= period_end
    ).all()

    if not emissions:
        raise HTTPException(status_code=404, detail="No emissions found for the specified period")

    # Calculate total emissions in kg CO2e
    total_co2e_kg = sum(e.total_co2e for e in emissions)

    # Convert to tonnes
    total_co2e_tonnes = total_co2e_kg / 1000

    # Calculate credits needed based on offset percentage
    credits_needed_tonnes = total_co2e_tonnes * (offset_percentage / 100)

    # Project pricing (mock marketplace data - in real implementation, fetch from carbon marketplace API)
    project_prices = {
        "renewable_energy": 25,  # USD per tonne CO2e
        "nature_based": 30,
        "industrial": 22,
        "forestry": 28,
        "carbon_capture": 35
    }

    price_per_tonne = project_prices.get(project_type, 25)
    estimated_cost_usd = credits_needed_tonnes * price_per_tonne

    # Calculate breakdown by emission source
    source_breakdown = {}
    for emission in emissions:
        source = emission.source_type.value if emission.source_type else "unknown"
        if source not in source_breakdown:
            source_breakdown[source] = 0
        source_breakdown[source] += emission.total_co2e

    return {
        "total_emissions_kg": round(total_co2e_kg, 2),
        "total_emissions_tonnes": round(total_co2e_tonnes, 4),
        "offset_percentage": offset_percentage,
        "credits_needed_tonnes": round(credits_needed_tonnes, 4),
        "project_type": project_type,
        "price_per_tonne_usd": price_per_tonne,
        "estimated_cost_usd": round(estimated_cost_usd, 2),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "emission_sources": source_breakdown,
        "available_projects": [
            {
                "type": "renewable_energy",
                "name": "UAE Solar Energy Project",
                "location": "Dubai, UAE",
                "price_per_tonne": 25,
                "certification": "Gold Standard"
            },
            {
                "type": "nature_based",
                "name": "Mangrove Restoration",
                "location": "Abu Dhabi, UAE",
                "price_per_tonne": 30,
                "certification": "Verified Carbon Standard"
            },
            {
                "type": "renewable_energy",
                "name": "Wind Energy Farm",
                "location": "Oman",
                "price_per_tonne": 22,
                "certification": "Gold Standard"
            }
        ]
    }


@app.get("/api/carbon-credits")
async def list_carbon_credits(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db_session)
):
    """
    List carbon credit purchase records
    """
    org_id = 1  # TODO: Get from authentication

    # Query carbon credits from database
    credits = db.query(CarbonCredit).filter(
        CarbonCredit.organization_id == org_id
    ).order_by(CarbonCredit.created_at.desc()).offset(skip).limit(limit).all()

    total = db.query(func.count(CarbonCredit.id)).filter(
        CarbonCredit.organization_id == org_id
    ).scalar()

    return {
        "items": [{
            "id": c.id,
            "project_name": c.project_name,
            "project_type": c.project_type,
            "credits_amount": c.credits_amount,
            "price_per_credit": c.price_per_credit,
            "total_cost": c.total_cost,
            "purchase_date": c.purchase_date.isoformat() if c.purchase_date else None,
            "status": c.status,
            "certificate_url": c.certificate_url,
            "retirement_date": c.retirement_date.isoformat() if c.retirement_date else None,
            "created_at": c.created_at.isoformat()
        } for c in credits],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@app.post("/api/carbon-credits/purchase")
async def purchase_carbon_credits(
    project_name: str,
    project_type: str,
    credits_amount: float,
    price_per_credit: float,
    db: Session = Depends(get_db_session)
):
    """
    Record a carbon credit purchase
    """
    org_id = 1  # TODO: Get from authentication

    total_cost = credits_amount * price_per_credit

    # Create carbon credit record
    credit = CarbonCredit(
        organization_id=org_id,
        project_name=project_name,
        project_type=project_type,
        credits_amount=credits_amount,
        price_per_credit=price_per_credit,
        total_cost=total_cost,
        purchase_date=datetime.now(),
        status="active",
        certificate_url=None,  # TODO: Generate or receive certificate URL
        retirement_date=None
    )

    db.add(credit)
    db.commit()
    db.refresh(credit)

    return {
        "success": True,
        "message": "Carbon credits purchased successfully",
        "credit": {
            "id": credit.id,
            "project_name": credit.project_name,
            "project_type": credit.project_type,
            "credits_amount": credit.credits_amount,
            "total_cost": credit.total_cost,
            "purchase_date": credit.purchase_date.isoformat(),
            "status": credit.status
        }
    }


# Analytics endpoints
@app.get("/api/analytics/trends")
async def get_analytics_trends(
    start_date: datetime,
    end_date: datetime,
    granularity: str = "monthly"
):
    """
    Get trend analytics for emissions and consumption
    """
    # TODO: Implement analytics
    return {
        "emissions_trend": [],
        "consumption_trend": [],
        "cost_trend": []
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=str(exc)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc)
        ).dict()
    )


# Lambda handler (for AWS deployment)
handler = Mangum(app)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
