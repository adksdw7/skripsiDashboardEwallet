# Library
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import base64


# Konfigurasi halaman
st.set_page_config(
    page_title="Klasifikasi Sentimen E-Wallet",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# Konstanta
APP_COLOR_MAP = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}

MODEL_COLOR_MAP = {
    "NBC": "#4f46e5",
    "SVM": "#f59e0b"
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

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True
}

METRIC_ORDER = [
    "Accuracy",
    "Precision",
    "Recall",
    "Specificity",
    "F1-Score"
]


# Style dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"],
    p, div, h1, h2, h3, h4, h5, h6, label {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }

    .stApp {
        background: #FFFAF3;
        background-attachment: fixed;
    }

    .block-container {
        width: 100%;
        max-width: 1500px;
        padding-left: clamp(0.75rem, 2vw, 2.5rem);
        padding-right: clamp(0.75rem, 2vw, 2.5rem);
    }

    hr {
        border: none;
        height: 4px;
        border-radius: 2px;
        background: linear-gradient(90deg, #2377ca, #01aed6, #ff773c);
        margin: 2.2rem 0;
        opacity: 1;
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

    .metric-card {
        background: #ffffff;
        border: 2px solid #d7dce2;
        border-radius: 12px;
        padding: 18px 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        min-height: 90px;
        box-sizing: border-box;
    }

    .metric-card h2,
    .metric-card h3 {
        margin: 0;
    }

    .metric-card p {
        margin: 5px 0 0 0;
        color: #6b7280;
        font-size: 13px;
    }

    .section-anchor {
        scroll-margin-top: 18px;
    }

    .dashboard-header-wrap {
        width: min(100%, 1050px);
        margin: 0 auto;
        padding: clamp(0.25rem, 1vw, 0.65rem) clamp(0.5rem, 2vw, 1.25rem);
        box-sizing: border-box;
        text-align: center;
    }

    .dashboard-main-title {
        margin: 0;
        color: #111827;
        font-size: clamp(28px, 4vw, 54px);
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -0.02em;
        text-align: center;
    }

    .dashboard-subtitle,
    .section-subtitle {
        width: min(100%, 980px);
        margin: clamp(10px, 1.4vw, 16px) auto 0 auto;
        padding: clamp(10px, 1.1vw, 14px) clamp(12px, 2vw, 24px);
        box-sizing: border-box;
        text-align: center;
        color: #111827;
        background: linear-gradient(
            to bottom,
            #FFF2DB 0%,
            #FFF5E6 34%,
            #FFF8EE 68%,
            #FFFAF3 100%
        );
        border-radius: 12px;
        font-size: clamp(11px, 1.15vw, 15px);
        line-height: 1.5;
    }

    .section-subtitle {
        margin-bottom: clamp(16px, 2vw, 24px);
    }

    .distribution-app-title {
        width: 100%;
        text-align: center;
        margin: 0 0 clamp(8px, 1vw, 14px) 0;
        font-size: clamp(24px, 3vw, 42px);
        font-weight: 800;
        line-height: 1.1;
    }

    .st-key-sentiment_panel_dana,
    .st-key-sentiment_panel_gopay,
    .st-key-sentiment_panel_shopeepay {
        width: min(100%, 1100px);
        margin-left: auto;
        margin-right: auto;
        margin-bottom: clamp(14px, 1.8vw, 22px);
    }

    .st-key-sentiment_panel_dana [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #2377ca !important;
    }

    .st-key-sentiment_panel_gopay [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #01aed6 !important;
    }

    .st-key-sentiment_panel_shopeepay [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #ff773c !important;
    }

    .sentiment-summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        width: 100%;
        gap: clamp(8px, 1.2vw, 14px);
        margin-top: 4px;
    }

    .sentiment-summary-item {
        min-width: 0;
        text-align: center;
    }

    .sentiment-summary-value {
        margin: 0;
        font-size: clamp(18px, 2vw, 29px);
        font-weight: 800;
        line-height: 1.15;
    }

    .sentiment-summary-label {
        margin: 3px 0 0 0;
        color: #6b7280;
        font-size: clamp(9px, 0.9vw, 12px);
        line-height: 1.3;
    }

    .section-title {
        width: 100%;
        text-align: center;
        margin: 0 0 18px 0;
        color: #111827;
    }

    .panel-title {
        text-align: center;
        font-weight: 700;
        font-size: clamp(14px, 1vw, 18px);
        margin-bottom: 10px;
        color: #111827;
    }

    .model-title {
        text-align: center;
        font-weight: 800;
        font-size: clamp(16px, 1.3vw, 22px);
        margin-bottom: 8px;
    }

    .sentiment-row {
        display: flex;
        width: 100%;
        gap: 12px;
        justify-content: space-between;
        margin-top: 4px;
    }

    .sentiment-item {
        flex: 1;
        text-align: center;
    }

    .sentiment-item h2 {
        margin: 0;
        font-size: clamp(20px, 2vw, 30px);
    }

    .sentiment-item p {
        margin: 2px 0 0 0;
        color: #6b7280;
        font-size: 13px;
    }

    .compare-kpi {
        background: #ffffff;
        border: 1px solid #d7dce2;
        border-top: 4px solid var(--model-color);
        border-radius: 10px;
        padding: 10px 6px;
        text-align: center;
        box-shadow: 0 3px 9px rgba(0,0,0,0.07);
        min-height: 78px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .compare-kpi-label {
        color: #5f6368;
        font-size: clamp(9px, 0.72vw, 11px);
        margin: 0;
    }

    .compare-kpi-value {
        color: var(--model-color);
        font-size: clamp(15px, 1.25vw, 20px);
        font-weight: 800;
        margin: 4px 0 0 0;
    }

    .compare-kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 8px;
        width: 100%;
    }

    .insight-card {
        background: #ffffff;
        border: 1px solid #d7dce2;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 5px 14px rgba(0,0,0,0.06);
        min-height: 92px;
        box-sizing: border-box;
    }

    .insight-label {
        color: #6b7280;
        font-size: 12px;
        margin: 0;
    }

    .insight-value {
        color: #111827;
        font-size: clamp(19px, 1.8vw, 28px);
        font-weight: 800;
        margin: 4px 0 0 0;
    }

    .insight-caption {
        color: #6b7280;
        font-size: 11px;
        margin: 4px 0 0 0;
    }

    .note-box {
        width: 100%;
        box-sizing: border-box;
        background: rgba(255,255,255,0.75);
        border: 1px solid #e3e5e8;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: center;
        color: #4b5563;
        font-size: 12px;
        line-height: 1.45;
    }

    .wallet-card {
        background: #ffffff;
        border: 2px solid var(--app-color);
        border-radius: 14px;
        padding: 18px 14px 14px 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        min-height: 185px;
        box-sizing: border-box;
    }

    .wallet-card.selected-wallet {
        border-width: 4px;
        box-shadow: 0 10px 28px var(--selected-shadow);
    }

    .wallet-logo {
        min-height: 90px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }

    .wallet-logo img {
        width: 90px;
        height: 90px;
        object-fit: contain;
    }

    .wallet-links {
        display: flex;
        gap: 8px;
    }

    .wallet-link {
        flex: 1;
        border: 1.5px solid var(--app-color);
        border-radius: 8px;
        padding: 7px 5px;
        text-align: center;
        text-decoration: none !important;
        color: #374151 !important;
        font-size: 11px;
        font-weight: 600;
        background: #ffffff;
    }


    /* Komposisi Data Penelitian */
    .dataset-summary-wrap {
        width: min(100%, 980px);
        margin: 0 auto;
    }

    .dataset-app-panel {
        width: 100%;
        box-sizing: border-box;
        border: 1.5px solid var(--app-color);
        border-radius: 14px;
        background: rgba(255,255,255,0.28);
        padding: clamp(10px, 1.4vw, 18px);
        margin: 0 auto clamp(14px, 1.8vw, 22px) auto;
    }

    .dataset-app-title {
        width: 100%;
        text-align: center;
        margin: 0 0 clamp(10px, 1.2vw, 16px) 0;
        color: var(--app-color);
        font-size: clamp(24px, 3vw, 42px);
        font-weight: 800;
        line-height: 1.1;
    }

    .dataset-metric-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: clamp(8px, 1.2vw, 16px);
        width: 100%;
    }

    .dataset-metric-card {
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
        background: #ffffff;
        border: 1px solid #d7dce2;
        border-radius: 10px;
        padding: clamp(10px, 1.3vw, 18px) clamp(7px, 1vw, 14px);
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .dataset-metric-value {
        margin: 0;
        color: #111827;
        font-size: clamp(19px, 2.3vw, 31px);
        font-weight: 800;
        line-height: 1.15;
    }

    .dataset-metric-label {
        margin: clamp(5px, 0.7vw, 9px) 0 0 0;
        color: #6b7280;
        font-size: clamp(9px, 0.9vw, 12px);
        line-height: 1.25;
    }

    @media (max-width: 700px) {
        .dataset-summary-wrap {
            width: 100%;
        }

        .dataset-app-panel {
            padding: 10px;
        }

        .dataset-app-title {
            font-size: clamp(22px, 8vw, 32px);
        }

        .dataset-metric-grid {
            gap: 7px;
        }

        .dataset-metric-card {
            padding: 9px 5px;
        }

        .dataset-metric-value {
            font-size: clamp(16px, 5vw, 24px);
        }

        .dataset-metric-label {
            font-size: clamp(8px, 2.7vw, 10px);
        }
    }

    @media (max-width: 480px) {
        .dataset-metric-grid {
            grid-template-columns: 1fr;
        }

        .dataset-metric-card {
            padding: 10px 8px;
        }
    }

    [data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
    }

    @media (max-width: 900px) {
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }

        [data-testid="stHorizontalBlock"] > [data-testid="column"],
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            flex: 1 1 100% !important;
            width: 100% !important;
        }

        .compare-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .wallet-links {
            flex-direction: column;
        }
    }
</style>
""", unsafe_allow_html=True)


# Load data
@st.cache_data
def load_data():
    df_nbc = pd.read_csv("hasilSentimenNBC.csv")
    df_svm = pd.read_csv("hasilSentimenSVM.csv")
    eval_nbc = pd.read_csv("hasilEvaluasiNBC.csv")
    eval_svm = pd.read_csv("hasilEvaluasiSVM.csv")

    for df in [df_nbc, df_svm, eval_nbc, eval_svm]:
        df.columns = df.columns.str.strip()

    df_nbc["appName"] = df_nbc["appName"].astype(str).str.strip()
    df_svm["appName"] = df_svm["appName"].astype(str).str.strip()

    df_nbc["actualLabel"] = (
        df_nbc["actualLabel"].astype(str).str.strip().str.lower()
    )
    df_svm["actualLabel"] = (
        df_svm["actualLabel"].astype(str).str.strip().str.lower()
    )

    df_nbc["predictLabelNBC"] = (
        df_nbc["predictLabel"].astype(str).str.strip().str.lower()
    )
    df_svm["predictLabelSVM"] = (
        df_svm["predictLabelSVM"].astype(str).str.strip().str.lower()
    )

    df_nbc["date"] = pd.to_datetime(df_nbc["date"], errors="coerce")
    df_svm["date"] = pd.to_datetime(df_svm["date"], errors="coerce")

    eval_nbc["appName"] = eval_nbc["appName"].astype(str).str.strip()
    eval_svm["appName"] = eval_svm["appName"].astype(str).str.strip()

    # Validasi bahwa NBC dan SVM membandingkan data yang sama per aplikasi.
    for app_name in ["DANA", "GoPay", "ShopeePay"]:
        nbc_app = df_nbc[df_nbc["appName"] == app_name]
        svm_app = df_svm[df_svm["appName"] == app_name]

        if len(nbc_app) != len(svm_app):
            raise ValueError(
                f"Jumlah data NBC dan SVM berbeda untuk {app_name}."
            )

        if set(nbc_app["reviewId"]) != set(svm_app["reviewId"]):
            raise ValueError(
                f"reviewId NBC dan SVM tidak identik untuk {app_name}."
            )

        row_nbc = eval_nbc[eval_nbc["appName"] == app_name]
        row_svm = eval_svm[eval_svm["appName"] == app_name]

        if row_nbc.empty or row_svm.empty:
            raise ValueError(
                f"Data evaluasi {app_name} tidak lengkap."
            )

        if int(row_nbc.iloc[0]["dataTrain"]) != int(row_svm.iloc[0]["dataTrain"]):
            raise ValueError(
                f"Jumlah data training NBC dan SVM berbeda untuk {app_name}."
            )

        if int(row_nbc.iloc[0]["dataTest"]) != int(row_svm.iloc[0]["dataTest"]):
            raise ValueError(
                f"Jumlah data testing NBC dan SVM berbeda untuk {app_name}."
            )

    return df_nbc, df_svm, eval_nbc, eval_svm


try:
    df_nbc, df_svm, eval_nbc, eval_svm = load_data()
except Exception as e:
    st.error(
        "Gagal memuat atau memvalidasi data. Pastikan empat file hasil NBC "
        f"dan SVM berada di folder yang sama. Error: {e}"
    )
    st.stop()


# Session state aplikasi
# User dapat memilih satu atau lebih E-Wallet menggunakan toggle.
if "tgl_dana" not in st.session_state:
    st.session_state["tgl_dana"] = True

if "tgl_gopay" not in st.session_state:
    st.session_state["tgl_gopay"] = True

if "tgl_shopeepay" not in st.session_state:
    st.session_state["tgl_shopeepay"] = True


# Helper
def rgba(hex_color, alpha):
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]
    return f"rgba({r}, {g}, {b}, {alpha})"


def judul_bagian(teks, anchor):
    st.markdown(
        f"""
        <div id="{anchor}" class="section-anchor"></div>
        <h1 class="section-title">{teks}</h1>
        """,
        unsafe_allow_html=True
    )


def get_img_html(file_path, alt_text):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")

        return (
            f'<img src="data:image/png;base64,{data}" '
            f'alt="{alt_text}">'
        )

    return (
        f'<div style="color:#6b7280;text-align:center;">'
        f'{alt_text}</div>'
    )


def get_app_data(app_name):
    nbc_app = df_nbc[df_nbc["appName"] == app_name].copy()
    svm_app = df_svm[df_svm["appName"] == app_name].copy()

    row_nbc = eval_nbc[eval_nbc["appName"] == app_name].iloc[0]
    row_svm = eval_svm[eval_svm["appName"] == app_name].iloc[0]

    return nbc_app, svm_app, row_nbc, row_svm


def sentiment_summary(df, prediction_column):
    counts = (
        df[prediction_column]
        .value_counts()
        .reindex(["positif", "negatif"], fill_value=0)
    )

    total = int(counts.sum())
    positif = int(counts["positif"])
    negatif = int(counts["negatif"])

    positif_pct = (positif / total * 100) if total > 0 else 0
    negatif_pct = (negatif / total * 100) if total > 0 else 0

    return {
        "total": total,
        "positif": positif,
        "negatif": negatif,
        "positifPct": positif_pct,
        "negatifPct": negatif_pct
    }


def confusion_figure(row_eval, model_name):
    model_color = MODEL_COLOR_MAP[model_name]

    tn = int(row_eval["TN"])
    fp = int(row_eval["FP"])
    fn = int(row_eval["FN"])
    tp = int(row_eval["TP"])

    fig = go.Figure(
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
            textfont=dict(size=13, color="#111111"),
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "%{y}<br>"
                "%{x}<br>"
                "Jumlah: %{customdata[0]}"
                "<extra></extra>"
            ),
            hoverlabel=dict(
                bgcolor="white",
                bordercolor=model_color,
                font=dict(color="#111111", size=12)
            ),
            colorscale=[
                [0, rgba(model_color, 0.10)],
                [0.49, rgba(model_color, 0.10)],
                [0.50, rgba(model_color, 0.48)],
                [1, rgba(model_color, 0.48)]
            ],
            zmin=0,
            zmax=1,
            showscale=False,
            xgap=3,
            ygap=3
        )
    )

    fig.update_layout(
        autosize=True,
        height=410,
        margin=dict(l=65, r=25, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#111111", size=10),
        xaxis=dict(
            side="top",
            fixedrange=True,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            autorange="reversed",
            fixedrange=True,
            tickfont=dict(size=10)
        )
    )

    return fig


def wordcloud_figure(text, sentiment):
    if not text.strip():
        return None

    wc = WordCloud(
        background_color="white",
        max_words=50,
        width=520,
        height=280
    ).generate(text)

    if sentiment == "positif":
        wc = wc.recolor(
            color_func=lambda *args, **kwargs: "#1a9c11"
        )
    else:
        wc = wc.recolor(
            color_func=lambda *args, **kwargs: "#cc0000"
        )

    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    fig.tight_layout(pad=0)

    return fig


# Sidebar
st.markdown("""
<style>
    [data-testid="stHeader"],
    header[data-testid="stHeader"] {
        background: #fff1ea !important;
        border-bottom: 1px solid rgba(255, 119, 60, 0.16) !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }

    .sidebar-nav-title {
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e5e7eb;
        color: #111827;
        font-weight: 800;
        font-size: 18px;
    }

    .sidebar-nav-link {
        display: block;
        padding: 9px 11px;
        margin: 3px 0;
        border-radius: 9px;
        color: #222222 !important;
        text-decoration: none !important;
        font-size: 13px;
        font-weight: 500;
    }

    .sidebar-nav-link:hover {
        background: #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

NAV_ITEMS = [
    ("Pilih E-Wallet", "pilih-e-wallet"),
    ("Hasil Analisis", "hasil-analisis"),
    ("Distribusi Sentimen", "distribusi-sentimen"),
    ("Perbedaan Prediksi", "perbedaan-prediksi"),
    ("Tren Sentimen", "tren-sentimen"),
    ("Distribusi Rating", "distribusi-rating"),
    ("Word Cloud", "word-cloud"),
    ("Perbandingan Kinerja Model", "perbandingan-model"),
    ("Confusion Matrix", "confusion-matrix"),
    ("Ringkasan Model", "ringkasan-model")
]

with st.sidebar:
    nav_links = "".join(
        f'<a class="sidebar-nav-link" href="#{anchor}" target="_self">'
        f'{label}</a>'
        for label, anchor in NAV_ITEMS
    )

    st.markdown(
        f"""
        <div class="sidebar-nav-title">Navigasi</div>
        {nav_links}
        """,
        unsafe_allow_html=True
    )


# Header
st.markdown(
    """
    <div class="dashboard-header-wrap">
        <h1 class="dashboard-main-title">
            KLASIFIKASI SENTIMEN<br>
            DANA, GOPAY, & SHOPEEPAY
        </h1>
        <div class="dashboard-subtitle">
            Menampilkan klasifikasi sentimen menggunakan model
            Multinomial Naïve Bayes dan Support Vector Machine
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 1. Pilih E-Wallet
# ============================================================
st.markdown("---")
judul_bagian("Pilih E-Wallet", "pilih-e-wallet")

# Tampilan pilihan E-Wallet mengikuti desain app.py sebelumnya:
# logo, website resmi, Play Store, dan toggle multi-pilihan.
wallet_columns = st.columns(3)

wallet_toggle_keys = {
    "DANA": "tgl_dana",
    "GoPay": "tgl_gopay",
    "ShopeePay": "tgl_shopeepay"
}

for idx, app_name in enumerate(["DANA", "GoPay", "ShopeePay"]):
    with wallet_columns[idx]:
        app_color = APP_COLOR_MAP[app_name]
        logo_html = get_img_html(
            APP_LOGO_FILE[app_name],
            f"Logo {app_name}"
        )

        wallet_html = (
            f'<div class="wallet-card" '
            f'style="--app-color:{app_color};--selected-shadow:{rgba(app_color, 0.22)};">'
            f'<div class="wallet-logo">{logo_html}</div>'
            f'<div class="wallet-links">'
            f'<a class="wallet-link" href="{APP_WEBSITE_URL[app_name]}" '
            f'target="_blank" rel="noopener noreferrer">Kunjungi Website Resmi</a>'
            f'<a class="wallet-link" href="{APP_PLAYSTORE_URL[app_name]}" '
            f'target="_blank" rel="noopener noreferrer">Download di Play Store</a>'
            f'</div>'
            f'</div>'
        )

        st.markdown(
            wallet_html,
            unsafe_allow_html=True
        )

        st.toggle(
            app_name,
            key=wallet_toggle_keys[app_name]
        )

selected_apps = []

if st.session_state["tgl_dana"]:
    selected_apps.append("DANA")

if st.session_state["tgl_gopay"]:
    selected_apps.append("GoPay")

if st.session_state["tgl_shopeepay"]:
    selected_apps.append("ShopeePay")

if not selected_apps:
    st.warning("⚠️ Silakan pilih minimal satu aplikasi E-Wallet")
    st.stop()

# ============================================================
# 2. Hasil Analisis
# ============================================================
st.markdown("---")
judul_bagian(
    "Hasil Analisis",
    "hasil-analisis"
)

st.markdown(
    '<div class="section-subtitle">'
    'Data yang disajikan merupakan ulasan pengguna selama periode '
    '1 Juni 2025 hingga 31 Mei 2026'
    '</div>',
    unsafe_allow_html=True
)

dataset_panels_html = '<div class="dataset-summary-wrap">'

for app_name in ["DANA", "GoPay", "ShopeePay"]:
    if app_name not in selected_apps:
        continue

    nbc_app_summary, _, row_nbc_summary, _ = get_app_data(app_name)
    app_color_summary = APP_COLOR_MAP[app_name]

    total_data_summary = len(nbc_app_summary)
    data_train_summary = int(row_nbc_summary["dataTrain"])
    data_test_summary = int(row_nbc_summary["dataTest"])

    dataset_panels_html += (
        f'<div class="dataset-app-panel" style="--app-color:{app_color_summary};">'
        f'<div class="dataset-app-title">{app_name}</div>'
        f'<div class="dataset-metric-grid">'
        f'<div class="dataset-metric-card">'
        f'<p class="dataset-metric-value">{total_data_summary:,}</p>'
        f'<p class="dataset-metric-label">Total Data Preparation</p>'
        f'</div>'
        f'<div class="dataset-metric-card">'
        f'<p class="dataset-metric-value">{data_train_summary:,}</p>'
        f'<p class="dataset-metric-label">Data Training</p>'
        f'</div>'
        f'<div class="dataset-metric-card">'
        f'<p class="dataset-metric-value">{data_test_summary:,}</p>'
        f'<p class="dataset-metric-label">Data Testing</p>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

dataset_panels_html += '</div>'

st.markdown(
    dataset_panels_html,
    unsafe_allow_html=True
)


# ============================================================
# 3. Distribusi Sentimen
# ============================================================
st.markdown("---")
judul_bagian(
    "Distribusi Sentimen",
    "distribusi-sentimen"
)

for selected_app in ["DANA", "GoPay", "ShopeePay"]:
    if selected_app not in selected_apps:
        continue

    app_color = APP_COLOR_MAP[selected_app]
    nbc_app, svm_app, row_nbc, row_svm = get_app_data(selected_app)

    nbc_summary = sentiment_summary(
        nbc_app,
        "predictLabelNBC"
    )

    svm_summary = sentiment_summary(
        svm_app,
        "predictLabelSVM"
    )

    with st.container(
        border=True,
        key=f"sentiment_panel_{selected_app.lower()}"
    ):
        st.markdown(
            f'<div class="distribution-app-title" '
            f'style="color:{app_color};">'
            f'{selected_app}'
            f'</div>',
            unsafe_allow_html=True
        )

        classification_cols = st.columns(2, gap="medium")

        classification_models = [
            (
                "NBC",
                nbc_app,
                "predictLabelNBC",
                nbc_summary
            ),
            (
                "SVM",
                svm_app,
                "predictLabelSVM",
                svm_summary
            )
        ]

        for col, (
            model_name,
            df_model,
            prediction_col,
            summary
        ) in zip(
            classification_cols,
            classification_models
        ):
            with col:
                with st.container(border=True):
                    model_color = MODEL_COLOR_MAP[model_name]

                    model_label = (
                        "Multinomial Naïve Bayes"
                        if model_name == "NBC"
                        else "Support Vector Machine"
                    )

                    st.markdown(
                        f'<div class="model-title" '
                        f'style="color:{model_color};">'
                        f'{model_label}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    pie_data = pd.DataFrame({
                        "Sentimen": ["Positif", "Negatif"],
                        "Jumlah": [
                            summary["positif"],
                            summary["negatif"]
                        ]
                    })

                    fig_pie = px.pie(
                        pie_data,
                        values="Jumlah",
                        names="Sentimen",
                        hole=0.45,
                        color="Sentimen",
                        color_discrete_map={
                            "Positif": "#1ccc0d",
                            "Negatif": "#cc0000"
                        },
                        category_orders={
                            "Sentimen": ["Positif", "Negatif"]
                        }
                    )

                    fig_pie.update_traces(
                        sort=False,
                        textinfo="percent+label",
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Jumlah: %{value:,}<br>"
                            "Proporsi: %{percent}"
                            "<extra></extra>"
                        )
                    )

                    fig_pie.update_layout(
                        height=300,
                        margin=dict(t=15, b=50, l=20, r=20),
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.05,
                            xanchor="center",
                            x=0.5
                        ),
                        paper_bgcolor="rgba(0,0,0,0)"
                    )

                    st.plotly_chart(
                        fig_pie,
                        use_container_width=True,
                        config=PLOTLY_CONFIG
                    )

                    # HTML dibuat tanpa indentasi multiline agar tidak
                    # terbaca sebagai code block oleh Markdown Streamlit.
                    sentiment_html = (
                        f'<div class="sentiment-summary-grid">'
                        f'<div class="sentiment-summary-item">'
                        f'<p class="sentiment-summary-value" style="color:#1a9c11;">'
                        f'{summary["positifPct"]:.1f}%</p>'
                        f'<p class="sentiment-summary-label">'
                        f'Positif ({summary["positif"]:,})</p>'
                        f'</div>'
                        f'<div class="sentiment-summary-item">'
                        f'<p class="sentiment-summary-value" style="color:#cc0000;">'
                        f'{summary["negatifPct"]:.1f}%</p>'
                        f'<p class="sentiment-summary-label">'
                        f'Negatif ({summary["negatif"]:,})</p>'
                        f'</div>'
                        f'</div>'
                    )

                    st.markdown(
                        sentiment_html,
                        unsafe_allow_html=True
                    )


# Bagian analisis lanjutan tetap dirender per aplikasi yang dipilih.
for selected_app in selected_apps:
    app_color = APP_COLOR_MAP[selected_app]
    nbc_app, svm_app, row_nbc, row_svm = get_app_data(selected_app)

    # ============================================================
    # 4. Perbedaan Prediksi NBC vs SVM
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Perbedaan Prediksi NBC dan SVM - {selected_app}",
        "perbedaan-prediksi"
    )

    prediction_compare = nbc_app[
        [
            "reviewId",
            "content",
            "score",
            "date",
            "actualLabel",
            "predictLabelNBC"
        ]
    ].merge(
        svm_app[
            [
                "reviewId",
                "predictLabelSVM"
            ]
        ],
        on="reviewId",
        how="inner",
        validate="one_to_one"
    )

    prediction_compare["kesepakatan"] = (
        prediction_compare["predictLabelNBC"]
        == prediction_compare["predictLabelSVM"]
    )

    same_count = int(prediction_compare["kesepakatan"].sum())
    different_count = int((~prediction_compare["kesepakatan"]).sum())
    agreement_pct = (
        same_count / len(prediction_compare) * 100
        if len(prediction_compare) > 0
        else 0
    )

    nbc_pos_svm_neg = int(
        (
            (prediction_compare["predictLabelNBC"] == "positif")
            & (prediction_compare["predictLabelSVM"] == "negatif")
        ).sum()
    )

    nbc_neg_svm_pos = int(
        (
            (prediction_compare["predictLabelNBC"] == "negatif")
            & (prediction_compare["predictLabelSVM"] == "positif")
        ).sum()
    )

    agreement_cols = st.columns([1.15, 1], gap="medium")

    with agreement_cols[0]:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Kesepakatan Prediksi Seluruh Data Preparation</div>',
                unsafe_allow_html=True
            )

            agreement_data = pd.DataFrame({
                "Kategori": ["Prediksi Sama", "Prediksi Berbeda"],
                "Jumlah": [same_count, different_count]
            })

            fig_agreement = px.pie(
                agreement_data,
                values="Jumlah",
                names="Kategori",
                hole=0.52,
                color="Kategori",
                color_discrete_map={
                    "Prediksi Sama": "#22c55e",
                    "Prediksi Berbeda": "#ef4444"
                }
            )

            fig_agreement.update_traces(
                textinfo="percent+label",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Jumlah: %{value:,}<br>"
                    "Proporsi: %{percent}"
                    "<extra></extra>"
                )
            )

            fig_agreement.update_layout(
                height=330,
                margin=dict(t=10, b=35, l=20, r=20),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig_agreement,
                use_container_width=True,
                config=PLOTLY_CONFIG
            )

    with agreement_cols[1]:
        with st.container(border=True):
            st.markdown(
                '<div class="panel-title">Ringkasan Perbedaan Prediksi</div>',
                unsafe_allow_html=True
            )

            c1, c2 = st.columns(2)

            with c1:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <p class="insight-label">Prediksi Sama</p>
                        <p class="insight-value">{same_count:,}</p>
                        <p class="insight-caption">
                            {agreement_pct:.2f}% dari seluruh data
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with c2:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <p class="insight-label">Prediksi Berbeda</p>
                        <p class="insight-value">{different_count:,}</p>
                        <p class="insight-caption">
                            {100 - agreement_pct:.2f}% dari seluruh data
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            diff_direction = pd.DataFrame({
                "Perubahan": [
                    "NBC Positif → SVM Negatif",
                    "NBC Negatif → SVM Positif"
                ],
                "Jumlah": [
                    nbc_pos_svm_neg,
                    nbc_neg_svm_pos
                ]
            })

            fig_diff = px.bar(
                diff_direction,
                x="Jumlah",
                y="Perubahan",
                orientation="h",
                text="Jumlah",
                color="Perubahan",
                color_discrete_sequence=[
                    MODEL_COLOR_MAP["NBC"],
                    MODEL_COLOR_MAP["SVM"]
                ]
            )

            fig_diff.update_traces(
                textposition="outside",
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Jumlah: %{x:,}"
                    "<extra></extra>"
                )
            )

            fig_diff.update_layout(
                height=225,
                margin=dict(t=10, b=35, l=20, r=45),
                showlegend=False,
                xaxis_title="Jumlah Ulasan",
                yaxis_title="",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig_diff,
                use_container_width=True,
                config=PLOTLY_CONFIG
            )

    st.markdown(
        '<div class="note-box">'
        'Bagian ini membandingkan prediksi NBC dan SVM pada ulasan yang sama. '
        'Nilai ini bukan metrik evaluasi model, tetapi menunjukkan tingkat '
        'kesepakatan hasil klasifikasi kedua algoritma.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 5. Tren Sentimen NBC vs SVM
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Tren Sentimen NBC dan SVM - {selected_app}",
        "tren-sentimen"
    )

    trend_nbc = nbc_app[
        ["date", "predictLabelNBC"]
    ].copy()

    trend_nbc["Model"] = "NBC"
    trend_nbc["Sentimen"] = (
        trend_nbc["predictLabelNBC"]
        .str.capitalize()
    )

    trend_svm = svm_app[
        ["date", "predictLabelSVM"]
    ].copy()

    trend_svm["Model"] = "SVM"
    trend_svm["Sentimen"] = (
        trend_svm["predictLabelSVM"]
        .str.capitalize()
    )

    trend_data = pd.concat(
        [
            trend_nbc[["date", "Model", "Sentimen"]],
            trend_svm[["date", "Model", "Sentimen"]]
        ],
        ignore_index=True
    )

    trend_data = trend_data.dropna(subset=["date"])
    trend_data["Bulan"] = (
        trend_data["date"]
        .dt.to_period("M")
        .astype(str)
    )

    trend_group = (
        trend_data
        .groupby(
            ["Bulan", "Model", "Sentimen"]
        )
        .size()
        .reset_index(name="Jumlah")
    )

    trend_cols = st.columns(2, gap="medium")

    for col, sentiment_name in zip(
        trend_cols,
        ["Positif", "Negatif"]
    ):
        with col:
            with st.container(border=True):
                df_trend_sentiment = trend_group[
                    trend_group["Sentimen"] == sentiment_name
                ]

                fig_trend = px.line(
                    df_trend_sentiment,
                    x="Bulan",
                    y="Jumlah",
                    color="Model",
                    markers=True,
                    color_discrete_map=MODEL_COLOR_MAP,
                    title=f"Sentimen {sentiment_name}"
                )

                fig_trend.update_layout(
                    height=340,
                    margin=dict(t=55, b=75, l=55, r=25),
                    legend_title_text="",
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    ),
                    xaxis_title="Periode Bulan",
                    yaxis_title="Jumlah Ulasan",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig_trend,
                    use_container_width=True,
                    config=PLOTLY_CONFIG
                )


    # ============================================================
    # 6. Distribusi Rating
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Distribusi Rating Ulasan {selected_app}",
        "distribusi-rating"
    )

    rating_data = (
        nbc_app
        .groupby("score")
        .size()
        .reset_index(name="Jumlah")
    )

    with st.container(border=True):
        fig_rating = px.bar(
            rating_data,
            x="score",
            y="Jumlah",
            text="Jumlah",
            color_discrete_sequence=[app_color],
            labels={
                "score": "Rating Bintang",
                "Jumlah": "Jumlah Ulasan"
            }
        )

        fig_rating.update_traces(
            textposition="outside",
            hovertemplate=(
                "Rating: %{x}<br>"
                "Jumlah Ulasan: %{y:,}"
                "<extra></extra>"
            )
        )

        fig_rating.update_layout(
            height=430,
            margin=dict(t=35, b=65, l=60, r=30),
            xaxis=dict(dtick=1),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_rating,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )

    st.markdown(
        '<div class="note-box">'
        'Distribusi rating merupakan informasi dari dataset aplikasi dan tidak '
        'bergantung pada algoritma NBC maupun SVM.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 7. Word Cloud NBC vs SVM
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Word Cloud Hasil Klasifikasi {selected_app}",
        "word-cloud"
    )

    wordcloud_cols = st.columns(2, gap="medium")

    wc_models = [
        ("NBC", nbc_app, "predictLabelNBC"),
        ("SVM", svm_app, "predictLabelSVM")
    ]

    for col, (
        model_name,
        df_model,
        prediction_col
    ) in zip(wordcloud_cols, wc_models):

        with col:
            with st.container(border=True):
                model_color = MODEL_COLOR_MAP[model_name]

                st.markdown(
                    f"""
                    <div
                        class="model-title"
                        style="color:{model_color};"
                    >
                        {model_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                for sentiment_value, sentiment_title in [
                    ("positif", "Positif"),
                    ("negatif", "Negatif")
                ]:
                    st.markdown(
                        f"""
                        <div class="panel-title">
                            Sentimen {sentiment_title}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    text_wc = " ".join(
                        df_model[
                            df_model[prediction_col]
                            == sentiment_value
                        ]["content"]
                        .astype(str)
                    )

                    fig_wc = wordcloud_figure(
                        text_wc,
                        sentiment_value
                    )

                    if fig_wc is not None:
                        st.pyplot(
                            fig_wc,
                            use_container_width=True
                        )
                        plt.close(fig_wc)
                    else:
                        st.info(
                            f"Tidak ada data sentimen {sentiment_title.lower()}."
                        )


    # ============================================================
    # 8. Perbandingan Kinerja Model
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Perbandingan Kinerja NBC dan SVM - {selected_app}",
        "perbandingan-model"
    )

    performance_cols = st.columns(2, gap="medium")

    for col, (
        model_name,
        row_eval
    ) in zip(
        performance_cols,
        [
            ("NBC", row_nbc),
            ("SVM", row_svm)
        ]
    ):
        with col:
            with st.container(border=True):
                model_color = MODEL_COLOR_MAP[model_name]

                st.markdown(
                    f"""
                    <div
                        class="model-title"
                        style="color:{model_color};"
                    >
                        {
                            "Multinomial Naïve Bayes"
                            if model_name == "NBC"
                            else "Support Vector Machine"
                        }
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                metric_html = "".join(
                    f"""
                    <div
                        class="compare-kpi"
                        style="--model-color:{model_color};"
                    >
                        <p class="compare-kpi-label">
                            {metric_name}
                        </p>
                        <p class="compare-kpi-value">
                            {float(row_eval[metric_name]) * 100:.2f}%
                        </p>
                    </div>
                    """
                    for metric_name in METRIC_ORDER
                )

                st.markdown(
                    f"""
                    <div class="compare-kpi-grid">
                        {metric_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    performance_long = []

    for model_name, row_eval in [
        ("NBC", row_nbc),
        ("SVM", row_svm)
    ]:
        for metric_name in METRIC_ORDER:
            performance_long.append({
                "Model": model_name,
                "Metrik": metric_name,
                "Nilai": float(row_eval[metric_name])
            })

    performance_df = pd.DataFrame(performance_long)
    performance_df["Label"] = (
        performance_df["Nilai"]
        .map(lambda x: f"{x:.4f}")
    )

    with st.container(border=True):
        st.markdown(
            '<div class="panel-title">Diagram Perbandingan Metrik Evaluasi</div>',
            unsafe_allow_html=True
        )

        fig_performance = px.bar(
            performance_df,
            x="Metrik",
            y="Nilai",
            color="Model",
            barmode="group",
            text="Label",
            category_orders={
                "Metrik": METRIC_ORDER,
                "Model": ["NBC", "SVM"]
            },
            color_discrete_map=MODEL_COLOR_MAP,
            labels={
                "Nilai": "Nilai",
                "Metrik": "",
                "Model": "Model"
            }
        )

        fig_performance.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Metrik: %{x}<br>"
                "Nilai: %{y:.4f}"
                "<extra></extra>"
            )
        )

        fig_performance.update_layout(
            height=440,
            margin=dict(t=25, b=55, l=55, r=25),
            yaxis=dict(
                range=[0, 1.08],
                tickformat=".2f",
                gridcolor="rgba(0,0,0,0.08)",
                zeroline=False
            ),
            legend_title_text="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_performance,
            use_container_width=True,
            config=PLOTLY_CONFIG
        )


    # ============================================================
    # 9. Confusion Matrix NBC vs SVM
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Confusion Matrix NBC dan SVM - {selected_app}",
        "confusion-matrix"
    )

    cm_cols = st.columns(2, gap="medium")

    for col, (
        model_name,
        row_eval
    ) in zip(
        cm_cols,
        [
            ("NBC", row_nbc),
            ("SVM", row_svm)
        ]
    ):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div
                        class="panel-title"
                        style="color:{MODEL_COLOR_MAP[model_name]};"
                    >
                        Confusion Matrix {model_name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                fig_cm = confusion_figure(
                    row_eval,
                    model_name
                )

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
        '<div class="note-box">'
        'Warna lebih pekat menunjukkan klasifikasi benar (TP dan TN), '
        'sedangkan warna lebih muda menunjukkan kesalahan klasifikasi '
        '(FP dan FN). Kedua confusion matrix berasal dari data testing '
        'aplikasi yang sama.'
        '</div>',
        unsafe_allow_html=True
    )


    # ============================================================
    # 10. Ringkasan Model
    # ============================================================
    st.markdown("---")
    judul_bagian(
        f"Ringkasan Perbandingan Model - {selected_app}",
        "ringkasan-model"
    )

    comparison_rows = []

    nbc_wins = 0
    svm_wins = 0
    ties = 0

    for metric_name in METRIC_ORDER:
        nbc_value = float(row_nbc[metric_name])
        svm_value = float(row_svm[metric_name])

        difference_pp = (
            svm_value - nbc_value
        ) * 100

        if abs(difference_pp) < 0.000001:
            winner = "Sama"
            ties += 1
        elif nbc_value > svm_value:
            winner = "NBC"
            nbc_wins += 1
        else:
            winner = "SVM"
            svm_wins += 1

        comparison_rows.append({
            "Metrik": metric_name,
            "NBC": nbc_value * 100,
            "SVM": svm_value * 100,
            "Unggul": winner,
            "Selisih (SVM - NBC)": difference_pp
        })

    comparison_table = pd.DataFrame(comparison_rows)

    accuracy_nbc = float(row_nbc["Accuracy"]) * 100
    accuracy_svm = float(row_svm["Accuracy"]) * 100

    if accuracy_nbc > accuracy_svm:
        accuracy_winner = "NBC"
        accuracy_best = accuracy_nbc
        accuracy_gap = accuracy_nbc - accuracy_svm
    elif accuracy_svm > accuracy_nbc:
        accuracy_winner = "SVM"
        accuracy_best = accuracy_svm
        accuracy_gap = accuracy_svm - accuracy_nbc
    else:
        accuracy_winner = "Sama"
        accuracy_best = accuracy_nbc
        accuracy_gap = 0

    summary_cols = st.columns(3)

    with summary_cols[0]:
        st.markdown(
            f"""
            <div class="insight-card">
                <p class="insight-label">
                    Accuracy Lebih Tinggi
                </p>
                <p
                    class="insight-value"
                    style="
                        color:{
                            MODEL_COLOR_MAP.get(
                                accuracy_winner,
                                "#111827"
                            )
                        };
                    "
                >
                    {accuracy_winner}
                </p>
                <p class="insight-caption">
                    {accuracy_best:.2f}% |
                    selisih {accuracy_gap:.2f} poin persentase
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_cols[1]:
        st.markdown(
            f"""
            <div class="insight-card">
                <p class="insight-label">
                    Metrik Unggul NBC
                </p>
                <p
                    class="insight-value"
                    style="color:{MODEL_COLOR_MAP["NBC"]};"
                >
                    {nbc_wins} / {len(METRIC_ORDER)}
                </p>
                <p class="insight-caption">
                    Jumlah metrik dengan nilai lebih tinggi
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with summary_cols[2]:
        st.markdown(
            f"""
            <div class="insight-card">
                <p class="insight-label">
                    Metrik Unggul SVM
                </p>
                <p
                    class="insight-value"
                    style="color:{MODEL_COLOR_MAP["SVM"]};"
                >
                    {svm_wins} / {len(METRIC_ORDER)}
                </p>
                <p class="insight-caption">
                    Jumlah metrik dengan nilai lebih tinggi
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    display_table = comparison_table.copy()
    display_table["NBC"] = display_table["NBC"].map(
        lambda x: f"{x:.2f}%"
    )
    display_table["SVM"] = display_table["SVM"].map(
        lambda x: f"{x:.2f}%"
    )
    display_table["Selisih (SVM - NBC)"] = (
        display_table["Selisih (SVM - NBC)"]
        .map(lambda x: f"{x:+.2f} p.p.")
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    if accuracy_winner == "Sama":
        conclusion_text = (
            f"Pada data testing {selected_app}, NBC dan SVM memperoleh "
            f"Accuracy yang sama sebesar {accuracy_best:.2f}%."
        )
    else:
        conclusion_text = (
            f"Pada data testing {selected_app}, {accuracy_winner} memperoleh "
            f"Accuracy lebih tinggi sebesar {accuracy_gap:.2f} poin persentase. "
            f"Hasil ini hanya menjelaskan kinerja pada dataset dan konfigurasi "
            f"penelitian ini, bukan menyatakan satu algoritma selalu lebih baik "
            f"untuk seluruh kondisi."
        )

    st.info(conclusion_text)
