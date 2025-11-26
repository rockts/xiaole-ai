from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import time
from config import UPLOADS_DIR

router = APIRouter(
    prefix="/api/vision",
    tags=["vision"]
)


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for vision processing
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )

        # Ensure images directory exists
        images_dir = os.path.join(UPLOADS_DIR, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir, exist_ok=True)

        # Generate unique filename
        timestamp = int(time.time())
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(images_dir, filename)

        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Return relative path for frontend to use
        # Assuming static mount is at /uploads
        relative_path = f"/uploads/images/{filename}"

        return {
            "success": True,
            "filename": filename,
            "file_path": relative_path,  # Frontend expects file_path
            "path": relative_path,
            "url": relative_path  # For compatibility
        }

    except Exception as e:
        print(f"Image upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

