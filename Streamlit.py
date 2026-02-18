import streamlit as st
from streamlit_option_menu import option_menu
import os
import pandas as pd
import time
import tranform
import load
import shutil
import traceback
import importlib

# ================================
# 🔹 KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Dashboard HIV Surabaya", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# 🔹 CSS STYLING MODERN (GLASSMORPHISM & ANIMATIONS)
# ================================
st.markdown("""
    <style>
    /* Import Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Variables */
    :root {
        --primary: #0ea5e9;
        --primary-dark: #0284c7;
        --secondary: #6366f1;
        --bg-light: #f8fafc;
        --text-dark: #0f172a;
        --text-grey: #64748b;
    }

    /* Base Styles */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--text-dark);
    }

    /* Background Animation */
    .stApp {
        background: radial-gradient(circle at top left, #f0f9ff, #f8fafc, #eff6ff);
        background-attachment: fixed;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 4px 0 24px rgba(0,0,0,0.02);
    }
    
    /* Custom Header with Gradient */
    .dashboard-header {
        background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 50%, #6366f1 100%);
        padding: 40px;
        border-radius: 24px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px -10px rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-header::before {
        content: "";
        position: absolute;
        top: 0; right: 0; bottom: 0; left: 0;
        background: url('https://www.transparenttextures.com/patterns/cubes.png');
        opacity: 0.1;
    }

    .header-content {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .header-icon {
        background: rgba(255, 255, 255, 0.2);
        width: 60px;
        height: 60px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.03);
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s ease;
        margin-bottom: 24px;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.08);
        border-color: rgba(14, 165, 233, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(to right, #0ea5e9, #2563eb);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.25);
    }

    .stButton > button:hover {
        background: linear-gradient(to right, #0284c7, #1d4ed8);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(14, 165, 233, 0.4);
    }

    /* Iframe Styling */
    iframe {
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    }

    /* Custom File Uploader */
    .stFileUploader > div > div {
        background-color: white;
        border: 2px dashed #cbd5e1;
        border-radius: 16px;
        padding: 20px;
    }
    
    /* Animation Fade In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.6s ease-out forwards;
    }
    
    /* Remove default top padding */
    .block-container {
        padding-top: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ================================
# 🔹 SIDEBAR
# ================================
with st.sidebar:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Logo Area
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([0.2, 2, 0.2])
        with col2:
            st.image("logo.png", use_container_width=True)
    
    st.markdown("""
        <div style='text-align: center; margin: 20px 0 30px 0;'>
            <h2 style='font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 5px; letter-spacing: -0.5px;'>Dinas Kesehatan</h2>
            <div style='background: #e0f2fe; color: #0284c7; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-block;'>Kota Surabaya</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Input Data", "Tentang"],
        icons=["grid-fill", "cloud-arrow-up-fill", "info-circle-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#64748b", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "15px", 
                "text-align": "left", 
                "margin": "8px 12px", 
                "color": "#475569",
                "border-radius": "12px",
                "padding": "12px 16px",
                "transition": "all 0.2s"
            },
            "nav-link-selected": {
                "background-color": "#fff", 
                "color": "#0ea5e9", 
                "font-weight": "600",
                "box-shadow": "0 4px 15px rgba(0,0,0,0.05)",
                "icon-color": "#0ea5e9"
            },
        }
    )
    
    # Sidebar Footer
    st.markdown("""
        <div style='position: fixed; bottom: 30px; left: 20px; right: 20px; text-align: center;'>
            <p style='color: #94a3b8; font-size: 11px; font-weight: 500;'>
                &copy; 2026 Health Data Portal<br>v2.1.0 • Stable Build
            </p>
        </div>
    """, unsafe_allow_html=True)

# ================================
# 🔹 PAGE: DASHBOARD (POWER BI)
# ================================
if selected == "Dashboard":
    # Hero Header
    st.markdown("""
        <div class="dashboard-header animate-fade-in">
            <div class="header-content">
                <div class="header-icon">📊</div>
                <div>
                    <h1 style='font-size: 28px; font-weight: 700; margin: 0; letter-spacing: -0.5px;'>Executive Dashboard</h1>
                    <p style='font-size: 16px; margin: 5px 0 0 0; opacity: 0.9; font-weight: 400;'>Monitoring Real-time Kasus HIV Global & Surabaya</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Content Area
    st.markdown('<div class="glass-card animate-fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
    
    # Status Bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
            <div style='display: flex; gap: 15px; align-items: center;'>
                <span style='background: #dcfce7; color: #166534; padding: 6px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;'>● Live Data</span>
                <span style='color: #64748b; font-size: 14px;'>Last sync: Just now</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div style='text-align: right;'>
                <a href="https://app.powerbi.com" target="_blank" style='color: #0ea5e9; text-decoration: none; font-weight: 600; font-size: 14px; border-bottom: 2px solid transparent; transition: all 0.2s;'>Open Power BI ↗</a>
            </div>
        """, unsafe_allow_html=True)

    # INFO BOX UNTUK REFRESH DATA
    st.info("💡 **Info Update Data:** Karena berjalan di Localhost, data di Power BI tidak update otomatis real-time. Buka **Power BI Desktop** > Klik **Refresh** > Klik **Publish** untuk melihat data baru di sini.")
        
    st.markdown("<hr style='margin: 20px 0; border: 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
    
    # Power BI Iframe
    # Default URL (bisa diganti lewat UI)
    default_url = "https://app.powerbi.com/reportEmbed?reportId=704edb10-c9ae-431f-9145-b060c4a0807a&autoAuth=true&ctid=61b85544-c039-4649-b5f1-3baaf5e5d109"
    
    # Opsi Konfigurasi URL (Agar user bisa mengganti jika link mati/private)
    with st.expander("⚙️ Pengaturan Tampilan Power BI (Klik jika dashboard tidak muncul)"):
        st.markdown("""
        <small style='color: #64748b;'>
        Jika tampilan kosong atau meminta login, link default mungkin bersifat privat. 
        Silakan masukkan <b>Link Embed Publik</b> dari Power BI Anda.
        <br>Caranya: Buka Power BI Service > File > Embed report > Publish to web (public).
        </small>
        """, unsafe_allow_html=True)
        power_bi_url = st.text_input("Masukkan URL Power BI Embed:", value=default_url)

    st.markdown(
        f"""
        <iframe 
            title="Power BI Report" 
            width="100%" 
            height="800" 
            src="{power_bi_url}" 
            frameborder="0" 
            allowFullScreen="true"
            style="width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        </iframe>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ================================
# 🔹 PAGE: INPUT DATA
# ================================
elif selected == "Input Data":
    st.markdown("""
        <div class="dashboard-header animate-fade-in" style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);">
            <div class="header-content">
                <div class="header-icon">📂</div>
                <div>
                    <h1 style='font-size: 28px; font-weight: 700; margin: 0;'>Data Management</h1>
                    <p style='font-size: 16px; margin: 5px 0 0 0; opacity: 0.9;'>Upload dan Validasi Data Baru</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card animate-fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
        st.markdown("### 📤 Upload File")
        st.markdown("<p style='color: #64748b; font-size: 14px; margin-bottom: 20px;'>Dukung format .xlsx (Excel). Pastikan struktur data sesuai template.</p>", unsafe_allow_html=True)
        
        # File Type Selection
        file_type_map = {
            "Jenis Kelamin (Global)": "jeniskelamin.xlsx",
            "Jenis Kelamin (Surabaya)": "jenkelsby.xlsx",
            "Per Kecamatan": "perkecamatan.xlsx",
            "Status Pasien": "statuspasien.xlsx",
            "Temuan per Tahun": "temuantahun.xlsx",
            "Umur (Global)": "umur.xlsx",
            "Umur (Surabaya)": "umursby.xlsx"
        }
        
        selected_type = st.selectbox("Pilih Jenis Data", list(file_type_map.keys()))
        target_filename = file_type_map[selected_type]

        uploaded_file = st.file_uploader("", type=["xlsx"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            # Setup directories
            DATA_FOLDER = "data"
            os.makedirs(DATA_FOLDER, exist_ok=True)
            save_path = os.path.join(DATA_FOLDER, target_filename)
            
            try:
                # Save & Read
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                df = pd.read_excel(save_path)
                
                # --- PREVIEW LOGIC: Transform & Sort ---
                preview_df = df.copy()
                try:
                    if selected_type == "Jenis Kelamin (Global)":
                        preview_df = tranform.transform_jeniskelamin(df)
                    elif selected_type == "Jenis Kelamin (Surabaya)":
                        preview_df = tranform.transform_jeniskelaminsby(df)
                    elif selected_type == "Per Kecamatan":
                        preview_df = tranform.transform_perkecamatan(df)
                    elif selected_type == "Status Pasien":
                        preview_df = tranform.transform_statuspasien(df)
                    elif selected_type == "Temuan per Tahun":
                        preview_df = tranform.transform_temuantahun(df)
                    elif selected_type == "Umur (Global)":
                        preview_df = tranform.transform_umur(df)
                    elif selected_type == "Umur (Surabaya)":
                        preview_df = tranform.transform_umursby(df)
                    
                    # Sort Descending by Tahun if available (to show latest data 2024-2025)
                    if "Tahun" in preview_df.columns:
                        preview_df = preview_df.sort_values(by="Tahun", ascending=False)
                        
                except Exception as e:
                    # If transform fails (e.g. wrong format), show raw
                    pass
                
                # Success Message
                st.markdown(f"""
                    <div style='background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 12px; margin: 20px 0; display: flex; align-items: center; gap: 10px;'>
                        <span style='font-size: 20px;'>✅</span>
                        <div>
                            <div style='color: #166534; font-weight: 600;'>File Berhasil Diupload</div>
                            <div style='color: #15803d; font-size: 12px;'>Disimpan sebagai {target_filename} • {len(df)} baris data</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Preview
                st.markdown("#### 📄 Data Preview (Sesuai Database)")
                st.dataframe(preview_df, use_container_width=True, hide_index=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Button Layout
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("⚙️ Proses ETL", use_container_width=True):
                        with st.spinner("Menjalankan Transformasi Data..."):
                            try:
                                # Force Reload Modules to apply latest fixes
                                importlib.reload(tranform)
                                
                                # Mapping selection to internal keys
                                key_map = {
                                    "Jenis Kelamin (Global)": "jeniskelamin",
                                    "Jenis Kelamin (Surabaya)": "jeniskelaminsby",
                                    "Per Kecamatan": "perkecamatan",
                                    "Status Pasien": "statuspasien",
                                    "Temuan per Tahun": "temuantahun",
                                    "Umur (Global)": "umur",
                                    "Umur (Surabaya)": "umursby"
                                }
                                
                                etl_key = key_map[selected_type]
                                
                                # 1. Prepare Data Dictionary
                                data_dict = {etl_key: df.copy()}
                                
                                # 2. Common Validations & Fixes
                                tranform.check_missing_values(data_dict)
                                tranform.cek_kata_kecamatan(data_dict)
                                data_dict = tranform.benarkan_kata_kecamatan(data_dict)
                                
                                # 3. Specific Transformation
                                df_to_transform = data_dict[etl_key]
                                result_df = None
                                
                                if etl_key == "jeniskelamin":
                                    result_df = tranform.transform_jeniskelamin(df_to_transform)
                                elif etl_key == "jeniskelaminsby":
                                    result_df = tranform.transform_jeniskelaminsby(df_to_transform)
                                elif etl_key == "perkecamatan":
                                    result_df = tranform.transform_perkecamatan(df_to_transform)
                                elif etl_key == "statuspasien":
                                    result_df = tranform.transform_statuspasien(df_to_transform)
                                elif etl_key == "temuantahun":
                                    result_df = tranform.transform_temuantahun(df_to_transform)
                                elif etl_key == "umur":
                                    result_df = tranform.transform_umur(df_to_transform)
                                elif etl_key == "umursby":
                                    result_df = tranform.transform_umursby(df_to_transform)
                                
                                # 4. Save Result
                                if result_df is not None:
                                    tranform.simpan_ke_csv({etl_key: result_df})
                                    st.toast("Transformasi Data Selesai!", icon="✅")
                                    st.success(f"Data {selected_type} berhasil di-transform dan siap di-upload.")
                                    
                                    # Show Result Preview
                                    st.markdown("##### 📊 Hasil Transformasi Final:")
                                    st.dataframe(result_df, use_container_width=True, hide_index=True)
                                else:
                                    st.error("Gagal melakukan transformasi data.")
                                    
                            except Exception as e:
                                st.error(f"Gagal Transformasi: {e}")
                                with st.expander("Lihat Detail Error"):
                                    st.code(traceback.format_exc())

                with col_btn2:
                    if st.button("🚀 Upload ke Database", type="primary", use_container_width=True):
                        with st.spinner("Memuat data ke Database MySQL..."):
                            try:
                                # Force Reload Modules to apply latest fixes
                                importlib.reload(load)

                                # Determine specific target based on selection to avoid mixing data
                                key_map = {
                                    "Jenis Kelamin (Global)": ["jeniskelamin"],
                                    "Jenis Kelamin (Surabaya)": ["jeniskelaminsby"],
                                    "Per Kecamatan": ["perkecamatan"],
                                    "Status Pasien": ["statuspasien"],
                                    "Temuan per Tahun": ["temuantahun"],
                                    "Umur (Global)": ["umur"],
                                    "Umur (Surabaya)": ["umursby"]
                                }
                                target_tables = key_map.get(selected_type)
                                
                                load.run_load_process(target_tables=target_tables)
                                st.toast("Data berhasil masuk Database!", icon="🎉")
                                st.balloons()
                                st.success(f"Proses Upload Selesai! Data {selected_type} telah diperbarui di database.")
                            except Exception as e:
                                st.error(f"Gagal Upload Database: {e}")
                                with st.expander("Lihat Detail Error"):
                                    st.code(traceback.format_exc())
                
            except Exception as e:
                st.error(f"Error: {e}")
                with st.expander("Lihat Detail Error"):
                    st.code(traceback.format_exc())
                
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card animate-fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
        st.markdown("### 📝 Panduan Upload")
        st.markdown("""
        <ul style='padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.6;'>
            <li>Pastikan format file adalah <b>.xlsx</b></li>
            <li>Header kolom harus sesuai template standar</li>
            <li>Hindari cell kosong pada kolom wajib (Tahun, Kecamatan)</li>
            <li>Maksimal ukuran file 10MB</li>
        </ul>
        """, unsafe_allow_html=True)
        # st.markdown("<div style='background: #f1f5f9; height: 1px; margin: 20px 0;'></div>", unsafe_allow_html=True)
        # st.button("📥 Download Template Excel", use_container_width=True)
        # st.markdown('</div>', unsafe_allow_html=True)

# ================================
# 🔹 PAGE: TENTANG
# ================================
elif selected == "Tentang":
    st.markdown("""
        <div class="dashboard-header animate-fade-in" style="background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);">
            <div class="header-content">
                <div class="header-icon">ℹ️</div>
                <div>
                    <h1 style='font-size: 28px; font-weight: 700; margin: 0;'>Tentang Sistem</h1>
                    <p style='font-size: 16px; margin: 5px 0 0 0; opacity: 0.9;'>Informasi Teknis & Pengembang</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card animate-fade-in" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
        if os.path.exists("logo.png"):
            st.image("logo.png", width=120)
        st.markdown("""
        ### Portal Data HIV Surabaya v2.1
        
        Sistem informasi untuk memberikan wawasan mendalam mengenai sebaran dan tren kasus HIV di Kota Surabaya.
        
        **Teknologi Stack:**
        *   **Frontend**: Streamlit (Python)
        *   **Visualisasi**: Microsoft Power BI 
        *   **Backend**: Python ETL Engine
        *   **Database**: MySQL
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card animate-fade-in" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
        st.markdown("### 📞 Kontak")
        st.markdown("""
<div style='display: flex; flex-direction: column; gap: 15px; margin-top: 15px;'>
    <div style='display: flex; align-items: center; gap: 15px; padding: 15px; background: #f8fafc; border-radius: 12px;'>
        <div>
            <div style='font-weight: 600; color: #1e293b;'>Dinas Kesehatan Surabaya</div>
            <div style='font-size: 13px; color: #64748b;'>Jl. Raya Jemursari No.197, Sidosermo, Kec. Wonocolo, Surabaya, Jawa Timur 60239</div>
        </div>
    </div>
    <div style='display: flex; align-items: center; gap: 15px; padding: 15px; background: #f8fafc; border-radius: 12px;'>
        <div>
            <div style='font-weight: 600; color: #1e293b;'>Telp: </div>
            <div style='font-size: 13px; color: #64748b;'>(031) 8439473</div>
        </div>
        <div>
            <div style='font-weight: 600; color: #1e293b;'>Email: </div>
            <div style='font-size: 13px; color: #64748b;'>dinkes@surabaya.go.id</div>
        </div>
    </div>
</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
