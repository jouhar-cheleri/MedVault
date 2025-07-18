from pydantic import BaseModel
from typing import Optional, Any
from datetime import date, datetime

class MedicalDocumentBase(BaseModel):
    filename: str
    doc_type: str
    llm_summary: Optional[str] = None
    extracted_data: Any
    document_date: Optional[date] = None

class MedicalDocumentCreate(MedicalDocumentBase):
    pass

class MedicalDocumentResponse(MedicalDocumentBase):
    id: str
    uploaded_at: datetime

    class Config:
        from_attributes = True