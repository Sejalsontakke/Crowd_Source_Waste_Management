# --- STREAMLIT APP CODE (Must be run in a separate cell to create app.py) ---
%%writefile app.py
import streamlit as st
from PIL import Image
import pandas as pd
import uuid # For unique report IDs
import time # For simulation of processing
import io
import os 

# --- Configuration & Data Handling ---

# --- Google Drive Placeholder for External Dataset ---
GOOGLE_DRIVE_DATASET_ID = "YOUR_CLASSIFICATION_DATA_ID_HERE"

@st.cache_data
def load_classification_data_from_drive(file_id):
    """Placeholder to load a dataset, e.g., for model mapping or instructions."""
    st.sidebar.info(f"Using a *dummy classification map*. Implement Google Drive loading logic for ID: {file_id}")

    # Dummy Data for the ML Model mapping
    classification_map = {
        'Plastic': 'Recyclables',
        'Metal': 'Recyclables',
        'Organic': 'General Trash',
        'Battery': 'Hazardous',
        'Tire': 'Construction Debris',
        'Unknown': 'Other'
    }
    return classification_map

# Load the dummy/real classification data
CLASSIFICATION_MAP = load_classification_data_from_drive(GOOGLE_DRIVE_DATASET_ID)


def load_reports():
    """Loads reports from a CSV or initializes a new DataFrame."""
    columns = [
        'ID', 'Location', 'Waste_Type', 'Description', 'Reported_By',
        'Timestamp', 'Status', 'Is_Valid', 'Predicted_Area', 'Priority',
        'Image_Filename' # Added column to track image
    ]
    try:
        df = pd.read_csv('waste_reports.csv')
        for col in columns:
            if col not in df.columns:
                df[col] = None
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)

    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    return df

def save_reports(df):
    """Saves the reports DataFrame to a CSV file."""
    df.to_csv('waste_reports.csv', index=False)

# Initialize session state for reports
if 'reports_df' not in st.session_state:
    st.session_state['reports_df'] = load_reports()

# --- Flowchart Step 1: Report Issue ---

def report_issue_form():
    """Handles the Report Issue form submission."""
    st.header("Report a New Waste Issue 🗑")
    with st.form(key='issue_report_form'):
        
        # Image Uploader Input
        uploaded_file = st.file_uploader(
            "Upload Image of Waste (Highly Recommended)",
            type=["png", "jpg", "jpeg"],
            key="image_uploader"
        )
        
        default_waste_type = 'General Trash'
        
        if uploaded_file is not None:
            col1, col2 = st.columns([1, 2])
            with col1:
                 st.image(uploaded_file, caption='Image Preview', width=150)
            
            # Simulate ML Prediction
            predicted_waste = st.radio(
                "Simulated ML Prediction (Select the category):",
                list(CLASSIFICATION_MAP.keys()),
                index=0
            )
            default_waste_type = CLASSIFICATION_MAP.get(predicted_waste, 'Other')
            
        st.markdown("---") 

        location = st.text_input("Location (e.g., street address, landmark):", key="loc_input")
        
        waste_type = st.selectbox(
            "Type of Waste:",
            ['General Trash', 'Recyclables', 'Construction Debris', 'Hazardous', 'Other'],
            index=['General Trash', 'Recyclables', 'Construction Debris', 'Hazardous', 'Other'].index(default_waste_type),
            key="type_input"
        )
        
        description = st.text_area("Detailed Description (What, How much, etc.):", key="desc_input")
        reported_by = st.text_input("Your Name/Contact (Optional):", key="contact_input")

        submitted = st.form_submit_button("Submit Report")

        if submitted:
            if not location or not description:
                st.error("Please enter both a *Location* and a *Detailed Description*.")
                return None
            
            # Save the image if uploaded
            image_filename = None
            if uploaded_file is not None:
                image_filename = f"img_{str(uuid.uuid4())[:8]}.jpg"
                try:
                    with open(image_filename, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.toast(f"Image saved locally as {image_filename}")
                except Exception as e:
                    st.error(f"Could not save image locally: {e}")
                    image_filename = "Saving Failed"


            # Package the report data
            return {
                'ID': str(uuid.uuid4()),
                'Location': location,
                'Waste_Type': waste_type,
                'Description': description,
                'Reported_By': reported_by,
                'Timestamp': pd.Timestamp.now(),
                'Status': 'New',
                'Is_Valid': None,
                'Predicted_Area': None,
                'Priority': None,
                'Image_Filename': image_filename 
            }
        return None

# --- Flowchart Step 2 & 3: Predict Problem Areas & Validate Report (Simulated) ---

def simulate_validation(report_data):
    """Simulates 'Predict Problem Areas' and 'Validate Report' steps."""
    st.toast("Predicting Problem Areas and Validating...")
    time.sleep(1) 

    location_valid = len(report_data['Location'].split()) >= 3
    description_detailed = len(report_data['Description']) > 30
    has_image = report_data['Image_Filename'] not in (None, 'Saving Failed')

    is_valid = (location_valid and description_detailed) or has_image

    if 'Hazardous' in report_data['Waste_Type']:
        predicted_area = "Hazardous Waste Zone"
    elif is_valid:
        predicted_area = "Urban Cleanup Sector A"
    else:
        predicted_area = "Validation Pending/Vague Location"

    report_data['Is_Valid'] = is_valid
    report_data['Predicted_Area'] = predicted_area
    return report_data

# --- Flowchart Step 4 & 5: AI Routing and Prioritization & Resolve Issue (Simulated) ---

def simulate_routing_and_prioritization(report_data):
    """Simulates 'AI Routing and Prioritization' and sets the initial resolution status."""
    st.toast("AI Routing and Prioritization...")
    time.sleep(1) 

    priority = "Medium"
    status = "Queued for Standard Pickup (72 hr target)"

    if report_data['Waste_Type'] == 'Hazardous':
        priority = "Critical (Immediate Action)"
        status = "Awaiting Specialized Team Dispatch"
    elif 'Urban Cleanup Sector A' in report_data['Predicted_Area']:
        priority = "High"
        status = "Assigned to Local Crew (24 hr target)"
    
    if report_data['Image_Filename'] not in (None, 'Saving Failed') and priority == "Medium":
        priority = "Medium/High (Visual Verified)"
        status = "Assigned to Local Crew (48 hr target)"


    report_data['Priority'] = priority
    report_data['Status'] = status

    st.success(f"Report Routed! *Priority: {priority}. Initial Status: **{status}*.")
    st.markdown(f"*Predicted Area:* {report_data['Predicted_Area']}")
    return report_data

# --- Main Application Layout ---

st.set_page_config(page_title="Crowd-Sourced Waste Management", layout="wide")
st.title("Crowd-Sourced Waste Management System ♻")
st.markdown("---")

tab1, tab2 = st.tabs(["Report New Issue", "View All Reports (Admin/Public Dashboard)"])

with tab1:
    new_report_data = report_issue_form()

    if new_report_data:
        st.subheader("Processing Report Flow")

        with st.spinner('Running Validation and Prediction...'):
            processed_report = simulate_validation(new_report_data)

        if processed_report['Is_Valid']:
            st.success("✅ *Report is Valid!* Proceeding to Routing.")

            with st.spinner('Running AI Routing and Prioritization...'):
                final_report = simulate_routing_and_prioritization(processed_report)

            df_new_row = pd.DataFrame([final_report])
            st.session_state['reports_df'] = pd.concat([st.session_state['reports_df'], df_new_row], ignore_index=True)
            save_reports(st.session_state['reports_df']) 

            st.balloons()
            st.markdown(f"Report ID: {final_report['ID'][:8]} has been *successfully submitted and prioritized*.")
        else:
            st.error("❌ *Report is Invalid/Vague.*")
            st.warning("Please refine the *Location* and provide a *Detailed Description* (more than 30 characters) or *Upload an Image* to ensure better prioritization.")

            df_new_row = pd.DataFrame([processed_report])
            st.session_state['reports_df'] = pd.concat([st.session_state['reports_df'], df_new_row], ignore_index=True)
            save_reports(st.session_state['reports_df'])


with tab2:
    st.header("Reports Dashboard 📊")
    df = st.session_state['reports_df']

    if not df.empty:
        st.metric("Total Reports", len(df))
        pending_count = len(df[df['Status'].str.contains('target|Dispatch')])
        st.metric("Reports Awaiting Action", pending_count, delta=f"{len(df[df['Status'] == 'New'])} New")

        st.subheader("Report List")

        status_filter = st.multiselect(
            'Filter by Status:',
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )

        df_filtered = df[df['Status'].isin(status_filter)]

        display_cols = ['Timestamp', 'Location', 'Waste_Type', 'Status', 'Priority', 'Predicted_Area', 'Image_Filename']
        st.dataframe(
            df_filtered[display_cols].sort_values(by='Timestamp', ascending=False),
            use_container_width=True
        )
        
        st.markdown("---")
        st.subheader("Image Review")
        
        reports_with_images = df_filtered[df_filtered['Image_Filename'].notna() & (df_filtered['Image_Filename'] != 'Saving Failed')]
        
        if not reports_with_images.empty:
            
            image_options = reports_with_images.apply(
                lambda row: f"{row['ID'][:8]} - {row['Location']} ({row['Waste_Type']})", axis=1
            )
            
            report_to_view = st.selectbox(
                "Select a Report to View its Image:",
                options=image_options
            )
            
            selected_id_prefix = report_to_view.split(' - ')[0]
            selected_report = reports_with_images[reports_with_images['ID'].str.startswith(selected_id_prefix)].iloc[0]
            image_path = selected_report['Image_Filename']
            
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    st.image(img, caption=f"Image for Report ID: {selected_id_prefix}", use_column_width=False, width=300)
                    st.info(f"Report Details: {selected_report['Description']}")
                except Exception as e:
                    st.error(f"Error loading image: {e}")
            else:
                 st.warning(f"Image file not found on the server: {image_path}.")
        else:
            st.info("No reports with images found in the current filter.")
        
        st.markdown("---")
        st.subheader("Admin Actions (Simulated)")
        unresolved_reports = df[df['Status'].str.contains('target|Dispatch')]

        if not unresolved_reports.empty:
            report_id_to_resolve = st.selectbox(
                "Select Report ID to Resolve:",
                options=unresolved_reports['ID'].apply(lambda x: f"{x[:8]} - {df.loc[df['ID'] == x, 'Location'].iloc[0]}"),
                key="resolve_select"
            )

            if st.button("Mark Selected Report as Resolved ✅"):
                selected_id = report_id_to_resolve.split(' - ')[0]
                full_id = unresolved_reports[unresolved_reports['ID'].str.startswith(selected_id)].iloc[0]['ID']

                index_to_resolve = st.session_state['reports_df'][st.session_state['reports_df']['ID'] == full_id].index[0]

                st.session_state['reports_df'].loc[index_to_resolve, 'Status'] = 'Resolved'
                st.session_state['reports_df'].loc[index_to_resolve, 'Priority'] = 'Resolved'
                save_reports(st.session_state['reports_df'])
                st.toast(f"Report {selected_id} marked as RESOLVED!")
                time.sleep(1)
                st.rerun() 
        else:
            st.info("All submitted and valid reports are currently marked as Resolved or Invalid.")
            
