import streamlit as st
import pandas as pd

# ---------- Load Dataset from Google Drive ----------
# Replace this with your actual Google Drive File ID
file_id = "YOUR_FILE_ID_HERE"
url = f"https://drive.google.com/uc?export=download&id={file_id}"

st.title("♻ Crowd Source Waste Management System")
st.write("Analyzing waste reports with dataset integration.")

try:
    data = pd.read_csv(url)
    st.success("✅ Dataset loaded successfully!")
    st.dataframe(data.head())
except Exception as e:
    st.error(f"⚠️ Unable to load dataset. Please check your Google Drive link.\n\nError: {e}")

# ---------- User Input Form ----------
with st.form("waste_form"):
    st.subheader("📝 Report Waste Issue")

    location = st.text_input("📍 Location")
    waste_type = st.selectbox("♻ Type of Waste", ["Plastic", "Organic", "E-waste", "Metal", "Other"])
    description = st.text_area("🗒 Description")
    image = st.file_uploader("📸 Upload a photo (optional)", type=["jpg", "png"])
    
    submitted = st.form_submit_button("Submit Report")

    if submitted:
        st.success("✅ Report submitted successfully!")

        # Optional: Example dataset-based response
        if 'Waste_Type' in data.columns:
            similar = data[data['Waste_Type'].str.contains(waste_type, case=False, na=False)]
            st.write(f"Found {len(similar)} similar waste records in dataset.")
            st.dataframe(similar.head())

# ---------- End of App ----------
st.caption("Developed by Sejal Sontakke | Powered by Streamlit")
