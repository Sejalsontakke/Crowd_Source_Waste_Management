import streamlit as st
from PIL import Image
import pandas as pd
import uuid
import time
import os
from predict import predict_from_image


# Basic paths
IMAGES_DIR = 'images'
MODELS_DIR = 'models'
REPORTS_CSV = 'waste_reports.csv'


os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


st.set_page_config(page_title="Crowd-Sourced Waste Management", layout="wide")
st.title("Crowd-Sourced Waste Management System ♻️")
st.markdown("---")


@st.cache_data
def load_reports():
columns = [
'ID', 'Location', 'Waste_Type', 'Description', 'Reported_By',
'Timestamp', 'Status', 'Is_Valid', 'Predicted_Area', 'Priority', 'Image_Filename'
]
try:
df = pd.read_csv(REPORTS_CSV)
for col in columns:
if col not in df.columns:
df[col] = None
except FileNotFoundError:
df = pd.DataFrame(columns=columns)
df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
return df


@st.cache_data
def save_reports(df):
df.to_csv(REPORTS_CSV, index=False)


st.session_state.setdefault('reports_df', load_reports())


# Helper to set priority based on prediction
def priority_from_prediction(top_label, top_prob):
if 'Hazardous' in top_label:
return 'Critical (Immediate Action)', 'Awaiting Specialized Team Dispatch'
if top_prob >= 0.75:
waste_type = st.selectbox(