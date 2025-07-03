from .database import db
from datetime import datetime

class MedicalDocument(db.Model):
    __tablename__ = 'medical_documents'
    id = db.Column(db.String(36), primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    llm_summary = db.Column(db.Text, nullable=True)
    extracted_data = db.Column(db.JSON, nullable=False)
    date = db.Column(db.Date, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)