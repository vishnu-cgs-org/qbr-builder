from google_services import build_services

# Build the Google services instance
services = build_services()
drive_service = services.drive_service  # Google Drive service to handle duplication
slides_service = services.slides_service  # Google Slides service

# Original presentation ID
original_presentation_id = '1gZm_8NRYsUJENaekos7LD1EALKgQYX5yFH5fROTrPAM'

# Step 1: Duplicate the presentation using Google Drive API
duplicate = drive_service.files().copy(
    fileId=original_presentation_id,
    body={"name": "Duplicated Presentation - Modified"}
).execute()

# Get the new presentation ID
duplicate_presentation_id = duplicate['id']
print(f"Duplicated presentation created: https://docs.google.com/presentation/d/{duplicate_presentation_id}/edit")

# Step 2: Define placeholders and their replacements
placeholders = {
    '{firstName}': 'Fred',  # Placeholder for full name
    '{lastName}': 'Rogers',  # Placeholder for full name
    '{geo}': 'EMEA',  # Placeholder for geographical location
    '{slide2customerCount}': '222', # Placeholder for customer count in slide 2
    '{slide2totalAcv}': '$333M', # Placeholder for total acv in slide 2
    '{slide2totalTcv}': '$444M', # Placeholder for total tcv in slide 2
    '{slide2oppCount}': '555', # Placeholder for opportunity count in slide 2
    '{slide2rhelGrowth}': '$666M', # Placeholder for rhel growth in slide 2
    '{slide2ansibleGrowth}': '$777M', # Placeholder for ansible growth in slide 2
    '{slide2ocpGrowth}': '$888M' # Placeholder for rhel openshift growth in slide 2



}

# Prepare the batch update requests
requests = []
for placeholder, replacement in placeholders.items():
    requests.append({
        'replaceAllText': {
            'containsText': {
                'text': placeholder
            },
            'replaceText': replacement
        }
    })

# Execute the batch update to modify text in the duplicated presentation
slides_service.presentations().batchUpdate(
    presentationId=duplicate_presentation_id,
    body={'requests': requests}
).execute()

print("Text replaced successfully in the duplicated presentation.")
print(f"Modified duplicated presentation: https://docs.google.com/presentation/d/{duplicate_presentation_id}/edit")
