from datetime import date
import streamlit as st
import mysql.connector
from connstr import get_connection

st.set_page_config(layout="wide")

# 1. INITIALIZE USER SESSION STATE AT THE VERY TOP
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "error" not in st.session_state:
    st.session_state.error = ""

# 2. AUTO-ROUTE IF ALREADY LOGGED IN (Prevents back-button loops)
if st.session_state.logged_in and st.session_state.user:
    user = st.session_state.user
    if user["sp"] is None and user["fr"] is None:
        st.switch_page("pages/placement.py")
    elif user["sp"] is not None and user["fr"] is None:
        st.switch_page("pages/sp_dashboard.py")
    elif user["sp"] is None and user["fr"] is not None:
        st.switch_page("pages/fr_dashboard.py")
    else:
        st.switch_page("pages/sp_dashboard.py")

# ----------------------------
# DATABASE ACCESS HELPER FUNCTION
# ----------------------------
# Context managers (with) ensure connections close immediately after use, preventing cross-user bugs.
def check_user_login(username, password):
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE email=%s AND password=%s",
                    (username, password)
                )
                return cursor.fetchone()
    except Exception as e:
        st.error("Database connection error.")
        return None

def get_background():
    today = str(date.today())
    try:
        with get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM country_images
                    ORDER BY MD5(CONCAT(id, %s))
                    LIMIT 1
                """, (today,))
                return cursor.fetchone()
    except Exception:
        return None

# ----------------------------
# STYLES & BACKGROUND
# ----------------------------
st.markdown("""
<style>
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
    [class*="st-key-my_container"] {
        background: rgba(201, 195, 228, 0.6);
        border-radius: 16px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.15);
        backdrop-filter: blur(3px);
        -webkit-backdrop-filter: blur(3px);
        border: 1px solid rgba(201, 195, 228, 0.52);
        padding: 20px 20px 50px 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

bg = get_background()
bg_url = bg["image_url"] if bg else ""

st.markdown(f"""
<style>
.stApp {{
    background-image: linear-gradient(rgba(0,0,0,0.20), rgba(0,0,0,0.20)), url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# LOGIN FORM UI
# ----------------------------
with st.container(key="my_container_1"):
    st.title("AILO")
    st.subheader("Log In")
    
    with st.form("login_form"):
        username = st.text_input("Username or email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    # ----------------------------
    # LOGIN LOGIC
    # ----------------------------
    if submitted:
        if not username or not password:
            st.session_state.error = "Please enter both fields."
        else:
            # Query isolated safely for this specific user execution thread
            user = check_user_login(username, password)

            if user:
                # Clear prior error messages
                st.session_state.error = ""
                
                # STORE SESSION DATA
                st.session_state.logged_in = True
                st.session_state.user_email = username
                st.session_state.user = user

                # FORCE RERUN SO THE ROUTER AT THE TOP REDIRECTS CLEANLY
                st.rerun()
            else:
                st.session_state.error = "Invalid username or password"

    # ----------------------------
    # ERROR DISPLAY
    # ----------------------------
    if st.session_state.error:
        st.error(st.session_state.error)

    st.write("Don't have an account?")
    if st.button("Sign up here"):
        st.switch_page("pages/signup.py")
