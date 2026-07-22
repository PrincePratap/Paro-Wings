from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.upload_schema import UploadResponse
from service.auth_service import get_current_user
from service.upload_service import upload_image

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/image", response_model=UploadResponse)
async def upload_image_endpoint(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        base_url = str(request.base_url)
        result = await upload_image(file, base_url=base_url)
        return {
            "success": True,
            "message": "Image uploaded successfully.",
            "data": result,
        }
    except HTTPException as exc:
        return JSONResponse(status_code=exc.status_code, content={"success": False, "message": exc.detail})
    except Exception as exc:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"success": False, "message": "Internal server error"})
