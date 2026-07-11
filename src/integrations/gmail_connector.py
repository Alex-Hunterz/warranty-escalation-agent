"""
Gmail Connector (Optional Integration)
Auto-extract warranty case data from user's Gmail emails.

NOT REQUIRED for demo. Architecture only.
Can be integrated later for production use.
"""

from typing import List, Dict, Any, Optional
import json

class GmailConnector:
    """
    Connect to user's Gmail (with OAuth consent).
    Search for warranty-related emails.
    Extract case data automatically.

    Usage:
    ```python
    gmail = GmailConnector()
    gmail.authenticate()  # Opens OAuth flow
    cases = gmail.search_warranty_emails()
    case_data = gmail.parse_email_thread(cases[0])
    ```
    """

    def __init__(self):
        self.service = None
        self.user_email = None
        self.authenticated = False

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API (requires user OAuth consent).

        Steps:
        1. User clicks "Connect Gmail"
        2. Redirects to Google OAuth flow
        3. User grants permission to read emails only (no send/delete)
        4. Returns access token
        """
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.service_account import Credentials
            from google.auth.oauthlib.flow import InstalledAppFlow
            from google.apps import gmail_v1

            # OAuth scopes (read-only)
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

            print("[GMAIL] Authenticating with Gmail API...")
            print("[GMAIL] ⚠️  User must grant permission to read emails only")
            print("[GMAIL] ℹ️  No emails will be sent, stored, or shared")

            # In production:
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     'credentials.json', SCOPES)
            # creds = flow.run_local_server(port=0)
            # self.service = build('gmail', 'v1', credentials=creds)

            print("[GMAIL] ✅ Authentication successful (simulated)")
            self.authenticated = True
            return True

        except Exception as e:
            print(f"[GMAIL] ❌ Authentication failed: {e}")
            return False

    def search_warranty_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Gmail for warranty-related emails.

        Keywords: "warranty", "refund", "defect", "replacement", "support ticket"
        """
        if not self.authenticated:
            print("[GMAIL] ❌ Not authenticated. Call authenticate() first.")
            return []

        print("[GMAIL] Searching for warranty-related emails...")

        query = 'subject:(warranty OR refund OR defect OR replacement OR support) OR body:(warranty OR defund OR defect)'

        # In production:
        # results = self.service.users().messages().list(
        #     userId='me', q=query, maxResults=max_results).execute()
        # messages = results.get('messages', [])

        # Simulated results
        simulated_results = [
            {
                "id": "msg_1",
                "subject": "Nothing Phone 4a Pro - Water patches in Glyph Matrix",
                "from": "support@nothing.tech",
                "date": "2026-04-08",
                "snippet": "Water patches in device..."
            }
        ]

        print(f"[GMAIL] Found {len(simulated_results)} warranty emails")
        return simulated_results

    def get_email_full_text(self, message_id: str) -> str:
        """
        Retrieve full email text for a message.
        """
        print(f"[GMAIL] Retrieving email {message_id}...")

        # In production:
        # message = self.service.users().messages().get(
        #     userId='me', id=message_id, format='full').execute()
        # payload = message['payload']
        # headers = payload['headers']
        # body_data = payload['parts'][0]['data']

        simulated_email = """
From: support@nothing.tech
To: manit_bohra@gmail.com
Date: Tue, 8 Apr 2026 12:27:31 +0530
Subject: A message from Nothing Support

Hi Manit,

Thank you for contacting Nothing India Support.

We sincerely apologize for the inconvenience you are experiencing...
[Email content continues...]
        """

        return simulated_email

    def extract_warranty_case(self, email_thread: str) -> Dict[str, Any]:
        """
        Parse email thread into structured case data.

        Extracts:
        - Product name & serial
        - Defect description
        - Timeline of communication
        - Company's SLA promises
        - Requested relief
        """
        print("[GMAIL] Parsing email thread into case data...")

        # In production, use LLM to parse:
        # from src.agents.extraction_agent import extract_case
        # case_obj = extract_case({
        #     "chat_thread": email_thread,
        #     "receipt_text": "",  # Would need to search separately
        #     ...
        # })

        case_data = {
            "source": "gmail",
            "email_subject": "Nothing Phone 4a Pro - Water patches issue",
            "product": "Nothing Phone 4a Pro",
            "serial": "357998630967556",
            "defect": "Water patches in Glyph Matrix",
            "defect_date": "2026-03-25",
            "company": "Nothing India",
            "ticket_number": "1700763",
            "chat_thread": email_thread,
            "extracted_at": "2026-04-08T14:30:00Z"
        }

        print("[GMAIL] ✅ Case extracted")
        return case_data

    def list_all_conversations(self) -> List[Dict[str, Any]]:
        """
        List all warranty-related conversation threads.
        Each thread = one case.
        """
        if not self.authenticated:
            return []

        print("[GMAIL] Listing warranty conversations...")

        # Simulated threads
        threads = [
            {
                "thread_id": "thread_1",
                "subject": "Nothing Phone 4a Pro - Defect",
                "messages_count": 7,
                "latest_date": "2026-04-08",
                "status": "unresolved"
            },
            {
                "thread_id": "thread_2",
                "subject": "Samsung TV - No Picture",
                "messages_count": 5,
                "latest_date": "2026-04-05",
                "status": "resolved"
            }
        ]

        return threads


def demo_gmail_connector():
    """Demo showing Gmail integration workflow."""
    print("\n" + "="*70)
    print("📧 GMAIL CONNECTOR DEMO (Architecture)")
    print("="*70)

    gmail = GmailConnector()

    print("\n[STEP 1] Authenticate with Gmail API")
    gmail.authenticate()

    print("\n[STEP 2] Search for warranty emails")
    emails = gmail.search_warranty_emails()
    for email in emails[:2]:
        print(f"  • {email['subject']}")

    print("\n[STEP 3] Extract case from email thread")
    if emails:
        full_email = gmail.get_email_full_text(emails[0]['id'])
        case = gmail.extract_warranty_case(full_email)
        print(f"  ✅ Extracted: {case['product']} - {case['defect']}")
        print(f"     Ticket: {case['ticket_number']}")
        print(f"     Status: {case_data.get('status', 'To be analyzed')}")

    print("\n[READY FOR NEXT STEPS]")
    print("  Case data can now be analyzed by the warranty agent:")
    print("  → Extraction Agent")
    print("  → Advocate Agent")
    print("  → ... (full pipeline)")

    print("\n" + "="*70)


if __name__ == "__main__":
    demo_gmail_connector()
