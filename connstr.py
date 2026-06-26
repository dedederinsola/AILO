import streamlit as st
import mysql.connector

def get_connection():
    # 1. Grab credentials safely from your Streamlit cloud secrets panel
    db_secrets = st.secrets["connections"]["mysql"]
    
    # 2. Open a direct driver connection and explicitly pass the Aiven SSL flag
    conn = mysql.connector.connect(
        host=db_secrets["host"],
        port=int(db_secrets["port"]),
        user=db_secrets["username"],
        password=db_secrets["password"],
        database=db_secrets["database"],
        ssl_disabled=False  # This forces mysql-connector to use SSL manually
    )
    return conn