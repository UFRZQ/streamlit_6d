import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlparse
from collections import Counter
from wordcloud import WordCloud
import re
import altair as alt

# --- Konfigurasi Halaman ---
st.set_page_config(page_title="Analisis Data Crawling", layout="wide")
st.title("📊 Analisis Data Crawling: Artikel atau Video Voli")

# --- Koneksi ke MongoDB ---
client = MongoClient(
    "mongodb://bigdata:bigdata@ac-yvsgtuk-shard-00-00.iimtdot.mongodb.net:27017,"
    "ac-yvsgtuk-shard-00-01.iimtdot.mongodb.net:27017,"
    "ac-yvsgtuk-shard-00-02.iimtdot.mongodb.net:27017/"
    "?replicaSet=atlas-ggmsij-shard-0&ssl=true&authSource=admin&retryWrites=true&w=majority&appName=Cluster0"
)
db = client["Bigdata"]
collection = db["video_voli"]

# --- Ambil & Proses Data ---
documents = list(collection.find())

if not documents:
    st.warning("⚠️ Tidak ada data tersedia.")
    st.stop()

# Buat DataFrame dengan kolom yang relevan
data = pd.DataFrame([{
    "title": doc.get("title", ""),
    "url": doc.get("url", ""),
    "uploader": doc.get("uploader", "")
} for doc in documents])

# Ekstrak domain dari URL
data["domain"] = data["url"].apply(lambda x: urlparse(x).netloc if pd.notnull(x) and x else "Unknown")

# --- Statistik Umum ---
st.markdown("### 🧾 Statistik Umum")
col1, col2 = st.columns(2)
col1.metric("📄 Total Dokumen", len(data))
col2.metric("🌐 Total Domain", data['domain'].nunique())

# --- Tampilkan Daftar Dokumen ---
with st.expander("📋 Lihat Daftar Dokumen"):
    st.dataframe(data[['title', 'url', 'uploader']], use_container_width=True)

# --- Visualisasi Jumlah Dokumen per Domain ---
st.markdown("### 🌐 Jumlah Dokumen per Domain")
st.bar_chart(data['domain'].value_counts())

# --- Word Frequency dari Judul ---
all_text = " ".join(data["title"].tolist()).lower()
clean_words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
word_freq = Counter(clean_words)
top_words = word_freq.most_common(20)
df_words = pd.DataFrame(top_words, columns=["Kata", "Frekuensi"])

# --- Word Cloud dari Judul ---
st.markdown("### ☁️ Word Cloud dari Judul")
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(clean_words))
fig_wc, ax_wc = plt.subplots()
ax_wc.imshow(wordcloud, interpolation='bilinear')
ax_wc.axis('off')
st.pyplot(fig_wc)

# --- Grafik Frekuensi Kata ---
st.markdown("### 📊 Grafik Kata Terpopuler")
bar_chart = alt.Chart(df_words).mark_bar().encode(
    x=alt.X("Frekuensi:Q"),
    y=alt.Y("Kata:N", sort='-x'),
    tooltip=["Kata", "Frekuensi"]
).properties(width=700, height=400)
st.altair_chart(bar_chart, use_container_width=True)

# --- Pencarian Berdasarkan Judul ---
st.markdown("### 🔍 Cari Judul Tertentu")
search_term = st.text_input("Masukkan kata kunci:")
if search_term:
    results = data[data["title"].str.contains(search_term, case=False)]
    st.write(f"Menampilkan {len(results)} hasil untuk: **{search_term}**")
    for i, row in results.iterrows():
        st.markdown(f"- [{row['title']}]({row['url']}) – *{row['uploader']}*")

# --- Tampilkan Sampel Data ---
st.markdown("### 📄 Sampel Data Crawling")
sample_size = st.slider("Jumlah sampel ditampilkan:", 5, 50, 10)
for i, row in data.head(sample_size).iterrows():
    st.markdown(f"**{i+1}.** [{row['title']}]({row['url']}) – *{row['uploader']}*")
