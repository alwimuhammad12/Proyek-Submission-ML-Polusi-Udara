# 🌏 Dashboard Polusi Udara Beijing (2013 - 2017)

Dashboard ini dibuat menggunakan **Streamlit**.  
Fungsinya untuk menampilkan analisis interaktif terhadap data polusi udara di berbagai stasiun di Beijing dari tahun 2013 sampai 2017.

---

## 📁 Struktur Direktori Project

Proyek Submission Machine Learning Polusi Udara/ ├── app.py ├── data/ │ ├── PRSA_Data_Aotizhongxin_20130301-20170228.csv │ ├── PRSA_Data_Changping_20130301-20170228.csv │ ├── ... (file CSV lainnya) ├── requirements.txt ├── README.md

---

## ✅ Cara Menjalankan Dashboard di Komputer (Lokal)

### 1️⃣ Buka Terminal/Command Prompt  
Pindah ke folder project anda:
cd "Proyek Submission Machine Learning Polusi Udara"

### 2️⃣ Pastikan Python Sudah Terinstall  
Gunakan Python versi 3.8 atau lebih baru: 
python --version

### 3️⃣ (Opsional tapi Disarankan) Buat Virtual Environment  
- Windows
python -m venv venv venv\Scripts\activate

- MacOS/Linux
python3 -m venv venv source venv/bin/activate


### 4️⃣ Install Semua Library yang Dibutuhkan  
Pastikan sudah ada file `requirements.txt`, lalu jalankan:
pip install -r requirements.txt


### 5️⃣ Jalankan Aplikasi Streamlit  
Ketik perintah berikut:
streamlit run dashboard.py


### 6️⃣ Buka di Browser  
Biasanya akan otomatis terbuka, tapi kalau tidak, buka secara manual di browser:
http://localhost:8501


---

## 🌐 Cara Deploy ke Streamlit Community Cloud (Gratis)

### 1️⃣ Upload Folder Project ke GitHub  
Pastikan kamu upload folder `Proyek Submission Machine Learning Polusi Udara` ke repository GitHub-mu.

### 2️⃣ Buka Streamlit Cloud  
Kunjungi halaman:  
[https://streamlit.io/cloud](https://streamlit.io/cloud)

### 3️⃣ Klik Tombol `New App`  
- Pilih repository GitHub yang sudah kamu upload tadi  
- Pilih branch (biasanya `main` atau `master`)  
- Isi nama file utama menjadi:  
Proyek Submission Machine Learning Polusi Udara/dashboard.py

- Klik `Deploy`

### 4️⃣ Tunggu Beberapa Saat  
Setelah selesai, link dashboard kamu akan muncul dan siap dibagikan!

---

## ℹ️ Catatan Tambahan
- Pastikan folder `data/` ada di dalam project dengan file CSV lengkap.  
- Kalau deploy di Streamlit Cloud, pastikan ukuran file `data/` tidak terlalu besar (maksimal 1GB untuk akun gratis).  
- Kalau ada error modul, cek apakah `requirements.txt` sudah lengkap.

---

🎉 Selamat! Dashboard siap dijalankan secara lokal maupun online!
