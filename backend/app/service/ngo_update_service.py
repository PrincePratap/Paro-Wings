from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.dependency import get_db
from models.ngo import NGOInfo
from schemas.ngo import(
     UpdateNGOLocationData,
     UpdateNGOResponse,
     UpdateNGOBasicInfo,
     UpdateContactInfo,
    UpdateNGOSettings,
    UpdateNGOStatistics,
    updateNGOOwnerInfo,
    UpdateNGOMapInfo)




def build_ngo_response(
    ngo: NGOInfo,
    message: str = "NGO profile fetched successfully."
) -> UpdateNGOResponse:
    return UpdateNGOResponse(
        success=True,
        message=message,

        ngo_settings=UpdateNGOSettings(
            ngo_id=ngo.id,
            accepts_rescue_requests=ngo.accepts_rescue_requests,
            is_verified=ngo.is_verified,
            is_active=ngo.is_active,
        ),

        ngo_statistics=UpdateNGOStatistics(
            total_reports=ngo.total_reports,
            total_rescues=ngo.total_rescues,
            rating=ngo.rating,
            total_volunteers=ngo.total_volunteers,
        ),

        ngo_basic_info=UpdateNGOBasicInfo(
            ngo_name=ngo.name,
            registration_number=ngo.registration_number,
            website=ngo.website,
            description=ngo.description,
        ),

        ngo_locations=UpdateNGOLocationData(
            address_line=ngo.address_line_1,
            landmark=ngo.landmark,
            city=ngo.city,
            district=ngo.district,
            state=ngo.state,
            postal_code=ngo.postal_code,
            country=ngo.country,
        ),

        ngo_contact_info=UpdateContactInfo(
            email=ngo.email,
            phone=ngo.phone,
            emergency_contact=ngo.emergency_contact,
        ),

        ngo_owner_info=updateNGOOwnerInfo(
            owner_name=ngo.owner_name,
            owner_email=ngo.owner_email,
            owner_phone=ngo.owner_phone,
        ),

        ngo_map=UpdateNGOMapInfo(
            latitude=ngo.latitude,
            longitude=ngo.longitude,
        ),
    )


def update_ngo_basic_info(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateNGOBasicInfo,
):
    current_ngo.ngo_name = data.ngo_name
    current_ngo.registration_number = data.registration_number
    current_ngo.description = data.description

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Basic information updated successfully."
    )

def update_ngo_contact_info(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateContactInfo,
):
    current_ngo.email = data.email
    current_ngo.phone = data.phone
    current_ngo.website = str(data.website) if data.website else None

    current_ngo.emergency_contact = data.emergency_contact

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Contact information updated successfully."
    )


def update_ngo_owner_info(
    session: Session,
    current_ngo: NGOInfo,
    data: updateNGOOwnerInfo,
):
    current_ngo.owner_name = data.owner_name
    current_ngo.owner_email = data.owner_email
    current_ngo.owner_phone = data.owner_phone

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Owner information updated successfully."
    )

def update_ngo_map_info(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateNGOMapInfo,
):
    current_ngo.latitude = data.latitude
    current_ngo.longitude = data.longitude

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Map information updated successfully."
    )

def update_ngo_settings(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateNGOSettings,
):
    current_ngo.accepts_rescue_requests = data.accepts_rescue_requests
    current_ngo.is_verified = data.is_verified
    current_ngo.is_active = data.is_active

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="NGO settings updated successfully."
    )

def update_ngo_location_info(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateNGOLocationData,
):
    current_ngo.address_line_1 = data.address_line_1
    current_ngo.landmark = data.landmark
    current_ngo.city = data.city
    current_ngo.district = data.district
    current_ngo.state = data.state
    current_ngo.postal_code = data.postal_code
    current_ngo.country = data.country

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Location information updated successfully."
    )

def update_map_info(
    session: Session,
    current_ngo: NGOInfo,
    data: UpdateNGOMapInfo,
):
    current_ngo.latitude = data.latitude
    current_ngo.longitude = data.longitude

    session.commit()
    session.refresh(current_ngo)

    return build_ngo_response(
        current_ngo,
        message="Map information updated successfully."
    )

