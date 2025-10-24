from app.core.config import settings

from groq import Groq

AI_Client = Groq(
    api_key=settings.GROQ_API,
)