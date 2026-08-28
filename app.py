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
    initial_sidebar_state="collapsed",
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

    /* LATAR BELAKANG LUAR */
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

    /* SEMUA CONTAINER STREAMLIT */
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

    /* HEADER HORIZONTAL */
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

    /* SEMUA CUSTOM BOX */
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

    .kpi-card { border-radius: 12px !important; }
    .sentiment-mini { border-radius: 9px !important; }
    .agreement-card { border-radius: 10px !important; }
    .cm-box { border-radius: 9px !important; }
    .cm-note { border-radius: 8px !important; }
    .metric-box { border-radius: 9px !important; }

    .nav-link {
        border-radius: 9px !important;
        margin: 8px 0 !important;
    }

    .nav-link:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 22px rgba(117,78,42,.14) !important;
    }

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

    [data-testid="stDataFrame"] {
        border: none !important;
        outline: none !important;
        border-radius: 10px !important;
        box-shadow: 0 5px 14px rgba(117,78,42,.11) !important;
        overflow: hidden !important;
    }

    [data-testid="stPlotlyChart"] {
        background: transparent !important;
    }

    [role="switch"][aria-checked="true"] {
        background-color: #9D6638 !important;
        border-color: transparent !important;
    }

    [role="switch"][aria-checked="false"] {
        background-color: #EEDDC7 !important;
        border-color: transparent !important;
    }

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
    .top-title-wrap {
        min-height: 158px !important;
        height: 158px !important;
        justify-content: center !important;
        padding: 6px 10px 6px 2px !important;
    }

    .st-key-top_header [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }

    .st-key-top_header [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
    }

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
    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 14px 16px !important;
        box-sizing: border-box !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
        gap: .55rem !important;
    }

    .st-key-top_header [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 12px 14px !important;
    }

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

    .cm-note-text {
        text-align: center;
        font-size: 12px;
        line-height: 1.45;
        color: #9D6638;
        margin-top: 12px;
        padding-top: 8px;
    }

    .metric-row {
        gap: 8px !important;
        margin-bottom: 12px !important;
    }

    .metric-box {
        min-height: 74px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 12px 6px !important;
    }

    [data-baseweb="select"] > div {
        min-height: 42px !important;
    }

    [data-testid="stDataFrame"] {
        margin-top: 4px !important;
    }

    @media (max-width: 900px) {
        .top-title-wrap {
            min-height: auto !important;
            height: auto !important;
        }

        .st-key-header_card_dana [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-header_card_gopay [data-testid="stVerticalBlockBorderWrapper"],
        .st-key-header_card_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 176px !important;
            height: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3E. FINAL HEADER LAYOUT
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .dashboard-heading-block {
        width: min(100%, 1180px);
        margin: 0 auto 22px auto;
        padding: 10px clamp(12px, 3vw, 42px) 6px clamp(12px, 3vw, 42px);
        box-sizing: border-box;
        text-align: center;
    }

    .dashboard-heading-title {
        margin: 0 auto !important;
        color: #9D6638 !important;
        font-size: clamp(30px, 4vw, 54px) !important;
        font-weight: 800 !important;
        line-height: 1.10 !important;
        letter-spacing: -0.03em !important;
        text-align: center !important;
    }

    .dashboard-heading-subtitle {
        width: min(100%, 980px);
        margin: 11px auto 0 auto;
        padding: 0 clamp(8px, 2vw, 28px);
        box-sizing: border-box;
        color: #9D6638 !important;
        font-size: clamp(11px, 1.05vw, 15px);
        line-height: 1.5;
        text-align: center;
    }

    .final-wallet-card {
        width: 100%;
        min-height: 210px;
        box-sizing: border-box;
        padding: 20px 18px 18px 18px;
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF5E5 45%,
            #FFFAF3 100%
        );
        border: none !important;
        outline: none !important;
        border-radius: 16px;
        box-shadow: 0 8px 22px rgba(117,78,42,.14);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .final-wallet-logo {
        width: 100%;
        height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
    }

    .final-wallet-logo img {
        width: 108px;
        height: 108px;
        object-fit: contain;
    }

    .final-wallet-links {
        width: 100%;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        box-sizing: border-box;
    }

    .final-wallet-link {
        min-height: 40px;
        padding: 7px 8px;
        box-sizing: border-box;
        border: none !important;
        outline: none !important;
        border-radius: 9px;
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFFAF3 100%
        );
        box-shadow: 0 4px 10px rgba(117,78,42,.09);
        color: #9D6638 !important;
        text-decoration: none !important;
        font-size: clamp(8px, .68vw, 11px);
        font-weight: 600;
        line-height: 1.2;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .final-wallet-link:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 13px rgba(117,78,42,.13);
    }

    .st-key-final_selector_dana [data-testid="stToggle"],
    .st-key-final_selector_gopay [data-testid="stToggle"],
    .st-key-final_selector_shopeepay [data-testid="stToggle"] {
        margin-top: 7px !important;
        margin-bottom: 0 !important;
        padding-left: 0 !important;
    }

    .st-key-final_selector_dana [data-testid="stToggle"] label,
    .st-key-final_selector_gopay [data-testid="stToggle"] label,
    .st-key-final_selector_shopeepay [data-testid="stToggle"] label {
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }

    .st-key-final_selector_dana [data-testid="stToggle"] label p,
    .st-key-final_selector_gopay [data-testid="stToggle"] label p,
    .st-key-final_selector_shopeepay [data-testid="stToggle"] label p {
        color: #9D6638 !important;
        font-size: clamp(11px, 1vw, 15px) !important;
        font-weight: 500 !important;
    }

    .st-key-final_selector_dana [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-final_selector_gopay [data-testid="stVerticalBlockBorderWrapper"],
    .st-key-final_selector_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        outline: none !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    .st-key-final_selector_dana [data-testid="stVerticalBlock"],
    .st-key-final_selector_gopay [data-testid="stVerticalBlock"],
    .st-key-final_selector_shopeepay [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    .final-wallet-spacer {
        height: 12px;
    }

    @media (max-width: 900px) {
        .dashboard-heading-block {
            margin-bottom: 16px;
            padding-left: 8px;
            padding-right: 8px;
        }

        .dashboard-heading-title {
            font-size: clamp(27px, 7vw, 38px) !important;
        }

        .final-wallet-card {
            min-height: 190px;
            padding: 16px 13px;
        }

        .final-wallet-logo {
            height: 92px;
        }

        .final-wallet-logo img {
            width: 88px;
            height: 88px;
        }

        .final-wallet-links {
            grid-template-columns: 1fr;
            gap: 7px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3F. UNIFORM PANEL HEIGHT
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* SIDEBAR BACKGROUND */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background: #FFF2DB !important;
    }

    .block-container [data-testid="stHorizontalBlock"] {
        align-items: stretch !important;
    }

    .block-container [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        display: flex !important;
        flex-direction: column !important;
        align-self: stretch !important;
        min-width: 0 !important;
    }

    .block-container [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]
    > [data-testid="stVerticalBlock"] {
        flex: 1 1 auto !important;
        height: 100% !important;
    }

    /* ROW 1 */
    [class*="st-key-panel_row1_"] {
        height: 100% !important;
    }
    [class*="st-key-panel_row1_"] [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 405px !important;
        height: 100% !important;
        padding: 18px !important;
        box-sizing: border-box !important;
    }

    /* ROW 2 */
    [class*="st-key-panel_row2_"] {
        height: 100% !important;
    }
    [class*="st-key-panel_row2_"] [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 575px !important;
        height: 100% !important;
        padding: 20px 18px 24px 18px !important;
        box-sizing: border-box !important;
    }
    [class*="st-key-panel_row2_"] .sentiment-mini-grid {
        margin-top: 2px !important;
        margin-bottom: 8px !important;
    }
    [class*="st-key-panel_row2_"] .sentiment-mini {
        min-height: 82px !important;
        box-sizing: border-box !important;
    }
    [class*="st-key-panel_row2_summary_"] [data-testid="stVerticalBlock"] {
        justify-content: center !important;
    }

    /* ROW 3 */
    [class*="st-key-panel_row3_"] {
        height: 100% !important;
    }
    [class*="st-key-panel_row3_"] [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 445px !important;
        height: 100% !important;
        padding: 20px 18px 22px 18px !important;
        box-sizing: border-box !important;
    }
    [class*="st-key-panel_row3_summary_"] [data-testid="stVerticalBlock"] {
        justify-content: center !important;
    }

    /* ROW 4 */
    [class*="st-key-panel_row4_"] {
        height: 100% !important;
    }
    [class*="st-key-panel_row4_"] [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 420px !important;
        height: 100% !important;
        padding: 20px 18px 22px 18px !important;
        box-sizing: border-box !important;
    }

    /* ROW 5 & ROW 6 */
    [class*="st-key-panel_row5_"],
    [class*="st-key-panel_row6_"] {
        height: 100% !important;
    }
    [class*="st-key-panel_row5_"] [data-testid="stVerticalBlockBorderWrapper"],
    [class*="st-key-panel_row6_"] [data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 560px !important;
        height: 100% !important;
        padding: 20px 18px 22px 18px !important;
        box-sizing: border-box !important;
    }

    [data-testid="stPlotlyChart"],
    [data-testid="stPlotlyChart"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    @media (max-width: 900px) {
        [class*="st-key-panel_row1_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-panel_row2_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-panel_row3_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-panel_row4_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-panel_row5_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-panel_row6_"] [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: auto !important;
            height: auto !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3H. PERFORMANCE WINNER CARDS
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .performance-winner-grid {
        width: 100%;
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 12px;
        align-items: stretch;
        margin-top: 14px;
        padding: 2px 4px 4px 4px;
        box-sizing: border-box;
    }

    .performance-winner-card {
        grid-column: span 2;
        min-height: 118px;
        border-radius: 12px;
        background: linear-gradient(
            180deg,
            #FFF2DB 0%,
            #FFF6E8 55%,
            #FFFAF3 100%
        );
        box-shadow: 0 5px 14px rgba(117,78,42,.11);
        padding: 14px 9px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }

    .performance-winner-card:nth-child(4) {
        grid-column: 2 / span 2;
    }

    .performance-winner-card:nth-child(5) {
        grid-column: 4 / span 2;
    }

    .performance-metric-name {
        font-size: 10px;
        line-height: 1.2;
        color: #9D6638;
        margin-bottom: 8px;
        font-weight: 500;
    }

    .performance-winner-name {
        font-size: clamp(21px, 1.65vw, 30px);
        line-height: 1;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .performance-score-line {
        font-size: 11px;
        line-height: 1.45;
        color: #9D6638;
        white-space: nowrap;
        font-weight: 500;
    }

    .performance-winner-caption {
        width: 100%;
        text-align: center;
        margin-top: 14px;
        font-size: 10px;
        line-height: 1.4;
        color: #9D6638;
    }

    @media (max-width: 1100px) {
        .performance-winner-grid {
            grid-template-columns: repeat(2, minmax(0,1fr));
        }

        .performance-winner-card,
        .performance-winner-card:nth-child(4),
        .performance-winner-card:nth-child(5) {
            grid-column: auto;
        }

        .performance-winner-card:nth-child(5) {
            grid-column: 1 / span 2;
            width: calc(50% - 6px);
            justify-self: center;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3I. FINAL POLISH & SINGLE SIDEBAR TOGGLE FIX
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Kembalikan font icon material bawaan Streamlit */
    [data-testid="stIconMaterial"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined",
                      "Material Symbols Sharp", "Material Icons" !important;
        color: #9D6638 !important;
    }

    /* -----------------------------------------------------------
       TOMBOL BUKA & TUTUP SIDEBAR (TAMPIL TUNGGAL & JELAS)
       ----------------------------------------------------------- */
    
    /* 1. Reset & hilangkan seluruh ::before / ::after / svg lama agar tidak menumpuk */
    [data-testid="stSidebarHeader"] button svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {
        display: none !important;
    }

    [data-testid="stSidebarHeader"]::after,
    [data-testid="stSidebarCollapseButton"]::after,
    [data-testid="stSidebarCollapsedControl"]::after,
    [data-testid="collapsedControl"]::after {
        content: none !important;
    }

    /* 2. Tombol Buka Sidebar (saat sidebar tertutup) */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {
        display: block !important;
        position: fixed !important;
        top: 0.45rem !important;
        left: 0.65rem !important;
        z-index: 1000000 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #FFF2DB !important;
        border: 1.4px solid #9D6638 !important;
        border-radius: 8px !important;
        width: 34px !important;
        height: 34px !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(157,102,56,.12) !important;
        padding: 0 !important;
        font-size: 0 !important;
    }

    [data-testid="stSidebarCollapsedControl"] button::before,
    [data-testid="collapsedControl"] button::before {
        content: "»" !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        color: #9D6638 !important;
    }

    /* 3. Tombol Tutup Sidebar (saat sidebar terbuka) */
    [data-testid="stSidebarHeader"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        padding: 0.6rem 0.8rem 0.2rem 0.8rem !important;
        background: transparent !important;
    }

    [data-testid="stSidebarHeader"] button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #FFFAF3 !important;
        border: 1.4px solid #9D6638 !important;
        border-radius: 8px !important;
        width: 34px !important;
        height: 34px !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(157,102,56,.10) !important;
        padding: 0 !important;
        margin-left: auto !important;
        font-size: 0 !important;
    }

    [data-testid="stSidebarHeader"] button::before {
        content: "«" !important;
        font-size: 20px !important;
        font-weight: 800 !important;
        line-height: 1 !important;
        color: #9D6638 !important;
    }

    [data-testid="stSidebarHeader"] button:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: #F4E1C2 !important;
        transform: scale(1.04) !important;
    }

    /* -----------------------------------------------------------
       NAVIGATION BAR ATAS FIXED
       ----------------------------------------------------------- */
    [data-testid="stHeader"] {
        background: #FFF2DB !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 99999 !important;
        height: 3rem !important;
        min-height: 3rem !important;
        box-shadow: 0 2px 10px rgba(157,102,56,.10) !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .block-container {
        padding-top: 3.2rem !important;
        margin-top: 0 !important;
    }

    [class*="st-key-panel_row2_summary_"] .agreement-grid {
        gap: 12px !important;
    }

    [class*="st-key-panel_row3_summary_"] .cm-summary-grid {
        gap: 10px !important;
    }

    [class*="st-key-panel_row3_summary_"] .cm-row-label {
        margin: 10px 0 8px 0 !important;
    }

    [class*="st-key-panel_row3_summary_"] .cm-row-label:first-child {
        margin-top: 0 !important;
    }

    [class*="st-key-panel_row4_compare_"] [data-testid="stVerticalBlock"] {
        justify-content: center !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 4. LOAD & VALIDASI DATA
# ------------------------------------------------------------
@st.cache_data
def load_data():
    df_nbc = pd.read_csv("hasilSentimenNBC.csv")
    df_svm = pd.read_csv("hasilSentimenSVM.csv")
    eval_nbc = pd.read_csv("hasilEvaluasiNBC.csv")
    eval_svm = pd.read_csv("hasilEvaluasiSVM.csv")

    for df in [df_nbc, df_svm, eval_nbc, eval_svm]:
        df.columns = df.columns.str.strip()

    required_nbc = {
        "reviewId", "appName", "content", "score", "date",
        "actualLabel", "predictLabel"
    }
    required_svm = {
        "reviewId", "appName", "content", "score", "date",
        "actualLabel", "predictLabelSVM"
    }
    required_eval = {
        "appName", "dataTrain", "dataTest", "TN", "FP", "FN", "TP",
        "Accuracy", "Precision", "Recall", "Specificity", "F1-Score"
    }

    if not required_nbc.issubset(df_nbc.columns):
        raise ValueError("Kolom hasilSentimenNBC.csv tidak sesuai kebutuhan dashboard.")
    if not required_svm.issubset(df_svm.columns):
        raise ValueError("Kolom hasilSentimenSVM.csv tidak sesuai kebutuhan dashboard.")
    if not required_eval.issubset(eval_nbc.columns):
        raise ValueError("Kolom hasilEvaluasiNBC.csv tidak sesuai kebutuhan dashboard.")
    if not required_eval.issubset(eval_svm.columns):
        raise ValueError("Kolom hasilEvaluasiSVM.csv tidak sesuai kebutuhan dashboard.")

    df_nbc["appName"] = df_nbc["appName"].astype(str).str.strip()
    df_svm["appName"] = df_svm["appName"].astype(str).str.strip()
    eval_nbc["appName"] = eval_nbc["appName"].astype(str).str.strip()
    eval_svm["appName"] = eval_svm["appName"].astype(str).str.strip()

    df_nbc["actualLabel"] = df_nbc["actualLabel"].astype(str).str.strip().str.lower()
    df_svm["actualLabel"] = df_svm["actualLabel"].astype(str).str.strip().str.lower()
    df_nbc["predictLabelNBC"] = df_nbc["predictLabel"].astype(str).str.strip().str.lower()
    df_svm["predictLabelSVM"] = df_svm["predictLabelSVM"].astype(str).str.strip().str.lower()

    df_nbc["date"] = pd.to_datetime(df_nbc["date"], errors="coerce")
    df_svm["date"] = pd.to_datetime(df_svm["date"], errors="coerce")
    df_nbc["score"] = pd.to_numeric(df_nbc["score"], errors="coerce")
    df_svm["score"] = pd.to_numeric(df_svm["score"], errors="coerce")

    for app in APP_ORDER:
        nbc_app = df_nbc[df_nbc["appName"] == app]
        svm_app = df_svm[df_svm["appName"] == app]

        if nbc_app.empty or svm_app.empty:
            raise ValueError(f"Data {app} tidak ditemukan pada salah satu file sentimen.")
        if len(nbc_app) != len(svm_app):
            raise ValueError(f"Jumlah data NBC dan SVM berbeda untuk {app}.")
        if set(nbc_app["reviewId"]) != set(svm_app["reviewId"]):
            raise ValueError(f"reviewId NBC dan SVM tidak identik untuk {app}.")

        rn = eval_nbc[eval_nbc["appName"] == app]
        rs = eval_svm[eval_svm["appName"] == app]
        if rn.empty or rs.empty:
            raise ValueError(f"Data evaluasi {app} tidak lengkap.")
        if int(rn.iloc[0]["dataTrain"]) != int(rs.iloc[0]["dataTrain"]):
            raise ValueError(f"Jumlah data training NBC dan SVM berbeda untuk {app}.")
        if int(rn.iloc[0]["dataTest"]) != int(rs.iloc[0]["dataTest"]):
            raise ValueError(f"Jumlah data testing NBC dan SVM berbeda untuk {app}.")

    return df_nbc, df_svm, eval_nbc, eval_svm


try:
    df_nbc, df_svm, eval_nbc, eval_svm = load_data()
except Exception as e:
    st.error(f"Gagal memuat data dashboard: {e}")
    st.stop()

# ------------------------------------------------------------
# 5. HELPER
# ------------------------------------------------------------
def resolve_logo(app_name):
    for filename in APP_LOGO_CANDIDATES[app_name]:
        if os.path.exists(filename):
            return filename
    return None


def image_html(path, alt):
    if not path:
        return f'<div style="font-weight:800;color:{TEXT};">{alt}</div>'
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f'<img src="data:image/png;base64,{encoded}" alt="{alt}">'


def slugify(app_name):
    return app_name.lower().replace(" ", "-")


def plot_theme(fig, height=320, margin=None):
    if margin is None:
        margin = dict(l=45, r=20, t=35, b=45)
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT, family="Plus Jakarta Sans"),
        hoverlabel=dict(bgcolor=BOX_BG, bordercolor=BORDER, font_color=TEXT),
        legend_title_text="",
    )
    fig.update_xaxes(gridcolor="rgba(157,102,56,.12)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(157,102,56,.12)", zeroline=False)
    return fig


def get_app_data(app_name):
    nbc_app = df_nbc[df_nbc["appName"] == app_name].copy()
    svm_app = df_svm[df_svm["appName"] == app_name].copy()
    row_nbc = eval_nbc[eval_nbc["appName"] == app_name].iloc[0]
    row_svm = eval_svm[eval_svm["appName"] == app_name].iloc[0]
    return nbc_app, svm_app, row_nbc, row_svm


def sentiment_summary(df, prediction_col):
    counts = df[prediction_col].value_counts().reindex(["positif", "negatif"], fill_value=0)
    total = int(counts.sum())
    pos = int(counts["positif"])
    neg = int(counts["negatif"])
    return {
        "total": total,
        "positif": pos,
        "negatif": neg,
        "positifPct": (pos / total * 100) if total else 0,
        "negatifPct": (neg / total * 100) if total else 0,
    }


def build_prediction_compare(nbc_app, svm_app):
    compare = nbc_app[
        ["reviewId", "content", "score", "date", "actualLabel", "predictLabelNBC"]
    ].merge(
        svm_app[["reviewId", "predictLabelSVM"]],
        on="reviewId",
        how="inner",
        validate="one_to_one",
    )
    compare["kesepakatan"] = compare["predictLabelNBC"] == compare["predictLabelSVM"]
    return compare


def rating_figure(nbc_app, svm_app):
    rating_nbc = (
        nbc_app["score"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0).rename("Jumlah").reset_index()
    )
    rating_nbc.columns = ["Rating", "Jumlah"]
    rating_nbc["Model"] = "NBC"

    rating_svm = (
        svm_app["score"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0).rename("Jumlah").reset_index()
    )
    rating_svm.columns = ["Rating", "Jumlah"]
    rating_svm["Model"] = "SVM"

    rating = pd.concat([rating_nbc, rating_svm], ignore_index=True)
    fig = px.bar(
        rating,
        x="Rating",
        y="Jumlah",
        color="Model",
        barmode="group",
        category_orders={"Model": ["NBC", "SVM"], "Rating": [1, 2, 3, 4, 5]},
        color_discrete_map=MODEL_COLOR,
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Rating: %{x}<br>Jumlah: %{y:,}<extra></extra>"
    )
    fig.update_xaxes(dtick=1, title="score")
    fig.update_yaxes(title="Jumlah Ulasan")
    fig.update_layout(legend=dict(orientation="h", x=.5, xanchor="center", y=1.12))
    return plot_theme(fig, height=315, margin=dict(l=45, r=15, t=45, b=45))


def trend_figure(nbc_app, svm_app, sentiment):
    nbc = nbc_app[["date", "predictLabelNBC"]].dropna(subset=["date"]).copy()
    nbc = nbc[nbc["predictLabelNBC"] == sentiment.lower()]
    nbc["Bulan"] = nbc["date"].dt.to_period("M").astype(str)
    nbc = nbc.groupby("Bulan").size().reset_index(name="Jumlah")
    nbc["Model"] = "NBC"

    svm = svm_app[["date", "predictLabelSVM"]].dropna(subset=["date"]).copy()
    svm = svm[svm["predictLabelSVM"] == sentiment.lower()]
    svm["Bulan"] = svm["date"].dt.to_period("M").astype(str)
    svm = svm.groupby("Bulan").size().reset_index(name="Jumlah")
    svm["Model"] = "SVM"

    trend = pd.concat([nbc, svm], ignore_index=True)
    fig = px.line(
        trend,
        x="Bulan",
        y="Jumlah",
        color="Model",
        markers=True,
        category_orders={"Model": ["NBC", "SVM"]},
        color_discrete_map=MODEL_COLOR,
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Bulan: %{x}<br>Jumlah: %{y:,}<extra></extra>"
    )
    fig.update_xaxes(title="Periode Bulan", tickangle=-35)
    fig.update_yaxes(title="Jumlah Ulasan")
    fig.update_layout(legend=dict(orientation="h", x=.5, xanchor="center", y=1.12))
    return plot_theme(fig, height=315, margin=dict(l=48, r=15, t=45, b=68))


def donut_figure(summary, model_name):
    data = pd.DataFrame({
        "Sentimen": ["Positif", "Negatif"],
        "Jumlah": [summary["positif"], summary["negatif"]],
    })
    fig = px.pie(
        data,
        values="Jumlah",
        names="Sentimen",
        hole=.52,
        color="Sentimen",
        color_discrete_map=MODEL_SENTIMENT_COLOR[model_name],
        category_orders={"Sentimen": ["Positif", "Negatif"]},
    )
    fig.update_traces(
        sort=False,
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value:,}<br>Proporsi: %{percent}<extra></extra>",
    )
    fig.update_layout(showlegend=False)
    return plot_theme(fig, height=270, margin=dict(l=12, r=12, t=8, b=8))


def difference_figure(compare):
    nbc_pos_svm_neg = int(((compare["predictLabelNBC"] == "positif") & (compare["predictLabelSVM"] == "negatif")).sum())
    nbc_neg_svm_pos = int(((compare["predictLabelNBC"] == "negatif") & (compare["predictLabelSVM"] == "positif")).sum())
    data = pd.DataFrame({
        "Perbedaan": ["NBC Positif → SVM Negatif", "NBC Negatif → SVM Positif"],
        "Jumlah": [nbc_pos_svm_neg, nbc_neg_svm_pos],
        "Warna": ["NBC", "SVM"],
    })
    fig = px.bar(
        data,
        x="Jumlah",
        y="Perbedaan",
        orientation="h",
        text="Jumlah",
        color="Warna",
        color_discrete_map=MODEL_COLOR,
    )
    fig.update_traces(textposition="outside", hovertemplate="<b>%{y}</b><br>Jumlah: %{x:,}<extra></extra>")
    fig.update_layout(showlegend=False)
    fig.update_xaxes(title="Jumlah Ulasan")
    fig.update_yaxes(title="")
    return plot_theme(fig, height=165, margin=dict(l=20, r=28, t=10, b=36))


def confusion_figure(row_eval, model_name):
    tn, fp, fn, tp = [int(row_eval[k]) for k in ["TN", "FP", "FN", "TP"]]
    model_color = MODEL_COLOR[model_name]

    light_text = "#FFFAF3"
    dark_text = NBC_NEG if model_name == "NBC" else SVM_NEG

    fig = go.Figure(
        go.Heatmap(
            z=[[1.0, 0.28], [0.28, 1.0]],
            x=["negatif", "positif"],
            y=["negatif", "positif"],
            customdata=[[tn, fp], [fn, tp]],
            colorscale=(
                [
                    [0.00, "#FFFAF3"],
                    [0.28, "rgba(163,72,90,0.20)"],
                    [0.60, "rgba(163,72,90,0.55)"],
                    [1.00, NBC],
                ]
                if model_name == "NBC"
                else [
                    [0.00, "#FFFAF3"],
                    [0.28, "rgba(75,86,148,0.20)"],
                    [0.60, "rgba(75,86,148,0.55)"],
                    [1.00, SVM],
                ]
            ),
            zmin=0,
            zmax=1,
            showscale=False,
            xgap=3,
            ygap=3,
            hovertemplate=(
                "actualLabel: %{y}<br>"
                "predictLabel: %{x}<br>"
                "Jumlah: %{customdata:,}"
                "<extra></extra>"
            ),
        )
    )

    annotations = [
        dict(
            x="negatif", y="negatif",
            text=f"<b>{tn}<br>TN</b>",
            font=dict(size=13, color=light_text),
        ),
        dict(
            x="positif", y="negatif",
            text=f"<b>{fp}<br>FP</b>",
            font=dict(size=13, color=dark_text),
        ),
        dict(
            x="negatif", y="positif",
            text=f"<b>{fn}<br>FN</b>",
            font=dict(size=13, color=dark_text),
        ),
        dict(
            x="positif", y="positif",
            text=f"<b>{tp}<br>TP</b>",
            font=dict(size=13, color=light_text),
        ),
    ]

    for annotation in annotations:
        fig.add_annotation(
            x=annotation["x"],
            y=annotation["y"],
            text=annotation["text"],
            showarrow=False,
            align="center",
            font=annotation["font"],
        )

    fig.update_layout(
        xaxis_title="predictLabel",
        yaxis_title="actualLabel",
        xaxis_side="bottom",
    )
    fig.update_yaxes(autorange="reversed")
    return plot_theme(fig, height=295, margin=dict(l=55, r=16, t=16, b=55))

def performance_figure(row_nbc, row_svm):
    records = []

    for model_name, row in [("NBC", row_nbc), ("SVM", row_svm)]:
        for metric in METRIC_ORDER:
            value_pct = float(row[metric]) * 100
            records.append({
                "Model": model_name,
                "Metrik": metric,
                "Nilai": value_pct
            })

    df = pd.DataFrame(records)

    fig = px.bar(
        df,
        x="Metrik",
        y="Nilai",
        color="Model",
        barmode="group",
        text=df["Nilai"].map(lambda x: f"{x:.2f}%"),
        category_orders={
            "Model": ["NBC", "SVM"],
            "Metrik": METRIC_ORDER
        },
        color_discrete_map=MODEL_COLOR,
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            "Metrik: %{x}<br>"
            "Nilai: %{y:.2f}%"
            "<extra></extra>"
        ),
    )

    fig.update_yaxes(
        title="Nilai (%)",
        range=[0, 108],
        ticksuffix="%",
        tickformat=".0f"
    )

    fig.update_xaxes(title="")

    fig.update_layout(
        legend=dict(
            orientation="h",
            x=.5,
            xanchor="center",
            y=1.12
        )
    )

    return plot_theme(
        fig,
        height=330,
        margin=dict(l=55, r=15, t=48, b=50)
    )

def wordcloud_plotly(text, color, key_title):
    if not str(text).strip():
        fig = go.Figure()
        fig.add_annotation(text="Tidak ada kata untuk ditampilkan", x=.5, y=.5, showarrow=False)
        return plot_theme(fig, height=215)

    wc = WordCloud(
        width=650,
        height=280,
        background_color=BOX_BG,
        max_words=60,
        collocations=False,
    ).generate(str(text))
    wc = wc.recolor(color_func=lambda *args, **kwargs: color)

    fig = go.Figure(go.Image(z=wc.to_array()))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x")
    fig.update_layout(dragmode="zoom", title=None)
    return plot_theme(fig, height=215, margin=dict(l=4, r=4, t=4, b=4))


def metric_cards_html(row_eval, model_name):
    color = MODEL_COLOR[model_name]
    cards = "".join(
        f'<div class="metric-box" style="color:{color};">'
        f'<small>{metric}</small><b>{float(row_eval[metric])*100:.2f}%</b></div>'
        for metric in METRIC_ORDER
    )
    return f'<div class="metric-row">{cards}</div>'


def cm_summary_html(row_eval, model_name):
    color = MODEL_COLOR[model_name]
    values = [("TN", int(row_eval["TN"])), ("TP", int(row_eval["TP"])), ("FN", int(row_eval["FN"])), ("FP", int(row_eval["FP"]))]
    boxes = "".join(
        f'<div class="cm-box" style="color:{color};"><small>{name}</small><b>{value:,}</b></div>'
        for name, value in values
    )
    return (
        f'<div class="cm-row-label" style="color:{color};">{model_name}</div>'
        f'<div class="cm-summary-grid">{boxes}</div>'
    )


def classification_table(df, pred_col, model_name, app_name):
    view = df[["content", "score", "actualLabel", pred_col]].copy()
    view.columns = ["Ulasan", "Rating", "Klasifikasi Pengguna", f"Klasifikasi {model_name}"]
    view.insert(0, "No.", range(1, len(view) + 1))

    filter_mode = st.selectbox(
        "Tampilkan contoh",
        ["Semua", "Prediksi Benar", "Prediksi Salah"],
        key=f"table_filter_{slugify(app_name)}_{model_name}",
        label_visibility="collapsed",
    )

    if filter_mode == "Prediksi Benar":
        view = view[view["Klasifikasi Pengguna"] == view[f"Klasifikasi {model_name}"]]
    elif filter_mode == "Prediksi Salah":
        view = view[view["Klasifikasi Pengguna"] != view[f"Klasifikasi {model_name}"]]

    st.dataframe(
        view.head(50),
        use_container_width=True,
        hide_index=True,
        height=390,
        column_order=["No.", "Ulasan", "Rating", "Klasifikasi Pengguna", f"Klasifikasi {model_name}"],
    )

# ------------------------------------------------------------
# 6. SESSION STATE + PILIH E-WALLET
# ------------------------------------------------------------
for app, default in [("DANA", True), ("GoPay", True), ("ShopeePay", True)]:
    key = f"toggle_{slugify(app)}"
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown(
    """
    <div class="dashboard-heading-block">
        <h1 class="dashboard-heading-title">
            DASHBOARD KLASIFIKASI SENTIMEN<br>
            DANA, GOPAY, & SHOPEEPAY
        </h1>
        <div class="dashboard-heading-subtitle">
            Perbandingan hasil klasifikasi sentimen menggunakan
            Multinomial Naïve Bayes (NBC) dan Support Vector Machine (SVM)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div id="pilih-aplikasi" style="scroll-margin-top:85px"></div>', unsafe_allow_html=True)
selector_cols = st.columns(3, gap="medium")

for col, app in zip(selector_cols, APP_ORDER):
    with col:
        with st.container(
            border=False,
            key=f"final_selector_{slugify(app)}"
        ):
            logo = resolve_logo(app)
            logo_markup = image_html(logo, f"Logo {app}")

            st.markdown(
                f'<div class="final-wallet-card">'
                f'<div class="final-wallet-logo">{logo_markup}</div>'
                f'<div class="final-wallet-links">'
                f'<a class="final-wallet-link" '
                f'href="{APP_WEBSITE_URL[app]}" target="_blank">'
                f'Kunjungi Website Resmi</a>'
                f'<a class="final-wallet-link" '
                f'href="{APP_PLAYSTORE_URL[app]}" target="_blank">'
                f'Download di Play Store</a>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.toggle(
                app,
                key=f"toggle_{slugify(app)}",
            )

selected_apps = [
    app for app in APP_ORDER
    if st.session_state[f"toggle_{slugify(app)}"]
]

if not selected_apps:
    st.warning("Silakan aktifkan minimal satu aplikasi E-Wallet.")
    st.stop()

st.markdown(
    '<div class="final-wallet-spacer"></div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 7. NAVIGASI SIDEBAR PER APLIKASI YANG DIPILIH
# ------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="nav-title">Navigasi Aplikasi</div>', unsafe_allow_html=True)
    pilih_aplikasi_link = '<a class="nav-link" href="#pilih-aplikasi" target="_self">Pilih Aplikasi</a>'
    links = pilih_aplikasi_link + "".join(
        f'<a class="nav-link" href="#{slugify(app)}" target="_self">{app}</a>'
        for app in selected_apps
    )
    st.markdown(links, unsafe_allow_html=True)

# ------------------------------------------------------------
# 8. DASHBOARD PER APLIKASI
# ------------------------------------------------------------
for selected_app in APP_ORDER:
    if selected_app not in selected_apps:
        continue

    nbc_app, svm_app, row_nbc, row_svm = get_app_data(selected_app)
    compare = build_prediction_compare(nbc_app, svm_app)
    nbc_summary = sentiment_summary(nbc_app, "predictLabelNBC")
    svm_summary = sentiment_summary(svm_app, "predictLabelSVM")

    total_data = len(nbc_app)
    data_train = int(row_nbc["dataTrain"])
    data_test = int(row_nbc["dataTest"])

    same_count = int(compare["kesepakatan"].sum())
    different_count = int((~compare["kesepakatan"]).sum())
    same_pct = (same_count / len(compare) * 100) if len(compare) else 0
    diff_pct = 100 - same_pct

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div id="{slugify(selected_app)}" style="scroll-margin-top:85px"></div>'
        f'<h1 class="app-title">{selected_app}</h1>'
        f'<div class="app-divider"></div>',
        unsafe_allow_html=True,
    )

    # ROW 0
    st.markdown(
        f'<div class="kpi-grid-3">'
        f'<div class="kpi-card"><p class="kpi-value">{total_data:,}</p><p class="kpi-label">Total Data Preparation</p></div>'
        f'<div class="kpi-card"><p class="kpi-value">{data_train:,}</p><p class="kpi-label">Data Training</p></div>'
        f'<div class="kpi-card"><p class="kpi-value">{data_test:,}</p><p class="kpi-label">Data Testing</p></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ROW 1
    row1 = st.columns([1, 1, 1], gap="medium")

    with row1[0]:
        with st.container(border=True, key=f"panel_row1_rating_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Distribusi Rating NBC & SVM</div>', unsafe_allow_html=True)
            st.plotly_chart(rating_figure(nbc_app, svm_app), use_container_width=True, config=PLOTLY_CONFIG)

    with row1[1]:
        with st.container(border=True, key=f"panel_row1_positive_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Tren Sentimen Positif</div>', unsafe_allow_html=True)
            st.plotly_chart(trend_figure(nbc_app, svm_app, "Positif"), use_container_width=True, config=PLOTLY_CONFIG)

    with row1[2]:
        with st.container(border=True, key=f"panel_row1_negative_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Tren Sentimen Negatif</div>', unsafe_allow_html=True)
            st.plotly_chart(trend_figure(nbc_app, svm_app, "Negatif"), use_container_width=True, config=PLOTLY_CONFIG)

    # ROW 2
    row2 = st.columns([1, 1, 1], gap="medium")

    with row2[0]:
        with st.container(border=True, key=f"panel_row2_nbc_{slugify(selected_app)}"):
            st.markdown(f'<div class="panel-title model-nbc">Distribusi Sentimen NBC</div>', unsafe_allow_html=True)
            st.plotly_chart(donut_figure(nbc_summary, "NBC"), use_container_width=True, config=PLOTLY_CONFIG)
            st.markdown(
                f'<div class="sentiment-mini-grid">'
                f'<div class="sentiment-mini" style="color:{NBC};"><b>{nbc_summary["positifPct"]:.1f}%</b><small>Positif ({nbc_summary["positif"]:,})</small></div>'
                f'<div class="sentiment-mini" style="color:{NBC_NEG};"><b>{nbc_summary["negatifPct"]:.1f}%</b><small>Negatif ({nbc_summary["negatif"]:,})</small></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with row2[1]:
        with st.container(border=True, key=f"panel_row2_svm_{slugify(selected_app)}"):
            st.markdown(f'<div class="panel-title model-svm">Distribusi Sentimen SVM</div>', unsafe_allow_html=True)
            st.plotly_chart(donut_figure(svm_summary, "SVM"), use_container_width=True, config=PLOTLY_CONFIG)
            st.markdown(
                f'<div class="sentiment-mini-grid">'
                f'<div class="sentiment-mini" style="color:{SVM};"><b>{svm_summary["positifPct"]:.1f}%</b><small>Positif ({svm_summary["positif"]:,})</small></div>'
                f'<div class="sentiment-mini" style="color:{SVM_NEG};"><b>{svm_summary["negatifPct"]:.1f}%</b><small>Negatif ({svm_summary["negatif"]:,})</small></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with row2[2]:
        with st.container(border=True, key=f"panel_row2_summary_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Ringkasan Distribusi Sentimen NBC & SVM</div>', unsafe_allow_html=True)
            inner_cols = st.columns([0.04, 0.92, 0.04])
            with inner_cols[1]:
                st.markdown(
                    f'<div class="agreement-grid">'
                    f'<div class="agreement-card"><div class="big">{same_count:,}</div><div class="small">Prediksi Sama<br>{same_pct:.2f}% dari seluruh data</div></div>'
                    f'<div class="agreement-card"><div class="big">{different_count:,}</div><div class="small">Prediksi Berbeda<br>{diff_pct:.2f}% dari seluruh data</div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.plotly_chart(difference_figure(compare), use_container_width=True, config=PLOTLY_CONFIG)

    # ROW 3
    row3 = st.columns([1, 1, 1], gap="medium")

    with row3[0]:
        with st.container(border=True, key=f"panel_row3_nbc_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-nbc">Confusion Matrix<br>Multinomial Naïve Bayes</div>', unsafe_allow_html=True)
            st.plotly_chart(confusion_figure(row_nbc, "NBC"), use_container_width=True, config=PLOTLY_CONFIG)

    with row3[1]:
        with st.container(border=True, key=f"panel_row3_svm_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-svm">Confusion Matrix<br>Support Vector Machine</div>', unsafe_allow_html=True)
            st.plotly_chart(confusion_figure(row_svm, "SVM"), use_container_width=True, config=PLOTLY_CONFIG)

    with row3[2]:
        with st.container(border=True, key=f"panel_row3_summary_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Ringkasan Tren Sentimen NBC & SVM</div>', unsafe_allow_html=True)
            st.markdown(cm_summary_html(row_nbc, "NBC"), unsafe_allow_html=True)
            st.markdown(cm_summary_html(row_svm, "SVM"), unsafe_allow_html=True)
            st.markdown(
                '<div class="cm-note-text">Warna lebih pekat menunjukkan klasifikasi benar (TP dan TN), '
                'sedangkan warna lebih muda menunjukkan kesalahan klasifikasi (FP dan FN)</div>',
                unsafe_allow_html=True,
            )

    # ROW 4
    row4 = st.columns([1, 1], gap="medium")

    with row4[0]:
        with st.container(border=True, key=f"panel_row4_metric_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Diagram Metrik Evaluasi</div>', unsafe_allow_html=True)
            st.plotly_chart(performance_figure(row_nbc, row_svm), use_container_width=True, config=PLOTLY_CONFIG)

    with row4[1]:
        with st.container(border=True, key=f"panel_row4_compare_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title">Perbandingan Kinerja</div>', unsafe_allow_html=True)

            winner_cards = []

            for metric_name in METRIC_ORDER:
                nbc_value = float(row_nbc[metric_name])
                svm_value = float(row_svm[metric_name])

                if nbc_value > svm_value:
                    winner = "NBC"
                    winner_color = NBC
                elif svm_value > nbc_value:
                    winner = "SVM"
                    winner_color = SVM
                else:
                    winner = "Sama"
                    winner_color = TEXT

                winner_cards.append(
                    f'<div class="performance-winner-card">'
                    f'<div class="performance-metric-name">{metric_name}</div>'
                    f'<div class="performance-winner-name" '
                    f'style="color:{winner_color};">{winner}</div>'
                    f'<div class="performance-score-line">'
                    f'<span style="color:{NBC};">NBC {nbc_value*100:.2f}%</span>'
                    f' &nbsp;•&nbsp; '
                    f'<span style="color:{SVM};">SVM {svm_value*100:.2f}%</span>'
                    f'</div>'
                    f'</div>'
                )

            st.markdown(
                '<div class="performance-winner-grid">'
                + ''.join(winner_cards)
                + '</div>'
                '<div class="performance-winner-caption">'
                'Model yang ditampilkan pada setiap kartu adalah model dengan nilai '
                'metrik evaluasi lebih tinggi.'
                '</div>',
                unsafe_allow_html=True,
            )

    # ROW 5
    row5 = st.columns([0.72, 2.1], gap="medium")

    with row5[0]:
        with st.container(border=True, key=f"panel_row5_wordcloud_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-nbc">Word Cloud Positif NBC</div>', unsafe_allow_html=True)
            text_pos_nbc = " ".join(nbc_app.loc[nbc_app["predictLabelNBC"] == "positif", "content"].dropna().astype(str))
            st.plotly_chart(wordcloud_plotly(text_pos_nbc, NBC, "NBC Positif"), use_container_width=True, config=PLOTLY_CONFIG)

            st.markdown('<div class="panel-title model-nbc">Word Cloud Negatif NBC</div>', unsafe_allow_html=True)
            text_neg_nbc = " ".join(nbc_app.loc[nbc_app["predictLabelNBC"] == "negatif", "content"].dropna().astype(str))
            st.plotly_chart(wordcloud_plotly(text_neg_nbc, NBC_NEG, "NBC Negatif"), use_container_width=True, config=PLOTLY_CONFIG)

    with row5[1]:
        with st.container(border=True, key=f"panel_row5_table_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-nbc">Contoh Hasil Klasifikasi Ulasan Model NBC</div>', unsafe_allow_html=True)
            classification_table(nbc_app, "predictLabelNBC", "NBC", selected_app)

    # ROW 6
    row6 = st.columns([0.72, 2.1], gap="medium")

    with row6[0]:
        with st.container(border=True, key=f"panel_row6_wordcloud_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-svm">Word Cloud Positif SVM</div>', unsafe_allow_html=True)
            text_pos_svm = " ".join(svm_app.loc[svm_app["predictLabelSVM"] == "positif", "content"].dropna().astype(str))
            st.plotly_chart(wordcloud_plotly(text_pos_svm, SVM, "SVM Positif"), use_container_width=True, config=PLOTLY_CONFIG)

            st.markdown('<div class="panel-title model-svm">Word Cloud Negatif SVM</div>', unsafe_allow_html=True)
            text_neg_svm = " ".join(svm_app.loc[svm_app["predictLabelSVM"] == "negatif", "content"].dropna().astype(str))
            st.plotly_chart(wordcloud_plotly(text_neg_svm, SVM_NEG, "SVM Negatif"), use_container_width=True, config=PLOTLY_CONFIG)

    with row6[1]:
        with st.container(border=True, key=f"panel_row6_table_{slugify(selected_app)}"):
            st.markdown('<div class="panel-title model-svm">Contoh Hasil Klasifikasi Ulasan Model SVM</div>', unsafe_allow_html=True)
            classification_table(svm_app, "predictLabelSVM", "SVM", selected_app)

# ------------------------------------------------------------
# 9. FOOTER
# ------------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;font-size:10px;padding:4px 0 14px 0;">'
    'Dashboard klasifikasi sentimen E-Wallet — NBC & SVM</div>',
    unsafe_allow_html=True,
)
