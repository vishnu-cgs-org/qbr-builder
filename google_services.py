from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Any
import logging
import gspread

# Scopes
scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/presentations'
]

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the JSON file with service account credentials
CREDENTIALS_FILE = 'gds-renewals-team-testing-b0346103fbfe.json'

class GoogleServices:
    def __init__(self, slides_service: Any, drive_service: Any, sheet_service: Any):
        self.slides_service = slides_service
        self.drive_service = drive_service
        self.sheet_service = sheet_service

def build_services() -> GoogleServices:
    try:
        service_creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
        services = GoogleServices(
            slides_service=build('slides', 'v1', credentials=service_creds),
            drive_service=build('drive', 'v3', credentials=service_creds),
            sheet_service=gspread.authorize(service_creds)  # Use gspread for sheets
        )
        return services
    except Exception as e:
        logger.error(f"Error creating Google services: {e}")
        raise
