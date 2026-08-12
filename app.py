# ============================================================
# DASHBOARD KLASIFIKASI SENTIMEN E-WALLET
# Multinomial Naive Bayes (NBC) vs Support Vector Machine (SVM)
# ============================================================

import os
import base64
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud

# ------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Klasifikasi Sentimen E-Wallet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",  # Sidebar dimulai dalam keadaan tertutup
)

# ------------------------------------------------------------
# 2. KONSTANTA WARNA & KONFIGURASI
# ------------------------------------------------------------
BG = "#FFF2DB"
BOX_BG = "#FFFAF3"
BORDER = "#9D6638"
TEXT = "#9D6638"
NBC = "#A3485A"
NBC_NEG = "#662222"
SVM = "#4B5694"
SVM_NEG = "#111844"

APP_ORDER = ["DANA", "GoPay", "ShopeePay"]
METRIC_ORDER = ["Accuracy", "Precision", "Recall", "Specificity", "F1-Score"]

MODEL_COLOR = {"NBC": NBC, "SVM": SVM}
MODEL_SENTIMENT_COLOR = {
    "NBC": {"Positif": NBC, "Negatif": NBC_NEG},
    "SVM": {"Positif": SVM, "Negatif": SVM_NEG},
}

APP_LOGO_CANDIDATES = {
    "DANA": ["logoDana.png"],
    "GoPay": ["logoGopay.png", "logoGoPay.png"],
    "ShopeePay": ["logoShopeepay.png", "logoShopeePay.png"],
}

APP_WEBSITE_URL = {
    "DANA": "https://www.dana.id/",
    "GoPay": "https://gopay.co.id/",
    "ShopeePay": "https://shopeepay.co.id/",
}

APP_PLAYSTORE_URL = {
    "DANA": "https://play.google.com/store/apps/details?id=id.dana&hl=id",
    "GoPay": "https://play.google.com/store/apps/details?id=com.gojek.gopay&hl=id",
    "ShopeePay": "https://play.google.com/store/apps/details?id=com.shopeepay.id&hl=id",
}

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "scrollZoom": True,
}

# ------------------------------------------------------------
# 3. STYLE DASHBOARD
# ------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"],
    p, div, span, label, h1, h2, h3, h4, h5, h6, button, input, textarea {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {TEXT};
    }}

    .stApp, [data-testid="stAppViewContainer"] {{
        background: {BG} !important;
    }}

    [data-testid="stHeader"] {{
        background: rgba(255, 242, 219, 0.96) !important;
    }}

    .block-container {{
        max-width: 1560px;
        padding-top: 1.0rem;
        padding-left: clamp(0.8rem, 2vw, 2.2rem);
        padding-right: clamp(0.8rem, 2vw, 2.2rem);
        padding-bottom: 3rem;
    }}

    [data-testid="stSidebar"] {{
        background: {BOX_BG} !important;
        border-right: 1.5px solid {BORDER};
    }}

    [data-testid="stSidebarContent"] {{
        background: {BOX_BG} !important;
    }}

    hr {{
        border: 0;
        height: 1px;
        background: rgba(157,102,56,.45);
        margin: 1.6rem 0;
    }}

    /* Panel bawaan Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {BOX_BG} !important;
        border: 1.35px solid {BORDER} !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 14px rgba(157, 102, 56, .08) !important;
    }}

    [data-testid="stPlotlyChart"] {{
        width: 100% !important;
    }}

    /* Toggle */
    [role="switch"][aria-checked="true"] {{
        background-color: {BORDER} !important;
        border-color: {BORDER} !important;
    }}
    [role="switch"][aria-checked="false"] {{
        background-color: #EEDDC7 !important;
        border-color: {BORDER} !important;
    }}

    /* Header */
    .hero {{
        background: {BOX_BG};
        border: 1.6px solid {BORDER};
        border-radius: 18px;
        padding: clamp(18px, 2.6vw, 34px);
        margin: 0 0 18px 0;
        box-shadow: 0 5px 18px rgba(157, 102, 56, .08);
    }}

    .hero h1 {{
        margin: 0;
        color: {TEXT};
        font-weight: 800;
        font-size: clamp(31px, 4vw, 56px);
        line-height: 1.08;
        letter-spacing: -0.035em;
    }}

    .hero p {{
        margin: 10px 0 0 0;
        font-size: clamp(12px, 1.15vw, 16px);
        color: {TEXT};
        line-height: 1.5;
    }}

    .section-title {{
        color: {TEXT};
        margin: 0 0 12px 0;
        font-size: clamp(22px, 2.4vw, 34px);
        font-weight: 800;
        line-height: 1.1;
    }}

    .app-title {{
        color: {TEXT};
        margin: 0;
        font-size: clamp(30px, 3.8vw, 50px);
        line-height: 1.0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}

    .app-divider {{
        height: 2px;
        background: {BORDER};
        opacity: .45;
        margin: 12px 0 18px 0;
    }}

    .panel-title {{
        text-align: center;
        font-weight: 700;
        font-size: clamp(12px, 1.0vw, 16px);
        margin: 2px 0 7px 0;
        color: {TEXT};
    }}

    .model-nbc {{ color: {NBC} !important; }}
    .model-svm {{ color: {SVM} !important; }}

    /* Selector aplikasi */
    .wallet-card {{
        background: {BOX_BG};
        border: 1.4px solid {BORDER};
        border-radius: 15px;
        padding: 14px;
        min-height: 176px;
        box-shadow: 0 4px 14px rgba(157,102,56,.07);
    }}

    .wallet-logo {{
        display: flex;
        height: 90px;
        align-items: center;
        justify-content: center;
        margin-bottom: 9px;
    }}

    .wallet-logo img {{
        width: 82px;
        height: 82px;
        object-fit: contain;
        border-radius: 10px;
    }}

    .wallet-links {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 7px;
    }}

    .wallet-link {{
        border: 1px solid {BORDER};
        border-radius: 8px;
        padding: 7px 6px;
        text-align: center;
        text-decoration: none !important;
        color: {TEXT} !important;
        background: {BG};
        font-size: 10px;
        font-weight: 700;
    }}

    /* KPI */
    .kpi-grid-3 {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 11px;
        margin-bottom: 14px;
    }}

    .kpi-card {{
        background: {BOX_BG};
        border: 1.3px solid {BORDER};
        border-radius: 12px;
        min-height: 84px;
        padding: 12px 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-sizing: border-box;
    }}

    .kpi-value {{
        margin: 0;
        font-size: clamp(19px, 2vw, 29px);
        font-weight: 800;
        line-height: 1.08;
    }}

    .kpi-label {{
        margin: 5px 0 0 0;
        font-size: clamp(8px, .85vw, 11px);
        line-height: 1.25;
    }}

    /* Sentiment summary */
    .sentiment-mini-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: -5px;
    }}

    .sentiment-mini {{
        border: 1px solid {BORDER};
        border-radius: 9px;
        padding: 8px 5px;
        text-align: center;
        background: {BG};
    }}

    .sentiment-mini b {{
        display: block;
        font-size: clamp(16px, 1.5vw, 23px);
        line-height: 1.1;
    }}

    .sentiment-mini small {{
        font-size: 9px;
    }}

    /* Agreement cards */
    .agreement-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 8px;
    }}

    .agreement-card {{
        border: 1px solid {BORDER};
        background: {BG};
        border-radius: 10px;
        padding: 10px 7px;
        text-align: center;
    }}

    .agreement-card .big {{
        font-size: clamp(18px, 1.7vw, 25px);
        font-weight: 800;
        margin: 0;
    }}

    .agreement-card .small {{
        font-size: 9px;
        margin-top: 3px;
    }}

    /* Confusion summary boxes */
    .cm-row-label {{
        font-size: 11px;
        font-weight: 800;
        margin: 6px 0 5px 0;
    }}

    .cm-summary-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 6px;
    }}

    .cm-box {{
        border: 1px solid currentColor;
        border-radius: 9px;
        padding: 9px 4px;
        text-align: center;
        background: {BG};
        min-width: 0;
    }}

    .cm-box b {{
        display: block;
        font-size: clamp(15px, 1.25vw, 21px);
        line-height: 1.05;
    }}

    .cm-box small {{
        font-size: 8px;
    }}

    .cm-note {{
        text-align: center;
        font-size: 9px;
        line-height: 1.35;
        margin-top: 10px;
        padding: 8px 9px;
        border-radius: 8px;
        background: {BG};
        border: 1px dashed {BORDER};
    }}

    /* Performance metric cards */
    .metric-row {{
        display: grid;
        grid-template-columns: repeat(5, minmax(0,1fr));
        gap: 6px;
        margin-bottom: 8px;
    }}

    .metric-box {{
        border: 1px solid currentColor;
        border-radius: 9px;
        background: {BG};
        padding: 9px 3px;
        text-align: center;
    }}

    .metric-box small {{ font-size: 8px; }}
    .metric-box b {{
        display: block;
        font-size: clamp(13px, 1.05vw, 18px);
        margin-top: 3px;
    }}

    /* Sidebar links */
    .nav-title {{
        font-size: 17px;
        font-weight: 800;
        margin: 4px 0 9px 0;
    }}

    .nav-link {{
        display: block;
        text-decoration: none !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER};
        background: {BG};
        border-radius: 9px;
        padding: 9px 10px;
        margin: 7px 0;
        font-size: 12px;
        font-weight: 700;
    }}

    .nav-link:hover {{
        background: #F4E1C2;
    }}

    .nav-hint {{
        font-size: 10px;
        line-height: 1.4;
        margin-top: 10px;
    }}

    /* dataframe */
    [data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    @media (max-width: 900px) {{
        .kpi-grid-3 {{ grid-template-columns: 1fr; }}
        .metric-row {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
        .cm-summary-grid {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
        .wallet-links {{ grid-template-columns: 1fr; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3B. FINAL VISUAL OVERRIDE
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --page-bg: #FFFAF3;
        --grad-start: #FFF2DB;
        --grad-mid: #FFF5E5;
        --grad-end: #FFFAF3;
        --text-main: #9D6638;
        --shadow-main: 0 8px 22px rgba(117, 78, 42, 0.14);
        --shadow-soft: 0 5px 14px rgba(117, 78, 42, 0.11);
    }

    /* =========================
       LATAR BELAKANG LUAR
       ========================= */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stHeader"] {
        background: #FFFAF3 !important;
    }

    [data-testid="stHeader"] {
        background: rgba(255,250,243,.96) !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background: #FFFAF3 !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* =========================
       SEMUA CONTAINER STREAMLIT
       ========================= */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
        overflow: hidden !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        outline: none !important;
    }

    /* =========================
       HEADER HORIZONTAL
       ========================= */
    .top-title-wrap {
        min-height: 120px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 4px 8px 4px 2px;
        box-sizing: border-box;
    }

    .top-title {
        margin: 0 !important;
        color: #9D6638 !important;
        font-size: clamp(25px, 2.35vw, 41px) !important;
        font-weight: 800 !important;
        line-height: 1.12 !important;
        letter-spacing: -0.025em !important;
    }

    .top-subtitle {
        margin: 7px 0 0 0;
        color: #9D6638 !important;
        font-size: clamp(8px, .72vw, 11px);
        line-height: 1.35;
    }

    .top-wallet-card {
        width: 100%;
        min-height: 96px;
        box-sizing: border-box;
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        border-radius: 12px !important;
        padding: 8px 6px 6px 6px;
        box-shadow: 0 5px 14px rgba(117,78,42,.11) !important;
    }

    .top-wallet-logo {
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 5px;
    }

    .top-wallet-logo img {
        width: 50px;
        height: 50px;
        object-fit: contain;
        border-radius: 6px;
    }

    .top-wallet-links {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 5px;
    }

    .top-wallet-link {
        display: block;
        min-width: 0;
        border: none !important;
        outline: none !important;
        border-radius: 7px;
        padding: 5px 3px;
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFFAF3 100%
        ) !important;
        box-shadow: 0 3px 8px rgba(117,78,42,.09) !important;
        color: #9D6638 !important;
        text-decoration: none !important;
        text-align: center;
        font-size: clamp(6px, .48vw, 8px);
        line-height: 1.15;
        font-weight: 600;
    }

    .top-wallet-link:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 12px rgba(117,78,42,.14) !important;
    }

    .st-key-top_header [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
        border-radius: 15px !important;
        padding: 10px 12px !important;
    }

    .st-key-top_header [data-testid="stHorizontalBlock"] {
        align-items: center !important;
    }

    .st-key-top_header [data-testid="stVerticalBlock"] {
        gap: .30rem !important;
    }

    .st-key-top_header [data-testid="stToggle"] {
        margin-top: -1px !important;
        margin-bottom: -6px !important;
    }

    .st-key-top_header [data-testid="stToggle"] label p {
        font-size: 9px !important;
        font-weight: 700 !important;
    }

    /* =========================
       SEMUA CUSTOM BOX
       ========================= */
    .hero,
    .wallet-card,
    .kpi-card,
    .sentiment-mini,
    .agreement-card,
    .cm-box,
    .cm-note,
    .metric-box,
    .nav-link {
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 5px 14px rgba(117,78,42,.11) !important;
    }

    .hero,
    .wallet-card,
    .kpi-card {
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
    }

    /* Link kecil dalam box */
    .wallet-link {
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 3px 8px rgba(117,78,42,.09) !important;
    }

    /* KPI */
    .kpi-card {
        border-radius: 12px !important;
    }

    /* Box sentiment */
    .sentiment-mini {
        border-radius: 9px !important;
    }

    /* Ringkasan prediksi */
    .agreement-card {
        border-radius: 10px !important;
    }

    /* TN TP FN FP */
    .cm-box {
        border-radius: 9px !important;
    }

    .cm-note {
        border-radius: 8px !important;
    }

    /* Accuracy / Precision / Recall / Specificity / F1 */
    .metric-box {
        border-radius: 9px !important;
    }

    /* Sidebar */
    .nav-link {
        border-radius: 9px !important;
        margin: 8px 0 !important;
    }

    .nav-link:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
    }

    /* Selectbox */
    [data-baseweb="select"] > div {
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFFAF3 100%
        ) !important;
        border: none !important;
        outline: none !important;
        box-shadow: 0 5px 14px rgba(117,78,42,.11) !important;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: none !important;
        outline: none !important;
        border-radius: 10px !important;
        box-shadow: 0 5px 14px rgba(117,78,42,.11) !important;
        overflow: hidden !important;
    }

    /* Plotly transparan agar gradient parent tetap terlihat */
    [data-testid="stPlotlyChart"] {
        background: transparent !important;
    }

    /* Toggle */
    [role="switch"][aria-checked="true"] {
        background-color: #9D6638 !important;
        border-color: transparent !important;
    }

    [role="switch"][aria-checked="false"] {
        background-color: #EEDDC7 !important;
        border-color: transparent !important;
    }

    /* Tidak ada border dekoratif lama */
    .app-divider {
        height: 1px !important;
        background: linear-gradient(
            90deg,
            rgba(157,102,56,.24),
            rgba(157,102,56,.05),
            rgba(157,102,56,0)
        ) !important;
        opacity: 1 !important;
    }

    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(
            90deg,
            rgba(157,102,56,0),
            rgba(157,102,56,.18),
            rgba(157,102,56,0)
        ) !important;
    }

    @media (max-width: 900px) {
        .top-title-wrap {
            min-height: auto;
            padding-bottom: 10px;
        }

        .top-title {
            font-size: clamp(25px, 7vw, 36px) !important;
        }

        .top-wallet-card {
            min-height: 102px;
        }

        .top-wallet-link {
            font-size: 8px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# ------------------------------------------------------------
# 3C. HEADER APP CARD FIX
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Tinggi judul kiri disamakan dengan kartu aplikasi kanan */
    .top-title-wrap {
        min-height: 158px !important;
        height: 158px !important;
        justify-content: center !important;
        padding: 6px 10px 6px 2px !important;
    }

    /* Outer header tetap rapi */
    .st-key-top_header [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }

    /* Kolom aplikasi dibuat setinggi judul kiri */
    .st-key-top_header [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
    }

    /* Container DANA / GoPay / ShopeePay = kartu sebenarnya */
    .st-key-header_card_dana,
    .st-key-header_card_gopay,
    .st-key-header_card_shopeepay {
        height: 100% !important;
    }

    .st-key-header_card_dana [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-header_card_gopay [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-header_card_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 158px !important;
        height: 158px !important;
        padding: 10px 10px 8px 10px !important;
        box-sizing: border-box !important;

        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        ) !important;

        border: none !important;
        outline: none !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
        overflow: visible !important;
    }

    .st-key-header_card_dana [data-testid="stVerticalBlock"],
    .st-key-header_card_gopay [data-testid="stVerticalBlock"],
    .st-key-header_card_shopeepay [data-testid="stVerticalBlock"] {
        height: 100% !important;
        gap: .28rem !important;
        justify-content: space-between !important;
    }

    /* Hilangkan box kedua pada HTML top-wallet-card.
       Box utamanya sekarang adalah container Streamlit di atas. */
    .top-wallet-card {
        min-height: auto !important;
        height: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }

    .top-wallet-logo {
        height: 65px !important;
        margin: 0 0 4px 0 !important;
    }

    .top-wallet-logo img {
        width: 62px !important;
        height: 62px !important;
        object-fit: contain !important;
    }

    .top-wallet-links {
        grid-template-columns: 1fr 1fr !important;
        gap: 7px !important;
        margin: 0 !important;
    }

    .top-wallet-link {
        min-height: 27px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 5px 4px !important;
        font-size: 7px !important;
        line-height: 1.15 !important;
    }

    /* Toggle sekarang benar-benar berada DI DALAM kartu */
    .st-key-header_card_dana [data-testid="stToggle"],
    .st-key-header_card_gopay [data-testid="stToggle"],
    .st-key-header_card_shopeepay [data-testid="stToggle"] {
        margin: 2px 0 0 0 !important;
        padding: 0 !important;
    }

    .st-key-header_card_dana [data-testid="stToggle"] label,
    .st-key-header_card_gopay [data-testid="stToggle"] label,
    .st-key-header_card_shopeepay [data-testid="stToggle"] label {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 25px !important;
    }

    .st-key-header_card_dana [data-testid="stToggle"] label p,
    .st-key-header_card_gopay [data-testid="stToggle"] label p,
    .st-key-header_card_shopeepay [data-testid="stToggle"] label p {
        font-size: 10px !important;
        font-weight: 600 !important;
        color: #9D6638 !important;
    }

    /* Supaya outer header tidak memotong shadow kartu */
    .st-key-top_header [data-testid="stVerticalBlockBorderWrapper"] {
        overflow: visible !important;
    }

    @media (max-width: 900px) {
        .top-title-wrap {
            min-height: auto !important;
            height: auto !important;
        }

        .st-key-header_card_dana [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-header_card_gopay [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-header_card_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 158px !important;
            height: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3D. PANEL SPACING & ALIGNMENT FIX
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Padding umum panel agar isi tidak mepet */
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 14px 16px !important;
        box-sizing: border-box !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        gap: .55rem !important;
    }

    /* Header tetap sedikit lebih rapat */
    .st-key-top_header [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 12px 14px !important;
    }

    /* Lebarkan kartu filter aplikasi */
    .top-title-wrap {
        min-height: 176px !important;
        height: 176px !important;
        padding: 8px 10px 8px 4px !important;
    }

    .st-key-header_card_dana [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-header_card_gopay [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-header_card_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 176px !important;
        height: 176px !important;
        padding: 12px 12px 10px 12px !important;
    }

    .top-wallet-card {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        gap: 10px !important;
    }

    .top-wallet-logo {
        height: 68px !important;
        margin-bottom: 2px !important;
    }

    .top-wallet-logo img {
        width: 64px !important;
        height: 64px !important;
    }

    .top-wallet-links {
        gap: 8px !important;
        margin-top: 2px !important;
    }

    .top-wallet-link {
        min-height: 30px !important;
        padding: 6px 5px !important;
        font-size: 7px !important;
    }

    .st-key-header_card_dana [data-testid="stToggle"],
    .st-key-header_card_gopay [data-testid="stToggle"],
    .st-key-header_card_shopeepay [data-testid="stToggle"] {
        margin-top: 6px !important;
    }

    .st-key-header_card_dana [data-testid="stToggle"] label,
    .st-key-header_card_gopay [data-testid="stToggle"] label,
    .st-key-header_card_shopeepay [data-testid="stToggle"] label {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 8px !important;
    }

    .st-key-header_card_dana [data-testid="stToggle"] label p,
    .st-key-header_card_gopay [data-testid="stToggle"] label p,
    .st-key-header_card_shopeepay [data-testid="stToggle"] label p {
        font-size: 11px !important;
        font-weight: 600 !important;
    }

    /* Konten panel ringkasan dibuat lebih simetris */
    .agreement-grid {
        gap: 10px !important;
        margin-bottom: 12px !important;
    }

    .agreement-card {
        padding: 18px 10px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 84px !important;
    }

    .agreement-card .big {
        line-height: 1 !important;
        margin-bottom: 8px !important;
    }

    .sentiment-mini {
        padding: 12px 8px !important;
    }

    /* Summary TN TP FN FP */
    .cm-summary-grid {
        gap: 10px !important;
    }

    .cm-box {
        padding: 14px 6px !important;
        min-height: 72px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .cm-box small {
        font-size: 10px !important;
        margin-bottom: 4px !important;
    }

    .cm-box b {
        font-size: clamp(18px, 1.45vw, 28px) !important;
    }

    /* Note bawah confusion summary tanpa box */
    .cm-note-text {
