from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# What we ask the LLM to return
class KPIExtraction(BaseModel):
    revenue: Optional[float] = Field(None, description="Total revenue in millions")
    ebitda: Optional[float] = Field(None, description="EBITDA in millions")
    gross_profit: Optional[float] = Field(None, description="Gross profit in millions")
    gross_margin_pct: Optional[float] = Field(None, description="Gross margin as a percentage, e.g. 45.2")
    arr: Optional[float] = Field(None, description="Annual Recurring Revenue in millions")
    mrr: Optional[float] = Field(None, description="Monthly Recurring Revenue in millions")
    net_income: Optional[float] = Field(None, description="Net income in millions, negative if loss")
    cash: Optional[float] = Field(None, description="Cash and cash equivalents in millions")
    net_debt: Optional[float] = Field(None, description="Net debt in millions")
    leverage_ratio: Optional[float] = Field(None, description="Leverage ratio (Net Debt / EBITDA)")
    headcount: Optional[int] = Field(None, description="Total employee headcount as integer")
    bookings: Optional[float] = Field(None, description="Total bookings in millions")
    period: Optional[str] = Field(None, description="Reporting period, e.g. FY2023 or Q3 2024")
    currency: Optional[str] = Field(None, description="Currency used, e.g. USD, EUR, GBP")


# API response shapes
class CompanyCreate(BaseModel):
    name: str

class CompanyResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    filename: str
    company_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class KPIResponse(BaseModel):
    id: int
    document_id: int
    revenue: Optional[float]
    ebitda: Optional[float]
    gross_profit: Optional[float]
    gross_margin_pct: Optional[float]
    arr: Optional[float]
    mrr: Optional[float]
    net_income: Optional[float]
    cash: Optional[float]
    net_debt: Optional[float]
    leverage_ratio: Optional[float]
    headcount: Optional[int]
    bookings: Optional[float]
    period: Optional[str]
    currency: Optional[str]
    extracted_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    message: str
    document: DocumentResponse
    kpis: KPIResponse
