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
from app.services import profile_service

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
    data_format = '{"title":"Prepare for exam-name Exam","description":"Focus on Biology, Physics, and Chemistry for medical entrance","todos":[{"title":"Eligibility checklist","checklists":[{"item":"Check age eligibility","is_done":false},{"item":"Verify educational qualifications","is_done":false},{"item":"Ensure required documents","is_done":false}]},{"title":"Syllabus breakdown","checklists":[{"item":"Biology: Study cellular structure and functions","is_done":false},{"item":"Biology: Focus on genetics and evolution","is_done":false},{"item":"Physics: Understand mechanics and motion","is_done":false},{"item":"Physics: Study electromagnetism and optics","is_done":false},{"item":"Chemistry: Learn organic and inorganic chemistry","is_done":false},{"item":"Chemistry: Focus on physical chemistry and labs","is_done":false}]},{"title":"Daily/Weekly study plan","checklists":[{"item":"Study 4 hours daily, 5 days a week","is_done":false},{"item":"Practice 1 previous year paper weekly","is_done":false},{"item":"Review notes daily for 30 minutes","is_done":false}]},{"title":"Mock tests & evaluation","checklists":[{"item":"Take 1 mock test every 2 weeks","is_done":false},{"item":"Evaluate performance and identify weak areas","is_done":false},{"item":"Track progress and adjust study plan","is_done":false}]},{"title":"Revision & retention plan","checklists":[{"item":"Revise notes every 3 days","is_done":false},{"item":"Use flashcards for key terms","is_done":false},{"item":"Teach someone what you learned","is_done":false}]},{"title":"Resources","checklists":[{"item":"NCERT Biology, Physics, and Chemistry textbooks","is_done":false},{"item":"Online practice platforms like Unacademy, Vedantu","is_done":false},{"item":"Previous year papers and mock tests","is_done":false}]},{"title":"Final checklist before exam","checklists":[{"item":"Admit card and ID proof","is_done":false},{"item":"Stationery and water bottle","is_done":false},{"item":"Reach exam center 1 hour before","is_done":false}]}]}'

    system_prompt = """
    You are an assistant named ExamPlanner.
    Task: Read the exam name and produce exactly one JSON object (only JSON) that is a practical to-do list for the requested exam, interview, or study topic.
    OUTPUT CONSTRAINT (mandatory):
    - Return exactly one JSON object and nothing else. No leading/trailing text, no explanations, no markdown, no code fences, and no additional attachments.
    SCHEMA & FIELD RULES (must follow exactly):
    - Overall structure must follow the canonical fields: id, title, description, target_date, status, priority, progress, todos.
    - Fields may be omitted only if explicitly allowed by the JSON Schema below.
    - id fields: optional. If present, id must be either null or a non-numeric string. Do NOT generate numeric ids.
    - title: required, string, concise and actionable. Max length 100 characters.
    - description: required, string. Short summary only — do not include multi-paragraph instructions here.
    - target_date: required, string in ISO format YYYY-MM-DD.
    - status (top-level and per-todo): required; allowed values: "todo", "in_progress", "done", "blocked".
    - priority (top-level and per-todo): required; allowed values: "low", "medium", "high".
    - progress: required; integer 0..100. If feasible, compute progress as the percentage of top-level todos whose status == "done" (rounded to nearest integer). If not computed, provide a reasonable integer estimate.
    - todos: required; array of todo objects ordered from highest priority/earliest to lowest.
    - todo object required fields: title, status, priority, checklists.
    - todo.id: optional; if present must be null or a non-numeric string.
    - duration: optional; if present must follow "<number> <unit>" where unit ∈ days|weeks|months|years (e.g., "2 weeks").
    - checklists: required; array of checklist objects.
    - checklist object must include: item (string) and is_done (boolean). checklist.id is optional (null or non-numeric string) if present.
    - Booleans must be literal true/false (no quotes).
    - Do NOT add any fields beyond: id, title, description, target_date, status, priority, progress, todos, checklists, duration. (If you need to include resources or notes, add them as checklist items.)
    - Arrays preserve order: earlier items = earlier/higher priority.
    FORMAT & VALIDITY (must follow exactly):
    - JSON must be valid and parseable: proper quoting, no trailing commas.
    - Dates must match regex YYYY-MM-DD.
    - Durations must match regex "^[0-9]+ (days|weeks|months|years)$".
    - Titles must be ≤100 characters.
    - If a required constraint cannot be met, output exactly one JSON object: {"error": "reason for failure"} (no other text).
    LANGUAGE:
    - Output language must be English.
    BEHAVIOR FOR UNKNOWN/AMBIGUOUS EXAMS:
    - If the exam name is ambiguous or not in typical examples, infer a short, realistic prep plan appropriate to the exam type (academic, government, professional). Do not ask clarifying questions.
    ADDITIONAL NOTES FOR DEBUGGING:
    - Keep each todo title short and actionable (example phrasing: "Read chapter 1 and make notes", "Attempt one mock test").
    - Use checklist items for fine-grained steps.
    - Generate large set up checklist for full coverage of topic
    - Syllabus topics must have at least 10 checklists
    - Progress computation is optional on the model side; server-side deterministic recomputation is recommended for production systems.
    """

    user_data = profile_service.get_profile_by_user_id(payload.user_id, session)
    if user_data:
        user_data = user_data.__dict__

    user_prompt = f"""
    Use the canonical example JSON and Schema above. Generate a to-do list for: exam-name= {input_data.exam_name} target-date= {input_data.target_date}
    Goal: Produce a clear, actionable to-do list for {input_data.exam_name} preparation that a student can follow.
    Requirements:
    - Output exactly one JSON object (only JSON) that validates against the provided JSON Schema.
    - Put short, actionable steps in todo titles and checklist items.
    - Provide rough timing estimates using `duration` for major phases where appropriate.
    - Do not include any paragraph text outside `description`.
    - If you cannot comply, return {{ "error": "reason for failure" }} as the sole output.
    
    here are some user data so you tailor output based on this {user_data}
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
        model="llama-3.1-8b-instant",
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




@router.get("/my-goals",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_goals(
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    goals = goal_service.list_user_goals(payload.user_id, session=session)
    if not goals:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Goals not found")

    return {'data': goals}




@router.get("/{goal_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def get_goal(
        goal_id: int,
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):

    goal = goal_service.get_user_goal(goal_id, session=session)

    if not goal:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Goals not found")

    if not payload.user_is_admin and goal.user_id != payload.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    return {'data': goal}




@router.delete(
    "/{goal_id}",
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def delete_goal(
    goal_id: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    goal_in_db = session.get(goal_model.Goal, goal_id)

    if goal_in_db.user_id != payload.user_id:
        raise HTTPException(status_code=400, detail="Does not have permission to delete goal!")

    try:
        session.delete(goal_in_db)
        session.commit()
    except Exception as e:
        print("Delete error:", e)
        session.rollback()
        raise HTTPException(status_code=400, detail="Failed to delete goal!")

    return {
        "message": "Goal deleted successfully",
        "deleted_id": goal_id
    }