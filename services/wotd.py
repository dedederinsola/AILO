import requests
import feedparser
from datetime import date
from connstr import get_connection

import streamlit as st

conn = st.connection('mysql', type='sql').driver_connection
cursor = conn.cursor(dictionary=True)


# ----------------------------
# OPTIONAL: external fallback source (no AI needed)
# ----------------------------
def fetch_spanish_word():
    url = "https://www.wordreference.com/wordoftheday/es"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return None

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        word = soup.find("div", class_="wotd").find("a").text.strip()
        meaning = soup.find("div", class_="wotd").text.strip()

        return {
            "word": word,
            "translation": meaning,
            "example_sentence": "",
            "example_translation": ""
        }
    except:
        return None


# ----------------------------
# MAIN FUNCTION (SAFE + DB CONTROLLED)
# ----------------------------
def safe_generate_word(language, level):
    today = date.today()

    # 1. check DB first
    cursor.execute("""
        SELECT * FROM word_of_the_day
        WHERE language=%s AND date_generated=%s
        LIMIT 1
    """, (language, today))

    existing = cursor.fetchone()

    if existing:
        return existing

    # 2. generate new word (NO CHATGPT)
    data = fetch_spanish_word()

    if not data:
        return None

    # 3. save into DB
    cursor.execute("""
        INSERT INTO word_of_the_day
        (language, date_generated, word, translation, example_sentence, example_translation)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (
        language,
        today,
        data["word"],
        data["translation"],
        data["example_sentence"],
        data["example_translation"]
    ))

    conn.commit()

    # 4. return structured response
    return data