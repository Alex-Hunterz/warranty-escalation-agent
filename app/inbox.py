"""
Inbox layer: real Gmail (OAuth) when credentials.json is present,
otherwise a realistic demo inbox so the full flow works end-to-end.

Real mode requirements:
  - app/credentials.json  (OAuth client from Google Cloud Console, Gmail API enabled)
  - pip install google-api-python-client google-auth-oauthlib
Token is cached at app/token.json after first consent.
"""
import base64
import os
import re
from typing import Any, Dict, List

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(APP_DIR, "credentials.json")
TOKEN_PATH = os.path.join(APP_DIR, "token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


# ------------------------------------------------- seeded evidence (real case)
DEMO_EMAILS: List[Dict[str, Any]] = [
    {
        "id": "r1",
        "thread_id": "t_support",
        "from": "Manit Bohra <bohra.manit@gmail.com>",
        "to": "Nothing Support <support.india@nothing.tech>",
        "date": "2026-04-06",
        "subject": "Patch/bubble inside Glyph Matrix — Nothing Phone (4a) Pro [Ticket #1700763]",
        "body": (
            "Dear Nothing India Support Team,\n\n"
            "I'm writing regarding an ongoing issue with my Nothing Phone 4a Pro "
            "(Serial No: 357998630967556), received on 23 March 2026.\n\n"
            "Within 2 days of receiving the device, I noticed a patch/bubble inside the Glyph Matrix. "
            "I initially assumed it was cosmetic and would resolve on its own. When it persisted, I raised "
            "a support ticket on 29 March (Ticket #1700763). At the time, your team suggested it was a "
            "pressure-related mark that would disappear within about 10 minutes; however it has now been "
            "over a week and the mark is still very much there.\n\n"
            "We then raised a complaint with Flipkart, who passed it on to the Nothing authorized service "
            "centre in Indiranagar, Bengaluru. A job was created (J260403NTASP156112165), and the service "
            "report noted the issue as \"water patches inside the Glyph Matrix\". The device was then "
            "\"kept under a temperature of 35°C, after which it was found to be working properly\" — however "
            "when I received the device back, there was absolutely no change. The issue was not resolved.\n\n"
            "I bought this phone brand new and I'm genuinely worried that the device may not be properly "
            "sealed, which could cause bigger problems down the line. The Nothing Phone 4a Pro is a recently "
            "launched device and I was among the first people to buy it — this really shouldn't be the "
            "experience for a brand new phone.\n\n"
            "I would really appreciate a replacement unit that doesn't have this issue. Could you please "
            "advise on the next steps?\n\nThank you,\nManit Bohra\nContact: 7042929394\n"
            "Ticket: #1700763 | Job No: J260403NTASP156112165"
        ),
    },
    {
        "id": "r2",
        "thread_id": "t_support",
        "from": "Nothing Support <support.india@nothing.tech>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-04-07",
        "subject": "A message from Nothing Support — request (1715515) updated",
        "body": (
            "Misty Gyanajherar Nadar (Nothing India) — Apr 7, 2026, 15:29 GMT+5:30\n\n"
            "Hi Manit,\n\nThank you for contacting Nothing India Support.\n\n"
            "We sincerely apologize for any inconvenience that has been caused to you. We're here to assist "
            "you with the issues you're experiencing with your Nothing Phone (4a) Pro.\n\n"
            "We kindly request that you provide images of the patch or bubble issue you are experiencing, "
            "so that we may review the concern and assist you further.\n\n"
            "Kind Regards,\nLuckysha Nadar\nNothing Support Team\n\n"
            "This email is a service from Nothing India. Delivered by Zendesk"
        ),
    },
    {
        "id": "r3",
        "thread_id": "t_support",
        "from": "Manit Bohra <bohra.manit@gmail.com>",
        "to": "Nothing Support <support.india@nothing.tech>",
        "date": "2026-04-08",
        "subject": "Re: request (1715515) — formally requesting replacement or refund",
        "body": (
            "Hi,\n\nThank you for your response. I appreciate the suggestion, however visiting the service "
            "centre again is not convenient for me as it is quite far from where I am based.\n\n"
            "More importantly, I'd like to highlight something. I raised the return/replacement request with "
            "Flipkart within the first week of receiving the device — well within any reasonable window for a "
            "defective product. At that point, I was clearly asking for a replacement. Instead of that being "
            "processed, the device was sent to the Nothing authorized service centre in Indiranagar "
            "(Job No: J260403NTASP156112165), which took another week on top of that. The service report then "
            "stated the issue was resolved — but when I received the phone back, nothing had changed. The "
            "patch/bubble is still there, exactly as it was from day one.\n\n"
            "So to summarise: I flagged this early, I asked for a replacement early, and instead I went "
            "through a repair process that didn't work and ate up another week of my time.\n\n"
            "As per Nothing's own policy, a defective product reported within 30 days of delivery entitles "
            "the customer to a repair, replacement, or refund. I am still well within that window and I am "
            "formally requesting a replacement or refund. I would appreciate this being escalated rather "
            "than being directed to visit a service centre again.\n\n"
            "Thank you,\nManit Bohra\nContact: 7042929394\n"
            "Ticket: #1700763 | Job No: J260403NTASP156112165\n"
            "Attachment(s): response.jpeg"
        ),
    },
    {
        "id": "r4",
        "thread_id": "t_support",
        "from": "Nothing Support <support.india@nothing.tech>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-04-08",
        "subject": "Re: request (1715515) — no refund policy, visit service center",
        "body": (
            "Shaikh Mohd Naushad Ali (Nothing India) — Apr 8, 2026, 12:27 GMT+5:30\n\n"
            "Hi Manit,\n\nThank you for contacting Nothing India Support.\n\n"
            "We sincerely apologize for the inconvenience you are experiencing and fully understand your "
            "concern. However, we would like to inform you that we do not have a refund policy in place. "
            "For any refund requests, we kindly ask you to reach out to the seller directly. Regarding a "
            "replacement or any other resolution, we recommend visiting the service center, where a "
            "technician will be able to diagnose your device and provide assistance based on their "
            "assessment. We appreciate your understanding and encourage you to visit the service center "
            "for further support.\n\n"
            "For more details, please visit our warranty policy page: "
            "https://in.nothing.tech/pages/warranty-policy\n\n"
            "Kind Regards,\nShaikh Daanish\nNothing Support Team"
        ),
    },
    {
        "id": "m1",
        "thread_id": "t_order",
        "from": "Flipkart <order-update@flipkart.com>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-03-20",
        "subject": "Your Flipkart order OD43311992 is confirmed — Nothing Phone (4a) Pro",
        "body": (
            "Hi Manit,\n\nThank you for shopping with Flipkart!\n\n"
            "Order ID: OD43311992\nItem: Nothing Phone (4a) Pro 5G (Grey, 256 GB)\n"
            "Amount Paid: Rs. 27,999 (UPI)\nSold by: RetailNet\n"
            "Invoice number: FAABJV2600841\nDelivery expected: 23 Mar 2026\n\n"
            "Warranty: 1 year manufacturer warranty from Nothing India.\n"
        ),
    },
    {
        "id": "m2",
        "thread_id": "t_order",
        "from": "Flipkart <order-update@flipkart.com>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-03-23",
        "subject": "Delivered: Nothing Phone (4a) Pro — Order OD43311992",
        "body": "Your item Nothing Phone (4a) Pro 5G was delivered on 23 Mar 2026. Invoice attached (PDF).",
    },
    {
        "id": "m8",
        "thread_id": "t_noise1",
        "from": "Swiggy <no-reply@swiggy.in>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-04-19",
        "subject": "Your order from Meghana Foods is on the way",
        "body": "Rider assigned. ETA 24 mins.",
    },
    {
        "id": "m9",
        "thread_id": "t_noise2",
        "from": "Nothing <news@nothing.tech>",
        "to": "bohra.manit@gmail.com",
        "date": "2026-04-10",
        "subject": "Nothing OS 4.0 is here",
        "body": "Newsletter: meet the new Nothing OS with smarter Glyphs.",
    },
]


class DemoInbox:
    mode = "demo"

    def search(self, terms: List[str], max_results: int = 20) -> List[Dict[str, Any]]:
        terms_l = [t.lower() for t in terms if t.strip()]
        hits = []
        for m in DEMO_EMAILS:
            hay = (m["subject"] + " " + m["body"] + " " + m["from"]).lower()
            score = sum(1 for t in terms_l if t in hay)
            if score > 0:
                hits.append((score, m))
        hits.sort(key=lambda x: (-x[0], x[1]["date"]))
        return [m for _, m in hits[:max_results]]

    def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        return [m for m in DEMO_EMAILS if m["thread_id"] == thread_id]


class GmailInbox:
    """Real Gmail via OAuth. Raises on any setup problem so caller can fall back."""

    mode = "gmail"

    def __init__(self):
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())
        self.service = build("gmail", "v1", credentials=creds)

    def search(self, terms: List[str], max_results: int = 20) -> List[Dict[str, Any]]:
        q = " OR ".join(f'"{t}"' for t in terms if t.strip()) or "warranty"
        res = self.service.users().messages().list(userId="me", q=q, maxResults=max_results).execute()
        out = []
        for ref in res.get("messages", []):
            out.append(self._fetch(ref["id"]))
        return out

    def get_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        th = self.service.users().threads().get(userId="me", id=thread_id, format="full").execute()
        return [self._parse(m) for m in th.get("messages", [])]

    def _fetch(self, msg_id: str) -> Dict[str, Any]:
        msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        return self._parse(msg)

    def _parse(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
        return {
            "id": msg["id"],
            "thread_id": msg["threadId"],
            "from": headers.get("from", ""),
            "to": headers.get("to", ""),
            "date": headers.get("date", ""),
            "subject": headers.get("subject", ""),
            "body": self._body(msg["payload"]) or msg.get("snippet", ""),
        }

    def _body(self, payload: Dict[str, Any]) -> str:
        if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
        for part in payload.get("parts", []) or []:
            text = self._body(part)
            if text:
                return re.sub(r"\n{3,}", "\n\n", text)
        return ""


def get_inbox():
    """Prefer real Gmail when configured; otherwise demo inbox."""
    if os.path.exists(CREDENTIALS_PATH):
        try:
            return GmailInbox()
        except Exception as e:
            print(f"[inbox] Gmail auth failed ({e}); using demo inbox")
    return DemoInbox()
