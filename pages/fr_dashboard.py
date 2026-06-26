import streamlit as st
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebarNav"] {
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

with st.sidebar:

    st.page_link("pages/sp_dashboard.py", label="Spanish")
    st.page_link("pages/fr_dashboard.py", label="French")

from datetime import date
from services.weather_service import get_weather
import requests
from services.time_service import get_local_time
from services.news_service import fetch_daily_news_all_languages
from connstr import get_connection
conn = get_connection()
cursor = conn.cursor(dictionary=True)

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="French Dashboard", layout="wide")

# ----------------------------
# SESSION CHECK
# ----------------------------
if "user_email" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

email = st.session_state.user_email

cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
user = cursor.fetchone()

if "news_initialized" not in st.session_state:
    fetch_daily_news_all_languages()
    st.session_state.news_initialized = True
    
if "page" not in st.session_state:
    st.session_state.page = "French"

# ----------------------------
# LANGUAGES AVAILABLE
# ----------------------------
# languages = []


if user["fr"] is None:
    st.info("No language found. Redirecting to placement test...")
    st.switch_page("pages/placement.py")



    
# ----------------------------
# CSS (GLOBAL THEME)
# ----------------------------
st.markdown("""
<style>

/* FULL PAGE */
.stApp {
    background: #F5F0E6 ;
    padding: 0px;
    
}

/* GLASS CARD */
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

.st-key-news-container {
    background-image: linear-gradient(
        rgba(0,0,0,0.20),
        rgba(0,0,0,0.20)
    ),
    url("https://www.shutterstock.com/image-vector/monochrome-seamless-pattern-collage-newspaper-600nw-2531479387.jpg");
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(3px);
    -webkit-backdrop-filter: blur(3px);
    border: 1px solid rgba(201, 195, 228, 0.52);
    padding: 20px 20px 50px 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

/* HERO */
.hero {
    height: 280px;
    border-radius: 25px;
    background-size: cover;
    background-position: center;
    position: relative;
    margin-bottom: 25px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
}

.hero-title {
    position: absolute;
    top: 20px;
    right: 25px;
    font-size: 32px;
    font-weight: 800;
    color: white;
    text-shadow: 0 5px 15px rgba(0,0,0,0.6);
}

/* SECTION TITLE */
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* BUTTONS */
button {
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div.stButton > button {
    background: rgba(201, 195, 228, 0.6);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(3px);
    -webkit-backdrop-filter: blur(3px);
    border: 1px solid rgba(201, 195, 228, 0.52);
    padding: 5px 20px 5px 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# FUNCTIONS
# ----------------------------
def get_daily_fact():
    today = str(date.today())

    # 1. try to get today's fact
    cursor.execute("""
        SELECT *
        FROM france_facts
        ORDER BY MD5(CONCAT(fact, %s))
        LIMIT 1
    """, (today,))

    return cursor.fetchone()


def get_daily_word(lang):
    today = str(date.today())

    cursor.execute("""
        SELECT *
        FROM word_of_the_day
        WHERE language=%s
        ORDER BY MD5(CONCAT(word, %s))
        LIMIT 1
    """, (lang, today))

    return cursor.fetchone()

def get_today_news(lang):
    cursor.execute("""
        SELECT * FROM daily_news
        WHERE language=%s AND date_generated=%s
    """, (lang, date.today()))

    return cursor.fetchall()


def get_daily_prompt(lang):
    today = str(date.today())

    cursor.execute("""
        SELECT *
        FROM journal_prompts
        WHERE language=%s
        ORDER BY MD5(CONCAT(prompt, %s))
        LIMIT 1
    """, (lang, today))

    return cursor.fetchone()


def get_background(lang):
    today = str(date.today())
    cursor.execute("""
        SELECT * FROM country_images
        WHERE language=%s
        ORDER BY MD5(CONCAT(id, %s))
        LIMIT 1
    """, (lang, today))
    background =  cursor.fetchone()
    
    return background

def top_nav():
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🇪🇸 Spanish"):
            st.session_state.page = "Spanish"

    with col2:
        st.button("🇫🇷 French")



# selected_lang = st.query_params.get("lang", None)

# if not selected_lang:
#     selected_lang = languages[0][0]
#     st.query_params["lang"] = selected_lang
    
# lang_map = {name: level for name, level in languages}
# lang = selected_lang
# level = lang_map[lang]

lang = "French"

# ----------------------------
# HERO SECTION
# ----------------------------


bg = get_background(lang)

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

# -------------------------
# 2. Get time data
# -------------------------
time_data = get_local_time(lang)

# -------------------------
# 3. Set background
# -------------------------
st.markdown(f"""

<style>
.stApp {{
    background-image: linear-gradient(
        rgba(0,0,0,0.35),
        rgba(0,0,0,0.35)
    ),
    url("{bg_url}");

    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 4. Location overlay (top-right)
# -------------------------
st.markdown(f"""
<div style="
    position: fixed;
    bottom: 25px;
    left: 30px;
    color: white;
    text-shadow: 0 4px 10px rgba(0,0,0,0.7);
    background: rgba(0,0,0,0.3);
    padding: 12px 14px;
    border-radius: 10px;
    z-index: 9999;
    line-height: 1.4;
">
    {location_text}
</div>
""", unsafe_allow_html=True)

# -------------------------
# 5. Time overlay (bottom-left)
# -------------------------
if time_data:
    time_html = f"""
    <div style="
        position: fixed;
        top: 25px;
        right: 30px;
        color: white;
        text-shadow: 0 4px 10px rgba(0,0,0,0.7);
        background: rgba(0,0,0,0.3);
        padding: 12px 14px;
        border-radius: 10px;
        z-index: 9999;
        line-height: 1.4;
    ">
        <div style="font-size:35px; font-weight:700;">
            {time_data['time']}
        </div>
        <div style="font-size:20px;">Local Time</div>
        <div style="font-size:20px;">
            {time_data['city']}
        </div>
        <div style="font-size:15px; opacity:0.9;">
            {time_data['date']}
        </div>
    </div>
    """
    st.markdown(time_html, unsafe_allow_html=True)

# ----------------------------
# WORD + WEATHER ROW
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    word = get_daily_word(lang)

    with st.container(key="my_container_1", border=True):
        st.markdown("### Word of the Day")

        if word:
            st.write(f"**Word**: {word['word']}")
            st.write(f"**Translation**: {word['translation']}")
            st.write(f"**Example Sentence**: {word['example_sentence']}")
            st.write(f"**Example Translation**: {word['example_translation']}")
        else:
            st.info("No word yet")
        
with col2:
    with st.container(key="my_container_2", border=True):
        weather = get_weather(lang)

        st.markdown("### Weather")

        st.write(f"📍 {weather['city']}")
        st.write(f"🌡️ {weather['temperature']}°C")
        st.write(f"💨 {weather['wind']} km/h")

# ----------------------------
# JOURNAL + YOUTUBE
# ----------------------------
col3, col4 = st.columns(2)

with col3:
    prompt = get_daily_prompt(lang)

    with st.container(key="my_container_3", height=220, border=True):
        
        st.markdown("### Journal Prompt")

        if prompt:
            st.write(prompt["prompt"])
            st.write(prompt["translation"])
        else:
            st.info("No prompt")

with col4:
    with st.container(key="my_container_4", border=True):
        st.html("""
            <a href="https://www.youtube.com" target="_blank" style="text-decoration:none;">
                <div style="
                    height:220px;
                    border-radius:20px;
                    position:relative;
                    overflow:hidden;
                    cursor:pointer;
                    box-shadow:0 10px 25px rgba(0,0,0,0.2);
                ">
                    <img
                        src="https://i.pinimg.com/736x/a3/bb/96/a3bb96ae22f859c884d1c6358a6d51a6.jpg"
                        style="
                            width:100%;
                            height:100%;
                            object-fit:cover;
                            display:block;
                        "
                    />
                </div>

            </a>
            """)
        st.write("##### Open YouTube and explore content in your target language!")

        

# ----------------------------
# NEWS
# ----------------------------
with st.container(key="news-container", border=True):
    st.markdown("### Daily News")

    cols = st.columns(3)
    news = get_today_news(lang)
    for i, item in enumerate(news[:3]):
        with cols[i]:
            
            img = item.get("image_url")

            if not img:
                img = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRF-cWlhchB1eGqrWzUQX__-XGpF3-I6Rdwdg&s"

            st.markdown(f"""
            <div style="
                background: white;
                border-radius: 15px;
                overflow: hidden;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                height: 250px;
            ">
                <img src="{img}" style="width:100%; height:120px; object-fit:cover;">
                <div style="padding:10px 10px 50px 10px;">
                    <small>{item['source']}</small>
                    <h4 style="font-size:14px;">{item['title'][:80]}</h4>
                    <a href="{item['url']}" target="_blank">Read</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# SPOTIFY + YOUTUBE
# ----------------------------
col5, col6 = st.columns(2)

with col5:
    with st.container(key="my_container_6", height=450, border=True):

        st.iframe(
            """
            <iframe
                
                data-testid="embed-iframe" style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZEVXbIPWwFssbupI?utm_source=generator" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy">
            </iframe>
            """,
            height=370
        )

with col6:            

    with st.container(key="my_container_7", height=450, border=True):
            
        fact = get_daily_fact()

        st.markdown("### Cultural Fact of the Day")
        st.write(fact["fact"])
        
top_nav()
if st.session_state.page == "Spanish":
    st.switch_page("pages/sp_dashboard.py")
