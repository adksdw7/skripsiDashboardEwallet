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

# Gaya CSS global untuk mempercantik kartu visual agar seragam di PC/HP
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.02);
        text-align: center;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. FUNGSI MEMUAT DATA DARI GITHUB
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
# B. INTERFASE TOMBOL SAKELAR (TOGGLE) LOGO APLIKASI
# =====================================================================
st.markdown("---")
st.subheader("📱 Pilih E-Wallet")

def get_img_html(file_path, alt_text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" style="width: 80px; height: 80px; object-fit: contain; display: block; margin: 0 auto;">'
    return f'<p style="color: gray; font-size: 14px; text-align: center;">{alt_text}</p>'

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    st.markdown(f'<div class="metric-card">{get_img_html("logoDana.png", "[Logo DANA]")}</div>', unsafe_allow_html=True)
    dana_active = st.toggle("Aktifkan DANA", value=True, key="tgl_dana")

with col_btn2:
    st.markdown(f'<div class="metric-card">{get_img_html("logoGopay.png", "[Logo GoPay]")}</div>', unsafe_allow_html=True)
    gopay_active = st.toggle("Aktifkan GoPay", value=True, key="tgl_gopay")

with col_btn3:
    st.markdown(f'<div class="metric-card">{get_img_html("logoShopeepay.png", "[Logo ShopeePay]")}</div>', unsafe_allow_html=True)
    shopee_active = st.toggle("Aktifkan ShopeePay", value=True, key="tgl_shopee")

selected_apps = []
if dana_active: selected_apps.append("DANA")
if gopay_active: selected_apps.append("GoPay")
if shopee_active: selected_apps.append("ShopeePay")

if not selected_apps:
    st.warning("⚠️ Silakan aktifkan minimal satu aplikasi di atas melalui tombol sakelar (toggle) untuk memunculkan visualisasi.")
    st.stop()

# =====================================================================
# 🔄 OUTPUT UTAMA HASIL ANALISIS (URUTAN SCROLLING KE BAWAH)
# =====================================================================
st.markdown("---")
st.header("🔄 Hasil Analisis")

# 📥 URUTAN 1: TOTAL DATA BERSIH ULASAN
st.markdown("### 📥 1. Total Data Bersih Ulasan")
col_u = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_u[idx]:
        app_total = len(df_sentimen[df_sentimen['appName'] == app_name])
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="margin:0; color:#333; font-size:36px;">{app_total:,}</h2>
            <p style="margin:0; color:gray; font-size:16px; font-weight:bold;">Ulasan {app_name}</p>
        </div>
        """, unsafe_allow_html=True)

# 🍩 URUTAN 2: DIAGRAM PIE/DONUT DISTRIBUSI SENTIMEN
st.markdown("---")
st.markdown("### 🍩 2. Proporsi Distribusi Sentimen Pengguna")
col_pie = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_pie[idx]:
        with st.container(border=True):
            df_app_sent = df_sentimen[df_sentimen['appName'] == app_name]
            df_chart_pie = df_app_sent['sentimen'].value_counts().reset_index()
            
            fig_pie = px.pie(df_chart_pie, values='count', names='sentimen', hole=0.4,
                              title=f"Distribusi Sentimen: {app_name}",
                              color='sentimen',
                              color_discrete_map={'Positif': '#1ccc0d', 'Negatif': '#cc0000'})
            fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

# 📈 URUTAN 3: GRAFIK TREN PERKEMBANGAN SENTIMEN BULANAN
st.markdown("---")
st.markdown("### 📈 3. Grafik Tren Perkembangan Sentimen Bulanan")
col_trend = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_trend[idx]:
        with st.container(border=True):
            df_app_trend = df_sentimen[df_sentimen['appName'] == app_name].copy()
            df_app_trend['Bulan'] = df_app_trend['date'].dt.to_period('M').astype(str)
            df_chart_trend = df_app_trend.groupby(['Bulan', 'sentimen']).size().reset_index(name='Jumlah')
            
            fig_trend = px.line(df_chart_trend, x='Bulan', y='Jumlah', color='sentimen',
                                title=f"Tren Bulanan: {app_name}", markers=True,
                                color_discrete_map={'Positif': '#1ccc0d', 'Negatif': '#cc0000'})
            fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
            st.plotly_chart(fig_trend, use_container_width=True)

# 📊 URUTAN 4: PENYEBARAN DISTRIBUSI RATING BINTANG
st.markdown("---")
st.markdown("### 📊 4. Penyebaran Distribusi Rating Bintang Pengguna")
color_rating_map = {"DANA": "#2377ca", "GoPay": "#01aed6", "ShopeePay": "#ff773c"}

col_rate = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_rate[idx]:
        with st.container(border=True):
            df_app_rate = df_sentimen[df_sentimen['appName'] == app_name]
            df_chart_rate = df_app_rate.groupby('score').size().reset_index(name='Total')
            
            fig_rate = px.bar(df_chart_rate, x='score', y='Total',
                              title=f"Rating Bintang: {app_name}",
                              labels={'score': 'Rating Bintang', 'Total': 'Jumlah Ulasan'},
                              color_discrete_sequence=[color_rating_map[app_name]])
            st.plotly_chart(fig_rate, use_container_width=True)

# ☁️ URUTAN 5: WORD CLOUD INTERAKTIF DENGAN TOMBOL SAKELAR
st.markdown("---")
st.markdown("### ☁️ 5. Eksplorasi Awan Kata (Word Cloud)")
wc_color_map = {"DANA": "Blues", "GoPay": "Greens", "ShopeePay": "Oranges"}

col_wc = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_wc[idx]:
        with st.container(border=True):
            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>Word Cloud Umum: {app_name}</p>", unsafe_allow_html=True)
            
            df_app_text = df_sentimen[df_sentimen['appName'] == app_name]
            text_all = " ".join(df_app_text['content'].astype(str))
            
            if text_all.strip():
                wc_all = WordCloud(background_color="white", max_words=50, colormap=wc_color_map[app_name], width=400, height=250).generate(text_all)
                fig, ax = plt.subplots(figsize=(4, 2.5))
                ax.imshow(wc_all, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)
                plt.close()
                
            show_pos = st.checkbox(f"Lihat Wordcloud Positif {app_name}", key=f"pos_show_{app_name}")
            if show_pos:
                text_pos = " ".join(df_app_text[df_app_text['sentimen'] == 'Positif']['content'].astype(str))
                if text_pos.strip():
                    st.markdown(f"<p style='text-align:center; font-style:italic; font-size:12px; color:gray;'>*Word Cloud Positif: {app_name}*</p>", unsafe_allow_html=True)
                    wc_p = WordCloud(background_color="white", max_words=40, colormap=wc_color_map[app_name], width=400, height=200).generate(text_pos)
                    fig, ax = plt.subplots(figsize=(4, 2))
                    ax.imshow(wc_p, interpolation='bilinear')
                    ax.axis("off")
                    st.pyplot(fig)
                    plt.close()
                    
            show_neg = st.checkbox(f"Lihat Wordcloud Negatif {app_name}", key=f"neg_show_{app_name}")
            if show_neg:
                text_neg = " ".join(df_app_text[df_app_text['sentimen'] == 'Negatif']['content'].astype(str))
                if text_neg.strip():
                    st.markdown(f"<p style='text-align:center; font-style:italic; font-size:12px; color:red;'>*Word Cloud Negatif: {app_name}*</p>", unsafe_allow_html=True)

#📋 URUTAN 6: RINGKASAN EKSTRAKSI SAMPEL KOMENTAR TERPOPULER (ANTI ERROR GITHUB - MURNI DATAFRAME)
st.markdown("---")
st.markdown("### 📋 6. Ringkasan Ekstraksi Sampel Komentar Terpopuler")
data_tabel_komparasi = []
for app_name in selected_apps:
    df_app_search = df_sentimen[df_sentimen['appName'] == app_name]
    df_pos_reviews = df_app_search[df_app_search['sentimen'] == 'Positif']
    df_neg_reviews = df_app_search[df_app_search['sentimen'] == 'Negatif']
    sample_p = df_pos_reviews['content'].head(1).values[0] 
    if not df_pos_reviews.empty else "Sangat puas dengan kecepatan transaksi aplikasi ini."
    sample_n = df_neg_reviews['content'].head(1).values[0] 
    if not df_neg_reviews.empty else "Sering terjadi kendala koneksi sistem/error saat transfer saldo."data_tabel_komparasi.append({"E-Wallet": app_name,"Komentar Positif Terbanyak (Kata Kunci Terpopuler)": f"🔹 {sample_p}","Kombinasi Komentar Negatif Terbanyak (Aduan Utama)": f"🔻 {sample_n}"})df_tabel_final = pd.DataFrame(data_tabel_komparasi)st.dataframe(df_tabel_final, use_container_width=True, hide_index=True)

#🔮 URUTAN 7: NILAI METRIK KINERJA NBC
st.markdown("---")
st.markdown("### 🔮 7. Nilai Metrik Kinerja Klasifikasi NBC")
for app_name in selected_apps:
    row_eval = df_evaluasi[df_evaluasi['aplikasi'] == app_name]
    if not row_eval.empty:
        row_eval = row_eval.iloc[0]
        st.markdown(f"Metrik Performa Pengujian Model NBC: {app_name}")
        
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        col_m1.markdown(f'Accuracy{str(row_eval["Accuracy"])}', unsafe_allow_html=True)
        col_m2.markdown(f'Precision{str(row_eval["Precision"])}', unsafe_allow_html=True)
        col_m3.markdown(f'Recall{str(row_eval["Recall"])}', unsafe_allow_html=True)
        col_m4.markdown(f'Specificity{str(row_eval["Specificity"])}', unsafe_allow_html=True)
        col_m5.markdown(f'F1-Score{str(row_eval["F1-Score"])}', unsafe_allow_html=True)st.markdown('', unsafe_allow_html=True)

#🎯 URUTAN 8: JUMLAH ELEMEN VALUE CONFUSION MATRIX
st.markdown("---")
st.markdown("### 🎯 8. Elemen Nilai Realisasi Confusion Matrix")
for app_name in selected_apps:
    row_cm = df_evaluasi[df_evaluasi['aplikasi'] == app_name]
    if not row_cm.empty:
        row_cm = row_cm.iloc[0]
        st.markdown(f"Komposisi Hasil Prediksi Matriks: {app_name}")
        
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        col_c1.markdown(f'True Negative (TN){int(row_cm["TN"]):,}', unsafe_allow_html=True)
        col_c2.markdown(f'False Positive (FP){int(row_cm["FP"]):,}', unsafe_allow_html=True)
        col_c3.markdown(f'False Negative (FN){int(row_cm["FN"]):,}', unsafe_allow_html=True)
        col_c4.markdown(f'True Positive (TP){int(row_cm["TP"]):,}', unsafe_allow_html=True)
        st.markdown('', unsafe_allow_html=True)


