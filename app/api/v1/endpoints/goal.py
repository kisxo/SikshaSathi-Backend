from app.core.config import settings
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from authx import TokenPayload
import httpx, base64, json
from app.db.session import SessionDep
from app.core.security import authx_security, auth_scheme
from app.services import mail_service, user_service
from app.db.models import goal_model
from app.db.schemas.goal import GoalGenerationForm, GoalCreate
from app.services import goal_service

from groq import Groq

client = Groq(
    api_key=settings.GROQ_API,
)

router = APIRouter()


@router.post("/generate",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def generate_goal(
        input_data: GoalGenerationForm,
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    data_format = '{"id":12,"title":"Prepare for CN Exam","description":"Focus on Unit 1–4 before midterm","target_date":"2025-11-15","status":"in_progress","priority":"high","progress":60,"todos":[{"id":101,"title":"Revise OSI Layers","status":"done","priority":"medium","checklists":[{"id":1001,"item":"Watch lecture","is_done":true},{"id":1002,"item":"Write summary notes","is_done":false}]},{"id":102,"title":"Practice previous papers","status":"todo","priority":"high","checklists":[{"id":1003,"item":"Attempt 2022 paper","is_done":false},{"id":1004,"item":"Attempt 2023 paper","is_done":false}]}]}'

    system_prompt = f"""
        You are an assistant named ExamPlanner.
        Task: Read the exam entries the user provides and produce a direct, goal, with todos and checklists for the requested exam, interview, study topic.
        Constraints:
        - Output ONLY the to-do list. Do not add introductions, labels, or commentary (no "Here is", "Summary:", or similar).
        - Keep language very simple — a child should understand each item.
        - Use the structure and fields present in the provided data (exam_eligibility, recomended_topics, exam_details, career_scope) as templates for building tasks.
        - If the requested exam (e.g., NEET) is not present in the provided data, infer missing NEET-specific topics and steps using typical medical-entrance exam patterns, but keep the output concise and practical.
        - Present tasks as short numbered steps and group them into clear sections (Eligibility checklist, Syllabus break-down, Daily/Weekly study plan, Mock tests & evaluation, Revision & retention, Resources, Final checklist).
        - Include approximate timing for each major block (e.g., 2 weeks, 3 months) as simple suggestions.
        - Only output in correct JSON data format, demo data {data_format}
        - do not generate id
        - generate a good title, description
    """

    user_prompt = f"""
        Use the exam entries below as reference examples. Now generate a to-do list for: NEET
        Goal: Produce a simple, actionable to-do list for NEET exam preparation that a young student can follow. Start directly with the tasks — do NOT add any preamble or explanation. Use short, numbered items and grouped sections.
        Output format hints (follow these, but keep output minimal):
        1) Eligibility checklist:
        1. ...
        2) Syllabus breakdown:
        1. Biology — short actionable tasks
        2. Physics — ...
        3) Daily / Weekly study plan (what to do each day/week)
        4) Mock tests & evaluation (how often, what to track)
        5) Revision & retention plan (spaced repetition schedule)
        6) Resources (compact list: book names/online practice)
        7) Final checklist before exam (documents, health, timing)

        Now produce the to-do list.
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        model="llama-3.3-70b-versatile",
    )

    goal_data = chat_completion.choices[0].message.content

    try:

        # Validate with Pydantic model
        validated_goal = GoalCreate(
            data=goal_data,
            user_id=payload.user_id
        )

        # Save to database
        new_goal = goal_model.Goal(**validated_goal.model_dump())
        session.add(new_goal)
        session.commit()
        session.refresh(new_goal)

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="AI output is not valid JSON")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return new_goal




@router.post("/my-goals",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def generate_goal(
        input_data: GoalGenerationForm,
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    goals = goal_service.list_user_goals(payload.user_id, session=session)
    if not goals:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Goals not found")

    return {'data': goals}