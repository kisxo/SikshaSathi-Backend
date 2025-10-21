title = "Anganwadi management backend API - AsyncMind"

summary = "This is the documentation of Fastapi API developed by Uday Subba."

contact = {
    "name": "Email- Uday Subba",
    "email": "udaysubba2004@gmail.com"
}

tags_metadata = [
    {
        "name": "Authentication",
        "description":
            """Authentication is required before using the API.
            Every API method requires the same authentication process.<br>
            <br>
            Header: JWT Bearer Auth<br>
            Format in header: `Authorization: Bearer <JWT-Token>`<br>
            <br>
            Every JWT-Token will be valid for 10 hours from the time of generation.<br>
            Example JSON request with authentication headers: Let the say the `JWT-Token = eyJhbGciOiJSUzI1.....`
    
        {
            "url": "https://magicminute.online/api/v1/students",
            "method": "POST",
            "headers": {
                "Authorization": "Bearer eyJhbGciOiJSUzI1.....",
            },
            "data": request_data
        }   
    """,
    }
]