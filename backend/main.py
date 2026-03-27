import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, get_db, Base
from models import Company, Document, KPIResult
from schemas import CompanyCreate, CompanyResponse, UploadResponse, KPIResponse
from extractor import extract_text_from_pdf, chunk_text
from llm import extract_kpis_from_text

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PE Intelligence API",
    description="Phase 1 — PDF KPI extraction pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- Company routes ---

@app.post("/companies", response_model=CompanyResponse)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    company = Company(name=payload.name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@app.get("/companies", response_model=list[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()


# --- Upload + extraction route ---

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    company_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Validate company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save PDF to disk
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save document record
    document = Document(
        filename=file.filename,
        file_path=file_path,
        company_id=company_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Extract text from PDF
    try:
        raw_text = extract_text_from_pdf(file_path)
        chunked_text = chunk_text(raw_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF extraction failed: {str(e)}")

    # Extract KPIs via LLM
    try:
        kpi_data, raw_llm_response = extract_kpis_from_text(chunked_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"KPI extraction failed: {str(e)}")

    # Store KPI result
    kpi_result = KPIResult(
        document_id=document.id,
        revenue=kpi_data.revenue,
        ebitda=kpi_data.ebitda,
        gross_profit=kpi_data.gross_profit,
        gross_margin_pct=kpi_data.gross_margin_pct,
        arr=kpi_data.arr,
        mrr=kpi_data.mrr,
        net_income=kpi_data.net_income,
        cash=kpi_data.cash,
        net_debt=kpi_data.net_debt,
        leverage_ratio=kpi_data.leverage_ratio,
        headcount=kpi_data.headcount,
        bookings=kpi_data.bookings,
        period=kpi_data.period,
        currency=kpi_data.currency,
        raw_llm_response=raw_llm_response
    )
    db.add(kpi_result)
    db.commit()
    db.refresh(kpi_result)

    return UploadResponse(
        message="Document processed and KPIs extracted successfully",
        document=document,
        kpis=kpi_result
    )


# --- KPI retrieval routes ---

@app.get("/kpis/{document_id}", response_model=KPIResponse)
def get_kpis(document_id: int, db: Session = Depends(get_db)):
    kpi = db.query(KPIResult).filter(KPIResult.document_id == document_id).first()
    if not kpi:
        raise HTTPException(status_code=404, detail="No KPIs found for this document")
    return kpi


@app.get("/companies/{company_id}/kpis", response_model=list[KPIResponse])
def get_company_kpis(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    results = (
        db.query(KPIResult)
        .join(Document)
        .filter(Document.company_id == company_id)
        .all()
    )
    return results


@app.get("/health")
def health_check():
    return {"status": "ok", "phase": 1}
