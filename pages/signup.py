import streamlit as st
import mysql.connector
from datetime import date
from connstr import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

st.set_page_config(layout="wide")

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
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
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

with st.container(key="my_container_1"):
    st.title("Create Account")

    # ----------------------------
    # INPUTS
    # ----------------------------
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    languages = st.multiselect(
        "Languages to Learn",
        ["French", "Spanish"]
    )

    # ----------------------------
    # SUBMIT
    # ----------------------------
    if st.button("Continue"):

        if not email or not password:
            st.error("Email and password are required.")

        elif not languages:
            st.error("Select at least one language.")

        else:

            # check if user exists
            cursor.execute(
                "SELECT id FROM users WHERE email=%s",
                (email,)
            )
            existing = cursor.fetchone()

            if existing:
                st.error("User already exists.")

            else:

                # ONLY INSERT EMAIL + PASSWORD
                cursor.execute("""
                    INSERT INTO users (email, password)
                    VALUES (%s, %s)
                """, (email, password))

                conn.commit()

                # store EVERYTHING in session for next page ONLY
                st.session_state["user_email"] = email
                st.session_state["languages"] = languages
                st.session_state["logged_in"] = True

                st.success("Account created successfully!")

                st.switch_page("pages/placement.py")
    st.write("Already have an account?")
    if st.button("Sign in here"):
        st.switch_page("app.py")