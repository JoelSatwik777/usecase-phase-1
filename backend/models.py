from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    documents = relationship("Document", back_populates="company")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="documents")
    kpis = relationship("KPIResult", back_populates="document")


class KPIResult(Base):
    __tablename__ = "kpi_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    # Core KPIs — all optional since not every doc has every field
    revenue = Column(Float, nullable=True)
    ebitda = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    gross_margin_pct = Column(Float, nullable=True)
    arr = Column(Float, nullable=True)
    mrr = Column(Float, nullable=True)
    net_income = Column(Float, nullable=True)
    cash = Column(Float, nullable=True)
    net_debt = Column(Float, nullable=True)
    leverage_ratio = Column(Float, nullable=True)
    headcount = Column(Integer, nullable=True)
    bookings = Column(Float, nullable=True)

    # Metadata
    period = Column(String, nullable=True)       # e.g. "FY2023", "Q3 2024"
    currency = Column(String, nullable=True)     # e.g. "USD", "EUR"
    raw_llm_response = Column(Text, nullable=True)  # store full LLM output for debugging
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="kpis")
