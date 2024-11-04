import logging
import uuid
from googleapiclient.discovery import build

# Set up logging
logger = logging.getLogger(__name__)

def insert_table_into_slide(service, presentation_id, slide_id, data_frame):
    """Insert a table into a specific slide of a Google Slides presentation."""
    try:
        # Generate unique ID for the table
        table_id = f'table_{uuid.uuid4().hex}'

        # Reset the index, but don't include it in the table
        data_frame_with_index = data_frame.reset_index()  # Reset index but don't keep it as a column
        num_rows, num_cols = data_frame_with_index.shape

        # Create a table in the existing slide
        create_table_request = [
            {
                'createTable': {
                    'objectId': table_id,
                    'elementProperties': {
                        'pageObjectId': slide_id,
                    },
                    'rows': num_rows + 1,  # Add 1 row for headers
                    'columns': num_cols
                }
            }
        ]
        
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': create_table_request}
        ).execute()

        # Prepare requests for inserting headers and data
        table_cells = []

        # Add headers
        headers = list(data_frame_with_index.columns)
        for c in range(num_cols):
            table_cells.append(
                {
                    'insertText': {
                        'objectId': table_id,
                        'cellLocation': {'rowIndex': 0, 'columnIndex': c},
                        'text': str(headers[c])
                    }
                }
            )
        
        # Add data (excluding the index)
        for r in range(num_rows):
            for c in range(num_cols):
                table_cells.append(
                    {
                        'insertText': {
                            'objectId': table_id,
                            'cellLocation': {'rowIndex': r + 1, 'columnIndex': c},
                            'text': str(data_frame_with_index.iloc[r, c])
                        }
                    }
                )
        
        # Execute batchUpdate to insert text into the table cells
        service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': table_cells}
        ).execute()

        logger.info(f'Table inserted into slide with ID: {slide_id}')
    except Exception as e:
        logger.error(f'Error inserting table into slide: {e}')

def get_slide_ids(slides_service, presentation_id):
    """Retrieve slide IDs from the presentation."""
    try:
        presentation = slides_service.presentations().get(presentationId=presentation_id).execute()
        slides = presentation.get('slides', [])
        slide_ids = [slide.get('objectId') for slide in slides]
        return slide_ids
    except Exception as e:
        logger.error(f'Error fetching slide IDs: {e}')
        return []
