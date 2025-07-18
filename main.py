import os
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import MedicalDocument
from db.schemas import MedicalDocumentResponse
from llm.gemini_client import extract_document_data
from pdf2image import convert_from_path
from io import BytesIO
import uuid
from datetime import date, datetime
from dotenv import load_dotenv
from typing import List, Tuple, Optional
from pydantic import BaseModel

load_dotenv()
app = FastAPI()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print("UPLOAD_FOLDER set to:", UPLOAD_FOLDER)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def preprocess_upload_file(file: UploadFile, upload_folder: str) -> Tuple[str, BytesIO]:
    """
    Saves the uploaded file, handles PDF/image conversion, and returns the filename and a BytesIO object ready for LLM processing.
    """
    import uuid
    from io import BytesIO
    from pdf2image import convert_from_path
    import os

    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(upload_folder, filename)
    print(f"Saving file to {file_path}")

    # Save file to disk
    await file.seek(0)
    file_bytes = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(file_bytes)
    print("File saved successfully.")

    # Prepare file for LLM
    if filename.lower().endswith('.pdf'):
        print("PDF detected, converting first page to image...")
        images = convert_from_path(file_path, first_page=1, last_page=1)
        if images:
            img_byte_arr = BytesIO()
            images[0].save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            print("PDF conversion successful.")
            return filename, img_byte_arr
        else:
            raise ValueError("PDF conversion failed: No images generated.")
    else:
        # For images, read into BytesIO
        img_byte_arr = BytesIO(file_bytes)
        img_byte_arr.seek(0)
        print("Image file prepared for LLM.")
        return filename, img_byte_arr

def save_document_to_db(
    db: Session,
    filename: str,
    doc_type: str,
    extracted_data: dict,
    document_date: Optional[date],
    llm_summary: str
) -> MedicalDocument:
    import uuid
    from datetime import datetime
    print("Saving document to database...")
    try:
        doc = MedicalDocument(
            id=str(uuid.uuid4()),
            filename=filename,
            doc_type=doc_type,
            extracted_data=extracted_data,
            document_date=document_date,
            llm_summary=llm_summary,
            uploaded_at=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        print("Document saved to database successfully.")
        return doc
    except Exception as e:
        print(f"Database save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database save failed: {e}")

class UploadResponse(BaseModel):
    message: str

@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print("Received upload request.")
    try:
        filename, file_to_process = await preprocess_upload_file(file, UPLOAD_FOLDER)
    except Exception as e:
        print(f"File preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail=f"File preprocessing failed: {e}")

    # Call LLM
    api_key = os.environ.get("GEMINI_API_KEY")
    print("GEMINI_API_KEY:", api_key)
    if not api_key:
        print("Gemini API key not set!")
        raise HTTPException(status_code=500, detail="Gemini API key not set")
    try:
        print("Calling extract_document_data...")
        llm_result = extract_document_data(file_to_process, api_key)
        print("LLM extraction result:", llm_result)
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {e}")

    doc_type = llm_result.get("doc_type", "unknown")
    extracted_data = llm_result.get("extracted_data", {})
    date_str = llm_result.get("date")
    summary = llm_result.get("llm_summary", "")

    doc_date = None
    if date_str:
        try:
            doc_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            print("Parsed doc_date:", doc_date)
        except Exception as e:
            print(f"Could not parse date: {e}")
            doc_date = None

    doc = save_document_to_db(
        db=db,
        filename=filename,
        doc_type=doc_type,
        extracted_data=extracted_data,
        document_date=doc_date,
        llm_summary=summary
    )
    print("Returning response to user.")
    return {"message": "Document uploaded successfully"}

@app.get("/documents", response_model=List[MedicalDocumentResponse])
def get_documents(db: Session = Depends(get_db)):
    print("Fetching all documents from the database...")
    docs = db.query(MedicalDocument).all()
    print(f"Found {len(docs)} documents.")
    print(docs)
    return docs

#from datetime import date, datetime
# @app.get("/documents1", response_model=List[MedicalDocumentResponse])
# def get_documents1(db: Session = Depends(get_db)):
#        return [{
#            "id": "test",
#            "filename": "file.pdf",
#            "doc_type": "test",
#            "llm_summary": "summary",
#            "extracted_data": {},
#            "document_date": date.today(),
#            "uploaded_at": datetime.now()
#        }]

