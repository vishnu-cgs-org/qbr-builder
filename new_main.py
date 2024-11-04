import pandas as pd
import logging
import sys
from google_services import build_services
from create_slide import insert_table_into_slide, get_slide_ids
from create_drive import copy_slide_presentation, share_presentation
from new_db_connection import load_data_from_csv, create_pivot_table

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TEMPLATE_PRESENTATION_ID = '1gZm_8NRYsUJENaekos7LD1EALKgQYX5yFH5fROTrPAM'  # Replace this with your template's presentation ID
NEW_PRESENTATION_NAME = 'Copy of Partner Data Slide'
USER_EMAIL = ['vanilkum@redhat.com']
CSV_PATH = "resources/sample_data_for_qbr_builder.csv"

def main(input_value, user_email):
    try:
        # Split the input value (comma-separated string) into a list of partner IDs
        partner_ids = input_value.split(',')

        # Step 1: Initialize Google services
        services = build_services()
        slides_service = services.slides_service
        drive_service = services.drive_service

        logger.info("Initialized Google services.")

        # Step 2: Load and filter the data from CSV
        data_df = load_data_from_csv(CSV_PATH, filter_column='Partner_ID', filter_value=partner_ids[0])
        if data_df is None or data_df.empty:
            logger.error("No data fetched from the CSV.")
            return

        # Step 3: Create pivot tables based on filtered data
        index_column_1 = 'FY FQ'
        value_column_1 = 'Opp #'
        agg_func_1 = lambda x: len(x.unique())
        
        index_column_2 = 'Opp Stage'
        value_column_2 = 'Est. Renewal Available'
        agg_func_2 = 'sum'

        index_column_3 = 'Product Group Detail'
        value_column_3 = 'Opp #'
        agg_func_3 = lambda x: len(x.unique())

        pivot_table_1 = create_pivot_table(data_df, index_column_1, value_column_1, agg_func_1)
        pivot_table_2 = create_pivot_table(data_df, index_column_2, value_column_2, agg_func_2)
        pivot_table_3 = create_pivot_table(data_df, index_column_3, value_column_3, agg_func_3)

        if pivot_table_1 is not None:
            logger.info("Pivot Table 1 created.")
        if pivot_table_2 is not None:
            logger.info("Pivot Table 2 created.")
        if pivot_table_3 is not None:
            logger.info("Pivot Table 3 created.")

        # Step 4: Copy the Google Slides template
        new_presentation_id = copy_slide_presentation(drive_service, TEMPLATE_PRESENTATION_ID, NEW_PRESENTATION_NAME)
        if not new_presentation_id:
            logger.error("Failed to copy the template presentation.")
            return

        logger.info(f"Copied template with new presentation ID: {new_presentation_id}")

        # Step 5: Get slide IDs and insert pivot table data into the existing slides
        slide_ids = get_slide_ids(slides_service, new_presentation_id)
        if len(slide_ids) < 4:
            logger.error("Expected 4 slides in the copied presentation, but found fewer.")
            return

        # Insert pivot tables into the existing slides (2nd, 3rd, 4th slides)
        if pivot_table_1 is not None:
            logger.info("Inserting Pivot Table 1 into slide 2.")
            insert_table_into_slide(slides_service, new_presentation_id, slide_ids[1], pivot_table_1)

        if pivot_table_2 is not None:
            logger.info("Inserting Pivot Table 2 into slide 3.")
            insert_table_into_slide(slides_service, new_presentation_id, slide_ids[2], pivot_table_2)

        if pivot_table_3 is not None:
            logger.info("Inserting Pivot Table 3 into slide 4.")
            insert_table_into_slide(slides_service, new_presentation_id, slide_ids[3], pivot_table_3)

        # Step 6: Share the copied presentation
        share_presentation(drive_service, new_presentation_id, [user_email])

        logger.info(f"Shared the presentation with {user_email}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)  # Exit with error code

if __name__ == '__main__':
    if len(sys.argv) > 2:
        input_value = sys.argv[1]  # First argument: input value 
        user_email = sys.argv[2] # Second argument: user email
        main(input_value, user_email)
    else:
        logger.error("No input value provided.")
        sys.exit(1)  # Exit with error code
