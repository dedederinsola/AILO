import streamlit as st

def get_connection():
    # Connects to Aiven using your Streamlit Cloud secrets
    conn = st.connection('mysql', type='sql').driver_connection
    return conn
