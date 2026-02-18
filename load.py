import mysql.connector
import pandas as pd
import re
import sys
import codecs
import os

# Menambahkan support untuk karakter unicode
try:
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
except AttributeError:
    pass # Streamlit or other environments might handle stdout differently

def run_load_process(target_tables=None):
    """
    Menjalankan proses loading data ke database.
    
    Args:
        target_tables (list, optional): List nama tabel/kategori yang ingin di-load. 
                                        Contoh: ['jeniskelamin', 'perkecamatan'].
                                        Jika None, akan memproses semua file yang ada di output_csv/.
    """
    print("🚀 Memulai proses Loading ke Database...")
    
    if target_tables:
        print(f"Target loading spesifik: {target_tables}")
    else:
        print("Target loading: SEMUA file yang tersedia")
    
    # 1. menkoneksi dan membuat db 
    # =============================
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = db.cursor()

    # cursor.execute("DROP DATABASE IF EXISTS datawarehouse_hiv")
    # cursor.execute("CREATE DATABASE datawarehouse_hiv")
    cursor.execute("USE datawarehouse_hiv")

    # 2. TABEL DIMENSI
    # =============================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_waktu (
        id_waktu INT AUTO_INCREMENT PRIMARY KEY,
        tahun INT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_kecamatan (
        id_kecamatan INT AUTO_INCREMENT PRIMARY KEY,
        nama_kecamatan VARCHAR(500) UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_kelompok_umur (
        id_kelompok_umur INT AUTO_INCREMENT PRIMARY KEY,
        kelompok_umur VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_jenis_kelamin (
        id_jenis_kelamin INT AUTO_INCREMENT PRIMARY KEY,
        jenis_kelamin VARCHAR(20)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_status_pasien (
        id_status_pasien INT AUTO_INCREMENT PRIMARY KEY,
        status_pasien VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_upk (
        id_upk INT AUTO_INCREMENT PRIMARY KEY,
        id_kecamatan INT,
        nama_upk VARCHAR(500),
        status_pemilik VARCHAR(100),
        jenis_pemilik VARCHAR(100),
        alamat TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_jenis_layanan (
        id_jenis_layanan INT AUTO_INCREMENT PRIMARY KEY,
        id_kecamatan INT,
        layanan_tes_hiv VARCHAR(255),
        layanan_pdp VARCHAR(255),
        layanan_vl VARCHAR(255),
        layanan_tes_eid VARCHAR(255),
        layanan_tes_cd4 VARCHAR(255)
    )
    """)


    # 3. tabel fakta
    # =============================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_kasus_perkecamatan (
        id_fact_kasus_perkecamatan INT AUTO_INCREMENT PRIMARY KEY,
        id_waktu INT,
        id_kecamatan INT,
        temuan_kasus INT,
        ART INT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_perkelompok_umur (
        id_fact_perkelompok_umur INT AUTO_INCREMENT PRIMARY KEY,
        id_waktu INT,
        id_kelompok_umur INT,
        temuan_kasus INT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_jenkel_statuspasien (
        id_fact INT AUTO_INCREMENT PRIMARY KEY,
        id_waktu INT NOT NULL,
        kategori ENUM('JK','SP') NOT NULL,
        id_dimensi INT NOT NULL,
        temuan_kasus INT NOT NULL,
        FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_umur_surabaya (
        id_fact_umur_surabaya INT AUTO_INCREMENT PRIMARY KEY,
        id_waktu INT,
        id_kelompok_umur INT,
        temuan_kasus_surabaya INT,
        FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu),
        FOREIGN KEY (id_kelompok_umur) REFERENCES dim_kelompok_umur(id_kelompok_umur)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_jenkel_surabaya (
        id_fact_jenkel_surabaya INT AUTO_INCREMENT PRIMARY KEY,
        id_waktu INT,
        id_jenis_kelamin INT,
        temuan_kasus_surabaya INT,
        FOREIGN KEY (id_waktu) REFERENCES dim_waktu(id_waktu),
        FOREIGN KEY (id_jenis_kelamin) REFERENCES dim_jenis_kelamin(id_jenis_kelamin)
    )
    """)
    db.commit()
    print("✅ Database dan tabel (jika belum ada) berhasil disiapkan")

    # 4. load atau memasukan data ke dimensi
    # =============================

    # ---- dim_waktu
    # Kumpulkan semua tahun dari berbagai file untuk memastikan kelengkapan
    all_years = set()
    
    # 1. Dari temuantahun.csv
    if os.path.exists("output_csv/temuantahun.csv"):
        df = pd.read_csv("output_csv/temuantahun.csv")
        all_years.update(df["Tahun"].dropna().astype(int).tolist())

    # 2. Dari perkecamatan.csv (ekstrak tahun dari nama kolom)
    if os.path.exists("output_csv/perkecamatan.csv"):
        df = pd.read_csv("output_csv/perkecamatan.csv")
        for col in df.columns:
            match = re.search(r"\d{4}", col)
            if match:
                all_years.add(int(match.group()))
    
    # 3. Dari file lain yang memiliki kolom Tahun
    for fname in ["umur.csv", "jeniskelamin.csv", "statuspasien.csv", "umursby.csv", "jeniskelaminsby.csv"]:
        fpath = f"output_csv/{fname}"
        if os.path.exists(fpath):
            try:
                df = pd.read_csv(fpath)
                if "Tahun" in df.columns:
                    all_years.update(df["Tahun"].dropna().astype(int).tolist())
            except Exception as e:
                print(f"Warning: Gagal membaca tahun dari {fname}: {e}")

    # Insert ke database
    for tahun in sorted(list(all_years)):
        try:
            # Pastikan tahun tidak 0 atau invalid
            if tahun > 1900 and tahun < 2100:
                cursor.execute(
                    "INSERT IGNORE INTO dim_waktu (tahun) VALUES (%s)",
                    (tahun,)
                )
        except mysql.connector.Error as err:
            print(f"Warning inserting year {tahun}: {err}")
            
    db.commit()

    # REFRESH MAPPING WAKTU SETELAH INSERT BARU
    cursor.execute("SELECT id_waktu, tahun FROM dim_waktu")
    map_waktu = {t: i for i, t in cursor.fetchall()}

    # ---- dim_kecamatan
    # ---- fact_kasus_perkecamatan
    should_process_perkecamatan = target_tables is None or "perkecamatan" in target_tables
    
    if should_process_perkecamatan and os.path.exists("output_csv/perkecamatan.csv"):
        try:
            df = pd.read_csv("output_csv/perkecamatan.csv")
            for kec in df["Kecamatan Wilayah Surabaya"].dropna().unique():
                cursor.execute(
                    "INSERT INTO dim_kecamatan (nama_kecamatan) VALUES (%s) ON DUPLICATE KEY UPDATE nama_kecamatan=nama_kecamatan",
                    (kec.strip(),)
                )
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses dim_kecamatan: {e}")

    # ---- dim_kelompok_umur
    if os.path.exists("output_csv/umur.csv"):
        try:
            df = pd.read_csv("output_csv/umur.csv")
            for col in df.columns:
                if col != "Tahun":
                    cursor.execute(
                        "INSERT INTO dim_kelompok_umur (kelompok_umur) VALUES (%s) ON DUPLICATE KEY UPDATE kelompok_umur=kelompok_umur",
                        (col,)
                    )
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses dim_kelompok_umur: {e}")

    # ---- dim_jenis_kelamin
    if os.path.exists("output_csv/jeniskelamin.csv"):
        try:
            df = pd.read_csv("output_csv/jeniskelamin.csv")
            for col in df.columns:
                if col != "Tahun":
                    cursor.execute(
                        "INSERT INTO dim_jenis_kelamin (jenis_kelamin) VALUES (%s) ON DUPLICATE KEY UPDATE jenis_kelamin=jenis_kelamin",
                        (col,)
                    )
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses dim_jenis_kelamin: {e}")

    # ---- dim_status_pasien
    for sp in ["Hidup", "Meninggal"]:
        cursor.execute(
            "INSERT INTO dim_status_pasien (status_pasien) VALUES (%s) ON DUPLICATE KEY UPDATE status_pasien=status_pasien",
            (sp,)
        )
    db.commit()

    # ---- dim_upk & dim_jenis_layanan
    if os.path.exists("output_csv/upk.csv"):
        try:
            df_upk = pd.read_csv("output_csv/upk.csv")
            df_upk.columns = df_upk.columns.str.strip().str.lower().str.replace(" ", "_")

            for _, r in df_upk.iterrows():
                cursor.execute("SELECT id_kecamatan FROM dim_kecamatan WHERE nama_kecamatan=%s", (r["kecamatan"],))
                res = cursor.fetchone()

                if not res:
                    # print(f"Kecamatan tidak ditemukan: {r['kecamatan']}")
                    continue

                id_kec = res[0]

                # Cek eksistensi UPK
                cursor.execute("SELECT id_upk FROM dim_upk WHERE nama_upk=%s AND id_kecamatan=%s", (r["nama"], id_kec))
                existing_upk = cursor.fetchone()

                if existing_upk:
                    # UPDATE UPK
                    cursor.execute("""
                        UPDATE dim_upk
                        SET status_pemilik=%s, jenis_pemilik=%s, alamat=%s
                        WHERE id_upk=%s
                    """, (r["status_pemilik"], r["jenis_pemilik"], r["alamat"], existing_upk[0]))
                    
                    # NOTE: dim_jenis_layanan tidak memiliki foreign key ke dim_upk, 
                    # sehingga sulit untuk mengupdate baris yang tepat secara akurat tanpa id_upk.
                    # Untuk mencegah duplikasi, kita SKIP update layanan jika UPK sudah ada.
                    # Idealnya schema dim_jenis_layanan harus punya id_upk.
                else:
                    # INSERT BARU
                    cursor.execute("""
                        INSERT INTO dim_upk
                        (id_kecamatan, nama_upk, status_pemilik, jenis_pemilik, alamat)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_kec,
                        r["nama"],
                        r["status_pemilik"],
                        r["jenis_pemilik"],
                        r["alamat"]
                    ))

                    cursor.execute("""
                    INSERT INTO dim_jenis_layanan
                    (id_kecamatan, layanan_tes_hiv, layanan_pdp, layanan_vl, layanan_tes_eid, layanan_tes_cd4)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        id_kec,
                        "Ya" if r["layanan_tes_hiv"] == "Ya" else "Tidak",
                        "Ya" if r["layanan_pdp"] == "Ya" else "Tidak",
                        "Ya" if r["layanan_tes_vl"] == "Ya" else "Tidak",
                        "Ya" if r["layanan_tes_eid"] == "Ya" else "Tidak",
                        "Ya" if r["layanan_tes_cd4"] == "Ya" else "Tidak"
                    ))

            db.commit()
            print("✅ Data UPK dan layanan berhasil dimuat.")
        except Exception as e:
            print(f"Warning: Gagal memproses dim_upk: {e}")
    
    #Mencocokkan data teks dengan ID yang sudah ada, menghubungkan fakta ke dim
    # 5. mapping dimensi
    # =============================
    
    # REFRESH SEMUA MAPPING UNTUK MEMASTIKAN DATA BARU TERAMBIL
    cursor.execute("SELECT id_waktu, tahun FROM dim_waktu")
    map_waktu = {t: i for i, t in cursor.fetchall()}

    cursor.execute("SELECT id_kecamatan, nama_kecamatan FROM dim_kecamatan")
    map_kec = {n: i for i, n in cursor.fetchall()}

    cursor.execute("SELECT id_kelompok_umur, kelompok_umur FROM dim_kelompok_umur")
    map_umur = {n: i for i, n in cursor.fetchall()}

    cursor.execute("SELECT id_jenis_kelamin, jenis_kelamin FROM dim_jenis_kelamin")
    map_jk = {n: i for i, n in cursor.fetchall()}

    cursor.execute("SELECT id_status_pasien, status_pasien FROM dim_status_pasien")
    map_sp = {n: i for i, n in cursor.fetchall()}

    # 6. load atau memasukan data ke tabel fakta
    # =============================

    # cursor.execute("TRUNCATE fact_kasus_perkecamatan")

    if os.path.exists("output_csv/perkecamatan.csv"):
        try:
            df = pd.read_csv("output_csv/perkecamatan.csv")

            for _, r in df.iterrows():
                kecamatan = str(r["Kecamatan Wilayah Surabaya"]).strip()
                id_kec = map_kec.get(kecamatan)
                if not id_kec:
                    continue

                for col in df.columns:
                    if "Temuan" in col:
                        match = re.search(r"\d{4}", col)
                        if not match: continue
                        
                        tahun = int(match.group())
                        id_waktu = map_waktu.get(tahun)

                        # Fallback: Jika ID Waktu tidak ditemukan di mapping (mungkin insert baru gagal sync), coba cari langsung di DB
                        if not id_waktu:
                            cursor.execute("SELECT id_waktu FROM dim_waktu WHERE tahun = %s", (tahun,))
                            res_fallback = cursor.fetchone()
                            if res_fallback:
                                id_waktu = res_fallback[0]
                                map_waktu[tahun] = id_waktu # Update map untuk iterasi berikutnya

                        col_art = [c for c in df.columns if str(tahun) in c and "ART" in c]
                        if not col_art or not id_waktu:
                            print(f"Skipping: Tahun {tahun} (ID: {id_waktu}) atau Kolom ART tidak ditemukan.")
                            continue

                        val_temuan = r[col]
                        val_art = r[col_art[0]]

                        temuan = 0 if pd.isna(val_temuan) or val_temuan == '' else int(float(val_temuan))
                        art = 0 if pd.isna(val_art) or val_art == '' else int(float(val_art))

                        # Cek apakah data fakta sudah ada
                        cursor.execute("""
                            SELECT id_fact_kasus_perkecamatan FROM fact_kasus_perkecamatan
                            WHERE id_waktu = %s AND id_kecamatan = %s
                        """, (id_waktu, id_kec))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Jika ada, UPDATE
                            cursor.execute("""
                                UPDATE fact_kasus_perkecamatan
                                SET temuan_kasus = %s, ART = %s
                                WHERE id_fact_kasus_perkecamatan = %s
                            """, (temuan, art, existing[0]))
                        else:
                            # Jika belum ada, INSERT
                            cursor.execute("""
                                INSERT INTO fact_kasus_perkecamatan
                                (id_waktu, id_kecamatan, temuan_kasus, ART)
                                VALUES (%s, %s, %s, %s)
                            """, (id_waktu, id_kec, temuan, art))

            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses fact_kasus_perkecamatan: {e}")


    # ---- fact_perkelompok_umur
    should_process_umur = target_tables is None or "umur" in target_tables
    
    if should_process_umur and os.path.exists("output_csv/umur.csv"):
        try:
            df = pd.read_csv("output_csv/umur.csv")
            for _, r in df.iterrows():
                id_waktu = map_waktu.get(int(r["Tahun"]))
                if id_waktu is None:
                    continue
                    
                for col in df.columns:
                    if col != "Tahun":
                        if col not in map_umur: continue
                        val = r[col]
                        nilai = 0 if pd.isna(val) or val == '' else int(float(val))
                        
                        # Cek eksistensi
                        cursor.execute("""
                            SELECT id_fact_perkelompok_umur FROM fact_perkelompok_umur
                            WHERE id_waktu = %s AND id_kelompok_umur = %s
                        """, (id_waktu, map_umur[col]))
                        existing = cursor.fetchone()

                        if existing:
                             cursor.execute("""
                                UPDATE fact_perkelompok_umur
                                SET temuan_kasus = %s
                                WHERE id_fact_perkelompok_umur = %s
                            """, (nilai, existing[0]))
                        else:
                            cursor.execute("""
                                INSERT INTO fact_perkelompok_umur
                                (id_waktu, id_kelompok_umur, temuan_kasus)
                                VALUES (%s, %s, %s)
                            """, (id_waktu, map_umur[col], nilai))
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses fact_perkelompok_umur: {e}")

    # ---- fact_jenis kelamin dan status pasien
    should_process_jk = target_tables is None or "jeniskelamin" in target_tables
    should_process_sp = target_tables is None or "statuspasien" in target_tables
    
    if (should_process_jk or should_process_sp) and (os.path.exists("output_csv/jeniskelamin.csv") or os.path.exists("output_csv/statuspasien.csv")):
        try:
            # JK
            if should_process_jk and os.path.exists("output_csv/jeniskelamin.csv"):
                df_jk = pd.read_csv("output_csv/jeniskelamin.csv")
                for i in range(len(df_jk)):
                    tahun = int(df_jk.loc[i, "Tahun"])
                    id_waktu = map_waktu.get(tahun)
                    if id_waktu is None:
                        continue

                    for jk in map_jk:
                        if jk in df_jk.columns:
                            val = df_jk.loc[i, jk]
                            nilai = 0 if pd.isna(val) or val == '' else int(float(val))
                            
                            # Cek eksistensi
                            cursor.execute("""
                                SELECT id_fact FROM fact_jenkel_statuspasien
                                WHERE id_waktu = %s AND kategori = 'JK' AND id_dimensi = %s
                            """, (id_waktu, map_jk[jk]))
                            existing = cursor.fetchone()

                            if existing:
                                cursor.execute("""
                                    UPDATE fact_jenkel_statuspasien
                                    SET temuan_kasus = %s
                                    WHERE id_fact = %s
                                """, (nilai, existing[0]))
                            else:
                                cursor.execute("""
                                    INSERT INTO fact_jenkel_statuspasien
                                    (id_waktu, kategori, id_dimensi, temuan_kasus)
                                    VALUES (%s, 'JK', %s, %s)
                                """, (id_waktu, map_jk[jk], nilai))
            
            # SP
            if should_process_sp and os.path.exists("output_csv/statuspasien.csv"):
                df_sp = pd.read_csv("output_csv/statuspasien.csv")
                for i in range(len(df_sp)):
                    tahun = int(df_sp.loc[i, "Tahun"])
                    id_waktu = map_waktu.get(tahun)
                    if id_waktu is None:
                        continue

                    for sp in map_sp:
                        if sp in df_sp.columns:
                            val = df_sp.loc[i, sp]
                            nilai = 0 if pd.isna(val) or val == '' else int(float(val))
                            
                            # Cek eksistensi
                            cursor.execute("""
                                SELECT id_fact FROM fact_jenkel_statuspasien
                                WHERE id_waktu = %s AND kategori = 'SP' AND id_dimensi = %s
                            """, (id_waktu, map_sp[sp]))
                            existing = cursor.fetchone()

                            if existing:
                                cursor.execute("""
                                    UPDATE fact_jenkel_statuspasien
                                    SET temuan_kasus = %s
                                    WHERE id_fact = %s
                                """, (nilai, existing[0]))
                            else:
                                cursor.execute("""
                                    INSERT INTO fact_jenkel_statuspasien
                                    (id_waktu, kategori, id_dimensi, temuan_kasus)
                                    VALUES (%s, 'SP', %s, %s)
                                """, (id_waktu, map_sp[sp], nilai))

            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses fact_jenkel_statuspasien: {e}")

    # ---- fact_perkelompok_umur surabaya
    should_process_umursby = target_tables is None or "umursby" in target_tables
    
    if should_process_umursby and os.path.exists("output_csv/umursby.csv"):
        try:
            df = pd.read_csv("output_csv/umursby.csv")
            for _, r in df.iterrows():
                id_waktu = map_waktu.get(int(r["Tahun"]))
                if id_waktu is None:
                    continue
                    
                for col in df.columns:
                    if col != "Tahun":
                        if col not in map_umur: continue
                        val = r[col]
                        nilai = 0 if pd.isna(val) or val == '' else int(float(val))
                        
                        # Cek eksistensi
                        cursor.execute("""
                            SELECT id_fact_umur_surabaya FROM fact_umur_surabaya
                            WHERE id_waktu = %s AND id_kelompok_umur = %s
                        """, (id_waktu, map_umur[col]))
                        existing = cursor.fetchone()

                        if existing:
                            cursor.execute("""
                                UPDATE fact_umur_surabaya
                                SET temuan_kasus_surabaya = %s
                                WHERE id_fact_umur_surabaya = %s
                            """, (nilai, existing[0]))
                        else:
                            cursor.execute("""
                                INSERT INTO fact_umur_surabaya
                                (id_waktu, id_kelompok_umur, temuan_kasus_surabaya)
                                VALUES (%s, %s, %s)
                            """, (id_waktu, map_umur[col], nilai))
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses fact_umur_surabaya: {e}")

    # ---- fact_jenkel_sby
    should_process_jksby = target_tables is None or "jeniskelaminsby" in target_tables
    
    if should_process_jksby and os.path.exists("output_csv/jeniskelaminsby.csv"):
        try:
            df_jenkel_sby = pd.read_csv("output_csv/jeniskelaminsby.csv")  
            for _, r in df_jenkel_sby.iterrows():
                id_waktu = map_waktu.get(int(r["Tahun"]))
                if id_waktu is None:
                    continue
                    
                for col in df_jenkel_sby.columns:
                    if col != "Tahun":
                        if col not in map_jk: continue
                        val = r[col]
                        nilai = 0 if pd.isna(val) or val == '' else int(float(val))
                        
                        # Cek eksistensi
                        cursor.execute("""
                            SELECT id_fact_jenkel_surabaya FROM fact_jenkel_surabaya
                            WHERE id_waktu = %s AND id_jenis_kelamin = %s
                        """, (id_waktu, map_jk[col]))
                        existing = cursor.fetchone()

                        if existing:
                            cursor.execute("""
                                UPDATE fact_jenkel_surabaya
                                SET temuan_kasus_surabaya = %s
                                WHERE id_fact_jenkel_surabaya = %s
                            """, (nilai, existing[0]))
                        else:
                            cursor.execute("""
                                INSERT INTO fact_jenkel_surabaya
                                (id_waktu, id_jenis_kelamin, temuan_kasus_surabaya)
                                VALUES (%s, %s, %s)
                            """, (id_waktu, map_jk[col], nilai))
            db.commit()
        except Exception as e:
            print(f"Warning: Gagal memproses fact_jenkel_surabaya: {e}")

    # =============================
    # 7️⃣ TUTUP KONEKSI
    # =============================
    cursor.close()
    db.close()

    print("✅ Berhasil Load Semuanya ke Database")

if __name__ == "__main__":
    run_load_process()