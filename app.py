import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os
import base64

# =====================================================================
# 1. KONFIGURASI HALAMAN UTAMA DASHBOARD
# =====================================================================
st.set_page_config(page_title="Komparasi Sentimen E-Wallet", layout="wide")

# =====================================================================
# 2. FUNGSI MEMUAT DATA (ANTI-BERAT, MEMBACA HASIL CSV)
# =====================================================================
@st.cache_data
def load_data():
    df_sentimen = pd.read_csv("hasilSentimen.csv")
    df_evaluasi = pd.read_csv("hasilEvaluasi.csv")
    
    if len(df_evaluasi.columns) >= 12:
        df_evaluasi.columns = ['aplikasi', 'Accuracy', 'Precision', 'Recall', 'Specificity', 'F1-Score', 
                               'jumlahDataTrain', 'jumlahDataTest', 'TN', 'FP', 'FN', 'TP']
        
    df_sentimen['date'] = pd.to_datetime(df_sentimen['date'])
    return df_sentimen, df_evaluasi

try:
    df_sentimen, df_evaluasi = load_data()
except Exception as e:
    st.error(f"Gagal memuat data CSV. Pastikan file berada di repositori yang sama. Error: {e}")
    st.stop()

# =====================================================================
# A. JUDUL DAN DESKRIPSI SINGKAT PENELITIAN
# =====================================================================
st.title("📊KOMPARATIF SENTIMEN E-WALLET DANA, GOPAY & SHOPEEPAY")

st.info("""
💡 **Kegunaan Dashboard Web**: Membandingkan sentimen pengguna terhadap E-Wallet DANA, GoPay, dan ShopeePay secara instan tanpa harus membaca puluhan ribu ulasan manual.
""")

# =====================================================================
# C. INTERFASE TOMBOL IKON LOGO APLIKASI (MENGGUNAKAN TOGGLE BAWAAN)
# =====================================================================
st.markdown("---")
st.subheader("📱 Pilih E-Wallet")

# Fungsi pembantu untuk membaca gambar lokal menjadi HTML aman
def get_img_html(file_path, alt_text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" style="width: 90px; height: 90px; object-fit: contain; display: block; margin: 0 auto; border-radius: 8px;">'
    return f'<p style="color: gray; font-size: 14px; text-align: center;">{alt_text}</p>'

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    st.markdown(f'<div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 5px;">{get_img_html("logoDana.png", "[Logo DANA]")}</div>', unsafe_allow_html=True)
    dana_active = st.toggle("Aktifkan DANA", value=True, key="tgl_dana")

with col_btn2:
    st.markdown(f'<div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 5px;">{get_img_html("logoGopay.png", "[Logo GoPay]")}</div>', unsafe_allow_html=True)
    gopay_active = st.toggle("Aktifkan GoPay", value=True, key="tgl_gopay")

with col_btn3:
    st.markdown(f'<div style="background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #e0e0e0; margin-bottom: 5px;">{get_img_html("logoShopeepay.png", "[Logo ShopeePay]")}</div>', unsafe_allow_html=True)
    shopee_active = st.toggle("Aktifkan ShopeePay", value=True, key="tgl_shopee")

# Menyusun kembali daftar aplikasi aktif untuk filter data grafik di bawahnya
selected_apps = []
if dana_active: selected_apps.append("DANA")
if gopay_active: selected_apps.append("GoPay")
if shopee_active: selected_apps.append("ShopeePay")

if not selected_apps:
    st.warning("⚠️ Silakan klik tombol sakelar (toggle) di atas untuk mengaktifkan minimal satu aplikasi.")
    st.stop()
    
# =====================================================================
# D. PROSES FILTER DATA & JUDUL PEMBATAS KOMPARASI ULASAN
# =====================================================================
filtered_df = df_sentimen[df_sentimen['appName'].isin(selected_apps)]
is_comparative = len(selected_apps) > 1

st.markdown("---")
st.header("🔄 Hasil Analisis")

# =====================================================================
# F. VISUALISASI GRAFIK INTERAKTIF PLOTLY
# =====================================================================
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("**Statistik Volume Jumlah Ulasan Terfilter**")
    st.metric(label="Ulasan Ditampilkan", value=f"{len(filtered_df):,}")
    
    df_rating = filtered_df.groupby(['appName', 'score']).size().reset_index(name='Total')
    fig_rate = px.bar(df_rating, x='score', y='Total', color='appName', 
                      barmode='group' if is_comparative else 'stack',
                      title="Penyebaran Distribusi Rating Bintang Pengguna",
                      labels={'score': 'Rating Bintang', 'Total': 'Jumlah Ulasan'})
    st.plotly_chart(fig_rate, use_container_width=True)

with col_v2:
    if is_comparative:
        st.markdown("**Diagram Batang Distribusi Sentimen Komparatif**")
        df_chart = filtered_df.groupby(['appName', 'sentimen']).size().reset_index(name='Jumlah')
        fig_sent = px.bar(df_chart, x='appName', y='Jumlah', color='sentimen', barmode='group',
                          title="Perbandingan Proporsi Volume Sentimen Antar Aplikasi",
                          color_discrete_map={'Positif': '#2ca02c', 'Negatif': '#d62728'})
        st.plotly_chart(fig_sent, use_container_width=True)
    else:
        st.markdown("**Diagram Donat Proporsi Distribusi Sentimen Tunggal**")
        df_chart = filtered_df['sentimen'].value_counts().reset_index()
        fig_sent = px.pie(df_chart, values='count', names='sentimen', hole=0.4,
                          title=f"Proporsi Sentimen Aplikasi {selected_apps[0]}",
                          color_discrete_map={'Positif': '#2ca02c', 'Negatif': '#d62728'})
        st.plotly_chart(fig_sent, use_container_width=True)

# =====================================================================
# E. OUTPUT EVALUASI MODEL (NBC) SEPERTI PERMINTAAN
# =====================================================================
st.markdown("#### 🔮 Metrik Kinerja Algoritma NBC")
df_eval_filtered = df_evaluasi[df_evaluasi['aplikasi'].isin(selected_apps)].reset_index(drop=True)
st.dataframe(df_eval_filtered[['aplikasi', 'Accuracy', 'Precision', 'Recall', 'Specificity', 'F1-Score', 'jumlahDataTrain', 'jumlahDataTest']], use_container_width=True)

st.info("""
💡Mengetahui kemampuan NBC dalam menghasilkan prediksi pada proses analisis sentimen
""")

# =====================================================================
# G. GRAFIK TREN BULANAN, CONFUSION MATRIX & WORD CLOUD MALAM KATA
# =====================================================================
st.markdown("---")
st.markdown("**Grafik Tren Perkembangan Sentimen Bulanan**")
filtered_df['Bulan'] = filtered_df['date'].dt.to_period('M').astype(str)

if is_comparative:
    df_trend = filtered_df.groupby(['Bulan', 'appName', 'sentimen']).size().reset_index(name='Jumlah')
    df_trend_pos = df_trend[df_trend['sentimen'] == 'Positif']
    fig_trend = px.line(df_trend_pos, x='Bulan', y='Jumlah', color='appName',
                        title="Tren Naik-Turun Sentimen POSITIF Pengguna Setiap Bulan (Komparatif)",
                        markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    df_trend = filtered_df.groupby(['Bulan', 'sentimen']).size().reset_index(name='Jumlah')
    fig_trend = px.line(df_trend, x='Bulan', y='Jumlah', color='sentimen',
                        title=f"Tren Dinamika Sentimen Bulanan Aplikasi {selected_apps[0]}",
                        markers=True, color_discrete_map={'Positif': '#2ca02c', 'Negatif': '#d62728'})
    st.plotly_chart(fig_trend, use_container_width=True)

# Confusion Matrix Interaktif
st.markdown("---")
st.subheader("🔮 Hasil Pengujian Model Klasifikasi (Confusion Matrix)")
col_cm = st.columns(len(selected_apps))

for idx, app_name in enumerate(selected_apps):
    with col_cm[idx]:
        row = df_evaluasi[df_evaluasi['aplikasi'] == app_name]
        if not row.empty:
            row = row.iloc
            matrix_data = [[int(row['TN']), int(row['FP'])], [int(row['FN']), int(row['TP'])]]
            
            fig_cm = px.imshow(
                matrix_data,
                labels=dict(x="Prediksi Model", y="Data Aktual", color="Jumlah Ulasan"),
                x=['Negatif', 'Positif'], y=['Negatif', 'Positif'],
                text_auto=True, color_continuous_scale='Blues',
                title=f"Confusion Matrix: {app_name}"
            )
            fig_cm.update_layout(width=280, height=280, margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig_cm, use_container_width=True)

# =====================================================================
# H. EKSPLORASI KATA DOMINAN (WORD CLOUD & TOP 5 KATA)
# =====================================================================
st.markdown("---")
col_w1, col_w2 = st.columns(2)

all_text = " ".join(filtered_df['content'].astype(str))
words = all_text.split()
top_5_words_tuples = Counter(words).most_common(5)
top_5_words = [item[0] for item in top_5_words_tuples] if top_5_words_tuples else ["aplikasi"]

with col_w1:
    st.markdown("**Awan Kata Keseluruhan (Word Cloud)**")
    if all_text.strip():
        wordcloud = WordCloud(background_color="white", max_words=60, colormap="viridis", width=600, height=300).generate(all_text)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.write("Teks ulasan kosong.")

with col_w2:
    st.markdown("**Daftar 5 Top Kata Paling Dominan**")
