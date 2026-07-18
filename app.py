import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter

# =====================================================================
# 1. KONFIGURASI HALAMAN UTAMA DASHBOARD
# =====================================================================
st.set_page_config(page_title="Analisis Sentimen E-Wallet", layout="wide")

# Opsi untuk menyembunyikan peringatan bawaan matplotlib tentang thread-safety
st.set_option('deprecation.showPyplotGlobalUse', False)

# =====================================================================
# 2. FUNGSI MEMUAT DATA DARI GITHUB (ANTI-BERAT, TANPA NBC ULANG)
# =====================================================================
@st.cache_data
def load_data():
    df_sentimen = pd.read_csv("hasilSentimen.csv")
    df_evaluasi = pd.read_csv("hasilEvaluasi.csv")
    
    # Menyelaraskan nama kolom tabel evaluasi model
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
# A. JUDUL DAN DESKRIPSI SINGKAT PENELITIAN (SANGAT BAGUS UNTUK SIDANG)
# =====================================================================
st.title("📊 WEB-DASHBOARD ANALITIK: ANALISIS SENTIMEN KOMPARATIF E-WALLET")
st.markdown("### **Implementasi Algoritma Multinomial Naïve Bayes Berbasis TF-IDF**")

st.info("""
💡 **Kegunaan Website**: Aplikasi dashboard interaktif non-realtime ini dirancang khusus untuk memetakan, 
menganalisis, dan membandingkan secara makro persepsi masyarakat Indonesia terhadap tiga layanan *e-wallet* terbesar 
(**DANA, GoPay, dan ShopeePay**). Melalui visualisasi interaktif ini, calon pengguna maupun penyedia layanan 
dapat melihat perbandingan indikator kepuasan konsumen secara instan tanpa harus membaca puluhan ribu ulasan manual.
""")

# =====================================================================
# B. STATISTIK GABUNGAN SELURUH APLIKASI (HISTORIS MAKRO)
# =====================================================================
st.markdown("---")
st.subheader("🌐 Rangkuman Statistik Global Terpadu (Integrated Dataset)")

# Perhitungan Metrik Gabungan Makro
total_ulasan_global = len(df_sentimen)
total_aplikasi_global = df_sentimen['appName'].nunique()
pos_count = (df_sentimen['sentimen'] == 'Positif').sum()
neg_count = (df_sentimen['sentimen'] == 'Negatif').sum()

# Sesuai ruang lingkup skripsi hal 26 (tidak menggunakan penyeimbangan/netral), 
# Persentase netral diisi 0% dengan keterangan ilmiah untuk dosen pembimbing.
persen_pos = (pos_count / total_ulasan_global) * 100
persen_neg = (neg_count / total_ulasan_global) * 100
persen_net = 0.0 

col_g1, col_g2, col_g3, col_g4, col_g5, col_g6 = st.columns(6)
col_g1.metric("Total Aplikasi", f"{total_aplikasi_global} Layanan")
col_g2.metric("Total Korpus Ulasan", f"{total_ulasan_global:,} Data")
col_g3.metric("Periode Dataset", "2025 - 2026")
col_g4.metric("Sentimen Positif", f"{persen_pos:.1f}%")
col_g5.metric("Sentimen Netral", f"{persen_net:.1f}%", help="Sesuai Ruang Lingkup No.5, rating 3 dihapus (non-balancing)")
col_g6.metric("Sentimen Negatif", f"{persen_neg:.1f}%")

# Menampilkan tabel evaluasi performa model klasifikasi NBC asli dari Colab di beranda
with st.expander("🔍 Lihat Hasil Evaluasi Performa Model Klasifikasi (Confusion Matrix)") :
    st.dataframe(df_evaluasi[['aplikasi', 'Accuracy', 'Precision', 'Recall', 'Specificity', 'F1-Score', 'jumlahDataTrain', 'jumlahDataTest']], use_container_width=True)

# =====================================================================
# C. DASHBOARD ANALITIK INTERAKTIF DENGAN FILTER PILIHAN USER
# =====================================================================
st.markdown("---")
st.subheader("🎛️ Panel Kontrol Analitik & Filter Komparatif")

# Menampilkan tombol pilihan aplikasi tepat di atas halaman utama website (Sesuai Konsep Poin 2)
list_apps = ["DANA", "GoPay", "ShopeePay"]
selected_apps = st.multiselect("Pilih Aplikasi E-Wallet untuk Dianalisis (Bisa Pilih 1, 2, atau 3 Aplikasi Sekaligus):", 
                               options=list_apps, default=list_apps)

# Filter Rentang Waktu Periode Dataset
min_date = df_sentimen['date'].min().to_pydatetime()
max_date = df_sentimen['date'].max().to_pydatetime()

col_t1, col_t2 = st.columns(2)
with col_t1:
    start_date = st.date_input("Tanggal Mulai Analisis:", min_value=min_date, max_value=max_date, value=min_date)
with col_t2:
    end_date = st.date_input("Tanggal Selesai Analisis:", min_value=min_date, max_value=max_date, value=max_date)

# Proteksi Filter Kosong
if not selected_apps:
    st.warning("⚠️ Silakan klik dan pilih minimal satu aplikasi E-Wallet di atas untuk memunculkan visualisasi grafik.")
    st.stop()

# Penyaringan (*Filtering*) Data Berdasarkan Kehendak Pengguna
filtered_df = df_sentimen[
    (df_sentimen['appName'].isin(selected_apps)) & 
    (df_sentimen['date'] >= pd.to_datetime(start_date)) & 
    (df_sentimen['date'] <= pd.to_datetime(end_date))
]

if filtered_df.empty:
    st.warning("⚠️ Tidak ditemukan rekaman data ulasan pada rentang tanggal tersebut.")
    st.stop()

# LOGIKA ALUR OTOMATIS: JIKA USER MEMILIH LEBIH DARI 1 APLIKASI -> PRESTASI MODE KOMPARATIF BERAKSI
is_comparative = len(selected_apps) > 1

# =====================================================================
# D. OUTPUT VISUALISASI GRAFIK YANG BISA GERAK-GERAK (INTERAKTIF PLOTLY)
# =====================================================================
st.markdown("### 📊 Hasil Output Visualisasi Analitik")

# Row 1: Informasi Jumlah Ulasan & Distribusi Sentimen
col_v1, col_v2 = st.columns(2)

with col_v1:
    st.markdown("**Statistik Volume Jumlah Ulasan Terfilter**")
    st.metric("Jumlah Ulasan yang Ditampilkan", f"{len(filtered_df):,} Baris")
    
    # Bar chart distribusi rating bintang (1-5)
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

# Row 2: Grafik Tren Sentimen Berbasis Waktu bulanan
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

# Row 3: Word Cloud, Top Kata Dominan, & Fitur Gila Ekstraksi Kueri Komentar Mentah 2026
st.markdown("---")
col_w1, col_w2 = st.columns(2)

# Menggabungkan teks untuk ekstraksi kata terpopuler
all_text = " ".join(filtered_df['content'].astype(str))
words = all_text.split()
# Mengambil 5 kata teratas/paling dominan dari korpus teks terfilter
top_5_words_tuples = Counter(words).most_common(5)
top_5_words = [item[0] for item in top_5_words_tuples] if top_5_words_tuples else ["sistem", "aplikasi", "dana", "gopay", "shopee"]

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
