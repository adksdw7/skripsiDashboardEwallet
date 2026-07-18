import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os

# =====================================================================
# 1. KONFIGURASI HALAMAN UTAMA DASHBOARD (MURNI SCROLLING, TANPA SIDEBAR)
# =====================================================================
st.set_config_option('deprecation.showPyplotGlobalUse', False) if hasattr(st, 'set_config_option') else None
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
💡 **Kegunaan Website**: Dashboard web komparatif ini digunakan untuk membandingkan sentimen pengguna terhadap E-Wallet DANA, GoPay, dan ShopeePay secara instan tanpa harus membaca puluhan ribu ulasan manual.
""")

# =====================================================================
# C. INTERFASE TOMBOL IKON LOGO APLIKASI (MENGGUNAKAN SESSION STATE)
# =====================================================================
st.markdown("---")
st.subheader("📱 Pilih E-Wallet")

if 'dana_active' not in st.session_state: st.session_state.dana_active = True
if 'gopay_active' not in st.session_state: st.session_state.gopay_active = True
if 'shopee_active' not in st.session_state: st.session_state.shopee_active = True

col_btn1, col_btn2, col_btn3 = st.columns(3)

# Fungsi untuk merender elemen kartu logo dan tombol nama aplikasi di bawahnya
def render_kartu_ewallet(file_path, alt_text, is_active, label_btn, key_btn):
    # CSS dinamis: Jika aktif diberi border & shadow hitam tebal, jika tidak aktif hanya border abu tipis biasa
    if is_active:
        border_style = "border: 2px solid #000000; box-shadow: 0px 0px 15px rgba(0,0,0,0.4);"
    else:
        border_style = "border: 1px solid #e0e0e0; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);"
    
    # Deteksi apakah gambar ada di repositori untuk diubah ke HTML img
    import base64
    img_html = f'<p style="color: gray; font-size: 14px;">{alt_text}</p>'
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        img_html = f'<img src="data:image/png;base64,{data}" style="width: 100px; height: 100px; object-fit: contain; border-radius: 12px; display: block; margin: 0 auto;">'

    # Tampilkan struktur visual kotak atas (Hanya berisi Logo saja, nama aplikasi sudah dihapus dari sini)
    st.markdown(f"""
    <div style="{border_style} border-radius: 16px; padding: 25px 15px; text-align: center; background-color: #ffffff; margin-bottom: 10px;">
        {img_html}
    </div>
    """, unsafe_allow_html=True)
    
    # Tombol bawaan Streamlit sekarang langsung menampilkan teks nama aplikasi di dalamnya
    if st.button(label_btn, key=key_btn, use_container_width=True):
        st.session_state[f"{key_btn.replace('btn_', '')}_active"] = not is_active
        st.rerun()

with col_btn1:
    render_kartu_ewallet("logoDana.png", "[Logo DANA]", st.session_state.dana_active, "DANA", "btn_dana")

with col_btn2:
    render_kartu_ewallet("logoGopay.png", "[Logo GoPay]", st.session_state.gopay_active, "GoPay", "btn_gopay")

with col_btn3:
    render_kartu_ewallet("logoShopeepay.png", "[Logo ShopeePay]", st.session_state.shopee_active, "ShopeePay", "btn_shopee")

# Menyusun kembali daftar aplikasi aktif untuk filter data grafik di bawahnya
selected_apps = []
if st.session_state.dana_active: selected_apps.append("DANA")
if st.session_state.gopay_active: selected_apps.append("GoPay")
if st.session_state.shopee_active: selected_apps.append("ShopeePay")

if not selected_apps:
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
    # Modifikasi format metrik ulasan ditampilkan sesuai Poin 1.b
    st.metric(label="Ulasan", value=f"{len(filtered_df):,}", delta="Ditampilkan")
    
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
                          tfitle="Perbandingan Proporsi Volume Sentimen Antar Aplikasi",
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
# E. OUTPUT EVALUASI MODEL (NBC) SEPERTI PERMINTAAN (MUNCUL PER APLIKASI)
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
