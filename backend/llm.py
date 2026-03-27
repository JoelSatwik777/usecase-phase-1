import os
import json
from groq import Groq
from dotenv import load_dotenv
from schemas import KPIExtraction

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a financial data extraction specialist working for a Private Equity firm.
Your job is to extract key financial KPIs from board deck documents and financial reports.

Rules:
- Extract ONLY values explicitly stated in the document. Do not estimate or infer.
- All monetary values must be in millions (e.g. $500M = 500, $1.2B = 1200).
- If a value is not present in the document, return null for that field.
- For percentages, return the number only (e.g. 45.2 for 45.2%).
- For headcount, return an integer.
- For period, identify the reporting period clearly (e.g. FY2023, Q3 2024, H1 2024).
- For currency, identify what currency is used (USD, EUR, GBP, etc.).
- Return ONLY a valid JSON object. No explanation, no markdown, no extra text.
"""

def build_extraction_prompt(text: str) -> str:
    return f"""
Extract the following KPIs from this financial document:
- revenue
- ebitda
- gross_profit
- gross_margin_pct
- arr (Annual Recurring Revenue)
- mrr (Monthly Recurring Revenue)
- net_income
- cash
- net_debt
- leverage_ratio
- headcount
- bookings
- period (reporting period)
- currency

Document text:
{text}

Return a JSON object with exactly these field names. Use null for any field not found.
"""


def extract_kpis_from_text(text: str) -> KPIExtraction:
    """
    Send extracted PDF text to Groq and parse structured KPI response.
    Returns a validated KPIExtraction Pydantic model.
    """
    prompt = build_extraction_prompt(text)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Best free Groq model for structured extraction
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0,        # Zero temp for deterministic extraction
        max_tokens=1024,
    )

    raw_content = response.choices[0].message.content.strip()

    # Strip markdown code fences if model wraps response in them
    if raw_content.startswith("```"):
        raw_content = raw_content.split("```")[1]
        if raw_content.startswith("json"):
            raw_content = raw_content[4:]
        raw_content = raw_content.strip()

    try:
        parsed = json.loads(raw_content)
        return KPIExtraction(**parsed), raw_content
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\nRaw response: {raw_content}")
