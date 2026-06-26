import streamlit as st

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

import mysql.connector
import random

from connstr import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

if "user_email" not in st.session_state:
    st.error("Session expired. Please login again.")
    st.switch_page("app.py")
    st.stop()

email = st.session_state.user_email

cursor.execute(
    "SELECT * FROM users WHERE email=%s",
    (email,)
)

user = cursor.fetchone()

st.title("Placement Test")

# ----------------------------
# SESSION INIT
# ----------------------------
if "language" not in st.session_state:
    st.session_state.language = None

if "table" not in st.session_state:
    st.session_state.table = None

if "question_count" not in st.session_state:
    st.session_state.question_count = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "current_level" not in st.session_state:
    st.session_state.current_level = "A1"

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = []

if "finished" not in st.session_state:
    st.session_state.finished = False

if "confirmed" not in st.session_state:
    st.session_state.confirmed = False


# ----------------------------
# STEP 1: LANGUAGE SELECTION
# ----------------------------
if st.session_state.language is None:

    choice = st.radio("Choose Placement Test:", ["Spanish", "French"])

    if st.button("Start Test"):

        st.session_state.language = choice

        if choice == "Spanish":
            st.session_state.table = "sp_placement"
        else:
            st.session_state.table = "fr_placement"

        st.rerun()

    st.stop()


# ----------------------------
# GET QUESTION FUNCTION
# ----------------------------
def get_question(level):

    query = f"""
        SELECT
            question_id,
            question,
            option_a,
            option_b,
            option_c,
            option_d,
            answer,
            difficulty
        FROM {st.session_state.table}
        WHERE difficulty = %s
    """

    cursor.execute(query, (level,))
    results = cursor.fetchall()

    available_questions = [
        q for q in results
        if q["question_id"] not in st.session_state.asked_questions
    ]

    if len(available_questions) == 0:
        available_questions = results

    return random.choice(available_questions)


# ----------------------------
# LOAD FIRST QUESTION
# ----------------------------
if st.session_state.current_question is None and not st.session_state.finished:
    st.session_state.current_question = get_question(
        st.session_state.current_level
    )


# ----------------------------
# FINISHED TEST SCREEN
# ----------------------------
if st.session_state.finished:

    st.success("Placement Test Complete!")

    st.write(f"Score: {st.session_state.score}/10")
    st.write(f"Final Level: {st.session_state.current_level}")
    st.write(f"Language: {st.session_state.language}")

    # ----------------------------
    # CONFIRM BUTTON (SAVE TO DB)
    # ----------------------------
    if st.button("Confirm Level") and not st.session_state.confirmed:

        column = "sp" if st.session_state.language == "Spanish" else "fr"

        cursor.execute(
            f"""
            UPDATE users
            SET {column} = %s
            WHERE email = %s
            """,
            (st.session_state.current_level, st.session_state.user_email)
        )

        conn.commit()

        st.session_state.confirmed = True

        lang = st.session_state.language

        st.success("Level saved successfully!")

        st.session_state.current_question = None
        st.session_state.question_count = 0
        st.session_state.score = 0
        st.session_state.current_level = "A1"
        st.session_state.finished = False
        st.session_state.language = None
        st.session_state.table = None
        st.session_state.asked_questions = []

        if lang == "Spanish":
            st.switch_page("pages/sp_dashboard.py")
        else:
            st.switch_page("pages/fr_dashboard.py")

        st.stop()

    if st.button("Restart Test"):

        st.session_state.question_count = 0
        st.session_state.score = 0
        st.session_state.current_level = "A1"
        st.session_state.current_question = None
        st.session_state.asked_questions = []
        st.session_state.finished = False
        st.session_state.language = None
        st.session_state.table = None
        st.session_state.confirmed = False

        st.rerun()


# ----------------------------
# QUIZ FLOW
# ----------------------------
else:

    q = st.session_state.current_question

    options = {
        "A": q["option_a"],
        "B": q["option_b"],
        "C": q["option_c"],
        "D": q["option_d"]
    }

    option_items = list(options.items())


    st.write(f"Question {st.session_state.question_count + 1} of 10")

    with st.form("quiz_form"):

        user_answer = st.radio(
            q["question"],
            [f"{key}: {value}" for key, value in option_items]
        )

        submitted = st.form_submit_button("Next")

    if submitted:

        st.session_state.asked_questions.append(q["question_id"])

        selected_letter = user_answer.split(":")[0].strip()

        # init streak tracker
        if "level_streak" not in st.session_state:
            st.session_state.level_streak = 0

        levels = ["A1", "B1", "B2"]
        idx = levels.index(st.session_state.current_level)

        if selected_letter == q["answer"]:
            st.session_state.score += 1

            # correct answer increases streak
            if st.session_state.level_streak >= 0:
                st.session_state.level_streak += 1
            else:
                st.session_state.level_streak = 1

            # level up only if streak hits 2
            if st.session_state.level_streak >= 2 and idx < len(levels) - 1:
                st.session_state.current_level = levels[idx + 1]
                st.session_state.level_streak = 0

        else:
            # wrong answer decreases streak
            if st.session_state.level_streak <= 0:
                st.session_state.level_streak -= 1
            else:
                st.session_state.level_streak = -1

            # level down only if streak hits -2
            if st.session_state.level_streak <= -2 and idx > 0:
                st.session_state.current_level = levels[idx - 1]
                st.session_state.level_streak = 0

        st.session_state.question_count += 1

        if st.session_state.question_count >= 10:
            st.session_state.finished = True
        else:
            st.session_state.current_question = get_question(
                st.session_state.current_level
            )

        st.rerun()