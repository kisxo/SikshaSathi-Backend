from fastapi import FastAPI
from app.core.security import authx_security
from app.startup import startup
from app.api import api_router
from app.openapi_docs import doc
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=doc.title,
    summary=doc.summary,
    openapi_tags=doc.tags_metadata,
    on_startup=[startup],
    contact=doc.contact,
    servers=[
        {"url": "/api", "description": "Default api URL Route"},
    ],
    root_path="/api",
)

origins = [
    "http://magicminute.online",
    "https://magicminute.online",
    "http://localhost:8081",
    "https://localhost:8081",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    # this regex allows request from both http and https and any port
    # allow_origin_regex = "^(http|https)://localhost(:([0-9]|[1-9][0-9]{1,4}))?$",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

authx_security.handle_errors(app)

@app.get("/",
    name= "Api Status",
    description= """
        Root route to check the status of the Backend.
            """,
    tags=["Root"]
         )
async def root():
    return {"status":"true", "message": "Api server is up and running"}

app.include_router(api_router.router)