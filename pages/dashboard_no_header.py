import streamlit as st
from datetime import date
import requests
from services.time_service import get_local_time
from services.news_service import fetch_daily_news
from connstr import get_connection
conn = get_connection()
cursor = conn.cursor(dictionary=True)

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="AILO Dashboard", layout="wide")

# ----------------------------
# SESSION CHECK
# ----------------------------
if "user_email" not in st.session_state:
    st.switch_page("app.py")
    st.stop()

email = st.session_state.user_email

cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
user = cursor.fetchone()

# ----------------------------
# LANGUAGES AVAILABLE
# ----------------------------
languages = []

if user["sp"] is not None:
    languages.append(("Spanish", user["sp"]))

if user["fr"] is not None:
    languages.append(("French", user["fr"]))

if not languages:
    st.error("No languages found.")
    st.stop()


    
# ----------------------------
# CSS (GLOBAL THEME)
# ----------------------------
st.markdown("""
<style>


/* 1. Completely remove the physical header element */
header[data-testid="stHeader"] {
    display: none !important;
}

/* 2. Kill the massive white top padding inside the main app content block */
.main .block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
}

/* 3. Handle specific version inner content wrapper shifts */
[data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
}

/* FULL PAGE */
.stApp {
    background: #F5F0E6 ;
    padding: 0px;
    
}

/* GLASS CARD */
[class*="st-key-my_container"] {
    background: rgba(85, 64, 169, 0.64);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5.8px);
    -webkit-backdrop-filter: blur(5.8px);
    border: 1px solid rgba(85, 64, 169, 0.52);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    margin-bottom: 20px;
}

.st-key-news-container {
    background: rgba(85, 64, 169, 0.64);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5.8px);
    -webkit-backdrop-filter: blur(5.8px);
    border: 1px solid rgba(85, 64, 169, 0.52);
    border-radius: 20px;
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

# ----------------------------
# FUNCTIONS
# ----------------------------
def get_daily_fact():
    today = str(date.today())

    # 1. try to get today's fact
    cursor.execute("""
        SELECT *
        FROM spain_facts
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

    news = cursor.fetchall()

    # if DB is empty → generate it
    if len(news) < 3:
        fetch_daily_news(lang)

        # re-query after generation
        cursor.execute("""
            SELECT * FROM daily_news
            WHERE language=%s AND date_generated=%s
        """, (lang, date.today()))

        news = cursor.fetchall()

    return news

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

# ----------------------------
# TABS
# ----------------------------
tab_names = [l[0] for l in languages]
tabs = st.tabs(tab_names)

# ----------------------------
# MAIN RENDER LOOP
# ----------------------------
for i, tab in enumerate(tabs):

    lang, level = languages[i]

    with tab:

        # ----------------------------
        # HERO SECTION
        # ----------------------------
        bg = get_background(lang)

        if bg:
            bg_url = bg["image_url"]
            location_text = f"{bg['location_name']}, {bg['city']}, {bg['country']}"
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
        <div style="
            height: 120vh;
            background: url('{bg_url}');
            background-size: cover;
            background-position: center;
            position: relative;
            padding: -10px;
            margin-bottom: 20px;
        ">
        
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
                <div style="font-size:22px; font-weight:700;">
                    {time_data['time']}
                </div>
                <div style="font-size:14px;">Local Time</div>
                <div style="font-size:14px;">
                    {time_data['city']}
                </div>
                <div style="font-size:13px; opacity:0.9;">
                    {time_data['date']}
                </div>
            </div>
            """
            st.markdown(time_html, unsafe_allow_html=True)

        # ----------------------------
        # WORD + TIME ROW
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
                time_data = get_local_time(lang)
                
                st.write(f"### {time_data['time']}")
                st.markdown("### Local Time")
                st.write(f"{time_data['city']}")
                
                st.write(f"{time_data['date']}")

        # ----------------------------
        # JOURNAL + FLASHCARDS
        # ----------------------------
        col3, col4 = st.columns(2)

        with col3:
            prompt = get_daily_prompt(lang)

            with st.container(key="my_container_3", border=True):
                
                st.markdown("### Journal Prompt")

                if prompt:
                    st.write(prompt["prompt"])
                    st.write(prompt["translation"])
                else:
                    st.info("No prompt")

        with col4:
            with st.container(key="my_container_4", border=True):
                st.markdown("### Flashcards")

                st.info("Coming soon")

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
           with st.container(key="my_container_6", height=500, border=True):
            st.markdown("### Spotify")

            st.components.v1.html(
                """
                <iframe
                    style="border-radius:12px"
                    src="https://open.spotify.com/embed/playlist/37i9dQZEVXbNFJfN1Vw8d9?utm_source=generator&theme=0"
                    width="100%"
                    height="352"
                    frameborder="0"
                    allowfullscreen=""
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
                    loading="lazy">
                </iframe>
                """,
                height=370
            );
        with col5:  
            with st.container(key="my_container_8", border=True):
                fact = get_daily_fact()

                st.markdown("### Cultural Fact of the Day")
                st.write(fact["fact"])

        with col6:
            API_KEY = "AIzaSyCjN5ZeeLHYapBFz9fM_DmSRY8rW5EYI48"
            
    
            with st.container(key="my_container_7", height=820, border=True):
                st.markdown("### YouTube Learning")

                if lang == "Spanish":
                    SEARCH_QUERY = "best everyday spanish videos"
            
                    # The exact destination URL where your extension triggers
                    TARGET_URL = f"https://youtube.com/results?search_query={SEARCH_QUERY.replace(' ', '+')}"
                
                    try:
                        api_url = (
                        "https://www.googleapis.com/youtube/v3/search"
                        f"?part=snippet"
                        f"&q={SEARCH_QUERY.replace(' ', '+')}"
                        f"&type=video"
                        f"&maxResults=5"
                        f"&key={API_KEY}"
                        )
                        response = requests.get(api_url).json()
                        
                        if "items" in response and len(response["items"]) > 0:
                            for item in response["items"]:
                                title = item["snippet"]["title"]
                                thumb = item["snippet"]["thumbnails"]["default"]["url"]
                                
                                # Layout each video as a clickable link leading to the search page
                                inner_col1, inner_col2 = st.columns([1, 3])
                                with inner_col1:
                                    st.image(thumb, use_container_width=True)
                                with inner_col2:
                                    st.markdown(f"**[{title}]({TARGET_URL})**")
                                    st.caption("Click to view on YouTube feed")
                                st.divider()
                        else:
                            st.write("No trending items found today.")
                            
                    except Exception as e:
                        st.error("Could not load fresh videos right now.")
                        
                    # 3. Direct Search Button at the bottom
                    st.link_button("Open YouTube", TARGET_URL, use_container_width=True)
                else:
                    st.markdown("""
                    - ▶️ [InnerFrench](https://www.youtube.com/@innerFrench)
                    - ▶️ [Français Authentique](https://www.youtube.com/@FrancaisAuthentique)
                    - ▶️ [Easy French](https://www.youtube.com/@EasyFrench)
                    - ▶️ [Piece of French](https://www.youtube.com/@PieceofFrench)
                    """)

                st.info("Future upgrade: embedded video recommendations per user level")
