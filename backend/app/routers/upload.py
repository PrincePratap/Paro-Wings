from fastapi import APIRouter, UploadFile, File, HTTPException

from core.storage import upload_image 

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/image")
async def upload_image_api(
    image: UploadFile = File(...)
):
    try:
        image_url = upload_image(
            file=image,
            folder="uploads"
        )

        return {
            "success": True,
            "message": "Image uploaded successfully.",
            "data": {
                "image_url": image_url
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )