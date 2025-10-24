from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.email_summary_model import EmailSummary


def list_summary_by_user_id(user_id: int, session: SessionDep):
    try:
        statement = select(EmailSummary)
        result =  session.execute(statement).filter(EmailSummary.user_id == user_id).all()
        summary_list = []
        for row in result:
            summary_list.append(row.EmailSummary.__dict__)

        return summary_list
    except Exception as e:
        print(e)