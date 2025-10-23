from fastapi import APIRouter, Depends, HTTPException, status, Query
from authx import TokenPayload

from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from app.services.google_account_service import fetch_user_gmail_messages

router = APIRouter()

@router.get(
    "/me",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_user_gmail_messages(
    session: SessionDep,
    user_id: int,
    max_results: int = Query(10, description="Number of emails to fetch"),
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    """
    Fetch Gmail messages for a specific user.
    Automatically refreshes the token if expired.
    Only accessible by the user themselves or an admin.
    """
    # Permission check
    if not payload.user_is_admin and payload.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

    try:
        result = fetch_user_gmail_messages(user_id, session, max_results)
        return {
            "success": True,
            "message": "Fetched Gmail messages successfully",
            "data": result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print("Error fetching Gmail messages:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )