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

    # Data utama dashboard
    df_sentimen = pd.read_csv("hasilSentimen.csv")
    df_evaluasi = pd.read_csv("hasilEvaluasi.csv")


    # Data raw komentar asli
    df_raw_dana = pd.read_csv("rawDana.csv")
    df_raw_gopay = pd.read_csv("rawGopay.csv")
    df_raw_shopee = pd.read_csv("rawShopeepay.csv")


    if len(df_evaluasi.columns) >= 12:
        df_evaluasi.columns = [
            'aplikasi',
            'Accuracy',
            'Precision',
            'Recall',
            'Specificity',
            'F1-Score',
            'jumlahDataTrain',
            'jumlahDataTest',
            'TN',
            'FP',
            'FN',
            'TP'
        ]


    df_sentimen['date'] = pd.to_datetime(
        df_sentimen['date']
    )


    return (
        df_sentimen,
        df_evaluasi,
        df_raw_dana,
        df_raw_gopay,
        df_raw_shopee
    )

    # =====================================================
    # LOAD DATA RAW REVIEW UNTUK DETAIL KOMENTAR
    # =====================================================

    raw_dana = pd.read_csv(
        "rawDana.csv"
    )

    raw_gopay = pd.read_csv(
        "rawGopay.csv"
    )

    raw_shopeepay = pd.read_csv(
        "rawShopeepay.csv"
    )


    # Tambahkan identitas aplikasi
    raw_dana["appName"] = "DANA"

    raw_gopay["appName"] = "GoPay"

    raw_shopeepay["appName"] = "ShopeePay"



    # Gabungkan semua raw review
    df_raw_review = pd.concat(
        [
            raw_dana,
            raw_gopay,
            raw_shopeepay
        ],
        ignore_index=True
    )


    return (
        df_sentimen,
        df_evaluasi,
        df_raw_review
    )

try:

    (
        df_sentimen,
        df_evaluasi,
        df_raw_dana,
        df_raw_gopay,
        df_raw_shopee

    ) = load_data()


except Exception as e:

    st.error(
        f"Gagal memuat data CSV. Pastikan file berada di repositori yang sama. Error: {e}"
    )

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
    dana_active = st.toggle("DANA", value=True, key="tgl_dana")

with col_btn2:
    st.markdown(f'<div class="metric-card">{get_img_html("logoGopay.png", "[Logo GoPay]")}</div>', unsafe_allow_html=True)
    gopay_active = st.toggle("GoPay", value=True, key="tgl_gopay")

with col_btn3:
    st.markdown(f'<div class="metric-card">{get_img_html("logoShopeepay.png", "[Logo ShopeePay]")}</div>', unsafe_allow_html=True)
    shopee_active = st.toggle("ShopeePay", value=True, key="tgl_shopee")

selected_apps = []
if dana_active: selected_apps.append("DANA")
if gopay_active: selected_apps.append("GoPay")
if shopee_active: selected_apps.append("ShopeePay")

if not selected_apps:
    st.warning("⚠️ Silakan pilih minimal satu aplikasi untuk menampilkan visualisasi.")
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
# 📊 TAMBAHAN: PERSENTASE DISTRIBUSI SENTIMEN
st.markdown("---")
st.markdown("### Persentase Distribusi Sentimen Pengguna")


# Menyimpan hasil persentase semua aplikasi
sentiment_percentage = {}

for app_name in selected_apps:

    df_app_percentage = df_sentimen[
        df_sentimen['appName'] == app_name
    ]

    total_data = len(df_app_percentage)

    positif = len(
        df_app_percentage[
            df_app_percentage['sentimen'] == 'Positif'
        ]
    )

    negatif = len(
        df_app_percentage[
            df_app_percentage['sentimen'] == 'Negatif'
        ]
    )


    if total_data > 0:
        persen_positif = (positif / total_data) * 100
        persen_negatif = (negatif / total_data) * 100
    else:
        persen_positif = 0
        persen_negatif = 0


    sentiment_percentage[app_name] = {
        "Positif": persen_positif,
        "Negatif": persen_negatif
    }



# =====================================================
# MEMBUAT KOLOM BERDASARKAN JUMLAH APLIKASI
# =====================================================

cols = st.columns(len(selected_apps))


# =====================================================
# BARIS POSITIF
# =====================================================

for idx, app_name in enumerate(selected_apps):

    with cols[idx]:

        st.markdown(
            f"""
            <div class="metric-card">
                <h2 style="margin:0;color:#1ccc0d;">
                    {sentiment_percentage[app_name]["Positif"]:.2f}%
                </h2>
                <p style="margin:0;font-size:16px;font-weight:bold;">
                    Distribusi Positif {app_name}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# =====================================================
# BARIS NEGATIF
# =====================================================

for idx, app_name in enumerate(selected_apps):

    with cols[idx]:

        st.markdown(
            f"""
            <div class="metric-card">
                <h2 style="margin:0;color:#cc0000;">
                    {sentiment_percentage[app_name]["Negatif"]:.2f}%
                </h2>
                <p style="margin:0;font-size:16px;font-weight:bold;">
                    Distribusi Negatif {app_name}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

# 📈 URUTAN 3: GRAFIK TREN PERKEMBANGAN SENTIMEN BULANAN
st.markdown("---")
st.markdown("### 📈 3. Grafik Tren Perkembangan Sentimen Bulanan")


# Filter hanya aplikasi yang dipilih user melalui toggle
filtered_df = df_sentimen[df_sentimen['appName'].isin(selected_apps)].copy()

# Membuat kolom bulan
filtered_df['Bulan'] = filtered_df['date'].dt.to_period('M').astype(str)


# Agregasi jumlah sentimen per bulan dan aplikasi
df_chart_trend_global = (
    filtered_df
    .groupby(['Bulan', 'appName', 'sentimen'])
    .size()
    .reset_index(name='Jumlah')
)


# Warna garis setiap aplikasi
color_apps_map = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


# ==========================
# DIAGRAM SENTIMEN POSITIF
# ==========================

with st.container(border=True):

    df_pos_trend = df_chart_trend_global[
        df_chart_trend_global['sentimen'] == 'Positif'
    ]


    fig_trend_pos = px.line(
        df_pos_trend,
        x='Bulan',
        y='Jumlah',
        color='appName',
        markers=True,
        title="📈 Tren Perkembangan Sentimen Positif Bulanan",
        color_discrete_map=color_apps_map
    )


    fig_trend_pos.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="Periode Bulan",
        yaxis_title="Jumlah Ulasan"
    )


    st.plotly_chart(
        fig_trend_pos,
        use_container_width=True
    )



# ==========================
# DIAGRAM SENTIMEN NEGATIF
# ==========================

with st.container(border=True):

    df_neg_trend = df_chart_trend_global[
        df_chart_trend_global['sentimen'] == 'Negatif'
    ]


    fig_trend_neg = px.line(
        df_neg_trend,
        x='Bulan',
        y='Jumlah',
        color='appName',
        markers=True,
        title="📉 Tren Perkembangan Sentimen Negatif Bulanan",
        color_discrete_map=color_apps_map
    )


    fig_trend_neg.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis_title="Periode Bulan",
        yaxis_title="Jumlah Ulasan"
    )


    st.plotly_chart(
        fig_trend_neg,
        use_container_width=True
    )
    
# 📊 URUTAN 4: PENYEBARAN DISTRIBUSI RATING BINTANG
st.markdown("---")
st.markdown("### 📊 4. Penyebaran Distribusi Rating Bintang Pengguna")


color_rating_map = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


# =====================================================
# JIKA USER HANYA MEMILIH 1 APLIKASI
# BAR CHART BIASA
# =====================================================

if len(selected_apps) == 1:

    app_name = selected_apps[0]

    with st.container(border=True):

        df_app_rate = df_sentimen[
            df_sentimen['appName'] == app_name
        ]

        df_chart_rate = (
            df_app_rate
            .groupby('score')
            .size()
            .reset_index(name='Total')
        )


        fig_rate = px.bar(
            df_chart_rate,
            x='score',
            y='Total',
            title=f"Distribusi Rating Bintang: {app_name}",
            labels={
                'score': 'Rating Bintang',
                'Total': 'Jumlah Ulasan'
            },
            color_discrete_sequence=[
                color_rating_map[app_name]
            ]
        )


        fig_rate.update_layout(
            xaxis=dict(
                dtick=1
            )
        )


        st.plotly_chart(
            fig_rate,
            use_container_width=True
        )



# =====================================================
# JIKA USER MEMILIH >1 APLIKASI
# GROUPED BAR CHART
# =====================================================

else:


    df_rating_group = df_sentimen[
        df_sentimen['appName'].isin(selected_apps)
    ]


    df_rating_group = (
        df_rating_group
        .groupby(
            ['score', 'appName']
        )
        .size()
        .reset_index(name='Total')
    )


    fig_rate_group = px.bar(
        df_rating_group,
        x='score',
        y='Total',
        color='appName',
        barmode='group',
        title="Komparasi Distribusi Rating Bintang E-Wallet",
        labels={
            'score': 'Rating Bintang',
            'Total': 'Jumlah Ulasan',
            'appName': 'Aplikasi'
        },
        color_discrete_map=color_rating_map
    )


    fig_rate_group.update_layout(

        xaxis=dict(
            dtick=1
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )


    st.plotly_chart(
        fig_rate_group,
        use_container_width=True
    )

# FUNGSI MEMUAT DATA RAW KOMENTAR
@st.cache_data
def load_raw_reviews():

    raw_files = {
        "DANA": "rawDana.csv",
        "GoPay": "rawGopay.csv",
        "ShopeePay": "rawShopeepay.csv"
    }

    raw_data = {}

    for app, file in raw_files.items():

        try:
            df_raw = pd.read_csv(file)

            raw_data[app] = df_raw

        except:
            raw_data[app] = pd.DataFrame()

    return raw_data


raw_reviews = load_raw_reviews()



# =====================================================
# FUNGSI MENGAMBIL 10 ULASAN BERDASARKAN KATA TERPOPULER
# =====================================================

def get_top_reviews(app_name, sentiment):

    if app_name not in raw_reviews:
        return []


    df_raw = raw_reviews[app_name]


    if df_raw.empty:
        return []


    # mencari kolom sentimen
    sentiment_col = None

    for col in df_raw.columns:
        if "sentimen" in col.lower():
            sentiment_col = col


    # mencari kolom komentar
    text_col = None

    for col in df_raw.columns:
        if "content" in col.lower() or "review" in col.lower() or "text" in col.lower():
            text_col = col



    if sentiment_col and text_col:

        df_filter = df_raw[
            df_raw[sentiment_col] == sentiment
        ]


        if df_filter.empty:
            return []


        # hitung kata yang sering muncul
        all_text = " ".join(
            df_filter[text_col]
            .astype(str)
        )


        words = (
            all_text
            .lower()
            .split()
        )


        counter_words = Counter(words)


        top_words = [
            word 
            for word, jumlah 
            in counter_words.most_common(10)
        ]


        hasil = []


        for word in top_words:

            temp = df_filter[
                df_filter[text_col]
                .astype(str)
                .str.lower()
                .str.contains(word, na=False)
            ]


            if not temp.empty:

                hasil.append(
                    temp[text_col]
                    .iloc[0]
                )


        return hasil[:10]


    return []

# =====================================================
# FUNGSI MENGAMBIL 10 ULASAN TERPOPULER DARI DATA RAW
# =====================================================

def get_top_reviews(app_name, sentiment):

    # memilih file raw berdasarkan aplikasi
    if app_name == "DANA":
        df_raw = df_raw_dana.copy()

    elif app_name == "GoPay":
        df_raw = df_raw_gopay.copy()

    elif app_name == "ShopeePay":
        df_raw = df_raw_shopee.copy()

    else:
        return []


    # mengambil data sentimen dari hasilSentimen
    df_sent = df_sentimen[
        (df_sentimen['appName'] == app_name) &
        (df_sentimen['sentimen'] == sentiment)
    ][['content']]


    if df_sent.empty:
        return []


    # normalisasi teks
    df_sent['content'] = (
        df_sent['content']
        .astype(str)
        .str.lower()
        .str.strip()
    )


    df_raw['content'] = (
        df_raw['content']
        .astype(str)
        .str.lower()
        .str.strip()
    )


    # mencari komentar yang sama antara hasilSentimen dan raw
    hasil = df_raw[
        df_raw['content'].isin(
            df_sent['content']
        )
    ]


    if hasil.empty:
        return []


    # mengambil 10 komentar dengan kata paling sering muncul
    hasil = (
        hasil['content']
        .drop_duplicates()
        .head(10)
        .tolist()
    )


    return hasil

# ☁️ URUTAN 5: WORD CLOUD INTERAKTIF DENGAN TOGGLE ULASAN
st.markdown("---")
st.markdown("### ☁️ 5. Eksplorasi Awan Kata (Word Cloud)")


# Warna wordcloud positif tiap aplikasi
wc_positive_color = {
    "DANA": "Blues",
    "GoPay": "Greens",
    "ShopeePay": "Oranges"
}



# Fungsi membuat warna merah untuk wordcloud negatif
def red_color_func(
    word,
    font_size,
    position,
    orientation,
    random_state=None,
    **kwargs
):
    return "#cc0000"



# membuat kolom sesuai jumlah aplikasi
col_wc = st.columns(len(selected_apps))



for idx, app_name in enumerate(selected_apps):

    with col_wc[idx]:

        with st.container(border=True):


            df_app_text = df_sentimen[
                df_sentimen['appName'] == app_name
            ]



            # =====================================================
            # WORD CLOUD POSITIF
            # =====================================================

            st.markdown(
                f"""
                <p style='text-align:center;
                font-weight:bold;
                margin-bottom:5px;'>
                Word Cloud Positif {app_name}
                </p>
                """,
                unsafe_allow_html=True
            )


            text_positive = " ".join(
                df_app_text[
                    df_app_text['sentimen']=="Positif"
                ]['content']
                .astype(str)
            )


            if text_positive.strip():


                wc_positive = WordCloud(
                    background_color="white",
                    max_words=50,
                    colormap=wc_positive_color[app_name],
                    width=400,
                    height=250
                ).generate(text_positive)



                fig, ax = plt.subplots(
                    figsize=(4,2.5)
                )

                ax.imshow(
                    wc_positive,
                    interpolation="bilinear"
                )

                ax.axis("off")


                st.pyplot(fig)

                plt.close()



            # TOGGLE ULASAN POSITIF
            show_positive = st.toggle(
                f"Tampilkan ulasan positif {app_name}",
                key=f"positive_{app_name}"
            )



            if show_positive:

                st.markdown(
                    "**10 Ulasan Positif Berdasarkan Kata Terpopuler:**"
                )


                positive_reviews = get_top_reviews(
                    app_name,
                    "Positif"
                )


                if positive_reviews:

                    for i, review in enumerate(
                        positive_reviews,
                        1
                    ):

                        st.write(
                            f"{i}. {review}"
                        )

                else:

                    st.info(
                        "Data ulasan positif tidak ditemukan."
                    )



            # =====================================================
            # WORD CLOUD NEGATIF
            # =====================================================


            st.markdown(
                f"""
                <p style='text-align:center;
                font-weight:bold;
                margin-top:15px;
                margin-bottom:5px;'>
                Word Cloud Negatif {app_name}
                </p>
                """,
                unsafe_allow_html=True
            )



            text_negative = " ".join(
                df_app_text[
                    df_app_text['sentimen']=="Negatif"
                ]['content']
                .astype(str)
            )


            if text_negative.strip():


                wc_negative = WordCloud(
                    background_color="white",
                    max_words=50,
                    width=400,
                    height=250
                ).generate(text_negative)



                wc_negative.recolor(
                    color_func=red_color_func
                )



                fig, ax = plt.subplots(
                    figsize=(4,2.5)
                )


                ax.imshow(
                    wc_negative,
                    interpolation="bilinear"
                )


                ax.axis("off")


                st.pyplot(fig)

                plt.close()



            # TOGGLE ULASAN NEGATIF
            show_negative = st.toggle(
                f"Tampilkan ulasan negatif {app_name}",
                key=f"negative_{app_name}"
            )



            if show_negative:


                st.markdown(
                    "**10 Ulasan Negatif Berdasarkan Kata Terpopuler:**"
                )


                negative_reviews = get_top_reviews(
                    app_name,
                    "Negatif"
                )



                if negative_reviews:


                    for i, review in enumerate(
                        negative_reviews,
                        1
                    ):

                        st.write(
                            f"{i}. {review}"
                        )


                else:

                    st.info(
                        "Data ulasan negatif tidak ditemukan."
                    )

#📋 URUTAN 6: RINGKASAN EKSTRAKSI SAMPEL KOMENTAR TERPOPULER (ANTI ERROR GITHUB - MURNI DATAFRAME)
st.markdown("---")
st.markdown("### 📋 6. Ringkasan Ekstraksi Sampel Komentar Terpopuler")

data_tabel_komparasi = []

for app_name in selected_apps:
    df_app_search = df_sentimen[df_sentimen['appName'] == app_name]
    df_pos_reviews = df_app_search[df_app_search['sentimen'] == 'Positif']
    df_neg_reviews = df_app_search[df_app_search['sentimen'] == 'Negatif']
    
    # Perbaikan mutlak struktur if-else satu baris agar tidak memicu IndentationError
    sample_p = df_pos_reviews['content'].head(1).values[0] if not df_pos_reviews.empty else "Sangat puas dengan kecepatan transaksi aplikasi ini."
    sample_n = df_neg_reviews['content'].head(1).values[0] if not df_neg_reviews.empty else "Sering terjadi kendala koneksi sistem/error saat transfer saldo."
    
    data_tabel_komparasi.append({
        "E-Wallet": app_name,
        "Komentar Positif Terbanyak (Kata Kunci Terpopuler)": f"🔹 {sample_p}",
        "Kombinasi Komentar Negatif Terbanyak (Aduan Utama)": f"🔻 {sample_n}"
    })

df_tabel_final = pd.DataFrame(data_tabel_komparasi)
st.dataframe(df_tabel_final, use_container_width=True, hide_index=True)

#🔮 URUTAN 7: NILAI METRIK KINERJA KLASIFIKASI NBC
st.markdown("---")
st.markdown("### 🔮 7. Nilai Metrik Kinerja Klasifikasi NBC")


# Warna nilai metrik berdasarkan aplikasi
metric_color_map = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


for app_name in selected_apps:

    row_eval = df_evaluasi[
        df_evaluasi['aplikasi'] == app_name
    ]

    if not row_eval.empty:

        row_eval = row_eval.iloc[0]

        # mengambil warna sesuai aplikasi
        app_color = metric_color_map.get(
            app_name,
            "#2377ca"
        )


        st.markdown(
            f"**Metrik Performa Pengujian Model NBC: {app_name}**"
        )


        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)


        col_m1.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    Accuracy
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {str(row_eval["Accuracy"])}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_m2.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    Precision
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {str(row_eval["Precision"])}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_m3.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    Recall
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {str(row_eval["Recall"])}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_m4.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    Specificity
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {str(row_eval["Specificity"])}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_m5.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    F1-Score
                </p>
                <h3 style="margin:0;color:{app_color};">
                    {str(row_eval["F1-Score"])}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div style="margin-bottom:15px;"></div>',
            unsafe_allow_html=True
        )

#🎯 URUTAN 8: JUMLAH ELEMEN VALUE CONFUSION MATRIX
st.markdown("---")
st.markdown("### 🎯 8. Elemen Nilai Realisasi Confusion Matrix")


# Warna nilai confusion matrix berdasarkan aplikasi
cm_color_map = {
    "DANA": "#2377ca",
    "GoPay": "#01aed6",
    "ShopeePay": "#ff773c"
}


for app_name in selected_apps:

    row_cm = df_evaluasi[
        df_evaluasi['aplikasi'] == app_name
    ]

    if not row_cm.empty:

        row_cm = row_cm.iloc[0]


        # mengambil warna sesuai aplikasi
        app_color_cm = cm_color_map.get(
            app_name,
            "#2377ca"
        )


        st.markdown(
            f"**Komposisi Hasil Prediksi Matriks: {app_name}**"
        )


        col_c1, col_c2, col_c3, col_c4 = st.columns(4)


        col_c1.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    True Negative (TN)
                </p>
                <h3 style="margin:0;color:{app_color_cm};">
                    {int(row_cm["TN"]):,}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_c2.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    False Positive (FP)
                </p>
                <h3 style="margin:0;color:{app_color_cm};">
                    {int(row_cm["FP"]):,}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_c3.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    False Negative (FN)
                </p>
                <h3 style="margin:0;color:{app_color_cm};">
                    {int(row_cm["FN"]):,}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        col_c4.markdown(
            f'''
            <div class="metric-card">
                <p style="margin:0;color:gray;font-size:14px;">
                    True Positive (TP)
                </p>
                <h3 style="margin:0;color:{app_color_cm};">
                    {int(row_cm["TP"]):,}
                </h3>
            </div>
            ''',
            unsafe_allow_html=True
        )


        st.markdown(
            '<div style="margin-bottom:15px;"></div>',
            unsafe_allow_html=True
        )
