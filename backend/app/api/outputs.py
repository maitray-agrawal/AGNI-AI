from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.app.config import settings

router = APIRouter()


@router.get("/outputs/{filename}")
async def get_output_file(filename: str):
    safe_name = Path(filename).name
    file_path = settings.OUTPUT_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested deliverable does not exist")

    media_type = "application/octet-stream"
    if safe_name.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif safe_name.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif safe_name.endswith(".json"):
        media_type = "application/json"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=safe_name,
    )
