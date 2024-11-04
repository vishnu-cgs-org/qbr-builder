import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from google_services import scope
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CREDENTIALS_FILE = 'gds-renewals-team-testing-b0346103fbfe.json'
SCOPES = scope

'''
 Important notes : This file is important when a new template has to be added 
The folder is in G drive 
Folder URL: https://drive.google.com/drive/u/0/folders/1bq-Ye0KYIKlz4y8ztxdyQ0qms6Rk1c2t
Folder text path: My Drive > qbr_builder > Sample QRR CDW 
Once the template is copied over, make sure that presentation id is added as a constant to the main.py
Constant name: TEMPLATE_PRESENTATION_ID
Make sure you share the presentation with "gr1tdatateam@gds-renewals-team-testing.iam.gserviceaccount.com"
This is the email of the service account that is added to the project

In case of a template source folder change:
Make sure that new folder is shared to this email as well

 '''

def create_drive_service():
    """Create a Google Drive service instance."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def get_folder_id(service, file_id):
    """Get the folder ID of the specified file."""
    try:
        file = service.files().get(fileId=file_id, fields='parents').execute()
        folder_id = file.get('parents')[0] if file.get('parents') else None
        return folder_id
    except Exception as e:
        logger.error(f'Error getting folder ID: {e}')
        return None

def copy_slide_presentation(service, source_presentation_id, new_presentation_name):
    """Copy a Google Slides presentation."""
    try:
        # Get the folder ID of the original presentation
        folder_id = get_folder_id(service, source_presentation_id)
        if not folder_id:
            logger.error('Folder ID could not be retrieved.')
            return None

        # Prepare the copy request with a timestamp in the name
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        body = {
            'name': f'{new_presentation_name}_{timestamp}',
            'parents': [folder_id]
        }

        # Copy the file
        copied_file = service.files().copy(fileId=source_presentation_id, body=body).execute()
        return copied_file.get('id')
    except Exception as e:
        logger.error(f'Error copying presentation: {e}')
        return None

def share_presentation(service, presentation_id, user_email):
    """Share the Google Slides presentation with a user."""
    try:
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': user_email
        }
        service.permissions().create(
            fileId=presentation_id,
            body=permission,
            fields='id'
        ).execute()
        logger.info(f'Successfully shared the presentation with {user_email}.')
    except Exception as e:
        logger.error(f'Error sharing presentation: {e}')
