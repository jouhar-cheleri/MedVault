from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from db.database import db, init_db
from utils.file_utils import allowed_file, save_file
from llm.gemini_client import extract_document_data
from db.models import MedicalDocument
import os
import uuid
import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Only call this ONCE
init_db(app)  

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        print("Received POST request for file upload.")
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            print("Invalid file type detected.")
            flash('Invalid file type.')
            return redirect(request.url)
        if file.content_length and file.content_length > app.config['MAX_CONTENT_LENGTH']:
            print("File too large.")
            flash('File too large.')
            return redirect(request.url)
        print("Saving file to uploads folder...")
        filename, file_id = save_file(file, app.config['UPLOAD_FOLDER'])
        print(f"File saved as {filename} with ID {file_id}.")
        file.seek(0)  # Reset file pointer before sending to LLM
        try:
            print("Starting LLM extraction...")
            llm_result = extract_document_data(file)
            print("LLM extraction completed.")
            doc_type = llm_result.get("doc_type", "unknown")
            extracted_data = llm_result.get("extracted_data", {})
            date_str = llm_result.get("date")
            summary = llm_result.get("llm_summary", "")

            # Parse date string to date object
            doc_date = None
            if date_str:
                try:
                    doc_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                except Exception as e:
                    print(f"Could not parse date: {e}")
                    doc_date = None
        except Exception as e:
            print(f"LLM extraction failed: {e}")
            flash(f'LLM extraction failed: {e}')
            return redirect(request.url)
        # Save to DB
        try:
            print("Saving extracted data to database...")
            doc = MedicalDocument(
                id=file_id,
                filename=filename,
                doc_type=doc_type,
                extracted_data=extracted_data,
                date=doc_date,
                llm_summary=summary
            )
            db.session.add(doc)
            db.session.commit()
            print("Data saved to database successfully.")
        except Exception as e:
            print(f"Database error: {e}")
            flash(f'Database error: {e}')
            return redirect(request.url)
        print("Upload and processing complete. Redirecting to history.")
        flash('File uploaded and processed!')
        return redirect(url_for('history'))
    print("Rendering upload page.")
    return render_template('upload.html')

@app.route('/history')
def history():
    print("Rendering history page.")
    docs = MedicalDocument.query.order_by(MedicalDocument.date.desc()).all()
    print("entries are",docs)
    return render_template('history.html', docs=docs)

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)