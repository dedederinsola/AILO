import mysql.connector
import feedparser
from datetime import date

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

conn = get_connection()
cursor = conn.cursor(dictionary=True)

SOURCES = {
    "Spanish": [
    ("El País", "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada"),
    ("20 Minutos", "https://www.20minutos.es/rss/"),
    ("BBC Mundo", "http://feeds.bbci.co.uk/mundo/rss.xml"),
    ("El Mundo", "https://e00-elmundo.uecdn.es/elmundo/rss/portada.xml"),
    ("ABC España", "https://www.abc.es/rss/feeds/abcPortada.xml"),
    ("La Vanguardia", "https://www.lavanguardia.com/rss/home.xml"),
    ("El Confidencial", "https://rss.elconfidencial.com/espana/"),
    ("Europa Press", "https://www.europapress.es/rss/rss.aspx"),
    ("Infobae España", "https://www.infobae.com/arc/outboundfeeds/rss/"),
    ("RT en Español", "https://actualidad.rt.com/feeds/all.rss"),
    ("DW Español", "https://rss.dw.com/rdf/rss-sp-all"),
    ("CNN Español", "https://cnnespanol.cnn.com/feed/"),
    ("El Diario", "https://www.eldiario.es/rss/"),
    ("Mundo Deportivo", "https://www.mundodeportivo.com/rss/home.xml"),
    ("Marca", "https://e00-marca.uecdn.es/rss/portada.xml")
    ],
    
    "French": [
    ("Le Monde", "https://www.lemonde.fr/rss/une.xml"),
    ("France24", "https://www.france24.com/fr/rss"),
    ("Radio France", "https://www.radiofrance.fr/franceinter/rss"),
    ("Le Figaro", "https://www.lefigaro.fr/rss/figaro_actualites.xml"),
    ("Libération", "https://www.liberation.fr/arc/outboundfeeds/rss-all/"),
    ("Les Echos", "https://www.lesechos.fr/rss/rss_une.xml"),
    ("France Info", "https://www.francetvinfo.fr/titres.rss"),
    ("RFI", "https://www.rfi.fr/fr/rss"),
    ("Courrier International", "https://www.courrierinternational.com/feed/rss"),
    ("Le Parisien", "https://feeds.leparisien.fr/leparisien/rss"),
    ("L'Obs", "https://www.nouvelobs.com/rss.xml"),
    ("BFMTV", "https://www.bfmtv.com/rss/news-24-7/"),
    ("TV5Monde", "https://information.tv5monde.com/rss"),
    ("Mediapart", "https://www.mediapart.fr/articles/feed"),
    ("La Croix", "https://www.la-croix.com/RSS/UNIVERS")
    ]
}

def fetch_daily_news(language):

    today = date.today()

    cursor.execute("""
        SELECT COUNT(*) as count
        FROM daily_news
        WHERE language=%s AND date_generated=%s
    """, (language, today))

    if cursor.fetchone()["count"] > 3:
        return

    headlines_found = 0

    for source_name, url in SOURCES[language]:

        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                continue

            entry = feed.entries[0]

            image = entry.get("media_thumbnail", [{}])[0].get("url", "")

            if not image:
                continue

            cursor.execute("""
                INSERT INTO daily_news
                (language, date_generated, title, url, image_url, source)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                language,
                today,
                entry.title,
                entry.link,
                image,
                source_name
            ))

            headlines_found += 1

            if headlines_found >= 3:
                break

        except Exception:
            continue


    conn.commit()

def fetch_daily_news_all_languages():
    for language in SOURCES:
        fetch_daily_news(language)
