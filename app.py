from datetime import date

import streamlit as st
import mysql.connector
from connstr import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

st.set_page_config(layout="wide")


st.markdown("""
<style>
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"] {
    display: none;
}
[data-testid="collapsedControl"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[class*="st-key-my_container"] {
    background: rgba(201, 195, 228, 0.6);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(3px);
    -webkit-backdrop-filter: blur(3px);
    border: 1px solid rgba(201, 195, 228, 0.52);
    padding: 20px 20px 50px 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)



def get_background():
    today = str(date.today())
    cursor.execute("""
        SELECT * FROM country_images
        ORDER BY MD5(CONCAT(id, %s))
        LIMIT 1
    """, (today,))
    background =  cursor.fetchone()
    
    return background

# ----------------------------
# PAGE CONFIG
# ----------------------------)



bg = get_background()

if bg:
    bg_url = bg["image_url"]
    location_text = ", ".join(
        filter(
            None,
            [
                bg.get("location_name"),
                bg.get("city"),
                bg.get("country")
            ]
        )
    )
else:
    bg_url = ""
    location_text = "None found"
    
st.markdown(f"""

<style>
.stApp {{
    background-image: linear-gradient(
        rgba(0,0,0,0.20),
        rgba(0,0,0,0.20)
    ),
    url("{bg_url}");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
""", unsafe_allow_html=True)


# ----------------------------
# LOGIN FORM
# ----------------------------
with st.container(key="my_container_1"):
    st.title("AILO")
    st.subheader("Log In")
    with st.form("login_form"):

        username = st.text_input("Username or email")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Login")

    # ----------------------------
    # ERROR HOLDER
    # ----------------------------
    if "error" not in st.session_state:
        st.session_state.error = ""

    # ----------------------------
    # LOGIN LOGIC
    # ----------------------------
    if submitted:

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            # STORE SESSION
            st.session_state.logged_in = True
            st.session_state.user_email = username
            st.session_state.user = user

            # ROUTE USER
            if user["sp"] is None and user["fr"] is None:
                st.switch_page("pages/placement.py")
            elif user["sp"] is not None and user["fr"] is None:
                st.switch_page("pages/sp_dashboard.py")
            elif user["sp"] is None and user["fr"] is not None:
                st.switch_page("pages/fr_dashboard.py")
            else:
                st.switch_page("pages/sp_dashboard.py")

        else:
            st.session_state.error = "Invalid username or password"

    # ----------------------------
    # ERROR DISPLAY (like your PHP span)
    # ----------------------------
    if st.session_state.error:
        st.error(st.session_state.error)
        
        

    st.write("Don't have an account?")
    if st.button("Sign up here"):
        st.switch_page("pages/signup.py")
