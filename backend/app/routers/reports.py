from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependency  import get_db
from app.models.animal_report import AnimalReport
from app.schemas.report import AnimalReportCreate


# Import your JWT dependency
# from auth.jwt import get_current_user

router = APIRouter(
    prefix="/reports",
    tags=["Animal Reports"]
)


@router.post("/")
async def create_report(
    report: AnimalReportCreate,
    db: Session = Depends(get_db),
):
    new_report = AnimalReport(
        user_id=report.current_user_id,
        animal_type=report.animal_type,
        description=report.description,
        latitude=report.latitude,
        longitude=report.longitude
        
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Animal report created successfully",
        "data": new_report
    }


# @router.get("/")
# async def get_all_reports(
#     db: Session = Depends(get_db)
# ):
#     reports = db.query(AnimalReport).all()

#     return {
#         "count": len(reports),
#         "data": reports
#     }


# @router.get("/{report_id}")
# async def get_report(
#     report_id: int,
#     db: Session = Depends(get_db)
# ):
#     report = db.query(AnimalReport).filter(
#         AnimalReport.id == report_id
#     ).first()

#     if not report:
#         raise HTTPException(
#             status_code=404,
#             detail="Report not found"
#         )

#     return report


# @router.put("/{report_id}/status")
# async def update_report_status(
#     report_id: int,
#     status: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     report = db.query(AnimalReport).filter(
#         AnimalReport.id == report_id
#     ).first()

#     if not report:
#         raise HTTPException(
#             status_code=404,
#             detail="Report not found"
#         )

#     report.status = status

#     db.commit()
#     db.refresh(report)

#     return {
#         "message": "Status updated successfully",
#         "data": report
#     }


# @router.delete("/{report_id}")
# async def delete_report(
    # report_id: int,
    db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     report = db.query(AnimalReport).filter(
#         AnimalReport.id == report_id
#     ).first()

#     if not report:
#         raise HTTPException(
#             status_code=404,
#             detail="Report not found"
#         )

#     db.delete(report)
#     db.commit()

#     return {
#         "message": "Report deleted successfully"
#     }