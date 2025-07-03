import os
import uuid

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'pdf'}

def save_file(file, upload_folder):
    ext = file.filename.rsplit('.', 1)[1].lower()
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.{ext}"
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename, file_id