# 📂 Struktur & Fungsi File Proyek

Dokumen ini menjelaskan secara teknis fungsi, logika, dan alur kerja dari setiap file utama dalam proyek ini.

---

## 🐍 1. Kode Utama (Backend & Frontend)

### 🔹 **Streamlit.py** (Main Application)
File ini adalah "wajah" dari aplikasi. Menggunakan library **Streamlit** untuk membangun antarmuka web interaktif tanpa perlu HTML/CSS manual.

*   **Fungsi Utama:**
    *   **Dashboard Page:** Menampilkan laporan interaktif menggunakan **Power BI Embedded** (via `iframe`). URL Power BI bisa dikonfigurasi langsung lewat UI.
    *   **Input Data Page:** Menyediakan form upload file `.xlsx`. Saat file diupload:
        1.  Menyimpan file sementara di folder `data/`.
        2.  Menampilkan preview data mentah.
        3.  Tombol **"⚙️ Proses ETL"**: Memanggil fungsi di `tranform.py`.
        4.  Tombol **"🚀 Upload ke Database"**: Memanggil fungsi di `load.py`.
    *   **Tentang Page:** Informasi versi aplikasi dan kontak support.
*   **Logika Kunci:** Menggunakan `st.session_state` (implisit) untuk menjaga interaksi antar komponen tetap responsif.

### 🔹 **extract.py** (ETL: Extract)
Modul pertama dalam pipeline ETL. Bertugas mengambil data dari sumber aslinya.

*   **Fungsi Utama:**
    *   `extract_data()`: Membaca seluruh file Excel yang ada di folder `data/` menggunakan library `pandas`.
*   **Cara Kerja:**
    *   Mendefinisikan dictionary path file (misal: `jeniskelamin.xlsx`).
    *   Membaca file tersebut menjadi **Pandas DataFrame**.
    *   Mengembalikan dictionary berisi DataFrame mentah untuk diproses oleh tahap selanjutnya.

### 🔹 **tranform.py** (ETL: Transform)
Otak dari sistem ini. Bertugas membersihkan, menstandarisasi, dan merapikan data agar siap masuk database.

*   **Fungsi Utama:**
    *   `transform_all()`: Fungsi orkestrator yang memanggil semua fungsi transformasi spesifik per jenis data.
    *   `benarkan_kata_kecamatan()`: Menggunakan dictionary `replace` untuk memperbaiki typo nama kecamatan (contoh: "semrowo" -> "Asemrowo").
    *   `check_missing_values()`: Audit data untuk mendeteksi `NaN` (nilai kosong).
*   **Logika Transformasi Spesifik:**
    *   **Deteksi Header:** Cerdas membedakan baris header vs sub-header (misal: melewati baris yang berisi teks "Temuan kasus" agar langsung ke data angka).
    *   **Pembersihan Tahun:** Mengubah format "2025 (hingga Juli)" menjadi integer `2025`.
    *   **Casting Tipe Data:** Memaksa kolom angka menjadi tipe `numeric` dan mengubah non-angka menjadi `NaN` atau `0`.
*   **Output:** Menyimpan hasil bersih ke folder `output_csv/` dalam format `.csv`.

### 🔹 **load.py** (ETL: Load)
Penghubung ke Database MySQL. Bertugas menyimpan data bersih ke dalam tabel yang terstruktur.

*   **Fungsi Utama:**
    *   `run_load_process()`: Menjalankan koneksi ke database dan proses insert data.
    *   **Auto-Setup Database:** Mengeksekusi perintah SQL `CREATE TABLE IF NOT EXISTS`. Ini membuat tabel Dimensi (`dim_waktu`, `dim_kecamatan`) dan Tabel Fakta (`fact_kasus`) secara otomatis jika belum ada.
*   **Logika "Smart Insert" (UPSERT):**
    *   Menggunakan pola **Star Schema** (Tabel Fakta dikelilingi Tabel Dimensi).
    *   **Mapping ID:** Mengubah data teks (misal: "Karang Pilang") menjadi ID angka (misal: `1`) dengan mencocokkannya ke tabel dimensi (`dim_kecamatan`).
    *   **Cek Duplikasi:** Sebelum insert, sistem mengecek apakah data untuk tahun & kecamatan tersebut sudah ada.
        *   Jika **Ada**: Lakukan `UPDATE` data.
        *   Jika **Belum**: Lakukan `INSERT` data baru.
    *   **Refresh Mapping:** Memastikan tahun baru (misal: 2026) langsung dikenali setelah ditambahkan ke `dim_waktu`.

---

## 🗂️ 2. Folder Data

### 📂 **data/** (Raw Data)
*   **Fungsi:** Staging area untuk file mentah.
*   **Alur:** User Upload di Streamlit -> Disimpan di sini -> Dibaca oleh `extract.py`.
*   **Penting:** Nama file di sini harus sesuai standar (misal: `perkecamatan.xlsx`) agar terbaca oleh script.

### 📂 **output_csv/** (Clean Data)
*   **Fungsi:** Tempat hasil olahan `tranform.py`.
*   **Alur:** `tranform.py` menyimpan hasil di sini -> `load.py` membaca dari sini -> Masuk MySQL.
*   **Format:** CSV standar (Comma Separated Values) yang lebih ringan dan cepat dibaca dibanding Excel.

### 📂 **data-2026/** & **inputan_data/** (Archive)
*   **Fungsi:** Folder arsip untuk menyimpan backup data asli atau data tahunan spesifik. Tidak diproses langsung oleh sistem, hanya sebagai cadangan.

---

## 📝 3. Dokumentasi

### 📄 **explain.md**
*   **Fungsi:** Dokumen teknis (yang sedang Anda baca ini). Menjelaskan arsitektur dan logika kode untuk developer.

### 📄 **how.md**
*   **Fungsi:** Panduan Pengguna (User Manual). Menjelaskan cara instalasi, cara menjalankan aplikasi (`streamlit run`), dan cara troubleshooting error dasar.

### 📄 **PANDUAN_INPUT_DATA_2026.md**
*   **Fungsi:** SOP Input Data. Memberikan contoh format kolom Excel yang benar agar tidak terjadi error saat upload (misal: kolom wajib "Tahun" dan "Kecamatan").

---

## 🖼️ 4. Aset & System

### 🖼️ **logo.png**
*   **Fungsi:** File gambar logo instansi yang dimuat oleh `Streamlit.py` untuk ditampilkan di sidebar navigasi.

### 📂 **__pycache__/**
*   **Fungsi:** Folder cache Python. Berisi bytecode (`.pyc`) hasil kompilasi script Python.
*   **Tujuan:** Mempercepat waktu loading aplikasi saat dijalankan ulang. Folder ini aman untuk dihapus dan akan dibuat ulang otomatis oleh Python.
