from sqlalchemy.orm import Session
from app.db.models.profile_model import Profile
from app.db.schemas.profile import ProfileCreate, ProfileUpdate


def get_profile_by_user_id(user_id: int, session: Session):
    return session.query(Profile).filter(Profile.user_id == user_id).first()


def create_profile(data: ProfileCreate, session: Session):
    new_profile = Profile(**data.model_dump())
    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)
    return new_profile


def update_profile(profile: Profile, data: ProfileUpdate, session: Session):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    session.commit()
    session.refresh(profile)
    return profile


def list_profiles(session: Session):
    return session.query(Profile).all()


def delete_profile(user_id: int, session: Session):
    profile = get_profile_by_user_id(user_id, session)
    if not profile:
        return False
    session.delete(profile)
    session.commit()
    return True
