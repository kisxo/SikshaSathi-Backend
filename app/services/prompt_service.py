from sqlalchemy import select
from app.db.models import prompts_model
from app.db.session import SessionDep

# Existing functions omitted for brevity…

def get_prompt_by_id(prompt_id: int, session: SessionDep):
    stmt = select(prompts_model.Prompt).where(prompts_model.Prompt.id == prompt_id)
    result = session.execute(stmt).scalar_one_or_none()
    return result

def get_prompt_by_name(name: str, session: SessionDep):
    stmt = select(prompts_model.Prompt).where(prompts_model.Prompt.name == name)
    result = session.execute(stmt).scalar_one_or_none()
    return result
