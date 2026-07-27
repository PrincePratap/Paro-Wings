from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.dependency  import get_db
from models.animal_report import AnimalReport
from schemas.report import AnimalReportCreate
from sqlalchemy import Column, DateTime
from datetime import datetime
from service.auth_service import get_current_user




router = APIRouter(
    prefix="/reports",
    tags=["Animal Reports"]
)


@router.post("/")
async def create_report(
    report: AnimalReportCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_report = AnimalReport(
        user_id=current_user.id,
        user_name=current_user.full_name,
        user_phone=current_user.phone,
        user_email=current_user.email,
        animal_type=report.animal_type,
        situation_type=report.situation_type,
        severity=report.severity,
        description=report.description,

        latitude=report.latitude,
        longitude=report.longitude,

        address_line_1=report.address_line_1,
        locality=report.locality,
        city=report.city,
        state=report.state,
        postal_code=report.postal_code,

        image_urls=report.image_urls,
        anonymous_report=report.anonymous_report,

        status="Pending",

        # Remove this if your model already has default=datetime.utcnow
        created_at=datetime.utcnow()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "success": True,
        "message": "Animal report created successfully",
        "report_id": new_report.id,
        "data": new_report
    }

@router.get("/")
async def get_all_reports(
    db: Session = Depends(get_db)
):
    reports = db.query(AnimalReport).all()

    return {
        "success": True,
        "count": len(reports),
        "data": reports
    }

@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(AnimalReport).filter(
        AnimalReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return {
        "success": True,
        "data": report
    }

@router.get("/postal-code/{postal_code}")
async def get_reports_by_postal_code(
    postal_code: str,
    db: Session = Depends(get_db)
):
    reports = db.query(AnimalReport).filter(
        AnimalReport.postal_code == postal_code
    ).all()

    return {
        "success": True,
        "count": len(reports),
        "data": reports
    }

from schemas.report import UpdateStatusRequest


@router.patch("/{report_id}/status")
async def update_report_status(
    report_id: int,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db)
):
    report = db.query(AnimalReport).filter(
        AnimalReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    report.status = request.status

    db.commit()
    db.refresh(report)

    return {
        "success": True,
        "message": "Status updated successfully",
        "data": report
    }

@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(AnimalReport).filter(
        AnimalReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    db.delete(report)
    db.commit()

    return {
        "success": True,
        "message": "Report deleted successfully"
    }

@router.get("/status/{status}")
async def get_reports_by_status(
    status: str,
    db: Session = Depends(get_db)
):
    reports = db.query(AnimalReport).filter(
        AnimalReport.status == status
    ).all()

    return {
        "success": True,
        "count": len(reports),
        "status": status,
        "data": reports
    }