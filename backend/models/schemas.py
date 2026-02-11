"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class BillTypeEnum(str, Enum):
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"
    FUEL = "fuel"
    WASTE = "waste"
    OTHER = "other"


class BillStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    FAILED = "failed"


class ReportTypeEnum(str, Enum):
    GRI_302 = "GRI-302"
    GRI_305 = "GRI-305"
    GRI_303 = "GRI-303"
    CDP = "CDP"
    TCFD = "TCFD"


# Organization schemas
class OrganizationBase(BaseModel):
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    cognito_sub: str
    organization_id: int


class UserResponse(UserBase):
    id: int
    cognito_sub: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Bill schemas
class BillUploadRequest(BaseModel):
    file_name: str
    file_size: int
    mime_type: str
    bill_type: Optional[BillTypeEnum] = None


class ExtractedBillData(BaseModel):
    bill_type: str
    provider_name: Optional[str] = None
    account_number: Optional[str] = None
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    consumption_amount: Optional[float] = None
    consumption_unit: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    raw_text: Optional[str] = None
    confidence_score: Optional[float] = None


class BillResponse(BaseModel):
    id: int
    organization_id: int
    file_name: str
    bill_type: BillTypeEnum
    status: BillStatusEnum
    extracted_data: Optional[Dict[str, Any]] = None
    ocr_confidence: Optional[float] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BillValidationRequest(BaseModel):
    validated_data: Dict[str, Any]


# Emission schemas
class EmissionCalculationRequest(BaseModel):
    bill_id: int
    consumption_amount: float
    consumption_unit: str
    source_type: BillTypeEnum
    country: str
    region: Optional[str] = None
    period_start: datetime
    period_end: datetime


class EmissionResponse(BaseModel):
    id: int
    organization_id: int
    bill_id: Optional[int] = None
    category: Optional[str] = None
    source_type: BillTypeEnum
    consumption_amount: float
    consumption_unit: str
    emission_factor: float
    total_co2e: float
    period_start: datetime
    period_end: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Report schemas
class ReportGenerationRequest(BaseModel):
    report_type: ReportTypeEnum
    period_start: datetime
    period_end: datetime
    title: Optional[str] = None
    description: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    organization_id: int
    report_type: ReportTypeEnum
    title: str
    period_start: datetime
    period_end: datetime
    status: str
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard schemas
class EmissionsSummary(BaseModel):
    total_emissions: float  # kg CO2e
    period_start: datetime
    period_end: datetime
    by_category: Dict[str, float]
    by_source: Dict[str, float]
    trend: str  # "increasing", "decreasing", "stable"
    change_percentage: Optional[float] = None


class DashboardStats(BaseModel):
    total_bills: int
    total_emissions: float
    current_month_emissions: float
    previous_month_emissions: float
    emissions_change: float
    compliance_status: str
    recent_bills: List[BillResponse]
    emissions_by_month: List[Dict[str, Any]]


# Compliance schemas
class ComplianceCheckResponse(BaseModel):
    rule_name: str
    regulation: str
    is_compliant: bool
    current_value: float
    threshold_value: float
    deviation: Optional[float] = None
    recommendation: Optional[str] = None


class ComplianceStatusResponse(BaseModel):
    overall_compliant: bool
    checks: List[ComplianceCheckResponse]
    checked_at: datetime


# Carbon credit schemas
class CarbonCreditEstimateRequest(BaseModel):
    period_start: datetime
    period_end: datetime
    project_type: str


class CarbonCreditResponse(BaseModel):
    id: int
    baseline_emissions: float
    actual_emissions: float
    avoided_emissions: float
    potential_credits: float  # tonnes
    credit_price: Optional[float] = None
    potential_value: Optional[float] = None
    project_type: str
    status: str

    class Config:
        from_attributes = True


# Analytics schemas
class TrendDataPoint(BaseModel):
    date: str
    value: float
    label: Optional[str] = None


class AnalyticsResponse(BaseModel):
    emissions_trend: List[TrendDataPoint]
    consumption_trend: List[TrendDataPoint]
    cost_trend: List[TrendDataPoint]
    breakdown_by_type: Dict[str, float]
    recommendations: List[str]


# Generic response schemas
class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
