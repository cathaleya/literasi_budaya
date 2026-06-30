import streamlit as st
import pandas as pd
import requests
import json
import base64
import os
from datetime import datetime
from questions import QUESTIONS

# ==========================================
# CONFIG & STYLES
# ==========================================
st.set_page_config(
    page_title="Instrumen PKM Literasi Budaya",
    page_icon="🎭",
    layout="centered"
)

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #fff1f2 0%, #ffffff 100%);
    }

    div[data-testid="stForm"] {
        border: none;
        padding: 0;
    }
    
    h1, h2, h3 { 
        color: #9f1239; 
        font-weight: 800; 
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%) !important;
        color: white !important;
        border-radius: 12px;
        padding: 14px;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 10px rgba(225, 29, 72, 0.2);
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(225, 29, 72, 0.3);
    }

    .header-section {
        background: linear-gradient(135deg, #be123c 0%, #e11d48 100%);
        padding: 35px 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(190, 18, 60, 0.15);
    }

    .success-card {
        background: #fff1f2;
        padding: 40px;
        border-radius: 24px;
        text-align: center;
        border: 2px solid #fecdd3;
        box-shadow: 0 8px 30px rgba(225, 29, 72, 0.1);
    }
    
    .score-text {
        font-size: 3rem;
        font-weight: 800;
        color: #be123c;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
# Initialize session state for pagination
if "page" not in st.session_state:
    st.session_state.page = "biodata"  # biodata, baca_buku, q_page_0..4, summary, finish

if "biodata" not in st.session_state:
    st.session_state.biodata = {}
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "score" not in st.session_state:
    st.session_state.score = 0

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def reset_state():
    st.session_state.page = "biodata"
    st.session_state.biodata = {}
    st.session_state.answers = {}
    st.session_state.score = 0

def get_apps_script_url():
    url = None
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    elif "gsheets_url" in st.secrets:
        url = st.secrets["gsheets_url"]
    elif "spreadsheet" in st.secrets:
        url = st.secrets["spreadsheet"]
    return url

def calculate_score():
    correct_count = 0
    for q in QUESTIONS:
        ans = st.session_state.answers.get(f"q_{q['id']}", "")
        if ans and ans.startswith(q['answer']):
            correct_count += 1
    return round((correct_count / len(QUESTIONS)) * 100, 2)

def submit_payload(payload):
    url = get_apps_script_url()
    if not url:
        st.error("Konfigurasi URL Google Apps Script tidak ditemukan di secrets.toml!")
        return False
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            try:
                res_json = response.json()
                if res_json.get("result") == "success":
                    return True
                else:
                    return res_json.get("status") == "ok" or res_json.get("result") == "ok"
            except Exception:
                return True
        else:
            st.error(f"Koneksi gagal (Status {response.status_code}): {response.text}")
            return False
    except Exception as e:
        st.error(f"Gagal koneksi ke server: {e}")
        return False

def build_payload():
    payload = {}
    
    # Sheet Name Configuration (Will be used by the updated Apps Script)
    payload["SheetName"] = "Data_Literasi_Budaya"
    
    payload["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload["Nama"] = st.session_state.biodata.get("nama", "")
    payload["Instansi"] = st.session_state.biodata.get("instansi", "")
    payload["Usia"] = st.session_state.biodata.get("usia", "")
    payload["Jenis_Kelamin"] = st.session_state.biodata.get("jenis_kelamin", "")
    payload["Tipe_Tes"] = st.session_state.biodata.get("tipe_tes", "")
    
    # Add score
    payload["Skor_Total"] = calculate_score()
    
    # Add answers
    for q in QUESTIONS:
        ans = st.session_state.answers.get(f"q_{q['id']}", "")
        # Get just the letter A, B, C, D, E for cleaner data
        letter = ans.split(".")[0] if ans else ""
        payload[f"Q{q['id']}"] = letter
        
    return payload

# ==========================================
# PAGE ROUTER
# ==========================================

# 1. BIODATA PAGE
if st.session_state.page == "biodata":
    st.markdown("""
        <div class="header-section">
            <h1 style="margin:0; color:white; font-size:1.6rem; font-weight:800;">DIALEKTIKA SENI INDONESIA DARI PERSPEKTIF AKULTURASI CHINA</h1>
            <p style="margin-top:8px; font-size:1.1rem; opacity:0.95; font-weight:600;">SOAL PRE TEST & POST TEST PKM LITERASI BUDAYA 2026</p>
            <div style="background-color:rgba(255,255,255,0.2); height:1px; margin: 15px 0;"></div>
            <h3 style="margin:0; color:white; font-size:1.2rem; font-weight:700;">📋 Data Responden</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("Silakan lengkapi identitas responden Anda sebelum memulai pengerjaan soal.")
    
    with st.form("form_biodata"):
        nama = st.text_input("Nama Lengkap", value=st.session_state.biodata.get("nama", ""))
        instansi = st.text_input("Asal Instansi / Sekolah", value=st.session_state.biodata.get("instansi", ""))
        usia = st.number_input("Usia (Tahun)", min_value=10, max_value=100, step=1, 
                              value=int(st.session_state.biodata.get("usia", 17)) if st.session_state.biodata.get("usia") else 17)
        
        jk_list = ["Laki-laki", "Perempuan"]
        existing_jk = st.session_state.biodata.get("jenis_kelamin", "Laki-laki")
        jenis_kelamin = st.selectbox("Jenis Kelamin", jk_list, index=jk_list.index(existing_jk) if existing_jk in jk_list else 0)
        
        tipe_list = ["Pre-test", "Post-test"]
        existing_tipe = st.session_state.biodata.get("tipe_tes", "Pre-test")
        tipe_tes = st.selectbox("Tipe Tes", tipe_list, index=tipe_list.index(existing_tipe) if existing_tipe in tipe_list else 0)
        
        submit_bio = st.form_submit_button("Mulai Jawab Soal ➡️")
        
        if submit_bio:
            if nama.strip() and instansi.strip():
                st.session_state.biodata = {
                    "nama": nama,
                    "instansi": instansi,
                    "usia": usia,
                    "jenis_kelamin": jenis_kelamin,
                    "tipe_tes": tipe_tes
                }
                st.session_state.page = "baca_buku"
                st.rerun()
            else:
                st.warning("Mohon lengkapi Nama dan Asal Instansi.")

# 1.5. BACA BUKU PAGE
elif st.session_state.page == "baca_buku":
    st.markdown("""
        <div class="header-section" style="padding: 20px;">
            <h2 style="margin:0; color:white;">📖 Buku Saku Literasi Budaya</h2>
            <p style="margin-top:5px; color:white; opacity:0.9;">Silakan baca dan pelajari buku saku berikut sebelum mengerjakan instrumen.</p>
        </div>
    """, unsafe_allow_html=True)
    
    import streamlit.components.v1 as components
    import os
    
    # Deklarasi custom component untuk 3D Flipbook
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "flipbook_frontend")
    
    if "_flipbook_component" not in st.session_state:
        st.session_state["_flipbook_component"] = components.declare_component(
            "flipbook_component",
            path=build_dir
        )
    
    # Tampilkan 3D Flipbook component
    st.session_state["_flipbook_component"]()
            
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Tombol Lanjut ke Instrumen
    col_back, col_next_instrumen = st.columns(2)
    with col_back:
        if st.button("⬅ Edit Biodata"):
            st.session_state.page = "biodata"
            st.rerun()
    with col_next_instrumen:
        if st.button("Lanjutkan ke Instrumen ➡️"):
            st.session_state.page = "q_page_0"
            st.rerun()

# 2. QUESTIONS PAGES
elif st.session_state.page.startswith("q_page_"):
    page_idx = int(st.session_state.page.split("_")[-1])
    
    # 22 questions, split into 5 pages: 5, 5, 4, 4, 4
    page_sizes = [5, 5, 4, 4, 4]
    start_idx = sum(page_sizes[:page_idx])
    end_idx = start_idx + page_sizes[page_idx]
    
    page_questions = QUESTIONS[start_idx:end_idx]
    
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <h3 style="margin: 0; color: #9f1239;">✍️ SOAL PILIHAN GANDA</h3>
            <div style="background-color: #fecdd3; height: 6px; border-radius: 3px; margin-top: 8px;">
                <div style="background-color: #be123c; height: 6px; border-radius: 3px; width: {((page_idx + 1) / 5) * 100}%;"></div>
            </div>
            <p style="font-size:0.85rem; color:#6b7280; text-align:right; margin-top:4px;">Halaman {page_idx + 1} dari 5</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form(f"form_q_page_{page_idx}"):
        responses = {}
        
        for q in page_questions:
            st.markdown(f"**Soal {q['id']}.** {q['text']}")
            existing_val = st.session_state.answers.get(f"q_{q['id']}", None)
            
            # Find index of existing answer to set as default
            idx = 0
            if existing_val in q['options']:
                idx = q['options'].index(existing_val)
                
            responses[f"q_{q['id']}"] = st.radio(
                f"Pilihan Jawaban Soal {q['id']}",
                q['options'],
                index=idx if existing_val else None,
                key=f"radio_q_{q['id']}",
                label_visibility="collapsed"
            )
            st.markdown("---")
            
        col_back, col_next = st.columns(2)
        with col_back:
            back_clicked = st.form_submit_button("⬅ Kembali")
        with col_next:
            next_clicked = st.form_submit_button("Lanjutkan ➡️")
            
        if back_clicked:
            if page_idx == 0:
                st.session_state.page = "baca_buku"
            else:
                st.session_state.page = f"q_page_{page_idx - 1}"
            st.rerun()
            
        if next_clicked:
            # Check if all questions on this page are answered
            all_answered = True
            for q in page_questions:
                if not responses[f"q_{q['id']}"]:
                    all_answered = False
                    break
                    
            if not all_answered:
                st.warning("Mohon jawab semua soal di halaman ini sebelum melanjutkan.")
            else:
                st.session_state.answers.update(responses)
                if page_idx < 4:
                    st.session_state.page = f"q_page_{page_idx + 1}"
                else:
                    st.session_state.page = "summary"
                st.rerun()

# 3. REVIEW SUMMARY PAGE
elif st.session_state.page == "summary":
    st.markdown("""
        <div class="header-section">
            <h1 style="margin:0; color:white; font-size:1.6rem; font-weight:800;">✅ RINGKASAN JAWABAN</h1>
            <p style="margin-top:8px; font-size:1.1rem; opacity:0.95; font-weight:600;">Silakan periksa kelengkapan jawaban Anda sebelum mengirim.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("👤 Identitas Responden")
    st.write(f"**Nama:** {st.session_state.biodata.get('nama', '')}")
    st.write(f"**Instansi:** {st.session_state.biodata.get('instansi', '')}")
    st.write(f"**Tipe Tes:** {st.session_state.biodata.get('tipe_tes', '')}")
    
    st.markdown("---")
    
    # Check for empty answers
    unanswered = [q['id'] for q in QUESTIONS if not st.session_state.answers.get(f"q_{q['id']}")]
    if unanswered:
        st.warning(f"Ada {len(unanswered)} soal yang belum dijawab: Soal nomor {', '.join(map(str, unanswered))}.")
    else:
        st.success("Semua soal telah dijawab!")
    
    col_back, col_submit = st.columns(2)
    with col_back:
        if st.button("⬅ Edit Jawaban"):
            st.session_state.page = "q_page_4"
            st.rerun()
            
    with col_submit:
        if st.button("🚀 Kirim Jawaban Sekarang", disabled=len(unanswered) > 0):
            payload = build_payload()
            st.session_state.score = payload["Skor_Total"]
            
            with st.spinner("Mengirim data ke Google Sheet..."):
                if submit_payload(payload):
                    st.session_state.page = "finish"
                    st.rerun()
                else:
                    st.error("Gagal mengirimkan data otomatis. Silakan cek secrets.toml atau koneksi internet.")
                    st.info("Anda masih bisa melihat skor Anda:")
                    if st.button("Lihat Skor Saja"):
                        st.session_state.page = "finish"
                        st.rerun()

# 4. FINISH PAGE
elif st.session_state.page == "finish":
    st.balloons()
    score = st.session_state.score
    
    st.markdown(f"""
        <div class="success-card">
            <h1 style="font-size: 5.5rem; margin:0;">🏆</h1>
            <h1 style="color:#9f1239; margin-top:10px;">SELESAI!</h1>
            <h3 style="color:#be123c; font-weight:700;">Terima Kasih, {st.session_state.biodata.get('nama', '')}!</h3>
            <p style="font-size: 1.15rem; color: #4b5563; font-weight:600; margin-bottom:10px;">
                Tipe Tes: {st.session_state.biodata.get('tipe_tes', '')}
            </p>
            <div style="background: white; padding: 20px; border-radius: 15px; margin: 20px 0;">
                <p style="margin:0; font-size: 1.2rem; color: #6b7280;">Skor Anda</p>
                <div class="score-text">{score} / 100</div>
            </div>
            <p style="color:#4b5563;">
                Jawaban Anda telah berhasil disimpan di database penelitian.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Kembali ke Awal"):
        reset_state()
        st.rerun()
