from fastapi import UploadFile, HTTPException
from pathlib import Path
import secrets

async def save_file(
    file: UploadFile,
    upload_dir: Path,
    max_size: int,
    allowed_extensions: set[str]
) -> str:
    contents = await file.read()
    if len(contents) > max_size:
        raise HTTPException(status_code=400, detail="File too large")
        
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="File type not allowed")
        
    filename = f"{secrets.token_urlsafe(16)}{file_extension}"
    file_path = upload_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(contents)
        
    return f"/uploads/{filename}"