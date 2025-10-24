import httpx
from fastapi import HTTPException
import base64
from app.db.models import Email_model
from sqlalchemy.orm import Session
import json

def fetch_gmail_message(access_token: str, message_id: str):
    """
    Fetch full Gmail message using stored access token.
    """
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"format": "full"}

    try:
        r = httpx.get(url, headers=headers, params=params)
        r.raise_for_status()
        msg = r.json()

        headers_map = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        body = extract_email_body(msg.get("payload", {}))

        return {
            "id": msg["id"],
            "threadId": msg.get("threadId"),
            "from": headers_map.get("From"),
            "to": headers_map.get("To"),
            "subject": headers_map.get("Subject"),
            "date": headers_map.get("Date"),
            "body": body,
        }

    except httpx.HTTPStatusError as e:
        print("Gmail API error:", e.response.text)
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        print("Error fetching Gmail message:", e)
        raise HTTPException(status_code=500, detail=str(e))




def extract_email_body(payload):
    """Recursively extract and decode the email body (HTML or plain text)."""
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            if mime_type in ["text/html", "text/plain"]:
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            inner_body = extract_email_body(part)
            if inner_body:
                return inner_body
    else:
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return "(No content found)"


def start_gmail_watch(access_token: str, topic_name: str):
    """
    Start Gmail push notifications for the user.

    Parameters:
        access_token: str - OAuth2 access token of the user
        topic_name: str - Fully qualified Pub/Sub topic name, e.g.,
            "projects/YOUR_PROJECT_ID/topics/gmail-notifications"

    Returns:
        dict - Response from Gmail API containing historyId
    """
    url = "https://gmail.googleapis.com/gmail/v1/users/me/watch"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "topicName": topic_name,
        "labelIds": ["INBOX"],  # only watch inbox
        "labelFilterAction": "include"  # include only these labels
    }

    response = httpx.post(url, headers=headers, json=body)

    if response.status_code != 200:
        print("Failed to start Gmail watch:", response.text)
        response.raise_for_status()

    return response.json()



def fetch_user_gmail_latest_message_id(access_token: str):
    """
    Fetch Gmail messages using an always-valid token.
    """

    headers = {"Authorization": f"Bearer {access_token}"}
    gmail_api_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": 1}

    response = httpx.get(gmail_api_url, headers=headers, params=params, timeout=10.0)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    messages = data.get("messages", [])

    if not messages:
        return None  # no messages found

    # Return the ID of the first message
    return messages[0]["id"]



def save_gmail(user_id: int, msg: dict, session: Session):
    """
    Save a Gmail message to the database.
    `msg` should be a dict with keys: id, threadId, from, to, subject, date, body
    """
    try:
        gmail_msg = Email_model.Email(
            user_id=user_id,
            message_id=msg["id"],
            thread_id=msg.get("threadId"),
            sender=msg.get("from"),
            recipient=msg.get("to"),
            subject=msg.get("subject"),
            date=msg.get("date"),
            body=msg.get("body"),
            raw=json.dumps(msg)
        )
        session.add(gmail_msg)
        session.commit()
        return gmail_msg.__dict__
    except Exception as e:
        session.rollback()
        print("Error saving email:", e)
        return None