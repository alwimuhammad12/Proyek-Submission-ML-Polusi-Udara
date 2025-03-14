import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from streamlit_folium import st_folium
import folium

# =========================
# KONFIGURASI DASAR
# =========================
st.set_page_config(
    page_title="Beijing Air Pollution Dashboard (2013 - 2017)",
    layout="wide",
    page_icon="🌫️"
)

# =========================
# CSS CUSTOM (Skema Warna Lebih Baik)
# =========================
st.markdown("""
    <style>
    /* Warna teks umum di konten utama */
    .stApp {
        background-color: #F8F3D9;
        color: #504B38; 
        font-family: 'Open Sans', sans-serif;
    }

    /* Sidebar gelap, teks putih */
    section[data-testid="stSidebar"] {
        background-color: #504B38;
        color: #FFFFFF;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label {
        color: #FFFFFF !important; 
    }
    .stRadio label {
        color: #FFFFFF !important;
    }

    /* Header Streamlit */
    header[data-testid="stHeader"] {
        background-color: #EBE5C2;
        color: #504B38;
        box-shadow: none;
    }
    header[data-testid="stHeader"] * {
        color: #504B38 !important;
    }

    /* Teks heading & paragraf di main page */
    h1, h2, h3, h4, p, li {
        color: #504B38 !important;
    }

    /* Menargetkan nilai di st.metric() */
    div[data-testid="stMetricValue"] {
        color: #504B38 !important;  /* Pastikan warna jadi #504B38 */
    }
    /* Target menu tiga titik (dropdown) */
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
    df = pd.read_csv('data/combined_data.csv')
    # Buat kolom date dari kolom year, month, day, hour
    df['date'] = pd.to_datetime(df[['year','month','day','hour']])
    return df

df = load_data()

# =========================
# SIDEBAR NAVIGASI
# =========================
st.sidebar.title("🌏 Navigasi")
pages = ["Beranda", "Metrik Utama", "Tren & Visualisasi", "Peta Geospasial"]
page = st.sidebar.radio("Pilih Halaman:", pages)

# =========================
# HALAMAN: BERANDA
# =========================
if page == "Beranda":
    st.title("Beijing Air Pollution Dashboard (2013 - 2017)")
    st.write("""
    Selamat datang di **Dashboard Analisis Polusi Udara Beijing**!
    
    **Fitur Utama**:
    - **Metrik Utama**: Lihat ringkasan PM2.5, PM10, dan cuaca
    - **Tren & Visualisasi**: Tampilkan distribusi dan tren polusi
    - **Peta Geospasial**: Periksa lokasi stasiun dan rata-rata PM2.5
    
    **Tujuan**:
    - Memberikan **pandangan menyeluruh** tentang kondisi polusi udara di Beijing.
    - Membantu **mendeteksi area/waktu kritis** untuk pengendalian polusi.
    """)
    st.image(
    "https://cdn.pixabay.com/photo/2016/05/27/16/55/smog-1420443_1280.jpg",
    caption="Polusi Udara di Beijing",
    use_container_width=True)


# =========================
# HALAMAN: METRIK UTAMA
# =========================
elif page == "Metrik Utama":
    st.title("📈 Metrik Utama")

    # Buat ringkasan data bulanan hanya dengan kolom numerik
    df2 = df.copy()
    df2['date'] = pd.to_datetime(df2['date'])
    df2.set_index('date', inplace=True)
    # Pilih kolom numerik yang ingin dihitung rata-ratanya
    numeric_cols = ['PM2.5', 'PM10', 'TEMP', 'WSPM']  # tambahkan kolom numerik lain jika perlu
    monthly_mean = df2[numeric_cols].resample('M').mean()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("PM2.5 Rata-rata")
        pm25_avg = monthly_mean['PM2.5'].mean()
        st.metric("PM2.5 (µg/m³)", f"{pm25_avg:.2f}")

        st.subheader("PM10 Rata-rata")
        pm10_avg = monthly_mean['PM10'].mean()
        st.metric("PM10 (µg/m³)", f"{pm10_avg:.2f}")

    with col2:
        st.subheader("Suhu Rata-rata")
        temp_avg = monthly_mean['TEMP'].mean()
        st.metric("Suhu (°C)", f"{temp_avg:.2f}")

        st.subheader("Kecepatan Angin Rata-rata")
        wspm_avg = monthly_mean['WSPM'].mean()
        st.metric("Wind Speed (m/s)", f"{wspm_avg:.2f}")

    st.write("---")

    st.subheader("Data PM2.5 Terbaru")
    recent_data = df.sort_values(by='date', ascending=False).head(5)
    st.dataframe(recent_data[['date','station','PM2.5','PM10','TEMP','WSPM']])

# =========================
# HALAMAN: TREN & VISUALISASI
# =========================
elif page == "Tren & Visualisasi":
    st.title("📊 Tren & Visualisasi Polusi")

    # Filter stasiun & tahun
    stations = df['station'].unique().tolist()
    stasiun_pilihan = st.sidebar.selectbox("Pilih Stasiun:", stations)
    df_filtered = df[df['station'] == stasiun_pilihan].copy()

    if df_filtered.empty:
        st.warning("Data kosong untuk stasiun ini.")
    else:
        # Distribusi PM2.5 & PM10
        st.subheader(f"Distribusi PM2.5 & PM10 - {stasiun_pilihan}")
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['PM2.5'], bins=30, color='#4A90E2', ax=ax)
            ax.set_title("Distribusi PM2.5")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots()
            sns.histplot(df_filtered['PM10'], bins=30, color='#F5A623', ax=ax)
            ax.set_title("Distribusi PM10")
            st.pyplot(fig)

        # Tren bulanan
        st.subheader("Tren Bulanan")
        # Pastikan 'date' sudah di-set sebagai index dengan tipe datetime
        df_filtered['date'] = pd.to_datetime(df_filtered[['year','month','day','hour']])
        df_filtered.set_index('date', inplace=True)

        # Pilih hanya kolom numerik yang ingin dihitung rata-rata
        numeric_cols = ['PM2.5','PM10']
        monthly_trend = df_filtered[numeric_cols].resample('M').mean()

        st.line_chart(monthly_trend)

        # Setelahnya, reset index jika diperlukan
        df_filtered.reset_index(inplace=True)
        

# =========================
# HALAMAN: PETA GEOSPASIAL
# =========================
elif page == "Peta Geospasial":
    st.title("🌍 Peta Konsentrasi PM2.5")

    # Hitung rata-rata PM2.5 per stasiun
    avg_pm25_station = df.groupby('station')['PM2.5'].mean()

    # Koordinat stasiun
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

    # 3. Perbaikan utama: Inisialisasi peta dengan parameter yang tepat
    m = folium.Map(
        location=[39.9, 116.4],
        zoom_start=10,
        control_scale=True,
        tiles='CartoDB positron',  # Tambahkan tiles eksplisit
        prefer_canvas=True  # Optimalkan rendering
    )

    def color_pm25(val):
        if val < 70:
            return 'green'
        elif val < 100:
            return 'orange'
        else:
            return 'red'

    # Tambahkan marker circle
    for stn, coords in station_coords.items():
        pm_val = avg_pm25_station.get(stn, 0)
        folium.CircleMarker(
            location=coords,
            radius=10,
            popup=f"{stn}: {pm_val:.2f} µg/m³",
            color=color_pm25(pm_val),
            fill=True,
            fill_color=color_pm25(pm_val)
        ).add_to(m)

    # 5. Legend - Simplifikasi tanpa JavaScript
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px;
        z-index: 1000;
        background-color: white;
        padding: 10px;
        border: 2px solid grey;
        border-radius: 5px;
        font-size: 14px;
    ">
        <b>Legend - PM2.5 (µg/m³)</b><br>
        <i style="background:green; width:12px; height:12px; display:inline-block;"></i> < 70<br>
        <i style="background:orange; width:12px; height:12px; display:inline-block;"></i> 70-100<br>
        <i style="background:red; width:12px; height:12px; display:inline-block;"></i> ≥100
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # 6. Tampilkan peta dengan parameter yang diperbaiki
    st_folium(
        m,
        width=700,  # Beri width yang cukup
        height=500, # Height minimal 400-500
        returned_objects=[],
        use_container_width=True
    )