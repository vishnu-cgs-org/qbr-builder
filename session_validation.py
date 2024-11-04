from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import subprocess
from user_form_table import cleaned_df
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your123'  # Keep a fixed secret key

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the cleaned DataFrame
df = cleaned_df

# Global state variable
state = "Waiting"

# List of allowed emails
allowed_emails = ['vanilkum@redhat.com', 'user2@example.com', 'admin@app.com']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if email in allowed_emails:
            session['logged_in'] = True  # Store the login state
            return redirect(url_for('home'))
        else:
            error_message = "Your email is not recognized. Please contact support@app.com."
            return render_template('login.html', error=error_message)
    return render_template('login.html')

@app.route('/')
def home():
    # Check if user is logged in
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get unique Assigned CRS values for the first form
    assigned_crs_list = df['Assigned CRS'].unique()
    return render_template('index.html', assigned_crs=assigned_crs_list, state=state)

@app.route('/filter', methods=['POST'])
def filter_data():
    assigned_crs = request.form.get('assigned_crs')
    if not assigned_crs:
        return "No Assigned CRS selected", 400
    
    # Filter Data
    filtered_df = df[df['Assigned CRS'] == assigned_crs]

    # Get unique Partner/Distributor Names for the next form
    partner_names = filtered_df['Partner/Distributor Name'].unique()
    
    return render_template('filter_by_partner.html', partner_names=partner_names)

@app.route('/filter_by_partner', methods=['POST'])
def filter_by_partner():
    partner_name = request.form.get('partner_name')
    if not partner_name:
        return "No Partner/Distributor Name selected", 400

    # Filter DataFrame based on Partner/Distributor Name
    filtered_df = df[df['Partner/Distributor Name'] == partner_name]
    
    # Check if the filtered DataFrame is empty
    if filtered_df.empty:
        return render_template('results.html', tables=[], titles=['No Data Found'])

    # Extract relevant information
    result = filtered_df[['Account ID', 'Total ACV 2024', 'Total TCV 2024']]

    # Convert the DataFrame to a dictionary for rendering
    tables = [{'Account ID': row['Account ID'],
               'Total ACV 2024': row['Total ACV 2024'],
               'Total TCV 2024': row['Total TCV 2024']} for _, row in result.iterrows()]
    
    titles = ['Filtered Results']
    
    return render_template('results.html', tables=tables, titles=titles)

@app.route('/trigger_by_account', methods=['POST'])
def trigger_by_account():
    account_ids = request.form.getlist('account_id')
    if not account_ids:
        return "No Account ID selected", 400

    # Convert the list of account_ids to a string representation
    account_ids_str = ','.join(account_ids)

    # Example: Path to the Python interpreter in your virtual environment
    venv_python = r'C:\Users\vanikumar\Desktop\QBR_Devops\.venv\Scripts\python.exe'

    # Command to run the subprocess with the selected Account IDs
    command = [venv_python, 'new_main.py', account_ids_str]

    try:
        # Run the subprocess
        logger.info(f"Running subprocess: {command}")
        result = subprocess.run(command, text=True, capture_output=True)

        # Log the result for debugging
        logger.info(f"Subprocess output: {result.stdout}")
        logger.error(f"Subprocess error (if any): {result.stderr}")

        # Parse presentation link if subprocess succeeded
        if result.returncode == 0:
            state = "Request processed successfully."
            presentation_link = result.stdout.strip()  # Assuming new_main.py returns the link in stdout
            logger.info(f"Presentation link: {presentation_link}")
        else:
            state = f"Failed to process the request. Error: {result.stderr}"
            presentation_link = None
    except subprocess.CalledProcessError as e:
        state = f"Failed to process the request. Error: {str(e)}"
        presentation_link = None

    # Return state and presentation link to the status page
    return render_template('status.html', state=state, presentation_link=presentation_link)

@app.route('/logout')
def logout():
    """Clear the session to force the user to re-authenticate."""
    session.clear()
    return redirect(url_for('login'))

# Clear session after specific requests to force login on next request
@app.after_request
def clear_session(response):
    # Only clear the session after actions except login-related requests
    if request.endpoint not in ['login', 'home']:
        session.clear()  # Clear session on each request except login/home
    return response

if __name__ == '__main__':
    app.run(debug=True)
