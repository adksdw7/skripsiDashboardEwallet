# Library
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import os
import base64


# Konfigurasi halaman
st.set_page_config(
    page_title="Komparasi Sentimen E-Wallet",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style dashboard
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

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"],
    p, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* Jangan timpa font ikon bawaan Streamlit. Jika font ikon berubah,
       nama ikon seperti keyboard_double_arrow_right tampil sebagai teks. */
    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }


    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(35, 119, 202, 0.16) 0%, transparent 42%),
            radial-gradient(circle at 92% 18%, rgba(1, 174, 214, 0.14) 0%, transparent 42%),
            radial-gradient(circle at 50% 100%, rgba(255, 119, 60, 0.13) 0%, transparent 48%),
            #fafbfc;
        background-attachment: fixed;
    }


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


# Responsive dashboard
st.markdown("""
<style>
    .block-container {
        width: 100%;
        max-width: 1500px;
        padding-left: clamp(0.75rem, 2vw, 2.5rem);
        padding-right: clamp(0.75rem, 2vw, 2.5rem);
    }

    [data-testid="stHorizontalBlock"] {
        gap: clamp(0.5rem, 1vw, 1rem) !important;
    }

    [data-testid="column"],
    [data-testid="stColumn"] {
        min-width: 0 !important;
    }

    .metric-card {
        padding: clamp(10px, 1.2vw, 20px) !important;
    }

    .metric-card h2,
    .metric-card h3 {
        font-size: clamp(17px, 1.8vw, 30px) !important;
    }

    .metric-card p {
        font-size: clamp(10px, 0.9vw, 14px) !important;
    }

    [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow: visible !important;
    }

    [data-testid="stPlotlyChart"] > div,
    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .plot-container {
        width: 100% !important;
        max-width: 100% !important;
    }

    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        width: 100% !important;
    }

    [data-testid="stImage"] img {
        width: min(100%, 460px) !important;
        max-width: 100% !important;
        height: auto !important;
        object-fit: contain !important;
    }

    @media (max-width: 1100px) {
        [data-testid="stImage"] img {
            width: min(100%, 380px) !important;
        }
    }

    @media (max-width: 900px) {
        .block-container {
            padding-left: 0.65rem;
            padding-right: 0.65rem;
        }

        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="column"],
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100% !important;
            width: 100% !important;
            min-width: 100% !important;
        }

        [data-testid="stImage"] img {
            width: min(100%, 320px) !important;
        }

        .metric-card {
            padding: 10px !important;
        }

        h1 {
            font-size: clamp(24px, 6vw, 36px) !important;
        }

        h2 {
            font-size: clamp(20px, 5vw, 30px) !important;
        }

        h3 {
            font-size: clamp(17px, 4vw, 24px) !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# Load data
@st.cache_data
def load_data():

    df_sentimen = pd.read_csv("hasilSentimen.csv")
    df_evaluasi = pd.read_csv("hasilEvaluasi.csv")

    df_sentimen.columns = df_sentimen.columns.str.strip()
    df_sentimen["appName"] = df_sentimen["appName"].astype(str).str.strip()
    df_sentimen["sentimen"] = df_sentimen["predictLabel"].astype(str).str.strip().str.capitalize()


    df_raw_dana = pd.read_csv("rawDana.csv")
    df_raw_gopay = pd.read_csv("rawGopay.csv")
    df_raw_shopee = pd.read_csv("rawShopeepay.csv")


    df_evaluasi.columns = df_evaluasi.columns.str.strip()

    df_evaluasi = df_evaluasi.rename(columns={
        "appName": "aplikasi",
        "dataTrain": "jumlahDataTrain",
        "dataTest": "jumlahDataTest"
    })


    df_sentimen['date'] = pd.to_datetime(df_sentimen['date'])

    return df_sentimen, df_evaluasi, df_raw_dana, df_raw_gopay, df_raw_shopee


try:
    df_sentimen, df_evaluasi, df_raw_dana, df_raw_gopay, df_raw_shopee = load_data()
except Exception as e:
    st.error(f"Gagal memuat data CSV. Pastikan file berada di repositori yang sama. Error: {e}")
    st.stop()


# Warna aplikasi
APP_COLOR_MAP = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True
}


# Warna transparan
def rgba(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    return f"rgba({r}, {g}, {b}, {alpha})"


# Judul bagian
def judul_bagian(teks, anchor):
    st.markdown(
        f"""
        <div id="{anchor}" class="section-anchor"></div>
        <h1 style="text-align:center; width:100%; margin-bottom:20px;">
            {teks}
        </h1>
        """,
        unsafe_allow_html=True
    )


# Logo aplikasi
def get_img_html(file_path, alt_text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data}" style="width: 100%; max-width: 80px; height: auto; object-fit: contain;">'
    return f'<p style="color: gray; font-size: 14px; text-align: center;">{alt_text}</p>'


# Ulasan pengguna
def get_top_reviews(app_name, sentiment):
    raw = {
        "DANA": df_raw_dana,
        "GoPay": df_raw_gopay,
        "ShopeePay": df_raw_shopee
    }[app_name]

    label = sentiment.lower()

    hasil = df_sentimen[
        (df_sentimen["appName"] == app_name) &
        (df_sentimen["actualLabel"].str.lower() == label) &
        (df_sentimen["predictLabel"].str.lower() == label)
    ][["reviewId", "score"]]

    hasil = hasil.merge(
        raw[["reviewId", "content"]],
        on="reviewId",
        how="inner"
    )

    hasil["content"] = hasil["content"].astype(str).str.strip()
    hasil = hasil[hasil["content"].str.split().str.len() >= 3]
    hasil = hasil.drop_duplicates("content")

    if hasil.empty:
        return []

    hasil = hasil.sample(
        n=min(10, len(hasil)),
        random_state=42
    )

    return [
        f"{row.content} — Rating {int(row.score)}"
        for row in hasil.itertuples()
    ]


# Warna word cloud negatif
def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "#cc0000"



# Sidebar navigasi
st.markdown("""
<style>
    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: #fff1ea !important;
        border-bottom: 1px solid rgba(255, 119, 60, 0.16) !important;
    }

    /* Tombol buka/tutup sidebar */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {
        background: transparent !important;
    }

    /* Sembunyikan ikon Material khusus tombol sidebar. */
    [data-testid="stSidebarCollapsedControl"] [data-testid="stIconMaterial"],
    [data-testid="collapsedControl"] [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"] [data-testid="stIconMaterial"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Hilangkan teks/nama ikon yang mungkin tersisa pada child tombol. */
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"] {
        min-width: 42px !important;
        min-height: 42px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: transparent !important;
        font-size: 0 !important;
        position: relative !important;
        overflow: hidden !important;
    }

    [data-testid="stSidebarCollapsedControl"] button > *,
    [data-testid="collapsedControl"] button > *,
    [data-testid="stSidebarCollapseButton"] button > *,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"] > * {
        font-size: 0 !important;
        color: transparent !important;
        text-indent: -9999px !important;
        overflow: hidden !important;
        max-width: 0 !important;
    }

    /* Simbol pengganti tanpa gambar tambahan. */
    [data-testid="stSidebarCollapsedControl"] button::before,
    [data-testid="collapsedControl"] button::before,
    [data-testid="stSidebarCollapseButton"] button::before,
    [data-testid="stSidebar"] button[aria-label="Collapse sidebar"]::before {
        content: ":::" !important;
        display: block !important;
        color: #555555 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        line-height: 1 !important;
        text-indent: 0 !important;
    }

    /* Fallback jika versi Streamlit menaruh kontrol tanpa elemen button. */
    [data-testid="stSidebarCollapsedControl"]:not(:has(button)),
    [data-testid="collapsedControl"]:not(:has(button)),
    [data-testid="stSidebarCollapseButton"]:not(:has(button)) {
        color: transparent !important;
        font-size: 0 !important;
        position: relative !important;
    }

    [data-testid="stSidebarCollapsedControl"]:not(:has(button))::before,
    [data-testid="collapsedControl"]:not(:has(button))::before,
    [data-testid="stSidebarCollapseButton"]:not(:has(button))::before {
        content: ":::" !important;
        color: #555555 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        line-height: 1 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff !important;
    }

    [data-testid="stSidebarContent"] {
        background-color: #ffffff !important;
    }

    .sidebar-nav-wrap {
        position: sticky;
        top: 0;
        background: #ffffff;
        z-index: 10;
        padding-top: 0.25rem;
    }

    .sidebar-nav-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 14px;
        padding: 2px 2px 10px 2px;
        border-bottom: 1px solid #e5e7eb;
    }

    .sidebar-nav-title strong {
        color: #111111;
        font-size: 18px;
    }

    .sidebar-nav-dots {
        color: #666666;
        font-size: 24px;
        line-height: 1;
    }

    .sidebar-nav-link {
        display: block;
        padding: 10px 12px;
        margin: 4px 0;
        border-radius: 9px;
        color: #222222 !important;
        text-decoration: none !important;
        font-size: 14px;
        font-weight: 500;
        line-height: 1.35;
        transition: background-color 0.15s ease;
    }

    .sidebar-nav-link:hover {
        background-color: #f3f4f6;
        color: #111111 !important;
    }

    .section-anchor {
        scroll-margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

NAV_ITEMS = [
    ("Pilih E-Wallet", "pilih-e-wallet"),
    ("Hasil Analisis", "hasil-analisis"),
    ("Proporsi Distribusi Sentimen Pengguna", "proporsi-sentimen"),
    ("Grafik Tren Perkembangan Sentimen Bulanan", "tren-sentimen"),
    ("Penyebaran Distribusi Rating Bintang Pengguna", "distribusi-rating"),
    ("Word Cloud Sentimen", "word-cloud"),
    ("Nilai Metrik Kinerja Klasifikasi NBC", "evaluasi-model")
]

with st.sidebar:
    nav_links = "".join(
        f'<a class="sidebar-nav-link" href="#{anchor}" target="_self">{label}</a>'
        for label, anchor in NAV_ITEMS
    )

    st.markdown(
        f"""
        <div class="sidebar-nav-wrap">
            <div class="sidebar-nav-title">
                <strong>Navigasi</strong>
                <span class="sidebar-nav-dots">⋮</span>
            </div>
            {nav_links}
        </div>
        """,
        unsafe_allow_html=True
    )

# Judul
st.title("📊 KOMPARATIF SENTIMEN E-WALLET DANA, GOPAY & SHOPEEPAY")
with st.container(key="info_kegunaan"):
    st.info("""**Kegunaan Dashboard Web**: Membandingkan sentimen pengguna terhadap E-Wallet DANA, GoPay, dan ShopeePay berdasarkan ulasan Google Play Store.""")


st.markdown("---")

# Informasi aplikasi
LANDING_CARD_COLOR = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


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


APP_PLAYSTORE_URL = {
    "DANA": "https://play.google.com/store/apps/details?id=id.dana&hl=id",
    "GoPay": "https://play.google.com/store/apps/details?id=com.gojek.gopay&hl=id",
    "ShopeePay": "https://play.google.com/store/apps/details?id=com.shopeepay.id&hl=id"
}


APP_WEBSITE_URL = {
    "DANA": "https://www.dana.id/",
    "GoPay": "https://gopay.co.id/",
    "ShopeePay": "https://shopeepay.co.id/"
}


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
        flex: 0 1 100px;
        width: clamp(48px, 10vw, 100px);
        aspect-ratio: 1 / 1;
        border-radius: 16px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .landing-logo-wrap img {
        width: 100%;
        max-width: 100%;
        height: auto;
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

    @media (max-width: 600px) {
        .landing-card {
            padding: 18px;
            gap: 14px;
        }
        .landing-logo-wrap {
            width: clamp(48px, 18vw, 75px);
            flex-basis: clamp(48px, 18vw, 75px);
        }
        .landing-text-wrap h2 {
            font-size: 22px;
        }
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


st.markdown("---")
judul_bagian("Pilih E-Wallet", "pilih-e-wallet")

# Pilih E-Wallet
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


if not selected_apps:
    st.warning("⚠️ Silakan pilih minimal satu aplikasi E-Wallet")
    st.stop()


st.markdown("---")
judul_bagian("Hasil Analisis", "hasil-analisis")
with st.container(key="info_periode"):
    st.info("Data yang disajikan merupakan ulasan pengguna selama periode 1 Juni 2025 hingga 31 Mei 2026")


# Total data ulasan
st.markdown("### 📥 Total Data Ulasan")

col_u = st.columns(len(selected_apps))
for idx, app_name in enumerate(selected_apps):
    with col_u[idx]:
        app_total = len(df_sentimen[df_sentimen['appName'] == app_name])
        st.markdown(
            f'<div class="metric-card"><h2 style="margin:0;color:{APP_COLOR_MAP[app_name]};">{app_total:,}</h2><p style="margin:5px 0 0 0;color:gray;font-size:14px;">Total Ulasan {app_name}</p></div>',
            unsafe_allow_html=True
        )


st.markdown("---")
# Diagram donat
judul_bagian("Proporsi Distribusi Sentimen Pengguna", "proporsi-sentimen")

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
            fig_pie.update_layout(
                autosize=True,
                height=280,
                margin=dict(t=55, b=70, l=20, r=20),
                font=dict(size=12),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True, config=PLOTLY_CONFIG)


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
                        <h2 style="margin:0; color:{color_code}; font-size: clamp(18px, 2.2vw, 30px); font-weight: bold;">{neg_pct:.1f}%</h2>
                        <p style="margin:2px 0 0 0; color: gray; font-size: 13px;">Sentimen Negatif</p>
                    </div>
                    ''', unsafe_allow_html=True)
                with col_pos:
                    st.markdown(f'''
                    <div style="text-align:center;">
                        <h2 style="margin:0; color:{color_code}; font-size: clamp(18px, 2.2vw, 30px); font-weight: bold;">{pos_pct:.1f}%</h2>
                        <p style="margin:2px 0 0 0; color: gray; font-size: 13px;">Sentimen Positif</p>
                    </div>
                    ''', unsafe_allow_html=True)


st.markdown("---")
# Tren sentimen
judul_bagian("Grafik Tren Perkembangan Sentimen Bulanan", "tren-sentimen")

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
        autosize=True,
        height=300,
        font=dict(size=12),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="Periode Bulan",
        yaxis_title="Jumlah Ulasan",
        margin=dict(t=55, b=85, l=55, r=25)
    )
    fig_trend_pos.update_xaxes(title_standoff=25)
    st.plotly_chart(fig_trend_pos, use_container_width=True, config=PLOTLY_CONFIG)

with st.container(border=True):
    df_neg_trend = df_chart_trend_global[df_chart_trend_global['sentimen'] == 'Negatif']
    fig_trend_neg = px.line(
        df_neg_trend, x='Bulan', y='Jumlah', color='appName', markers=True,
        title="📉 Tren Perkembangan Sentimen Negatif Bulanan",
        color_discrete_map=APP_COLOR_MAP
    )
    fig_trend_neg.update_layout(
        autosize=True,
        height=300,
        font=dict(size=12),
        legend_title_text="",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="Periode Bulan",
        yaxis_title="Jumlah Ulasan",
        margin=dict(t=55, b=85, l=55, r=25)
    )
    fig_trend_neg.update_xaxes(title_standoff=25)
    st.plotly_chart(fig_trend_neg, use_container_width=True, config=PLOTLY_CONFIG)


st.markdown("---")
# Distribusi rating
judul_bagian("Penyebaran Distribusi Rating Bintang Pengguna", "distribusi-rating")

# Ukuran responsif diagram rating
st.markdown("""
<style>
    .st-key-rating_chart {
        width: min(80vw, 760px);
        margin-left: auto;
        margin-right: auto;
    }

    .st-key-rating_chart [data-testid="stPlotlyChart"] {
        width: 100% !important;
        aspect-ratio: 1 / 1;
    }

    .st-key-rating_chart [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        height: 100% !important;
    }

    .st-key-rating_chart .js-plotly-plot,
    .st-key-rating_chart .plot-container,
    .st-key-rating_chart .svg-container {
        width: 100% !important;
        height: 100% !important;
    }

    @media (max-width: 700px) {
        .st-key-rating_chart {
            width: 90vw;
        }
    }
</style>
""", unsafe_allow_html=True)

with st.container(key="rating_chart"):
    if len(selected_apps) == 1:
        app_name = selected_apps[0]
        df_app_rate = df_sentimen[df_sentimen["appName"] == app_name]
        df_chart_rate = (
            df_app_rate
            .groupby("score")
            .size()
            .reset_index(name="Total")
        )

        fig_rate = px.bar(
            df_chart_rate,
            x="score",
            y="Total",
            title=f"Distribusi Rating Bintang: {app_name}",
            labels={
                "score": "Rating Bintang",
                "Total": "Jumlah Ulasan"
            },
            color_discrete_sequence=[APP_COLOR_MAP[app_name]]
        )

        fig_rate.update_layout(
            autosize=True,
            height=600,
            font=dict(size=12),
            margin=dict(t=60, b=70, l=65, r=30),
            xaxis=dict(dtick=1)
        )

        st.plotly_chart(
            fig_rate,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    else:
        df_rating_group = df_sentimen[
            df_sentimen["appName"].isin(selected_apps)
        ]
        df_rating_group = (
            df_rating_group
            .groupby(["score", "appName"])
            .size()
            .reset_index(name="Total")
        )

        fig_rate_group = px.bar(
            df_rating_group,
            x="score",
            y="Total",
            color="appName",
            barmode="group",
            title="Komparasi Distribusi Rating Bintang E-Wallet",
            labels={
                "score": "Rating Bintang",
                "Total": "Jumlah Ulasan",
                "appName": "Aplikasi"
            },
            color_discrete_map=APP_COLOR_MAP
        )

        fig_rate_group.update_layout(
            autosize=True,
            height=600,
            font=dict(size=12),
            legend_title_text="",
            bargap=0.03,
            bargroupgap=0,
            xaxis=dict(dtick=1),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=60, b=90, l=65, r=30)
        )

        fig_rate_group.update_xaxes(title_standoff=20)

        st.plotly_chart(
            fig_rate_group,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )


st.markdown("---")
# Word cloud
judul_bagian("Word Cloud Sentimen", "word-cloud")

wc_positive_color = {"DANA": "Blues", "GoPay": "Greens", "ShopeePay": "Oranges"}

# Posisi word cloud menyesuaikan jumlah aplikasi yang dipilih
if len(selected_apps) == 1:
    _, col_wc_center, _ = st.columns([1, 1, 1])
    col_wc = [col_wc_center]
elif len(selected_apps) == 2:
    _, col_wc_1, col_wc_2, _ = st.columns([0.5, 1, 1, 0.5])
    col_wc = [col_wc_1, col_wc_2]
else:
    col_wc = st.columns(3)

for idx, app_name in enumerate(selected_apps):
    with col_wc[idx]:
        with st.container(border=True):
            df_app_text = df_sentimen[df_sentimen['appName'] == app_name]

            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>Word Cloud Positif {app_name}</p>", unsafe_allow_html=True)

            text_positive = " ".join(df_app_text[df_app_text['sentimen'] == "Positif"]['content'].astype(str))
            if text_positive.strip():
                wc_positive = WordCloud(
                    background_color="white", max_words=50,
                    colormap=wc_positive_color[app_name], width=360, height=225
                ).generate(text_positive)

                fig, ax = plt.subplots(figsize=(3.6, 2.25))
                ax.imshow(wc_positive, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, use_container_width=True)
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

            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-top:15px; margin-bottom:5px;'>Word Cloud Negatif {app_name}</p>", unsafe_allow_html=True)

            text_negative = " ".join(df_app_text[df_app_text['sentimen'] == "Negatif"]['content'].astype(str))
            if text_negative.strip():
                wc_negative = WordCloud(
                    background_color="white", max_words=50, width=360, height=225
                ).generate(text_negative)
                wc_negative.recolor(color_func=red_color_func)

                fig, ax = plt.subplots(figsize=(3.6, 2.25))
                ax.imshow(wc_negative, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, use_container_width=True)
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


st.markdown("---")
# Evaluasi model
judul_bagian("Nilai Metrik Kinerja Klasifikasi NBC", "evaluasi-model")

# Ukuran responsif confusion matrix
st.markdown("""
<style>
    .st-key-confusion_matrix_dana,
    .st-key-confusion_matrix_gopay,
    .st-key-confusion_matrix_shopeepay {
        width: min(80vw, 650px);
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
    }

    .st-key-confusion_matrix_dana [data-testid="stPlotlyChart"],
    .st-key-confusion_matrix_gopay [data-testid="stPlotlyChart"],
    .st-key-confusion_matrix_shopeepay [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
        aspect-ratio: 1 / 1 !important;
    }

    .st-key-confusion_matrix_dana [data-testid="stPlotlyChart"] > div,
    .st-key-confusion_matrix_gopay [data-testid="stPlotlyChart"] > div,
    .st-key-confusion_matrix_shopeepay [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        height: 100% !important;
    }

    .st-key-confusion_matrix_dana .js-plotly-plot,
    .st-key-confusion_matrix_dana .plot-container,
    .st-key-confusion_matrix_dana .svg-container,
    .st-key-confusion_matrix_gopay .js-plotly-plot,
    .st-key-confusion_matrix_gopay .plot-container,
    .st-key-confusion_matrix_gopay .svg-container,
    .st-key-confusion_matrix_shopeepay .js-plotly-plot,
    .st-key-confusion_matrix_shopeepay .plot-container,
    .st-key-confusion_matrix_shopeepay .svg-container {
        width: 100% !important;
        height: 100% !important;
        max-width: 100% !important;
    }

    @media (max-width: 700px) {
        .st-key-confusion_matrix_dana,
        .st-key-confusion_matrix_gopay,
        .st-key-confusion_matrix_shopeepay {
            width: 90vw;
        }
    }
</style>
""", unsafe_allow_html=True)

for app_name in selected_apps:
    row_eval = df_evaluasi[df_evaluasi["aplikasi"] == app_name]

    if row_eval.empty:
        continue

    row_eval = row_eval.iloc[0]
    app_color = APP_COLOR_MAP[app_name]

    tp = int(row_eval["TP"])
    fn = int(row_eval["FN"])
    fp = int(row_eval["FP"])
    tn = int(row_eval["TN"])

    st.markdown(
        f"""
        <div style="width:100%; text-align:center; margin:0 auto 10px auto;">
            <strong>Confusion Matrix: {app_name}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig_cm = go.Figure(
        go.Heatmap(
            z=[
                [1, 0],
                [0, 1]
            ],
            x=[
                "Prediksi Positif",
                "Prediksi Negatif"
            ],
            y=[
                "Aktual Positif",
                "Aktual Negatif"
            ],
            text=[
                [f"{tp} (TP)", f"{fn} (FN)"],
                [f"{fp} (FP)", f"{tn} (TN)"]
            ],
            customdata=[
                [
                    [tp, "True Positive"],
                    [fn, "False Negative"]
                ],
                [
                    [fp, "False Positive"],
                    [tn, "True Negative"]
                ]
            ],
            texttemplate="<b>%{text}</b>",
            textfont=dict(
                size=15,
                color="#111111"
            ),
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "%{y}<br>"
                "%{x}<br>"
                "Jumlah: %{customdata[0]}"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=app_color,
                font=dict(
                    color="#111111",
                    size=12
                )
            ),
            colorscale=[
                [0, rgba(app_color, 0.12)],
                [0.49, rgba(app_color, 0.12)],
                [0.50, rgba(app_color, 0.48)],
                [1, rgba(app_color, 0.48)]
            ],
            zmin=0,
            zmax=1,
            showscale=False,
            xgap=4,
            ygap=4
        )
    )

    fig_cm.update_layout(
        autosize=True,
        height=600,
        margin=dict(l=70, r=40, t=70, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#111111",
            size=12
        ),
        xaxis=dict(
            side="top",
            fixedrange=True,
            tickfont=dict(
                color="#111111",
                size=12
            )
        ),
        yaxis=dict(
            autorange="reversed",
            fixedrange=True,
            tickfont=dict(
                color="#111111",
                size=12
            )
        )
    )

    with st.container(key=f"confusion_matrix_{app_name.lower()}"):
        st.plotly_chart(
            fig_cm,
            use_container_width=True,
            config={
                **PLOTLY_CONFIG,
                "modeBarButtonsToRemove": [
                    "lasso2d",
                    "select2d"
                ]
            }
        )

    st.markdown(
        """
        <div style="
            width:100%;
            text-align:center;
            margin:-10px auto 18px auto;
            padding:0 12px;
            box-sizing:border-box;
        ">
            <p style="
                color:#111111;
                font-size:clamp(11px, 1vw, 14px);
                margin:0;
            ">
                Warna lebih pekat menunjukkan klasifikasi benar (TP dan TN),
                sedangkan warna lebih muda menunjukkan kesalahan klasifikasi
                (FP dan FN).
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="width:100%; text-align:center; margin:0 auto 12px auto;">
            <strong>Metrik Performa Pengujian Model NBC: {app_name}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    metric_labels = [
        ("Accuracy", col_m1),
        ("Precision", col_m2),
        ("Recall", col_m3),
        ("F1-Score", col_m4)
    ]

    for label, col in metric_labels:
        nilai = float(row_eval[label]) * 100

        col.markdown(
            f"""
            <div class="metric-card">
                <p style="margin:0;color:#111111;font-size:14px;">
                    {label}
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {nilai:.2f}%
                </h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="margin-bottom:25px;"></div>',
        unsafe_allow_html=True
    )
