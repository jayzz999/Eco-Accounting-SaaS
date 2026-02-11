"""
Database models for Eco-Accounting SaaS
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()


class BillType(str, enum.Enum):
    ELECTRICITY = "electricity"
    WATER = "water"
    GAS = "gas"
    FUEL = "fuel"
    WASTE = "waste"
    OTHER = "other"


class BillStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    FAILED = "failed"


class ReportType(str, enum.Enum):
    GRI_302 = "GRI-302"  # Energy
    GRI_305 = "GRI-305"  # Emissions
    GRI_303 = "GRI-303"  # Water
    CDP = "CDP"
    TCFD = "TCFD"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    country = Column(String(100))
    region = Column(String(100))
    cognito_user_pool_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    bills = relationship("Bill", back_populates="organization")
    emissions = relationship("Emission", back_populates="organization")
    reports = relationship("Report", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cognito_sub = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    role = Column(String(50), default="user")
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="users")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    uploaded_by = Column(String(255))  # Cognito sub

    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # S3 path
    file_size = Column(Integer)
    mime_type = Column(String(100))

    # Bill classification
    bill_type = Column(Enum(BillType), nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.UPLOADED)

    # Extracted data (JSON format)
    extracted_data = Column(JSON)
    validated_data = Column(JSON)

    # Processing metadata
    ocr_confidence = Column(Float)
    processing_time = Column(Float)  # seconds
    error_message = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    validated_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="bills")
    emission = relationship("Emission", back_populates="bill", uselist=False)


class Emission(Base):
    __tablename__ = "emissions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id"), unique=True)

    # Emission details
    category = Column(String(100))  # Scope 1, 2, or 3
    source_type = Column(Enum(BillType))

    # Consumption data
    consumption_amount = Column(Float, nullable=False)
    consumption_unit = Column(String(50), nullable=False)

    # Carbon calculation
    emission_factor = Column(Float, nullable=False)
    emission_factor_source = Column(String(255))
    total_co2e = Column(Float, nullable=False)  # Total CO2 equivalent in kg

    # Geographic context
    country = Column(String(100))
    region = Column(String(100))

    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Metadata
    calculation_method = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="emissions")
    bill = relationship("Bill", back_populates="emission")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Report details
    report_type = Column(Enum(ReportType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Report period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Report data
    report_data = Column(JSON, nullable=False)  # Structured report content
    file_path = Column(String(500))  # S3 path for PDF

    # Metadata
    generated_by = Column(String(255))  # Cognito sub
    status = Column(String(50), default="draft")
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="reports")


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)

    # Rule details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    regulation = Column(String(255))  # e.g., "EU ETS", "UK ESOS"

    # Geographic scope
    countries = Column(JSON)  # List of applicable countries

    # Rule parameters
    threshold_value = Column(Float)
    threshold_unit = Column(String(50))
    emission_category = Column(String(100))

    # Validation
    is_active = Column(Boolean, default=True)
    effective_date = Column(DateTime)
    expiry_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"), nullable=False)

    # Check results
    is_compliant = Column(Boolean, nullable=False)
    current_value = Column(Float)
    threshold_value = Column(Float)
    deviation = Column(Float)  # Percentage or absolute deviation

    # Details
    check_date = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    notes = Column(Text)


class CarbonCredit(Base):
    __tablename__ = "carbon_credits"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Credit details
    baseline_emissions = Column(Float, nullable=False)  # kg CO2e
    actual_emissions = Column(Float, nullable=False)  # kg CO2e
    avoided_emissions = Column(Float, nullable=False)  # kg CO2e

    # Credit calculation
    potential_credits = Column(Float, nullable=False)  # tonnes CO2e
    credit_price = Column(Float)  # USD per tonne
    potential_value = Column(Float)  # USD

    # Project details
    project_type = Column(String(255))  # e.g., "Energy Efficiency", "Renewable Energy"
    methodology = Column(String(255))

    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Status
    status = Column(String(50), default="estimated")  # estimated, verified, issued
    verification_date = Column(DateTime)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


import os
from dotenv import load_dotenv

load_dotenv()

# Global engine and session factory
engine = None
SessionLocal = None


def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    # Fallback to individual components
    db_user = os.getenv('DB_USER', 'jayanthmuthina')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'eco_accounting')

    if db_password:
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        return f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"


def init_db():
    """Initialize database connection and create tables"""
    global engine, SessionLocal

    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def get_db_session():
    """Get database session (dependency for FastAPI)"""
    if SessionLocal is None:
        init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
