from sqlalchemy import Column, String, Text, Date, DateTime, JSON
from db.database import Base
from datetime import datetime

class MedicalDocument(Base):
    __tablename__ = 'medical_documents'
    id = Column(String(36), primary_key=True, index=True)
    filename = Column(String(256), nullable=False)
    doc_type = Column(String(50), nullable=False)
    llm_summary = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=False)
    document_date = Column(Date, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)