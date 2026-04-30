# backend/utils.py

import os
import json
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "pptx", "doc", "docx"
}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, folder):
    filename = secure_filename(file.filename)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file.save(path)
    return filename
# backend/utils.py

import json

def to_json(data):
    return json.dumps(data)

def from_json(data):
    return json.loads(data) if data else []

