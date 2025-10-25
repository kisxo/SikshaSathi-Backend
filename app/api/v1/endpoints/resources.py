from pydoc_data.topics import topics

from fastapi import APIRouter, HTTPException, Depends
from app.core.security import authx_security, auth_scheme
from authx import TokenPayload
from app.db.session import SessionDep
from app.db.schemas.user import User, UserCreate, UserPublic, UsersPublic
from app.core.security import hash_password
from app.db.models import user_model
from app.db.schemas.resource import ResourceForm
from app.core.ai import AI_Client
from app.core.config import settings
import json
from app.db.schemas.resource import ResourceCreate
from app.db.models import resources_model
from app.services import resource_service

from googleapiclient.discovery import build

router = APIRouter()


@router.get("/yt",
     dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
     )
async def get_ai_resources(
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    resources = resource_service.list_user_resources(payload.user_id, "videos", session=session)
    if not resources:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Resources not found")

    return {'data': resources}

@router.post("/yt",
dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def generate_resources(
    input_data: ResourceForm,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    raw_prompt = input_data.topic

    generate_yt_query_prompt = f"""
    You are a smart assistant that converts any raw user input into a concise YouTube search query.
    Instructions:
    - Take the given raw_prompt and create a short, natural search line for YouTube.
    - do not make it too longer.
    - Focus on relevance and clarity.
    - Output ONLY the final search line, in plain English. No quotes, explanations, or JSON.

    Raw_prompt: "{raw_prompt}"
    """

    chat_completion = AI_Client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": generate_yt_query_prompt,
            },
        ],
        model="llama-3.1-8b-instant",
    )

    yt_query = chat_completion.choices[0].message.content

    api_key = settings.YT_API
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.search().list(q=yt_query, part="snippet", type="video", maxResults=10)
    response = request.execute()

    videos = [
        {
            "title": item["snippet"]["title"],
            "videoId": item["id"]["videoId"],
            "url": f'https://www.youtube.com/watch?v={item["id"]["videoId"]}'
        }
        for item in response.get("items", [])
        if item["id"]["kind"] == "youtube#video"  # ensures it's a video, not a channel/playlist
    ]

    yt_resources= {
        "topic": input_data.topic,
        "recommended_videos": videos
    }
    try:

        # Validate with Pydantic model
        validated_resource = ResourceCreate(
            data=yt_resources,
            resource_type="videos",
            user_id=payload.user_id
        )

        # Save to database
        new_resource = resources_model.Resource(**validated_resource.model_dump())
        session.add(new_resource)
        session.commit()
        session.refresh(new_resource)

        return new_resource

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Resource Data is not valid JSON")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return book_data




@router.get("/books",
     dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
     )
async def get_ai_resources(
        session: SessionDep,
        payload: TokenPayload = Depends(authx_security.access_token_required),
):
    resources = resource_service.list_user_resources(payload.user_id, "books", session=session)
    if not resources:
        # Return 404 if not found
        raise HTTPException(status_code=404, detail="Resources not found")

    return {'data': resources}



@router.post("/books",
dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def generate_resources(
    input_data: ResourceForm,
    session: SessionDep,
payload: TokenPayload = Depends(authx_security.access_token_required),
):
    topic = input_data.topic  # change this to any topic
    data_format = '{"topic":"<string>","recommended_books":[{"category":"<string>","books":[{"Book_name":"<book title>","Year_of_publication":"<YYYY>","source":"<optional URL or empty string>","Publisher":"<optional name of publisher or empty strin>","Authors":"<name of authors>","ISBN":"<ISBN on book>"},{"Book_name":"<book title>","Year_of_publication":"<YYYY>","source":"<optional URL or empty string>","Publisher":"<optional name of publisher or empty strin>","Authors":"<name of authors>","ISBN":"<ISBN on book>"},{"Book_name":"<book title>","Year_of_publication":"<YYYY>","Publisher":"<optional name of publisher or empty strin>","Authors":"<name of authors>","source":"<optional URL or empty string>","ISBN":"<ISBN on book>"}]}]}'

    system_prompt = f"""
    You are an assistant named Siksha Sathi AI.
    Task: Based on the provided topic, suggest relevant and verifiable study-related books.

    STRICT RULES (must follow exactly):

    1. Output ONLY a single JSON object — no greetings, explanations, markdown, or code fences.


    2. The JSON must follow this exact structure:

    {data_format}


    3. Category mapping (use these canonical names when the topic matches exactly, case-insensitive):

    NEET => Physics, Chemistry, Biology, Mock Tests

    JEE => Physics, Chemistry, Mathematics, Mock Tests

    CUET => English, Aptitude, Domain Subjects, Previous Papers

    UPSC => Prelims, Mains, General Studies, Optional Subjects, Current Affairs

    Other topics: infer 2–3 logical categories and use simple canonical names (e.g., "Core", "Supplementary").



    4. Each category MUST contain exactly 3 books. Do not output fewer or more.


    5. Prefer books published 2018–2025. Allow canonical older texts if still widely used; when older texts are used, set Year_of_publication to the actual year.


    6. If a book title or publication year cannot be verified confidently, DO NOT invent it. Instead, output exactly:
    {{ "error": "no relevant books found" }}


    7. Book_name must be short, realistic, and directly relevant to the category. Do NOT include author names, publisher names, prices, or commentary inside Book_name.


    8. Year_of_publication must be a 4-digit year string (e.g., "2025").


    9. The "source" field is optional. If a reliable URL is known (publisher page, ISBN entry, or official exam resource), include it; otherwise set it to an empty string "".


    10. Do NOT add any fields beyond the ones specified above.


    11. JSON Object must be valid and parseable: properly quoted, no trailing commas, no commentary.


    12. Output language must be English.


    13. If the topic is ambiguous or contains typos, attempt the best interpretation using canonical mappings (do not ask clarifying questions).
    """

    user_prompt = f"""
    Generate a JSON response for the topic below:
    Topic: {topic}

    Goal: Recommend up-to-date, verifiable study-related books (latest editions when available) relevant to this topic.
    Automatically organize the books into relevant categories inferred from the exam or study topic.
    Return only valid JSON following the specified structure and rules in the system prompt.
    """

    chat_completion = AI_Client.chat.completions.create(
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

    book_data = json.loads(chat_completion.choices[0].message.content)

    try:

        # Validate with Pydantic model
        validated_resource = ResourceCreate(
            data=book_data,
            resource_type="books",
            user_id=payload.user_id
        )

        # Save to database
        new_resource = resources_model.Resource(**validated_resource.model_dump())
        session.add(new_resource)
        session.commit()
        session.refresh(new_resource)

        return new_resource

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Resource Data is not valid JSON")

    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Something went wrong!")

    return book_data


@router.delete(
    "/{resources_id}",
    # response_model = EmailSummariesPublic,
    dependencies=[Depends(authx_security.access_token_required), Depends(auth_scheme)],
)
async def delete_mail_summary(
    resources_id: int,
    session: SessionDep,
    payload: TokenPayload = Depends(authx_security.access_token_required),
):
    resource_in_db = session.get(resources_model.Resource, resources_id)

    if resource_in_db.user_id != payload.user_id:
        raise HTTPException(status_code=400, detail="Does not have permission to delete mail resource!")

    try:
        session.delete(resource_in_db)
        session.commit()
    except Exception as e:
        print("Delete error:", e)
        session.rollback()
        raise HTTPException(status_code=400, detail="Failed to delete email summary!")

    return {
        "message": "Resource deleted successfully",
        "deleted_id": resources_id
    }