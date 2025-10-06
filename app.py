import streamlit as st
import pandas as pd
import uuid # For unique report IDs
import time # For simulation of processing

# --- Configuration & Data Handling ---

def load_reports():
    """Loads reports from a CSV or initializes a new DataFrame."""
    # Columns reflect the data needed throughout the process
    columns = [
        'ID', 'Location', 'Waste_Type', 'Description', 'Reported_By',
        'Timestamp', 'Status', 'Is_Valid', 'Predicted_Area', 'Priority'
    ]
    try:
        # Attempt to load existing data
        df = pd.read_csv('waste_reports.csv')
        # Ensure all necessary columns exist even if the CSV is empty
        for col in columns:
            if col not in df.columns:
                df[col] = None
    except FileNotFoundError:
        # Initialize an empty DataFrame if the file doesn't exist
        df = pd.DataFrame(columns=columns)

    # Ensure Timestamp column is datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

    return df

def save_reports(df):
    """Saves the reports DataFrame to a CSV file."""
    # Saves to the same directory as the script
    df.to_csv('waste_reports.csv', index=False)

# Initialize session state for reports
# st.session_state is crucial for storing data across Streamlit reruns
if 'reports_df' not in st.session_state:
    st.session_state['reports_df'] = load_reports()

# --- Flowchart Step 1: Report Issue ---

def report_issue_form():
    """Handles the Report Issue form submission."""
    st.header("Report a New Waste Issue 🗑️")
    with st.form(key='issue_report_form'):
        # Input fields for crowd-sourcing the report
        location = st.text_input("Location (e.g., street address, landmark):", key="loc_input")
        waste_type = st.selectbox("Type of Waste:",
                                  ['General Trash', 'Recyclables', 'Construction Debris', 'Hazardous', 'Other'],
                                  key="type_input")
        description = st.text_area("Detailed Description (What, How much, etc.):", key="desc_input")
        reported_by = st.text_input("Your Name/Contact (Optional):", key="contact_input")

        submitted = st.form_submit_button("Submit Report")

        if submitted:
            if not location or not description:
                st.error("Please enter both a **Location** and a **Detailed Description**.")
                return None

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
                'Priority': None
            }
        return None

# --- Flowchart Step 2 & 3: Predict Problem Areas & Validate Report (Simulated) ---

def simulate_validation(report_data):
    """
    Simulates 'Predict Problem Areas' and 'Validate Report' steps.
    In a real app, this would involve NLP/Geocoding/ML models.
    """
    st.toast("Predicting Problem Areas and Validating...")
    time.sleep(1) # Simulate processing time

    # Simple validation/prediction logic for the prototype:
    location_valid = len(report_data['Location'].split()) >= 3 # Check if location has at least 3 words
    description_detailed = len(report_data['Description']) > 30 # Check if description is detailed enough

    is_valid = location_valid and description_detailed

    # Simple prediction based on waste type
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
    """
    Simulates 'AI Routing and Prioritization' and sets the initial resolution status.
    In a real app, this would integrate with a ticketing or dispatch system.
    """
    st.toast("AI Routing and Prioritization...")
    time.sleep(1) # Simulate processing time

    # Prioritization Logic:
    if report_data['Waste_Type'] == 'Hazardous':
        priority = "Critical (Immediate Action)"
        status = "Awaiting Specialized Team Dispatch"
    elif 'Urban Cleanup Sector A' in report_data['Predicted_Area']:
        priority = "High"
        status = "Assigned to Local Crew (24 hr target)"
    else:
        priority = "Medium"
        status = "Queued for Standard Pickup (72 hr target)"

    report_data['Priority'] = priority
    report_data['Status'] = status

    # Confirmation message for the user
    st.success(f"Report Routed! **Priority: {priority}**. Initial Status: **{status}**.")
    st.markdown(f"**Predicted Area:** {report_data['Predicted_Area']}")
    return report_data

# --- Main Application Layout ---

st.set_page_config(page_title="Crowd-Sourced Waste Management", layout="wide")
st.title("Crowd-Sourced Waste Management System ♻️")
st.markdown("---")

# Use tabs for a clean separation between reporting and viewing/admin tasks
tab1, tab2 = st.tabs(["Report New Issue", "View All Reports (Admin/Public Dashboard)"])

with tab1:
    new_report_data = report_issue_form()

    if new_report_data:
        st.subheader("Processing Report Flow")

        # 1. Predict Problem Areas & Validate Report
        with st.spinner('Running Validation and Prediction...'):
            processed_report = simulate_validation(new_report_data)

        # 2. Valid Report? (Diamond Check)
        if processed_report['Is_Valid']:
            st.success("✅ **Report is Valid!** Proceeding to Routing.")

            # 3. AI Routing and Prioritization & Resolve Issue (Initial Status)
            with st.spinner('Running AI Routing and Prioritization...'):
                final_report = simulate_routing_and_prioritization(processed_report)

            # Add the final report to the DataFrame
            df_new_row = pd.DataFrame([final_report])
            st.session_state['reports_df'] = pd.concat([st.session_state['reports_df'], df_new_row], ignore_index=True)
            save_reports(st.session_state['reports_df']) # Save to file persistence

            st.balloons()
            st.markdown(f"Report ID: `{final_report['ID'][:8]}` has been **successfully submitted and prioritized**.")
        else:
            # 4. If No (Invalid Report)
            st.error("❌ **Report is Invalid/Vague.**")
            st.warning("Please refine the **Location** and provide a **Detailed Description** (more than 30 characters) to ensure better prioritization.")

            # Add the invalid report for review/logging
            df_new_row = pd.DataFrame([processed_report])
            st.session_state['reports_df'] = pd.concat([st.session_state['reports_df'], df_new_row], ignore_index=True)
            save_reports(st.session_state['reports_df'])


with tab2:
    st.header("Reports Dashboard 📊")
    df = st.session_state['reports_df']

    if not df.empty:
        # Key Metrics
        st.metric("Total Reports", len(df))
        pending_count = len(df[df['Status'].isin(['Assigned to Local Crew (24 hr target)', 'Queued for Standard Pickup (72 hr target)', 'Awaiting Specialized Team Dispatch'])])
        st.metric("Reports Awaiting Action", pending_count, delta=f"{len(df[df['Status'] == 'New'])} New")

        # Filtering and Display
        st.subheader("Report List")

        # Filter by status
        status_filter = st.multiselect(
            'Filter by Status:',
            options=df['Status'].unique(),
            default=df['Status'].unique()
        )

        df_filtered = df[df['Status'].isin(status_filter)]

        # Display the DataFrame with relevant columns
        display_cols = ['Timestamp', 'Location', 'Waste_Type', 'Status', 'Priority', 'Predicted_Area', 'Is_Valid']
        st.dataframe(
            df_filtered[display_cols].sort_values(by='Timestamp', ascending=False),
            use_container_width=True
        )

        st.markdown("---")
        # Simplified Admin Action (Simulate Resolution)
        st.subheader("Admin Actions (Simulated)")
        unresolved_reports = df[df['Status'].str.contains('target|Dispatch')]

        if not unresolved_reports.empty:
            report_id_to_resolve = st.selectbox(
                "Select Report ID to Resolve:",
                options=unresolved_reports['ID'].apply(lambda x: f"{x[:8]} - {df.loc[df['ID'] == x, 'Location'].iloc[0]}"),
                key="resolve_select"
            )

            if st.button("Mark Selected Report as Resolved ✅"):
                # Extract the full ID from the display string
                selected_id = report_id_to_resolve.split(' - ')[0]
                full_id = unresolved_reports[unresolved_reports['ID'].str.startswith(selected_id)].iloc[0]['ID']

                # Find the index in the main dataframe
                index_to_resolve = st.session_state['reports_df'][st.session_state['reports_df']['ID'] == full_id].index[0]

                # Update status
                st.session_state['reports_df'].loc[index_to_resolve, 'Status'] = 'Resolved'
                st.session_state['reports_df'].loc[index_to_resolve, 'Priority'] = 'Resolved'
                save_reports(st.session_state['reports_df'])
                st.toast(f"Report {selected_id} marked as RESOLVED!")
                time.sleep(1)
                st.rerun() # Rerun to update the dashboard
        else:
            st.info("All submitted and valid reports are currently marked as Resolved or Invalid.")
