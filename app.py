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

# Menggabungkan seluruh korpus teks dari aplikasi terpilih
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
    df_top_kata = pd.DataFrame(top_5_words_tuples, columns=['Kata / Leksikon', 'Frekuensi Kemunculan'])
    st.dataframe(df_top_kata, use_container_width=True)
    
    st.markdown("**🕵️‍♂️ Detektif Ulasan Mentah Akhir Periode (Tahun 2026)**")
    pilihan_kata_user = st.selectbox("Pilih salah satu kata dominan untuk diekstraksi ulasan aslinya:", options=top_5_words)

# =====================================================================
# I. FITUR EKSTRAKSI 10 KOMENTAR MENTAH BERDASARKAN KATA KUNCI
# =====================================================================
if pilihan_kata_user:
    st.markdown(f"**10 Ulasan Mentah Terakhir (2026) yang Mengandung Kata: *'{pilihan_kata_user}'***")
    
    # Mencari ulasan mentah yang mengandung kata pilihan user
    raw_matches = filtered_df[filtered_df['content'].astype(str).str.contains(pilihan_kata_user, case=False, na=False)]
    
    # Mengurutkan berdasarkan tanggal terbaru kronologis mundur di tahun 2026
    raw_matches_sorted = raw_matches.sort_values(by='date', ascending=False)
    
    if not raw_matches_sorted.empty:
        sample_reviews = raw_matches_sorted[['date', 'appName', 'score', 'sentimen', 'content']].head(10).reset_index(drop=True)
        st.dataframe(sample_reviews, use_container_width=True)
    else:
        st.write("Tidak ditemukan contoh ulasan spesifik yang mengandung kata tersebut.")
