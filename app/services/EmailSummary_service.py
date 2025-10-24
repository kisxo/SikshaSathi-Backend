from app.core.ai import AI_Client
from app.db.session import SessionDep
from fastapi import HTTPException
from sqlalchemy import select
from app.db.models import email_summary_model
from app.db.schemas.EmailSummary import EmailSummary


def list_summary_by_user_id(user_id: int, session: SessionDep):
    try:
        statement = select(email_summary_model.EmailSummary).where(email_summary_model.EmailSummary.user_id == user_id)
        result =  session.execute(statement).all()
        summary_list = []
        for row in result:
            summary_list.append(row.EmailSummary.__dict__)

        return summary_list
    except Exception as e:
        print(e)


def generate_mail_summary(email: dict):
    system_prompt = "You are Siksha Sathi AI.Your task is to read an email and rewrite it in simple, clear English that even a small child can understand. Do not add introductions like 'Here's the summary' or 'This is what the email says'. Just output the simplified summary itself — nothing else. You naver reply in markdown format"

    input_prompt = f" Simplify this raw email message: {email} "

    chat_completion = AI_Client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": input_prompt,
            },
        ],
        model="llama-3.3-70b-versatile",
    )

    response = chat_completion.choices[0].message.content

    return response


def save_mail_summary(user_id: int, message_id: str, summary: str, session: SessionDep):
    try:

        validated_email_summary = EmailSummary(
            user_id=user_id,
            message_id=message_id,
            summary=summary
        )

        new_email_summary = email_summary_model.EmailSummary(**validated_email_summary.model_dump())

        session.add(new_email_summary)
        session.commit()
        session.refresh(new_email_summary)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_email_summary
