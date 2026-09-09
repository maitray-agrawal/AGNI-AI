import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.config import settings

router = APIRouter()


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = Path(file.filename).name
    # Categorize destination
    if filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        target_dir = settings.DATA_DIR / "raw" / "inspection_reports"
    else:
        target_dir = settings.DATA_DIR / "raw" / "industrial_docs"

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {str(e)}")

    size_bytes = target_path.stat().st_size

    return {
        "filename": filename,
        "saved_path": str(target_path).replace("\\", "/"),
        "size_bytes": size_bytes,
        "content_type": file.content_type,
    }
