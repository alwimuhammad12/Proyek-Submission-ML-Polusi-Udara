import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import folium
import xlsxwriter
from datetime import datetime
from streamlit_folium import st_folium
from PIL import Image
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# =========================
# KONFIGURASI DASAR
# =========================
st.set_page_config(
    page_title="Beijing Air Pollution Dashboard (2013 - 2017)",
    layout="wide",
    page_icon="🌫️"
)

# =========================
# CSS CUSTOM (Skema Warna)
# =========================
st.markdown("""
    <style>
    .stApp {
        background-color: #F8F3D9;
        color: #504B38;
        font-family: 'Open Sans', sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #504B38;
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    .stRadio label {
        color: #FFFFFF !important;
    }
    header[data-testid="stHeader"] {
        background-color: #EBE5C2;
        color: #504B38;
        box-shadow: none;
    }
    header[data-testid="stHeader"] * {
        color: #504B38 !important;
    }
    h1, h2, h3, h4, p, li {
        color: #504B38 !important;
    }
    div[data-testid="stMetricValue"] {
        color: #504B38 !important;
    }
    [data-testid="stHeaderDropdownMenu"] {
        background-color: #504B38 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stHeaderDropdownMenu"] * {
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATASET
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/combined_data.csv')
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df

df = load_data()

# =========================
# SIDEBAR NAVIGASI
# =========================
st.sidebar.title("🌏 Navigasi")
pages = [
    "Beranda",
    "Metrik Utama",
    "Tren & Visualisasi",
    "Faktor Cuaca",
    "Peta Geospasial",
    "Analisis Lanjutan"
]
page = st.sidebar.radio("Pilih Halaman:", pages)

# =========================
# HALAMAN: BERANDA
# =========================
if page == "Beranda":
    st.title("Beijing Air Pollution Dashboard (2013 - 2017)")
    st.write("""
    Selamat datang di **Dashboard Analisis Polusi Udara Beijing**!

    📌 **Fitur-fitur Utama**:
    - **Metrik Utama**: Menyajikan ringkasan data kualitas udara (PM2.5, PM10) dan kondisi cuaca.
    - **Tren & Visualisasi**: Menampilkan distribusi dan tren polusi udara di berbagai stasiun pengamatan.
    - **Faktor Cuaca**: Menganalisis hubungan antara kondisi cuaca (suhu, kecepatan angin) dengan tingkat polusi.
    - **Peta Geospasial**: Memvisualisasikan lokasi stasiun pemantauan dan sebaran rata-rata PM2.5.
    - **Analisis Lanjutan**: Menyediakan analisis clustering untuk mendeteksi pola polusi udara.

    🎯 **Tujuan Dashboard Ini**:
    - Memberikan **gambaran menyeluruh** tentang kondisi kualitas udara di Beijing selama periode 2013 - 2017.
    - Mendukung **pengambilan keputusan** terkait pengendalian polusi dan perencanaan kebijakan lingkungan berbasis data.

    """)
    st.image(
        "https://cdn.pixabay.com/photo/2016/05/27/16/55/smog-1420443_1280.jpg",
        caption="Polusi Udara di Beijing",
        use_container_width=True
    )

# =========================
# HALAMAN: METRIK UTAMA
# =========================
elif page == "Metrik Utama":
    st.title("📈 Metrik Utama")

    st.markdown("""
        Halaman **Metrik Utama** memberikan ringkasan statistik tahunan dan bulanan mengenai kualitas udara dan faktor cuaca di Beijing.
        Pilih tahun pada panel samping untuk mengeksplorasi rata-rata PM2.5, PM10, suhu, dan kecepatan angin.
    """)

    tahun_tersedia = sorted(df['year'].unique())
    tahun_pilihan = st.sidebar.selectbox("Pilih Tahun:", tahun_tersedia)

    df2 = df[df['year'] == tahun_pilihan].copy()
    df2['date'] = pd.to_datetime(df2['date'])
    df2.set_index('date', inplace=True)

    numeric_cols = ['PM2.5', 'PM10', 'TEMP', 'WSPM']
    monthly_mean = df2[numeric_cols].resample('M').mean()

    st.markdown(f"""
        **Rangkuman Tahunan untuk Tahun {tahun_pilihan}**
        
        Berikut adalah nilai rata-rata tahunan dari konsentrasi polusi udara dan faktor cuaca yang diperoleh dari agregasi data bulanan.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("PM2.5 (µg/m³)", f"{monthly_mean['PM2.5'].mean():.2f}")
        st.metric("PM10 (µg/m³)", f"{monthly_mean['PM10'].mean():.2f}")
    with col2:
        st.metric("Suhu Rata-rata (°C)", f"{monthly_mean['TEMP'].mean():.2f}")
        st.metric("Kecepatan Angin (m/s)", f"{monthly_mean['WSPM'].mean():.2f}")

    st.write("---")

    st.subheader("Data PM2.5 Terbaru")
    st.markdown(f"""
        Tabel berikut menampilkan **5 pengukuran PM2.5 terbaru** dari tahun {tahun_pilihan}.
        Data ini juga mencakup informasi terkait PM10, suhu, dan kecepatan angin.
    """)

    df_latest = df2.sort_values(by='date', ascending=False).head(5).reset_index()

    st.dataframe(df_latest[['date', 'station', 'PM2.5', 'PM10', 'TEMP', 'WSPM']])

    csv = df_latest.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Data", csv, "data_pm25.csv", "text/csv")

    if monthly_mean['PM2.5'].dropna().empty:
        st.warning(f"Tidak ada data PM2.5 untuk tahun {tahun_pilihan}")
    else:
        df_chart = monthly_mean[['PM2.5']].reset_index()
        fig = px.line(df_chart, x='date', y='PM2.5',
                      title=f'Tren Bulanan PM2.5 Tahun {tahun_pilihan}',
                      markers=True)
        fig.update_layout(xaxis_title='Bulan', yaxis_title='PM2.5 (µg/m³)')
        st.plotly_chart(fig)

# =========================
# HALAMAN: TREN & VISUALISASI
# =========================
elif page == "Tren & Visualisasi":
    st.title("📊 Tren & Visualisasi Polusi")

    st.markdown("""
        Analisis tren jangka panjang dan distribusi polusi udara **PM2.5** & **PM10** berdasarkan **stasiun pemantauan** dan **tahun** yang dipilih.
        Anda juga dapat mengunduh data untuk kebutuhan analisis lanjutan.
    """)

    stations = df['station'].unique().tolist()
    stasiun_pilihan = st.sidebar.selectbox("Pilih Stasiun:", stations)

    tahun_tersedia = sorted(df['year'].unique())
    tahun_pilihan = st.sidebar.selectbox("Pilih Tahun:", tahun_tersedia)

    df_filtered = df[(df['station'] == stasiun_pilihan) & (df['year'] == tahun_pilihan)].copy()

    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk stasiun dan tahun yang dipilih.")
    else:
        st.subheader(f"Distribusi PM2.5 & PM10 - {stasiun_pilihan} ({tahun_pilihan})")

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['PM2.5'], bins=30, color='skyblue', ax=ax)
            ax.set_title("Distribusi PM2.5")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['PM10'], bins=30, color='salmon', ax=ax)
            ax.set_title("Distribusi PM10")
            st.pyplot(fig)

        st.subheader("⬇️ Unduh Data Distribusi PM2.5 & PM10")
        st.markdown(f"""
            Klik tombol berikut untuk mengunduh data distribusi **PM2.5** dan **PM10** dari **{stasiun_pilihan}** pada tahun **{tahun_pilihan}**.
        """)

        df_download = df_filtered[['PM2.5', 'PM10']].dropna()

        import io
        csv_buffer = io.BytesIO()
        df_download.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer,
            file_name=f'Distribusi_PM25_PM10_{stasiun_pilihan}_{tahun_pilihan}.csv',
            mime='text/csv'
        )

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            df_download.to_excel(writer, index=False, sheet_name='Distribusi_PM')

        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name=f'Distribusi_PM25_PM10_{stasiun_pilihan}_{tahun_pilihan}.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        st.subheader("📈 Tren Bulanan PM2.5 & PM10")
        st.markdown(f"""
            Grafik di bawah ini menunjukkan **rata-rata bulanan PM2.5 dan PM10** di **{stasiun_pilihan}** selama tahun **{tahun_pilihan}**.
            Data ini membantu mengidentifikasi bulan-bulan dengan tingkat polusi tinggi.
        """)

        df_filtered['date'] = pd.to_datetime(df_filtered[['year', 'month', 'day', 'hour']])
        df_filtered.set_index('date', inplace=True)

        monthly_trend = df_filtered.resample('M').mean(numeric_only=True)

        st.line_chart(monthly_trend[['PM2.5', 'PM10']])

        df_filtered.reset_index(inplace=True)

# =========================
# HALAMAN: FAKTOR CUACA
# =========================
elif page == "Faktor Cuaca":
    st.title("🌤️ Faktor Cuaca & Polusi Udara")

    st.markdown("""
        Halaman ini menganalisis **hubungan antara faktor cuaca** seperti **suhu (TEMP)** dan **kecepatan angin (WSPM)** terhadap **tingkat polusi udara PM2.5** di Beijing.

        📊 Dengan visualisasi **scatter plot**, kamu bisa mengamati apakah ada korelasi atau pola yang konsisten antara cuaca dan kualitas udara.
    """)

    stations = df['station'].unique().tolist()
    stasiun_pilihan = st.sidebar.selectbox("Pilih Stasiun:", stations, key="faktor_cuaca_stasiun")

    df_filtered = df[df['station'] == stasiun_pilihan].copy()

    if df_filtered.empty:
        st.warning("Data tidak tersedia untuk stasiun yang dipilih.")
    else:
        st.subheader(f"Hubungan PM2.5 dengan Suhu dan Kecepatan Angin - {stasiun_pilihan}")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.scatter(df_filtered, x='TEMP', y='PM2.5',
                             trendline="ols",
                             labels={"TEMP": "Suhu (°C)", "PM2.5": "PM2.5 (µg/m³)"},
                             title=f"PM2.5 vs Suhu ({stasiun_pilihan})")
            st.plotly_chart(fig)

        with col2:
            fig = px.scatter(df_filtered, x='WSPM', y='PM2.5',
                             trendline="ols",
                             labels={"WSPM": "Kecepatan Angin (m/s)", "PM2.5": "PM2.5 (µg/m³)"},
                             title=f"PM2.5 vs Kecepatan Angin ({stasiun_pilihan})")
            st.plotly_chart(fig)

        st.markdown("""
            ✅ **Insight Awal**:
            - Perhatikan apakah **peningkatan kecepatan angin** berhubungan dengan **penurunan konsentrasi PM2.5**.
            - Lihat apakah **suhu ekstrem** (tinggi/rendah) mempengaruhi peningkatan polusi udara.
        """)

# =========================
# HALAMAN: PETA GEOSPASIAL
# =========================
elif page == "Peta Geospasial":
    st.title("🌍 Peta Geospasial Polusi Udara di Beijing")

    # ➕ Penjelasan awal halaman
    st.markdown("""
    Halaman ini menampilkan **lokasi stasiun pemantauan kualitas udara** di Beijing.  
    📍 Warna dan ukuran lingkaran menunjukkan tingkat **rata-rata konsentrasi PM2.5** yang tercatat oleh masing-masing stasiun.  
    ➡️ Gunakan **filter tahun** di sebelah kiri untuk menganalisis data pada periode waktu tertentu.
    """)

    # =========================
    # ➕ FILTER TAHUN
    # =========================
    tahun_tersedia = sorted(df['year'].unique())
    tahun_pilihan = st.sidebar.selectbox("Pilih Tahun untuk Peta Geospasial:", tahun_tersedia)

    # =========================
    # ➕ FILTER DATAFRAME BERDASARKAN TAHUN
    # =========================
    df_filtered = df[df['year'] == tahun_pilihan].copy()

    # =========================
    # ➕ RATA-RATA PM2.5 PER STASIUN UNTUK TAHUN YANG DIPILIH
    # =========================
    avg_pm25_station = df_filtered.groupby('station')['PM2.5'].mean()

    # =========================
    # ➕ KOORDINAT STASIUN (MANUAL DICTIONARY)
    # =========================
    station_coords = {
        'Aotizhongxin': [39.982, 116.497],
        'Changping': [40.218, 116.231],
        'Dingling': [40.292, 116.225],
        'Dongsi': [39.929, 116.417],
        'Guanyuan': [39.933, 116.366],
        'Gucheng': [39.937, 116.287],
        'Huairou': [40.36, 116.631],
        'Nongzhanguan': [39.933, 116.461],
        'Shunyi': [40.125, 116.654],
        'Tiantan': [39.873, 116.413],
        'Wanliu': [39.999, 116.325],
        'Wanshouxigong': [39.882, 116.344]
    }

    # =========================
    # ➕ FUNGSI UNTUK WARNA MARKER BERDASARKAN NILAI PM2.5
    # =========================
    def color_pm25(val):
        if val < 70:
            return 'green'
        elif val < 100:
            return 'orange'
        else:
            return 'red'

    # =========================
    # ➕ PETA FOLIUM DENGAN LOKASI TENGAH BEIJING
    # =========================
    m = folium.Map(location=[39.9, 116.4], zoom_start=10, tiles='CartoDB positron')

    # =========================
    # ➕ LOOPING MENAMBAHKAN CIRCLEMARKER UNTUK MASING-MASING STASIUN
    # =========================
    for stn, coords in station_coords.items():
        pm_val = avg_pm25_station.get(stn, 0)

        # ➕ CircleMarker dinamis
        folium.CircleMarker(
            location=coords,
            radius=8 + pm_val / 20,  # radius menyesuaikan PM2.5
            popup=folium.Popup(f"<b>{stn}</b><br>PM2.5: {pm_val:.2f} µg/m³", max_width=250),
            color=color_pm25(pm_val),
            fill=True,
            fill_color=color_pm25(pm_val),
            fill_opacity=0.7
        ).add_to(m)

    # =========================
    # ➕ LEGEND CUSTOM
    # =========================
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; width: 200px; height: 130px; 
        background-color: white; 
        border:2px solid grey; 
        z-index:9999; 
        font-size:14px;
        padding: 10px;
        ">
        <b>Legend - PM2.5 (µg/m³)</b><br>
        <i style="background:green;width:12px;height:12px;display:inline-block;"></i> &lt; 70 (Baik)<br>
        <i style="background:orange;width:12px;height:12px;display:inline-block;"></i> 70 - 100 (Sedang)<br>
        <i style="background:red;width:12px;height:12px;display:inline-block;"></i> &gt; 100 (Tinggi)<br>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # =========================
    # ➕ TAMPILKAN PETA DI STREAMLIT
    # =========================
    st_data = st_folium(m, width=900, height=600)

    # =========================
    # ➕ TAMPILKAN TABEL DATA RATA-RATA (OPSIONAL)
    # =========================
    st.markdown(f"### 📋 Rata-rata PM2.5 per Stasiun (Tahun {tahun_pilihan})")

    df_summary = avg_pm25_station.reset_index().rename(columns={'PM2.5': 'Rata-rata PM2.5 (µg/m³)'})
    st.dataframe(df_summary.style.format({'Rata-rata PM2.5 (µg/m³)': '{:.2f}'}))

    # =========================
    # ➕ TOMBOL DOWNLOAD CSV DATA
    # =========================
    csv = df_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv,
        file_name=f"rata_rata_pm25_{tahun_pilihan}.csv",
        mime='text/csv'
    )

    # =========================
    # ➕ PENJELASAN BAWAH
    # =========================
    st.markdown("""
    ✅ **Cara membaca peta**:
    - **Warna lingkaran** menunjukkan kategori tingkat polusi:
        - 🟢 **Hijau**: Baik
        - 🟠 **Oranye**: Sedang
        - 🔴 **Merah**: Tinggi  
    - **Ukuran lingkaran** bertambah besar seiring meningkatnya nilai PM2.5.  
    👉 **Klik** pada marker untuk melihat detail nilai PM2.5 per stasiun.
    """)

# =========================
# HALAMAN: ANALISIS LANJUTAN
# =========================
elif page == "Analisis Lanjutan":
    st.title("🔬 Analisis Lanjutan - Clustering Kualitas Udara")

    st.markdown("""
        Di halaman ini, kita melakukan **klasterisasi data polusi udara** berdasarkan **faktor PM2.5, PM10, Suhu, dan Kecepatan Angin**.

        🎯 Tujuan dari analisis ini adalah untuk mengelompokkan kondisi udara di Beijing menjadi beberapa **cluster** berdasarkan **karakteristik lingkungan dan kualitas udaranya**.
    """)

    df_cluster = df[['PM2.5', 'PM10', 'TEMP', 'WSPM']].dropna().copy()

    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_cluster)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(df_scaled)

    st.subheader("Distribusi Data Berdasarkan Cluster")

    fig = px.scatter_3d(df, x='PM2.5', y='PM10', z='TEMP',
                        color=df['Cluster'].astype(str),
                        labels={"PM2.5": "PM2.5 (µg/m³)", "PM10": "PM10 (µg/m³)", "TEMP": "Suhu (°C)"},
                        title="Klaster Polusi Udara (3D Scatter)")
    st.plotly_chart(fig)

    st.markdown("""
        ✅ **Penjelasan Cluster**:
        - Setiap cluster menunjukkan **kelompok kondisi kualitas udara** yang memiliki **karakteristik berbeda**.
        - Misalnya:
            - Cluster 0: Udara bersih, suhu sedang.
            - Cluster 1: Polusi tinggi, suhu rendah.
            - Cluster 2: Polusi sedang, suhu tinggi.
    """)

    st.subheader("Rata-rata Fitur di Setiap Cluster")

    df_clustered_avg = df.groupby('Cluster').agg({
        'PM2.5': 'mean',
        'PM10': 'mean',
        'TEMP': 'mean',
        'WSPM': 'mean'
    }).reset_index()

    st.dataframe(df_clustered_avg)

    st.markdown("""
        🔍 **Insight dari Analisis**:
        - Cluster dengan **PM2.5 dan PM10 tinggi** bisa menjadi fokus pengendalian polusi.
        - Cluster dengan **kecepatan angin tinggi** mungkin menunjukkan **pengaruh cuaca terhadap difusi polutan**.
    """)

# =========================
# PENUTUP
# =========================
st.sidebar.markdown("""
---
© 2025 - Dashboard Polusi Udara Beijing  
""")
