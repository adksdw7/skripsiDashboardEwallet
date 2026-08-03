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
# Tujuan   : mengatur judul tab browser, layout lebar penuh (tanpa sidebar
#            karena semua navigasi dilakukan dengan scrolling ke bawah),
#            dan gaya CSS global untuk kartu metrik (.metric-card)
# Output   : konfigurasi halaman + style yang dipakai di seluruh dashboard
# =====================================================================
st.set_page_config(page_title="Komparasi Sentimen E-Wallet", layout="wide")

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
    /* Menengahkan teks HANYA pada dua info box tertentu (dibungkus
       st.container(key=...) di bawah), supaya kotak info/warning lain
       di dashboard tidak ikut berubah perataannya. */
    .st-key-info_kegunaan [data-testid="stAlertContainer"],
    .st-key-info_kegunaan [data-testid="stAlert"],
    .st-key-info_periode [data-testid="stAlertContainer"],
    .st-key-info_periode [data-testid="stAlert"] {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    hr {
        border: none;
        height: 4px;
        border-radius: 2px;
        background: linear-gradient(90deg, #2377ca, #01aed6, #ff773c);
        margin: 2.5rem 0;
        opacity: 10;
    }
    /* ====== 1. FONT: Plus Jakarta Sans ====== */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"],
    p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* ====== 2. BACKGROUND: blur pastel perpaduan 3 warna aplikasi ====== */
    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(35, 119, 202, 0.16) 0%, transparent 42%),
            radial-gradient(circle at 92% 18%, rgba(1, 174, 214, 0.14) 0%, transparent 42%),
            radial-gradient(circle at 50% 100%, rgba(255, 119, 60, 0.13) 0%, transparent 48%),
            #fafbfc;
        background-attachment: fixed;
    }

    /* ====== 3. BORDER TEGAS + SHADOW di semua kartu & container ====== */
    .metric-card {
        border: 2px solid #d7dce2 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 16px rgba(0,0,0,0.08), 0 16px 32px rgba(0,0,0,0.1) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.12) !important;
    }

    .landing-card {
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 2px solid #d7dce2 !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important;
    }

    [data-testid="stAlertContainer"] {
        border-radius: 12px !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06) !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. FUNGSI MEMUAT SELURUH DATA (SUMBER TUNGGAL)
# Asal    : file CSV hasil pipeline Colab (01scraping, 02preparation,
#           03modelling) yang disimpan satu repo dengan app.py
# Tujuan  : membaca semua CSV yang dibutuhkan dashboard HANYA SEKALI,
#           lalu men-cache-nya (@st.cache_data) supaya tidak dibaca
#           ulang setiap kali user berinteraksi dengan toggle/tombol.
#           Ini menggantikan versi lama yang membaca rawDana.csv,
#           rawGopay.csv, rawShopeepay.csv DUA KALI (di dalam dan di
#           luar fungsi load_data) — bug redundansi yang sudah dihapus.
# Output  : df_sentimen, df_evaluasi, df_raw_dana, df_raw_gopay,
#           df_raw_shopee — lima DataFrame yang dipakai di seluruh
#           bagian dashboard.
# =====================================================================
@st.cache_data
def load_data():
    # --- Data hasil klasifikasi sentimen & evaluasi model ---
    df_sentimen = pd.read_csv("hasilSentimen.csv")
    df_evaluasi = pd.read_csv("hasilEvaluasi.csv")

    # --- Data ulasan mentah (dipakai untuk menampilkan teks ulasan asli) ---
    df_raw_dana = pd.read_csv("rawDana.csv")
    df_raw_gopay = pd.read_csv("rawGopay.csv")
    df_raw_shopee = pd.read_csv("rawShopeepay.csv")

    # Penamaan ulang kolom hasil evaluasi agar konsisten dipakai di dashboard
    if len(df_evaluasi.columns) >= 12:
        df_evaluasi.columns = [
            'aplikasi', 'Accuracy', 'Precision', 'Recall', 'Specificity',
            'F1-Score', 'jumlahDataTrain', 'jumlahDataTest',
            'TN', 'FP', 'FN', 'TP'
        ]

    # Konversi kolom tanggal ke tipe datetime agar bisa diagregasi per bulan
    df_sentimen['date'] = pd.to_datetime(df_sentimen['date'])

    return df_sentimen, df_evaluasi, df_raw_dana, df_raw_gopay, df_raw_shopee


try:
    df_sentimen, df_evaluasi, df_raw_dana, df_raw_gopay, df_raw_shopee = load_data()
except Exception as e:
    st.error(f"Gagal memuat data CSV. Pastikan file berada di repositori yang sama. Error: {e}")
    st.stop()


# Warna identitas tiap aplikasi — dipakai berulang di banyak grafik/kartu,
# jadi didefinisikan sekali di sini sebagai satu sumber kebenaran warna.
APP_COLOR_MAP = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


# =====================================================================
# FUNGSI BANTUAN: MENAMPILKAN LOGO SEBAGAI GAMBAR BASE64
# Tujuan : mengubah file logo lokal (png) menjadi tag <img> yang bisa
#          ditempel langsung di dalam HTML markdown Streamlit.
# Output : string HTML <img> jika file logo ditemukan, atau teks
#          placeholder abu-abu jika file tidak ada.
# =====================================================================
def get_img_html(file_path, alt_text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" style="width: 80px; height: 80px; object-fit: contain;">'
    return f'<p style="color: gray; font-size: 14px; text-align: center;">{alt_text}</p>'


# =====================================================================
# FUNGSI: MENGAMBIL 10 ULASAN ASLI TERKAIT KATA TERPOPULER
# Asal   : mencocokkan konten yang sudah diklasifikasi di df_sentimen
#          dengan teks aslinya di file raw (df_raw_dana/gopay/shopee)
# Tujuan : menampilkan ulasan asli (belum di-preprocessing) kepada user
#          agar lebih mudah dibaca, saat toggle "tampilkan ulasan" aktif
# Output : list berisi maksimal 10 string ulasan asli
# Catatan: versi lama mendefinisikan fungsi bernama sama ini DUA KALI —
#          definisi pertama (yang mengandalkan file eksternal terpisah
#          via load_raw_reviews) tidak pernah terpakai karena langsung
#          ditimpa definisi kedua. Duplikasi itu sudah dihapus di sini,
#          hanya menyisakan satu implementasi yang benar-benar dipakai.
# =====================================================================
def get_top_reviews(app_name, sentiment):
    if app_name == "DANA":
        df_raw = df_raw_dana.copy()
    elif app_name == "GoPay":
        df_raw = df_raw_gopay.copy()
    elif app_name == "ShopeePay":
        df_raw = df_raw_shopee.copy()
    else:
        return []

    df_sent = df_sentimen[
        (df_sentimen['appName'] == app_name) &
        (df_sentimen['sentimen'] == sentiment)
    ][['content']]

    if df_sent.empty:
        return []

    df_sent['content'] = df_sent['content'].astype(str).str.lower().str.strip()
    df_raw['content'] = df_raw['content'].astype(str).str.lower().str.strip()

    hasil = df_raw[df_raw['content'].isin(df_sent['content'])]

    if hasil.empty:
        return []

    return hasil['content'].drop_duplicates().head(10).tolist()


# Fungsi pewarna khusus wordcloud negatif (selalu merah, tidak memakai colormap)
def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "#cc0000"


# =====================================================================
# A. JUDUL DAN DESKRIPSI SINGKAT PENELITIAN
# =====================================================================
st.title("📊 KOMPARATIF SENTIMEN E-WALLET DANA, GOPAY & SHOPEEPAY")
with st.container(key="info_kegunaan"):
    st.info("""**Kegunaan Dashboard Web**: Membandingkan sentimen pengguna terhadap E-Wallet DANA, GoPay, dan ShopeePay berdasarkan ulasan Google Play Store.""")


# =====================================================================
# B. INFORMASI / TINJAUAN PUSTAKA PER APLIKASI (LANDING PAGE)
# Asal   : logo aplikasi (logoDana.png, logoGopay.png, logoShopeepay.png)
#          + teks tinjauan pustaka masing-masing aplikasi
# Tujuan : menyambut user dengan kartu penuh berisi logo + penjelasan
#          tiap aplikasi, langsung tampil tanpa perlu memilih apa pun.
#          Logo dipaksa berukuran sama persis (lebar & tinggi tetap,
#          object-fit: contain) supaya adil antar aplikasi meski file
#          logo aslinya punya rasio/resolusi berbeda-beda.
# Output : tiga kartu (DANA, GoPay, ShopeePay), masing-masing berwarna
#          sesuai identitas aplikasi, dan responsif — pada layar sempit
#          logo pindah ke atas teks (bertumpuk vertikal) via CSS
#          flex-wrap, bukan ukuran diperkecil paksa oleh Streamlit.
# =====================================================================
st.markdown("---")

LANDING_CARD_COLOR = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}

# Placeholder teks tinjauan pustaka — silakan ganti isi dictionary ini
APP_DESCRIPTIONS = {
    "DANA": "Aplikasi dengan penerapan sistem open platform yang mempermudah integrasi berbagai mitra bisnis dan aplikasi pihak ketiga. Fokus operasionalnya diarahkan untuk memfasilitasi ekosistem transaksi harian secara non-tunai, seperti transfer dana, pembayaran tagihan, dan pemindaian kode QRIS. Ketersediaan fitur DANA Bisnis menjadi nilai tambah penting dalam mendukung digitalisasi dan manajemen keuangan para pelaku UMKM",
    "GoPay": "Produk finansial dari GoTo Financial yang kini beroperasi sebagai aplikasi mandiri ini lebih menekankan fungsionalitasnya pada efisiensi manajemen keuangan personal. Di samping melayani kebutuhan transaksi pembayaran dan transfer dana, keunggulan utamanya berada pada sistem pencatatan pengeluaran otomatis. Aplikasi ini juga memperluas cakupan layanannya melalui integrasi perbankan digital lewat fitur GoPay Tabungan by Jago",
    "ShopeePay": "Keunggulan aplikasi yang dikelola oleh PT AirPay International Indonesia ini berakar kuat pada ekosistem belanja daring aplikasi Shopee. Setelah memperluas jangkauannya melalui aplikasi mandiri, sistem fokus pada penyelesaian transaksi komersial yang instan, pengelolaan beberapa sumber dana sekaligus, serta perluasan akses pembayaran berbasis QRIS di berbagai merchant luring"
}

APP_LOGO_FILE = {
    "DANA": "logoDana.png",
    "GoPay": "logoGopay.png",
    "ShopeePay": "logoShopeepay.png"
}

# Tautan resmi Play Store tiap aplikasi — dibuka di tab baru saat tombol
# "Download di Play Store" pada kartu masing-masing aplikasi diklik.
# Bukan auto-download, hanya mengarahkan user ke halaman Play Store.
APP_PLAYSTORE_URL = {
    "DANA": "https://play.google.com/store/apps/details?id=id.dana&hl=id",
    "GoPay": "https://play.google.com/store/apps/details?id=com.gojek.gopay&hl=id",
    "ShopeePay": "https://play.google.com/store/apps/details?id=com.shopeepay.id&hl=id"
}

# Tautan website resmi tiap aplikasi — dibuka di tab baru saat tombol
# "Kunjungi Website Resmi" pada kartu masing-masing aplikasi diklik.
APP_WEBSITE_URL = {
    "DANA": "https://www.dana.id/",
    "GoPay": "https://gopay.co.id/",
    "ShopeePay": "https://shopeepay.co.id/"
}

# CSS khusus kartu landing — ukuran logo dipatok tetap (fixed) di semua
# breakpoint, dan layout pakai flexbox agar otomatis menyesuaikan lebar
# layar (menciut jadi tumpukan vertikal di HP, sejajar di tablet/laptop)
st.markdown("""
<style>
    .landing-card {
        border: 2px solid var(--card-color);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 24px;
    }
    .landing-logo-wrap {
        flex: 0 0 auto;
        width: 100px;
        height: 100px;
        border-radius: 16px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .landing-logo-wrap img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    .landing-text-wrap {
        flex: 1 1 280px;
        min-width: 0;
    }
    .landing-text-wrap h2 {
        margin: 0 0 8px 0;
        color: var(--card-color);
        font-size: 28px;
    }
    .landing-text-wrap p {
        margin: 0;
        color: #333333;
        font-size: 15px;
        line-height: 1.6;
    }
    .landing-btn-row {
        display: flex;
        flex-direction: row;
        justify-content: flex-end;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 14px;
    }
    .landing-download-btn {
        display: inline-block;
        padding: 8px 18px;
        border: 2px solid var(--card-color);
        border-radius: 8px;
        color: #222222;
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        background-color: #ffffff;
        white-space: nowrap;
    }
    .landing-download-btn:hover {
        background-color: rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

for app_name in ["DANA", "GoPay", "ShopeePay"]:
    color_code = LANDING_CARD_COLOR[app_name]
    logo_html = get_img_html(APP_LOGO_FILE[app_name], f"[Logo {app_name}]")
    website_url = APP_WEBSITE_URL[app_name]
    playstore_url = APP_PLAYSTORE_URL[app_name]
    st.markdown(
        f'''
        <div class="landing-card" style="--card-color: {color_code};">
            <div class="landing-logo-wrap">{logo_html}</div>
            <div class="landing-text-wrap">
                <h2>{app_name}</h2>
                <p>{APP_DESCRIPTIONS[app_name]}</p>
                <div class="landing-btn-row">
                    <a class="landing-download-btn" href="{website_url}" target="_blank" rel="noopener noreferrer">Kunjungi Website Resmi</a>
                    <a class="landing-download-btn" href="{playstore_url}" target="_blank" rel="noopener noreferrer">Download di Play Store</a>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )


# =====================================================================
# D. INTERFASE TOMBOL SAKELAR (TOGGLE) LOGO APLIKASI
# Tujuan : menentukan aplikasi mana yang ikut dianalisis di seluruh
#          bagian "Hasil Analisis" di bawahnya.
# =====================================================================
st.markdown("---")
st.markdown(
    """
    <h3 style="text-align:center; width:100%; margin-bottom:10px;">
        📱 Pilih E-Wallet
    </h3>
    """,
    unsafe_allow_html=True
)

col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    st.markdown(f'<div class="metric-card">{get_img_html("logoDana.png", "[Logo DANA]")}</div>', unsafe_allow_html=True)
    dana_active = st.toggle("DANA", value=True, key="tgl_dana")
with col_btn2:
    st.markdown(f'<div class="metric-card">{get_img_html("logoGopay.png", "[Logo GoPay]")}</div>', unsafe_allow_html=True)
    gopay_active = st.toggle("GoPay", value=True, key="tgl_gopay")
with col_btn3:
    st.markdown(f'<div class="metric-card">{get_img_html("logoShopeepay.png", "[Logo ShopeePay]")}</div>', unsafe_allow_html=True)
    shopee_active = st.toggle("ShopeePay", value=True, key="tgl_shopee")

selected_apps = []
if dana_active:
    selected_apps.append("DANA")
if gopay_active:
    selected_apps.append("GoPay")
if shopee_active:
    selected_apps.append("ShopeePay")

# Jika tidak ada toggle yang aktif, seluruh bagian "Hasil Analisis" di
# bawah TIDAK akan ditampilkan sama sekali — dan warning tetap muncul.
if not selected_apps:
    st.warning("⚠️ Silakan pilih minimal satu aplikasi E-Wallet")
    st.stop()


# =====================================================================
# 🔄 OUTPUT UTAMA HASIL ANALISIS (URUTAN SCROLLING KE BAWAH)
# =====================================================================
st.markdown("---")
st.markdown(
    """
    <h1 style="text-align:center; width:100%; margin-bottom:20px;">
        🔄 Hasil Analisis 🔄
    </h1>
    """,
    unsafe_allow_html=True
)
with st.container(key="info_periode"):
    st.info("Data yang disajikan merupakan ulasan pengguna selama periode 1 Juni 2025 hingga 31 Mei 2026")

# ------------------------------------------------------------
# URUTAN 1: TOTAL DATA BERSIH ULASAN
# ------------------------------------------------------------
st.markdown("### 📥 Total Data Ulasan")

col_u = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_u[idx]:
        app_total = len(df_sentimen[df_sentimen['appName'] == app_name])
        st.markdown(
            f'<div class="metric-card"><h2 style="margin:0;color:{APP_COLOR_MAP[app_name]};">{app_total:,}</h2><p style="margin:5px 0 0 0;color:gray;font-size:14px;">Total Ulasan {app_name}</p></div>',
            unsafe_allow_html=True
        )

# ------------------------------------------------------------
# URUTAN 2: DIAGRAM PIE/DONUT DISTRIBUSI SENTIMEN + PERSENTASE
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### Proporsi Distribusi Sentimen Pengguna")

col_pie = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_pie[idx]:
        with st.container(border=True):
            df_app_sent = df_sentimen[df_sentimen['appName'] == app_name]
            df_chart_pie = df_app_sent['sentimen'].value_counts().reset_index()

            fig_pie = px.pie(
                df_chart_pie, values='count', names='sentimen', hole=0.4,
                title=f"Distribusi Sentimen: {app_name}",
                color='sentimen',
                color_discrete_map={'Positif': '#1ccc0d', 'Negatif': '#cc0000'}
            )
            fig_pie.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

            # --- Persentase digabung ke kartu yang sama ---
            total_app_review = len(df_app_sent)
            if total_app_review > 0:
                pos_count = len(df_app_sent[df_app_sent['sentimen'] == 'Positif'])
                neg_count = len(df_app_sent[df_app_sent['sentimen'] == 'Negatif'])
                pos_pct = (pos_count / total_app_review) * 100
                neg_pct = (neg_count / total_app_review) * 100
                color_code = APP_COLOR_MAP.get(app_name, "#2377ca")

                col_neg, col_pos = st.columns(2)
                with col_neg:
                    st.markdown(f'''
                    <div style="text-align:center;">
                        <h2 style="margin:0; color:{color_code}; font-size: 30px; font-weight: bold;">{neg_pct:.1f}%</h2>
                        <p style="margin:2px 0 0 0; color: gray; font-size: 13px;">Sentimen Negatif</p>
                    </div>
                    ''', unsafe_allow_html=True)
                with col_pos:
                    st.markdown(f'''
                    <div style="text-align:center;">
                        <h2 style="margin:0; color:{color_code}; font-size: 30px; font-weight: bold;">{pos_pct:.1f}%</h2>
                        <p style="margin:2px 0 0 0; color: gray; font-size: 13px;">Sentimen Positif</p>
                    </div>
                    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# URUTAN 3: GRAFIK TREN PERKEMBANGAN SENTIMEN BULANAN
# (positif & negatif ditampilkan terpisah — ini yang menggantikan
#  fungsi filter periode yang tidak lagi diperlukan)
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### 📈 Grafik Tren Perkembangan Sentimen Bulanan")

filtered_df = df_sentimen[df_sentimen['appName'].isin(selected_apps)].copy()
filtered_df['Bulan'] = filtered_df['date'].dt.to_period('M').astype(str)

df_chart_trend_global = (
    filtered_df
    .groupby(['Bulan', 'appName', 'sentimen'])
    .size()
    .reset_index(name='Jumlah')
)

with st.container(border=True):
    df_pos_trend = df_chart_trend_global[df_chart_trend_global['sentimen'] == 'Positif']
    fig_trend_pos = px.line(
        df_pos_trend, x='Bulan', y='Jumlah', color='appName', markers=True,
        title="📈 Tren Perkembangan Sentimen Positif Bulanan",
        color_discrete_map=APP_COLOR_MAP
    )
    fig_trend_pos.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        xaxis_title="Periode Bulan", yaxis_title="Jumlah Ulasan"
    )
    st.plotly_chart(fig_trend_pos, use_container_width=True)

with st.container(border=True):
    df_neg_trend = df_chart_trend_global[df_chart_trend_global['sentimen'] == 'Negatif']
    fig_trend_neg = px.line(
        df_neg_trend, x='Bulan', y='Jumlah', color='appName', markers=True,
        title="📉 Tren Perkembangan Sentimen Negatif Bulanan",
        color_discrete_map=APP_COLOR_MAP
    )
    fig_trend_neg.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        xaxis_title="Periode Bulan", yaxis_title="Jumlah Ulasan"
    )
    st.plotly_chart(fig_trend_neg, use_container_width=True)

# ------------------------------------------------------------
# URUTAN 4: PENYEBARAN DISTRIBUSI RATING BINTANG
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### 📊 Penyebaran Distribusi Rating Bintang Pengguna")

if len(selected_apps) == 1:
    app_name = selected_apps[0]
    with st.container(border=True):
        df_app_rate = df_sentimen[df_sentimen['appName'] == app_name]
        df_chart_rate = df_app_rate.groupby('score').size().reset_index(name='Total')

        fig_rate = px.bar(
            df_chart_rate, x='score', y='Total',
            title=f"Distribusi Rating Bintang: {app_name}",
            labels={'score': 'Rating Bintang', 'Total': 'Jumlah Ulasan'},
            color_discrete_sequence=[APP_COLOR_MAP[app_name]]
        )
        fig_rate.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_rate, use_container_width=True)
else:
    df_rating_group = df_sentimen[df_sentimen['appName'].isin(selected_apps)]
    df_rating_group = df_rating_group.groupby(['score', 'appName']).size().reset_index(name='Total')

    fig_rate_group = px.bar(
        df_rating_group, x='score', y='Total', color='appName', barmode='group',
        title="Komparasi Distribusi Rating Bintang E-Wallet",
        labels={'score': 'Rating Bintang', 'Total': 'Jumlah Ulasan', 'appName': 'Aplikasi'},
        color_discrete_map=APP_COLOR_MAP
    )
    fig_rate_group.update_layout(
        xaxis=dict(dtick=1),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_rate_group, use_container_width=True)

# ------------------------------------------------------------
# URUTAN 5: WORD CLOUD SENTIMEN + TOGGLE ULASAN TERKAIT
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### ☁️ Word Cloud Sentimen")

wc_positive_color = {"DANA": "Blues", "GoPay": "Greens", "ShopeePay": "Oranges"}

col_wc = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_wc[idx]:
        with st.container(border=True):
            df_app_text = df_sentimen[df_sentimen['appName'] == app_name]

            # --- Word Cloud Positif ---
            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>Word Cloud Positif {app_name}</p>", unsafe_allow_html=True)

            text_positive = " ".join(df_app_text[df_app_text['sentimen'] == "Positif"]['content'].astype(str))
            if text_positive.strip():
                wc_positive = WordCloud(
                    background_color="white", max_words=50,
                    colormap=wc_positive_color[app_name], width=400, height=250
                ).generate(text_positive)

                fig, ax = plt.subplots(figsize=(4, 2.5))
                ax.imshow(wc_positive, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                plt.close()

            show_positive = st.toggle(f"Tampilkan ulasan positif {app_name}", key=f"positive_{app_name}")
            if show_positive:
                st.markdown("**10 Contoh Ulasan Positif:**")
                positive_reviews = get_top_reviews(app_name, "Positif")
                if positive_reviews:
                    for i, review in enumerate(positive_reviews, 1):
                        st.write(f"{i}. {review}")
                else:
                    st.info("Data ulasan positif tidak ditemukan.")

            # --- Word Cloud Negatif ---
            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-top:15px; margin-bottom:5px;'>Word Cloud Negatif {app_name}</p>", unsafe_allow_html=True)

            text_negative = " ".join(df_app_text[df_app_text['sentimen'] == "Negatif"]['content'].astype(str))
            if text_negative.strip():
                wc_negative = WordCloud(
                    background_color="white", max_words=50, width=400, height=250
                ).generate(text_negative)
                wc_negative.recolor(color_func=red_color_func)

                fig, ax = plt.subplots(figsize=(4, 2.5))
                ax.imshow(wc_negative, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                plt.close()

            show_negative = st.toggle(f"Tampilkan ulasan negatif {app_name}", key=f"negative_{app_name}")
            if show_negative:
                st.markdown("**10 Contoh Ulasan Negatif:**")
                negative_reviews = get_top_reviews(app_name, "Negatif")
                if negative_reviews:
                    for i, review in enumerate(negative_reviews, 1):
                        st.write(f"{i}. {review}")
                else:
                    st.info("Data ulasan negatif tidak ditemukan.")

# ------------------------------------------------------------
# URUTAN 6: NILAI METRIK KINERJA KLASIFIKASI NBC
# ------------------------------------------------------------
st.markdown("---")
st.markdown("### Nilai Metrik Kinerja Klasifikasi NBC")

for app_name in selected_apps:
    row_eval = df_evaluasi[df_evaluasi['aplikasi'] == app_name]
    if not row_eval.empty:
        row_eval = row_eval.iloc[0]
        app_color = APP_COLOR_MAP.get(app_name, "#2377ca")

        st.markdown(f"**Metrik Performa Pengujian Model NBC: {app_name}**")
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

        metric_labels = [
            ("Accuracy", col_m1), ("Precision", col_m2), ("Recall", col_m3),
            ("Specificity", col_m4), ("F1-Score", col_m5)
        ]
        for label, col in metric_labels:
            col.markdown(
                f'''
                <div class="metric-card">
                    <p style="margin:0;color:gray;font-size:14px;">{label}</p>
                    <h3 style="margin:0;color:{app_color};">{str(row_eval[label])}</h3>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
            # Confusion Matrix
        st.markdown(f"<p style='text-align:center;font-weight:bold;margin-top:10px;'>Confusion Matrix: {app_name}</p>", unsafe_allow_html=True)
        st.markdown(f'''
        <table style="width:100%;text-align:center;border-collapse:collapse;">
            <tr>
                <td></td>
                <td style="font-weight:bold;padding:6px;">Prediksi Positif</td>
                <td style="font-weight:bold;padding:6px;">Prediksi Negatif</td>
            </tr>
            <tr>
                <td style="font-weight:bold;padding:6px;">Aktual Positif</td>
                <td style="background:#eafbe7;padding:10px;border:1px solid #ddd;">{int(row_eval['TP'])} (TP)</td>
                <td style="background:#fdeaea;padding:10px;border:1px solid #ddd;">{int(row_eval['FN'])} (FN)</td>
            </tr>
            <tr>
                <td style="font-weight:bold;padding:6px;">Aktual Negatif</td>
                <td style="background:#fdeaea;padding:10px;border:1px solid #ddd;">{int(row_eval['FP'])} (FP)</td>
                <td style="background:#eafbe7;padding:10px;border:1px solid #ddd;">{int(row_eval['TN'])} (TN)</td>
            </tr>
        </table>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-bottom:15px;"></div>', unsafe_allow_html=True)
