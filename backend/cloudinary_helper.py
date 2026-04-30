# backend/cloudinary_helper.py
# Single place for ALL Cloudinary operations.

import cloudinary
import cloudinary.uploader
from backend.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
    secure     = True,
)


def upload_file(file_storage, folder: str, resource_type: str = "auto") -> dict:
    """Upload a Werkzeug FileStorage to Cloudinary. Returns {public_id, secure_url}."""
    result = cloudinary.uploader.upload(
        file_storage,
        folder          = folder,
        resource_type   = resource_type,
        overwrite       = False,
        unique_filename = True,
    )
    return {
        "public_id":  result["public_id"],
        "secure_url": result["secure_url"],
    }


def delete_file(public_id: str, resource_type: str = "image") -> bool:
    """Delete a Cloudinary asset by public_id. Returns True on success."""
    if not public_id:
        return False
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get("result") == "ok"
    except Exception:
        return False
