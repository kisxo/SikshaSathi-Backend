from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from authx import TokenPayload
from typing import Optional

from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from app.services import profile_service
from app.db.schemas.profile import ProfileCreate, ProfileUpdate, ProfilePublic, ProfilesPublic


router = APIRouter()


# -----------------------------------------------------------
# Create Profile (one per user)
# -----------------------------------------------------------
@router.post(
    "/",
    response_model=ProfilePublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def create_profile(
    profile_data: ProfileCreate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    # Ensure only self or admin can create
    if not payload.user_is_admin:
        profile_data.user_id = payload.user_id

    existing_profile = profile_service.get_profile_by_user_id(profile_data.user_id, session)
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile already exists")

    try:
        new_profile = profile_service.create_profile(profile_data, session)
        return new_profile
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create profile")


# -----------------------------------------------------------
# Get Profile by User ID
# -----------------------------------------------------------
@router.get(
    "/{user_id}",
    response_model=ProfilePublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_profile_by_user_id(
    session: SessionDep,
    user_id: int,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):

    if not payload.user_is_admin:
        user_id = payload.user_id

    profile = profile_service.get_profile_by_user_id(user_id, session)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


# -----------------------------------------------------------
# Update Profile
# -----------------------------------------------------------
@router.put(
    "/{user_id}",
    response_model=ProfilePublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def update_profile(
    user_id: int,
    update_data: ProfileUpdate,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    if not payload.user_is_admin and payload.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    profile = profile_service.get_profile_by_user_id(user_id, session)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        updated = profile_service.update_profile(profile, update_data, session)
        return updated
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update profile")


# -----------------------------------------------------------
# List All Profiles (admin only)
# -----------------------------------------------------------
@router.get(
    "/",
    response_model=ProfilesPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def list_profiles(
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    if not payload.user_is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all profiles")

    profiles = profile_service.list_profiles(session)
    return {'data': profiles}


# -----------------------------------------------------------
# Delete Profile (admin)
# -----------------------------------------------------------
@router.delete(
    "/{user_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def delete_profile(
    user_id: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    if not payload.user_is_admin:
        raise HTTPException(status_code=400, detail="Does not have permission to delete profile!")

    deleted = profile_service.delete_profile(user_id, session)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return {"message": "Profile deleted successfully"}
