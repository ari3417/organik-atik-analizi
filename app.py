import streamlit as st
from ultralytics import YOLO
from PIL import Image
import os
import base64
from io import BytesIO
import json
import re
from datetime import date, timedelta
import google.generativeai as genai

# 1. Sayfa Ayarları (Sadece bir kez, en üstte çağrılır)
st.set_page_config(page_title="Gıda Kurtarma Tarayıcısı & Rehberi", page_icon="♻️", layout="centered")

# --- GEMINI AI KURULUMU (Kompost Modu İçin) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

# Görselleri HTML içine gömebilmek için dönüştürücü fonksiyon
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- ÖZEL CSS (Tüm Proje İçin Birleşik) ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* ==========================================
       MEVCUT PROJE CSS (SEKME 1 VE 3 İÇİN)
       ========================================== */
    .recipe-card {
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: #333333;
        height: 100%;
        font-family: sans-serif;
    }
    .bg-purple { background-color: #B5B2E5; color: white;}
    .bg-pink { background-color: #FFB7B2; color: #333;}
    .bg-blue { background-color: #AEC6CF; color: #333;}
    .bg-mint { background-color: #B2E2D4; color: #333;}
    .recipe-title { font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 15px; }
    .ingredient-list { font-size: 16px; line-height: 1.8; }

    [data-testid="stImage"] {
        margin-bottom: -55px; 
        position: relative;
        z-index: 1;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 15px;
        position: relative;
        z-index: 99;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 20px !important;
        border: 3px solid white !important;
        padding: 10px 25px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        color: #333 !important;
        font-weight: 800 !important;
        font-size: 16px !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(1) { background-color: #B2E2D4 !important; }
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(2) { background-color: #FFD580 !important; }
    [data-testid="stTabs"] [data-baseweb="tab"]:nth-child(3) { background-color: #FFB7B2 !important; }

    [data-testid="stFileUploader"] section {
        background-color: #A8C9B4 !important;
        border: 2px solid #333 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"] section > div > span { display: none !important; }
    [data-testid="stFileUploader"] small { display: none !important; }

    .mustard-box {
        background-color: #E2A600; border: 2px solid #5A4D2E; border-radius: 10px;
        padding: 10px; height: 100%; min-height: 250px; display: flex;
        flex-direction: column; align-items: center; justify-content: center;
        color: #333; font-weight: bold; text-align: center; font-family: sans-serif;
    }
    .mustard-box img { max-width: 100%; border-radius: 5px; border: 1px solid rgba(0,0,0,0.2); }

    .action-banner {
        background-color: #9A9B7A; color: white; text-align: right; padding: 12px 25px;
        font-size: 20px; font-weight: bold; border-radius: 0px 0px 10px 10px;
        margin-top: 10px; letter-spacing: 1px; font-family: sans-serif;
    }

       /* ==========================================
       HIZLI TEST GALERİSİ
       ========================================== */

    /* Ana satır: HER EKRANDA tek sıra, yatay kaydırmalı */
    .st-key-galeri_wrapper [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 15px !important;
        gap: 8px !important;
        -webkit-overflow-scrolling: touch !important;
    }

    .st-key-galeri_wrapper [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        height: 6px;
    }
    .st-key-galeri_wrapper [data-testid="stHorizontalBlock"]::-webkit-scrollbar-thumb {
        background-color: #A8C9B4;
        border-radius: 10px;
    }

    /* Kolonlar */
    .st-key-galeri_wrapper [data-testid="column"] {
        min-width: 75px !important;
        max-width: 95px !important;
        width: 75px !important;
        flex: 0 0 75px !important;
    }

    /* stImage global stilini sıfırla */
    .st-key-galeri_wrapper [data-testid="stImage"] {
        margin-bottom: 0px !important;
        position: static !important;
        z-index: auto !important;
    }

    .st-key-galeri_wrapper img {
        border-radius: 8px !important;
        width: 100% !important;
        height: auto !important;
    }

    .st-key-galeri_wrapper div[data-testid="stButton"] {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Butonlar: açık gri */
    .st-key-galeri_wrapper button {
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 4px 0 !important;
        min-height: 0 !important;
        height: auto !important;
        line-height: 1.3 !important;
        white-space: nowrap !important;
        background-color: #D5D5D5 !important;
        color: #666 !important;
        border: none !important;
        border-radius: 6px !important;
        cursor: pointer !important;
    }

    .st-key-galeri_wrapper button:hover {
        background-color: #BDBDBD !important;
    }

    /* Seçili buton: koyu gri */
    [class*="st-key-galeri_secili_"] button {
        background-color: #4A4A4A !important;
        color: white !important;
    }

    /* Mobil */
    @media (max-width: 768px) {
        .st-key-galeri_wrapper [data-testid="stHorizontalBlock"] {
            gap: 5px !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
        }
        .st-key-galeri_wrapper [data-testid="column"] {
            min-width: 58px !important;
            max-width: 68px !important;
            width: 58px !important;
            flex: 0 0 58px !important;
        }
        .st-key-galeri_wrapper button {
            font-size: 10px !important;
        }
    }
    /* ==========================================
       YENİ EKLENEN CSS (SADECE SEKME 2 İÇİN)
       ========================================== */
    :root {
      --mustard:   #FFD580;
      --cream:     #FFE9BD;
      --royal:     #464CE6;
      --peri:      #7C80ED;
      --lavender:  #B2B4F4;
      --mist:      #E8E8FC;
      --sage:      #B8CCB6;
      --orange:    #E8650A;
      --dark:      #242428;
      --mid:       #5A5A66;
      --light:     #8A8A98;
      --line:      #EDE8DC;
    }

    .compost-coach-wrapper { font-family: 'Plus Jakarta Sans', sans-serif !important; }

    .hero-card {
      background: linear-gradient(140deg, var(--cream) 0%, var(--mustard) 100%);
      border-radius: 26px; padding: 22px 22px 18px; margin-bottom: 16px;
      position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(232,101,10,0.08);
      margin-top: 20px;
    }

    .hero-title { font-size: 30px; font-weight: 800; letter-spacing: -0.04em; color: var(--dark); line-height: 1.08; position: relative; z-index: 1; }
    .hero-sub { font-size: 13px; color: #666; margin-top: 8px; position: relative; z-index: 1; }

    .c-card {
      background: white; border-radius: 22px; padding: 18px;
      border: 1px solid var(--line); margin-bottom: 14px;
      box-shadow: 0 8px 26px rgba(70,76,230,0.045);
    }
    .c-card-title { font-size: 16px; font-weight: 800; color: var(--dark); margin-bottom: 6px; letter-spacing: -0.02em; }
    .c-card-sub { font-size: 12px; color: var(--mid); line-height: 1.45; margin-bottom: 12px; }
    .c-card-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:10px; }
    .icon-chip { width: 42px; height: 42px; border-radius: 50%; background: var(--cream); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }

    .compost-summary { display:grid; grid-template-columns: 1.15fr .85fr; gap:12px; margin-top:12px; }
    .summary-main { background: linear-gradient(140deg, #FFF2CC, #FFD580); border: 1px solid #F2D18C; border-radius: 20px; padding: 16px; }
    .summary-side { background: #F0F1FF; border: 1px solid #DADCFB; border-radius: 20px; padding: 16px; }
    .summary-label { font-size: 10px; color: var(--light); text-transform: uppercase; letter-spacing: .06em; font-weight: 800; }
    .summary-value { font-size: 30px; font-weight: 800; color: var(--dark); letter-spacing: -.06em; line-height: 1.05; margin-top: 4px; }
    .summary-note { font-size: 11px; color: var(--mid); margin-top: 6px; }

    .journey-row { display: flex; justify-content: space-between; font-size: 11px; color: var(--light); margin: 12px 0 10px; }
    .journey-step.active { color: var(--royal); font-weight: 800; }
    .journey-track { height: 10px; background: var(--mist); border-radius: 999px; overflow: hidden; }
    .journey-fill { height: 100%; background: linear-gradient(90deg, var(--peri), var(--royal)); border-radius: 999px; transition: width 1s ease; }

    .st-key-weekly_goals_card {
      background: linear-gradient(180deg, #FFE9BD 0%, #FFF9EA 100%) !important;
      border: 1.5px solid #FFD580 !important; border-radius: 24px !important; padding: 18px !important; margin-top: 14px !important; margin-bottom: 16px !important;
    }
    .goal-title-row { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-bottom: 10px; }
    .goal-title { font-size: 16px; font-weight: 800; color: var(--dark); }
    .goal-progress { font-size: 11px; color: var(--royal); font-weight: 800; }

    .analysis-ready { background: #F0F1FF; border: 1px solid #DADCFB; color: var(--royal); border-radius: 20px; padding: 15px 16px; margin-bottom: 14px; font-size: 13px; font-weight: 800; }
    
    .health-card { background: var(--mustard); border-radius: 24px; padding: 20px; margin-bottom: 14px; display: flex; align-items: center; gap: 16px; }
    .health-icon-small { width:56px; height:56px; border-radius:50%; background:#FFE9BD; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
    .health-text-block h4 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #7A5E20; font-weight: 800; margin: 0; }
    .health-score-num { font-size: 52px; font-weight: 800; color: var(--dark); line-height: 1; margin: 2px 0; letter-spacing: -0.06em; }
    .health-status-label { font-size: 12px; color: #7A5E20; font-weight: 700; }

    .coach-card { background: white; border: 1px solid var(--line); border-radius: 22px; padding: 18px; margin-bottom: 14px; }
    .coach-label { font-size: 10px; color: var(--light); text-transform: uppercase; letter-spacing: .07em; font-weight: 800; margin-bottom: 7px; }
    .coach-text { font-size: 14px; color: var(--dark); line-height: 1.45; font-weight: 700; }

    .metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 14px; }
    .metric-card { background: white; border-radius: 18px; padding: 14px; border: 1px solid var(--line); }
    .metric-label { font-size: 10px; color: var(--light); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 800; margin-bottom: 4px; }
    .metric-value { font-size: 20px; font-weight: 800; color: var(--dark); letter-spacing: -0.04em; }

    .maturity-card { background: white; border-radius: 20px; padding: 16px 18px; margin-bottom: 14px; border: 1px solid var(--line); }
    .maturity-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
    .maturity-label { font-size: 10px; color: var(--light); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 800; }
    .maturity-value { font-size: 14px; color: var(--royal); font-weight: 800; }
    .maturity-track { height: 8px; background: var(--mist); border-radius: 99px; overflow: hidden; margin-bottom: 10px; }
    .maturity-fill { height: 100%; background: linear-gradient(90deg, var(--peri), var(--royal)); border-radius: 99px; }

    .sheet-card { background: white; border-radius: 22px; border: 2px solid var(--mist); padding: 18px 18px 16px; margin: 10px 0 14px; }
    .sheet-title { font-size: 18px; font-weight: 800; color: var(--royal); letter-spacing: -0.03em; margin-bottom: 12px; }
    .sheet-item { display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; font-size:13px; color:var(--mid); line-height:1.5; }
    .bullet-tri { border-left: 6px solid #464CE6; border-top: 4px solid transparent; border-bottom: 4px solid transparent; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# 2. LOGO YÜKLEME
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.title("🌱 GIDA KURTARMA TARAYICISI & REHBERİ")

# Modeli yükleme
@st.cache_resource
def load_model():
    return YOLO('best.pt')

model = load_model()

# ==========================================
# KOMPOST KOÇU YARDIMCI FONKSİYONLAR (SEKME 2 İÇİN)
# ==========================================
HERO_SVG = """<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:44px;height:44px;margin-bottom:8px">
  <circle cx="22" cy="22" r="20" fill="#FFD580" opacity="0.5"/>
  <path d="M22 34 L22 20" stroke="#5A8A40" stroke-width="2" stroke-linecap="round"/>
  <path d="M22 24 Q16 20 14 14 Q20 13 24 18 Q26 20 22 24Z" fill="#7ABD5A"/>
  <path d="M22 28 Q28 24 30 18 Q24 16 20 22 Q19 24 22 28Z" fill="#5A8A40"/>
</svg>"""
SPROUT_SVG = """<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:30px;height:30px">
  <path d="M22 34 L22 19" stroke="#5A8A40" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M22 22 Q15 18 14 11 Q21 11 25 17 Q26 20 22 22Z" fill="#7ABD5A"/>
  <path d="M22 27 Q29 22 31 15 Q24 14 20 21 Q19 24 22 27Z" fill="#5A8A40"/>
</svg>"""
MOISTURE_SVG = """<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <path d="M13 4 Q10 8 8 12 Q6 16 8 20 Q10 24 13 24 Q16 24 18 20 Q20 16 18 12 Q16 8 13 4Z" fill="#B2D4F4" stroke="#464CE6" stroke-width="1.2"/>
</svg>"""
BALANCE_SVG = """<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <rect x="4" y="14" width="7" height="8" rx="2" fill="#B8CCB6" stroke="#5A8A40" stroke-width="1.2"/>
  <rect x="15" y="10" width="7" height="12" rx="2" fill="#FFD580" stroke="#C8A020" stroke-width="1.2"/>
  <path d="M2 22 L24 22" stroke="#ccc" stroke-width="1"/>
</svg>"""

def score_label(score: int) -> str:
    if score >= 80: return "İyi durumda"
    if score >= 60: return "Geliştirilebilir"
    if score >= 40: return "Dikkat gerekli"
    return "Hemen müdahale"

def parse_months(ready_in_str: str) -> tuple[float, float]:
    text = str(ready_in_str).lower().replace("-", " ")
    nums = [int(s) for s in text.split() if s.isdigit()]
    if nums:
        low = nums[0]
        high = nums[-1] if len(nums) > 1 else low
        avg = (low + high) / 2
        return max(0.05, min(0.95, 1 - (avg / 12))), avg
    return 0.3, 4

def tri(color: str) -> str:
    return f'<span class="bullet-tri" style="border-left-color:{color}"></span>'

def turning_interval_days(c_type: str) -> int:
    if "Sıcak" in c_type: return 3
    if "Bahçe" in c_type: return 7
    return 10

def turning_message(days: int) -> str:
    if days < 0: return f"{abs(days)} gün gecikti"
    if days == 0: return "Bugün"
    if days == 1: return "Yarın"
    return f"{days} gün sonra"

def last_turn_message(days: int) -> str:
    if days == 0: return "Bugün"
    if days == 1: return "Dün"
    return f"{days} gün önce"

def normalize_list(val, limit=3):
    if not val: return []
    if isinstance(val, str): val = [val]
    return [str(i).strip() for i in val if str(i).strip()][:limit]

def normalize_ai_data(data: dict) -> dict:
    issue = data.get("issue") or data.get("main_issue") or "Belirgin sorun yok"
    problems = normalize_list(data.get("detected_problems") or data.get("problems"), 3)
    recs = normalize_list(data.get("recommendations"), 3)
    score = int(data.get("health_score", 60))
    score = max(0, min(100, score))
    return {
        "health_score": score,
        "moisture": data.get("moisture", "Belirsiz"),
        "balance": data.get("balance", "Belirsiz"),
        "ready_in": data.get("ready_in", "3-6 ay"),
        "current_status": str(data.get("current_status", "İzlenebilir durumda.")).strip(),
        "moisture_check": str(data.get("moisture_check", "Nemi kontrol edin.")).strip(),
        "carbon_nitrogen_note": str(data.get("carbon_nitrogen_note", "Dengeyi koruyun.")).strip(),
        "issue": str(issue).strip(),
        "detected_problems": problems or [str(issue).strip()],
        "recommendations": recs or ["Karıştırın."],
        "coach_note": str(data.get("coach_note", "İzlemeye devam edin.")).strip(),
    }

def make_weekly_goals(ai_data, days_until, c_type, odor) -> list[str]:
    goals = []
    if days_until <= 3: goals.append("Kompostu çevir")
    if odor == "Belirgin": goals.append("Havalandırmayı artır")
    elif odor == "Hafif": goals.append("Kompostu karıştır")
    if ai_data:
        m = ai_data.get("moisture", "")
        if m == "Kuru": goals.extend(["Bir miktar su ekle", "Nemi kontrol et"])
        elif m == "Islak": goals.extend(["Kuru yaprak/karton ekle", "Nemi kontrol et"])
        bal = ai_data.get("balance", "")
        if bal == "Karbon Fazla": goals.append("Yeşil atık artır")
        elif bal == "Azot Fazla": goals.append("Kahverengi ekle")
    else:
        goals.extend(["İlk fotoğraf analizini yap", "Koku durumunu kontrol et"])
    unique = []
    for g in goals:
        if g not in unique: unique.append(g)
    return unique[:3]

def goal_completion(g_list):
    done = sum(1 for g in g_list if st.session_state.goal_done.get(g, False))
    return done, len(g_list), done / max(1, len(g_list))

def journey_progress(age, c_type, h_score, g_ratio):
    tot = 90 if "Sıcak" in c_type else 180
    pct = int((age/tot)*100*0.5 + (h_score or 70)*0.3 + (g_ratio*100)*0.2)
    pct = max(8, min(95, pct))
    stage = "Başlangıç" if pct < 25 else "Aktif" if pct < 65 else "Olgunlaşma" if pct < 90 else "Hazır"
    return stage, pct

def analyze_compost_image(img, c_type, start, age, stage, last_t, days_since, days_until, amount, odor):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are Smart Compost Coach. Analyze compost image. Return ONLY valid JSON.
    {{ "health_score": 0, "moisture": "Kuru|Optimal|Islak", "balance": "Karbon Fazla|Dengeli|Azot Fazla", "ready_in": "2-3 ay", "current_status": "Tr sentence", "moisture_check": "Tr sentence", "carbon_nitrogen_note": "Tr sentence", "issue": "Short tr issue", "detected_problems": ["Tr bullet 1"], "recommendations": ["Tr action 1"], "coach_note": "Tr note" }}
    Data: Type:{c_type}, Age:{age} days, Stage:{stage}, Next turn in:{days_until} days, Odor:{odor}"""
    resp = model.generate_content([prompt, img])
    
    b_tick = "`" * 3
    cleaned = resp.text.strip().replace(b_tick + "json", "").replace(b_tick, "").strip()
    
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match: cleaned = match.group(0)
    return normalize_ai_data(json.loads(cleaned))

# --- SESSION DEFAULTS ---
today = date.today()
for k, v in {"c_type": "Ev tipi / soğuk kompost", "start_date": today - timedelta(days=22), "last_turn": today - timedelta(days=3), "amount": 2.0, "odor": "Yok", "ai_data": None, "ai_image": None, "goal_done": {}, "goal_sig": "", "analysis_ready": False}.items():
    if k not in st.session_state: st.session_state[k] = v

age_d = max(0, (today - st.session_state.start_date).days)
turn_int = turning_interval_days(st.session_state.c_type)
since_t = max(0, (today - st.session_state.last_turn).days)
until_t = (st.session_state.last_turn + timedelta(days=turn_int) - today).days
c_goals = make_weekly_goals(st.session_state.ai_data, until_t, st.session_state.c_type, st.session_state.odor)
sig = "|".join(c_goals)
if st.session_state.goal_sig != sig:
    st.session_state.goal_sig = sig
    st.session_state.goal_done = {g: False for g in c_goals}
g_done, g_tot, g_rat = goal_completion(c_goals)
j_stage, j_pct = journey_progress(age_d, st.session_state.c_type, st.session_state.ai_data.get("health_score") if st.session_state.ai_data else None, g_rat)

@st.dialog("📷 Kompostunu Analiz Et")
def analysis_dialog():
    ufile = st.file_uploader("Fotoğraf yükle", type=["jpg", "png"])
    if ufile: st.image(Image.open(ufile))
    c1, c2 = st.columns([3, 1])
    if c2.button("Kapat"): st.rerun()
    if c1.button("🔍 Analiz Et", type="primary"):
        if not ufile: return st.warning("Fotoğraf yükleyin.")
        with st.spinner("Analiz ediliyor..."):
            try:
                img = Image.open(ufile)
                st.session_state.ai_data = analyze_compost_image(img, st.session_state.c_type, st.session_state.start_date, age_d, j_stage, st.session_state.last_turn, since_t, until_t, st.session_state.amount, st.session_state.odor)
                st.session_state.ai_image = img.copy()
                st.session_state.analysis_ready = True
                st.session_state.goal_sig = ""
                st.rerun()
            except Exception as e: st.error(f"Hata: {e}")

@st.dialog("🌱 Kompost Bilgileri")
def edit_dialog():
    with st.form("c_form"):
        ntype = st.selectbox("Tipi", ["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"], index=0)
        c1, c2 = st.columns(2)
        ns = c1.date_input("Başlangıç", value=st.session_state.start_date)
        nl = c2.date_input("Son Çevirme", value=st.session_state.last_turn)
        namt = st.number_input("Miktar (kg)", value=float(st.session_state.amount))
        nod = st.radio("Koku", ["Yok", "Hafif", "Belirgin"], index=["Yok", "Hafif", "Belirgin"].index(st.session_state.odor), horizontal=True)
        if st.form_submit_button("✓ Kaydet", type="primary"):
            st.session_state.update({"c_type": ntype, "start_date": ns, "last_turn": nl, "amount": namt, "odor": nod, "goal_sig": ""})
            st.rerun()

@st.dialog("📊 Analiz Sonuçları")
def results_dialog():
    d = st.session_state.ai_data
    if not d: return st.info("Sonuç yok.")
    st.markdown(f'<div class="health-card"><div class="health-icon-small">{SPROUT_SVG}</div><div class="health-text-block"><h4>Health Score</h4><div class="health-score-num">{d["health_score"]}<span>/100</span></div><div class="health-status-label">{score_label(d["health_score"])}</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="coach-card"><div class="coach-label">AI Coach</div><div class="coach-text">{d["coach_note"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metrics-grid"><div class="metric-card">{MOISTURE_SVG}<div class="metric-label">Nem</div><div class="metric-value">{d["moisture"]}</div></div><div class="metric-card">{BALANCE_SVG}<div class="metric-label">Denge</div><div class="metric-value">{d["balance"]}</div></div></div>', unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["Durum", "Problem", "Öneri", "Fotoğraf"])
    with t1: st.markdown(f'<div class="sheet-card"><div class="sheet-item">{tri("#464CE6")}<span>{d["current_status"]}</span></div><div class="sheet-item">{tri("#7C80ED")}<span>{d["moisture_check"]}</span></div><div class="sheet-item">{tri("#B8CCB6")}<span>{d["carbon_nitrogen_note"]}</span></div></div>', unsafe_allow_html=True)
    with t2: st.markdown('<div class="sheet-card">' + "".join([f'<div class="sheet-item">{tri("#E8A020")}<span>{p}</span></div>' for p in d["detected_problems"]]) + '</div>', unsafe_allow_html=True)
    with t3: st.markdown('<div class="sheet-card">' + "".join([f'<div class="sheet-item">{tri("#7C80ED")}<span>{r}</span></div>' for r in d["recommendations"]]) + '</div>', unsafe_allow_html=True)
    with t4:
        if st.session_state.ai_image: st.image(st.session_state.ai_image)

# 3. Sekmelerin (Tabs) Oluşturulması
tab1, tab2, tab3 = st.tabs(["📸 Kurtarma Tarayıcısı", "🍂 Kompost Modu", "📖 Eğitim Desteği"])

# ==========================================
# SEKME 1: AYRIŞTIRMA VE TARİFLER
# ==========================================
with tab1:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Üst Panel: Tam genişlikte başlık ve yükleme alanı
    st.markdown("""
    <div style="font-family: 'Arial Black', sans-serif; font-size: 42px; color: #A8C9B4; line-height: 1; margin-bottom: 20px; letter-spacing: -1px; text-align: center;">
        KURTARILACAK ÜRÜNÜ TARAYIN
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], key="scanner", label_visibility="collapsed")
    
    st.markdown("""
    <div style="font-size: 14px; color: #555; margin-top: 15px; margin-bottom: 10px; line-height: 1.4; text-align: center;">
        Yumuşamış veya hasar görmüş meyvenizin fotoğrafını yükleyin, sistem onu tanıp size özel harika bir sıfır atık tarifi sunsun.
    </div>
    """, unsafe_allow_html=True)

    # --- ÖRNEK FOTOĞRAF GALERİSİ BAŞLANGICI ---
    if "secilen_ornek" not in st.session_state:
        st.session_state.secilen_ornek = None

    tum_ornek_fotolar = [
        "curumus_elma.png", "curumus_muz.png", "curumus_portakal.png", "curumus_domates.jpg", "curumus_salatalik.png",
        "kurtarilabilecek_elma.png", "kurtarilabilecek_muz.png", "kurtarilabilecek_portakal.png", "kurtarilabilecek_domates.jpg", "kurtarilabilecek_salatalik.png",
        "taze_elma.png", "taze_muz.png", "taze_portakal.png", "taze_domates.png", "taze_salatalik.png"
    ]

    mevcut_fotolar = [f for f in tum_ornek_fotolar if os.path.exists(f)]

    def secim_yap(foto):
        st.session_state.secilen_ornek = foto

    if mevcut_fotolar:
        st.markdown("<p style='text-align:center; font-size:13px; font-weight:bold; color:#A8C9B4; margin-bottom:5px;'>Hızlı Taramak İçin Fotoğraflardan Birine Tıklayın:</p>", unsafe_allow_html=True)
        
        with st.container(key="galeri_wrapper"):
            galeri_kolonlari = st.columns(len(mevcut_fotolar))
            
            for i, ornek_foto in enumerate(mevcut_fotolar):
                with galeri_kolonlari[i]:
                    is_secili = (st.session_state.secilen_ornek == ornek_foto)
                    wrapper_key = f"galeri_secili_{i}" if is_secili else f"galeri_{i}"
                    with st.container(key=wrapper_key):
                        st.image(ornek_foto, use_container_width=True)
                        st.button("Seç", key=f"sec_{ornek_foto}", on_click=secim_yap, args=(ornek_foto,), use_container_width=True)
                    
    st.markdown("<br>", unsafe_allow_html=True)
    # --- ÖRNEK FOTOĞRAF GALERİSİ BİTİŞİ ---

    # Alt Panel: İki büyük sarı kutu
    col1, col2 = st.columns(2, gap="large")

    # İşlenecek Görüntü Mantığı (Kullanıcı kendi mi yükledi, yoksa örnek mi seçti?)
    islenecek_resim = None
    if uploaded_file is not None:
        islenecek_resim = Image.open(uploaded_file)
        st.session_state.secilen_ornek = None # Kendisi yüklerse örnek seçimi sıfırla
    elif st.session_state.secilen_ornek is not None:
        islenecek_resim = Image.open(st.session_state.secilen_ornek)

    # Görüntü Kutuları Yönetimi
    if islenecek_resim is None:
        with col1:
            st.markdown('<div class="mustard-box">Seçilen fotoğraf</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="mustard-box">AI Taraması</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="action-banner">AKSİYON PLANI (HASAR ORANI: - )</div>', unsafe_allow_html=True)

    else:
        image = islenecek_resim
        img_b64 = image_to_base64(image)
        
        st.write("🔄 Yapay zeka görüntüyü işliyor...")
        results = model(image, conf=0.20)
        
        toplam_meyve_alani = 0
        toplam_bozuk_alan = 0
        tespit_edilen_urunler = []
        
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                alan = (x2 - x1) * (y2 - y1)
                
                sinif_id = int(box.cls[0])
                sinif_adi = model.names[sinif_id]
                
                if sinif_adi == 'bozuk_kısım':
                    toplam_bozuk_alan += alan
                else:
                    toplam_meyve_alani += alan
                    if sinif_adi not in tespit_edilen_urunler:
                        tespit_edilen_urunler.append(sinif_adi)
            
            res_plotted = result.plot()[:, :, ::-1]
            res_img = Image.fromarray(res_plotted)
            res_b64 = image_to_base64(res_img)
            
            with col1:
                st.markdown(f'''
                <div class="mustard-box">
                    <div style="margin-bottom:10px;">Seçilen fotoğraf</div>
                    <img src="data:image/png;base64,{img_b64}">
                </div>
                ''', unsafe_allow_html=True)
            with col2:
                st.markdown(f'''
                <div class="mustard-box">
                    <div style="margin-bottom:10px;">AI Taraması</div>
                    <img src="data:image/png;base64,{res_b64}">
                </div>
                ''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- MATEMATİK VE AKSİYON PLANI ---
        if len(tespit_edilen_urunler) > 0:
            urun_ismi = ", ".join(tespit_edilen_urunler).upper()
            bozukluk_orani = (toplam_bozuk_alan / toplam_meyve_alani) * 100 if toplam_meyve_alani > 0 else 100
            if bozukluk_orani > 100: bozukluk_orani = 100.0
            
            st.markdown(f'<div class="action-banner">AKSİYON PLANI (HASAR ORANI: %{bozukluk_orani:.1f})</div><br>', unsafe_allow_html=True)
            
            if bozukluk_orani <= 5.0:
                st.success("**Kategori: Doğrudan Yeniden Dağıtım (Taze Tüketim)**")
                st.write("Ürün kusursuz veya kusura çok yakın. Taze olarak tüketime veya gıda bankalarına gönderilmeye tamamen uygundur.")
                
            elif bozukluk_orani <= 45.0:
                st.warning("**Kategori: Yenilebilir Geri Kazanım (Sıfır Atık İleri Dönüşüm)**")
                st.write("Hasarlı kısımları kestikten sonra kalan temiz bölümlerle maksimum verim elde edebileceğiniz tarifler:")
                
                # --- DİNAMİK YAPAY ZEKA TARİFLERİ ---
                
                if "portakal" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-purple">
                        <div class="recipe-title">🍊 Sihirli Portakal Kabuğu Şekerlemesi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🔪 3 Adet Portakalın Kabuğu<br>
                            🧊 2 Su Bardağı Şeker<br>
                            💧 1 Su Bardağı Su<br>
                            🍋 Çeyrek Limon Suyu
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Portakal kabuklarını ince uzun şeritler halinde doğrayın.</li>
                            <li>Acısını almak için suda 3 kez kaynatıp süzün.</li>
                            <li>Şeker ve su ile hazırladığınız şerbette kabukları şeffaflaşana kadar kaynatın.</li>
                            <li>Son olarak limon suyunu ekleyip yağlı kağıda dizerek kurutun.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=lhbUMg1Swbo") 
                    
                    st.markdown("""
                    <div class="recipe-card bg-purple">
                        <div class="recipe-title">🍊 Doğal Yüzey Temizleyici Sirke</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍊 Sıkılmış portakal/limon kabukları<br>
                            🥃 Beyaz Sirke<br>
                            🫙 Büyük Cam Kavanoz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Kullanılmış narenciye kabuklarını kavanoza ağzına kadar doldurun.</li>
                            <li>Üzerini tamamen geçecek kadar beyaz sirke ekleyin ve kapağını sıkıca kapatın.</li>
                            <li>2 hafta boyunca karanlık bir dolapta bekletip süzün.</li>
                            <li>Sprey şişesine alıp yarı yarıya suyla seyrelterek mutfak tezgahlarında kullanın!</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "muz" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍌 Rafinesiz Muzlu Vegan Dondurma</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍌 2 Adet Kararmış (Çok Olgun) Muz<br>
                            🥜 1 Yemek Kaşığı Fıstık Ezmesi<br>
                            🍫 1 Tatlı Kaşığı Kakao<br>
                            🥛 Yarım Çay Bardağı Süt
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Kararmış muzların kabuklarını soyup dilimleyin ve dondurucuda 4 saat dondurun.</li>
                            <li>Donmuş muzları blender'a alın.</li>
                            <li>Üzerine fıstık ezmesi, kakao ve sütü ekleyip kremsi bir kıvam alana kadar çekin.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=HYQaK-6-9L4")
                    
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍌 Muz Kabuğu Sıvı Bitki Gübresi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍌 Tüketilmiş muzların kabukları<br>
                            💧 1 Litre İçme Suyu<br>
                            🫙 Geniş Cam Kavanoz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Muz kabuklarını makasla küçük parçalar halinde doğrayın.</li>
                            <li>Kavanoza alıp üzerine suyu ekleyin ve kapağını kapatın.</li>
                            <li>24-48 saat oda sıcaklığında bekletin.</li>
                            <li>Bu potasyum zengini suyu süzerek ev bitkilerinizi sulamak için kullanın (Kalan kabukları komposta atın!).</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                if "elma" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-mint">
                        <div class="recipe-title">🍏 Probiyotik Elma Kabuğu Sirkesi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍎 Tüketilmeyecek elma kabukları ve çekirdekleri<br>
                            💧 1 Litre İçme Suyu<br>
                            🍯 1 Yemek Kaşığı Bal veya Şeker<br>
                            🫙 1 Büyük Cam Kavanoz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Kavanozun yarısına kadar elma artıklarını doldurun.</li>
                            <li>Üzerine suyu ve tatlandırıcıyı ekleyip tahta kaşıkla karıştırın.</li>
                            <li>İlk 10 gün her gün karıştırın. 20 gün sonra süzün.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    st.video("https://www.youtube.com/watch?v=eE0I39eGMQA")
                    
                    st.markdown("""
                    <div class="recipe-card bg-mint">
                        <div class="recipe-title">🍏 Tarçınlı Fırın Elma Cipsi</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍎 Yumuşamış elmalar<br>
                            🍂 Toz Tarçın<br>
                            🍋 Çeyrek Limonun Suyu
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Elmaları kararmaması için limonlu suda bekleterek çok ince halkalar halinde dilimleyin.</li>
                            <li>Yağlı kağıt serili tepsiye dizip üzerlerine tarçın serpin.</li>
                            <li>100 derece fırında iyice kuruyana kadar (yaklaşık 1.5 - 2 saat) pişirin.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "domates" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-pink">
                        <div class="recipe-title">🍅 Fırınlanmış Konsantre Domates Sosu</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🍅 Yumuşamış domatesler<br>
                            🫒 3 Yemek Kaşığı Zeytinyağı<br>
                            🧄 2 Diş Sarımsak<br>
                            🌿 Kekik ve Tuz
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Domatesleri iri parçalara bölün ve fırın tepsisine dizin.</li>
                            <li>Üzerine zeytinyağı, sarımsak ve baharatları gezdirin.</li>
                            <li>200 derece fırında suları hafif çekip karamelize olana kadar pişirin.</li>
                            <li>Fırından çıkınca blenderdan geçirip kavanozlayın.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                if "salatalık" in tespit_edilen_urunler:
                    st.markdown("""
                    <div class="recipe-card bg-blue">
                        <div class="recipe-title">🥒 Sıfır Atık Detoks & Cilt Toniği</div>
                        <div class="ingredient-list">
                            <b>Malzemeler:</b><br>
                            🥒 Pörsümüş salatalık ve sap kısımları<br>
                            🍋 Yarım Limon<br>
                            🌿 Taze Nane<br>
                            💧 İçme Suyu
                        </div>
                        <hr>
                        <b>Adımlar:</b>
                        <ul>
                            <li>Salatalığın orta kısımlarını halka doğrayıp limon ve nane ile sürahiye atın (İçme suyu için).</li>
                            <li>Tüketilmeyen uç kısımlarını ve kabuklarını blenderdan geçirin.</li>
                            <li>Çıkan saf salatalık suyunu süzüp buz kalıplarına dondurun.</li>
                            <li>Sabahları yüzünüzde gezdirerek doğal tonik olarak kullanın!</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

                # KOMPOST POTANSİYELİ HESAPLAYICI
                if bozukluk_orani > 0:
                    tahmini_atik_gr = int((bozukluk_orani / 100) * 150) 
                    tahmini_gubre_gr = int(tahmini_atik_gr * 0.4) 
                    if tahmini_atik_gr > 0:
                        st.markdown(f"""
                        <div style="background-color: #E8F5E9; border: 2px solid #4CAF50; padding: 20px; border-radius: 15px; margin-top: 20px; color: #2E7D32;">
                            <h4 style="margin-top:0px; margin-bottom: 10px; color: #2E7D32;">🌱 Kesilen Çürükler İçin Kompost Potansiyeli</h4>
                            <span style="font-size: 16px; line-height: 1.6;">
                                Yukarıdaki tarifleri uygularken kestiğiniz <b>%{bozukluk_orani:.1f}</b>'lik hasarlı kısım (ortalama bir porsiyon meyvede yaklaşık <b>{tahmini_atik_gr} gram</b> organik atığa denk gelir) çöpe gitmek yerine kompost kutunuza eklendiğinde, bitkileriniz için <b>~{tahmini_gubre_gr} gram</b> besin değeri yüksek, saf organik gübreye (humus) dönüşecektir. Lütfen bu kısımları çöpe değil, toprağa kazandırın!
                            </span>
                        </div>
                        """, unsafe_allow_html=True)

            elif bozukluk_orani <= 80.0:
                st.error("**Kategori: Kompost (Organik Gübre)**")
                st.write(f"Bu {urun_ismi.lower()} tüketim limitlerini aşmış durumda. Lütfen 'Kompost Modu' sekmesine geçerek bu ürünü toprağa nasıl geri kazandıracağınızı öğrenin.")
            else:
                st.error("**Kategori: Güvenli Olmayan Atık**")
                st.write("Aşırı çürüme veya küflenme tespit edildi. Standart yığın kompostuna atmak patojen riski taşıyabilir. Kahverengi çöp kutusuna atın.")

        elif toplam_bozuk_alan > 0:
            st.info("Sistem sadece hasarlı bölgeyi algıladı ancak meyvenin türünü net olarak tanıyamadığı için özel bir tarif sunamıyor.")
        else:
            st.info("Sistem bu fotoğrafta net bir ürün tanıyamadı.")

    # --- SABİT (HER ZAMAN GÖRÜNEN) GENEL TARİFLER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📚 Fotoğraf Yüklemeden Yapabileceğiniz Klasikler")
    st.markdown("Evinizde birikmeye başlayan meyve ve sebzeler için israfı önleyen, uzun ömürlü temel teknikler.")
    
    # SATIR 1
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("""
        <div class="recipe-card bg-blue">
            <div class="recipe-title">🥒 Hızlı Turşu Kurulumu</div>
            <p>Hafif pörsümüş her türlü sebzeyi (salatalık, havuç, lahana) kurtarın.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🫙 Cam Kavanoz<br>
                🧅 Sarımsak & Nohut<br>
                🧂 2 YK Kaya Tuzu<br>
                🥃 1 Çay Bardağı Sirke<br>
                💧 Kaynar Su
            </div><br>
            <p><b>Yapılışı:</b> Sebzeleri sıkıca dizin. Tuzu, sirkeyi ekleyip üzerine kaynar suyu dökün. Kapağı sıkıca kapatıp ters çevirin. 10 günde hazır!</p>
        </div>
        """, unsafe_allow_html=True)
        
    with row1_col2:
        st.markdown("""
        <div class="recipe-card bg-pink">
            <div class="recipe-title">🍓 Evrensel Meyve Reçeli</div>
            <p>Yumuşamış ve taze yenmeyecek tüm meyveler için standart formül.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🍑 1 Ölçü Meyve<br>
                🍚 1 Ölçü Şeker<br>
                🍋 Çeyrek Limon Suyu
            </div><br>
            <p><b>Yapılışı:</b> Meyveleri doğrayıp akşamdan şekerle bekletin. Sabah kendi suyuyla kıvam alana kadar kaynatın. Kapatmadan hemen önce limon suyunu ekleyin.</p>
        </div>
        """, unsafe_allow_html=True)

    # SATIR 2
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.markdown("""
        <div class="recipe-card bg-mint">
            <div class="recipe-title">🍵 Atık Sebze Suyu (Bulyon)</div>
            <p>Yemek yaparken ayırdığınız yıkanmış sebze kabuklarını ve köklerini değerlendirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥬 Biriktirilmiş Sebze Artıkları (Havuç ucu, soğan kabuğu vb.)<br>
                💧 2 Litre Su<br>
                🧄 3 Diş Sarımsak<br>
                🌿 Defne Yaprağı & Karabiber
            </div><br>
            <p><b>Yapılışı:</b> Tüm malzemeleri tencereye alın. 1 saat kaynatın. Süzüp kavanozlayın ve buzdolabına kaldırın. Çorba ve pilavlarda bulyon olarak kullanın.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with row2_col2:
        st.markdown("""
        <div class="recipe-card bg-purple">
            <div class="recipe-title">🥔 Baharatlı Kabuk Cipsi</div>
            <p>Soyduğunuz patates, havuç ve elma kabuklarını çöpe atmak yerine çıtır bir atıştırmalığa dönüştürün.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥕 Kalın soyulmuş sebze/meyve kabukları<br>
                🫒 2 Yemek Kaşığı Zeytinyağı<br>
                🧂 Tuz ve Karabiber<br>
                🌶️ Toz Kırmızı Biber
            </div><br>
            <p><b>Yapılışı:</b> Kabukları yıkayıp iyice kurulayın. Yağ ve baharatlarla harmanlayıp yağlı kağıt serili tepsiye dizin. 180° fırında 10-15 dk çıtırlaşana kadar pişirin.</p>
        </div>
        """, unsafe_allow_html=True)

    # SATIR 3
    row3_col1, row3_col2 = st.columns(2)
    with row3_col1:
        st.markdown("""
        <div class="recipe-card bg-pink">
            <div class="recipe-title">🌿 Solmuş Yeşillik Pesto Sosu</div>
            <p>Formunu kaybetmiş taze otları veya turp/havuç saplarını harika bir makarna sosuna çevirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🥬 Pörsümüş yeşillikler (maydanoz, fesleğen, roka)<br>
                🫒 Yarım Çay Bardağı Zeytinyağı<br>
                🧄 2 Diş Sarımsak<br>
                🥜 Ceviz veya Fındık
            </div><br>
            <p><b>Yapılışı:</b> Bütün malzemeleri mutfak robotuna alın. Pürüzsüz bir sos kıvamına gelene kadar çekin. Cam kavanozda üzerine zeytinyağı dökerek dolapta 1 hafta saklayabilirsiniz.</p>
        </div>
        """, unsafe_allow_html=True)

    with row3_col2:
        st.markdown("""
        <div class="recipe-card bg-blue">
            <div class="recipe-title">☕ Kurutulmuş Meyve Çayı</div>
            <p>Yenmeyen elma, armut, ayva kabuklarını ve portakal dilimlerini kış çayı yapmak için değerlendirin.</p>
            <div class="ingredient-list">
                <b>Malzemeler:</b><br>
                🍎 Temiz meyve kabukları ve çekirdek yuvaları<br>
                🍂 Çubuk Tarçın<br>
                🌸 Karanfil<br>
                💧 Kaynar Su
            </div><br>
            <p><b>Yapılışı:</b> Kabukları fırında veya kış güneşi gören bir yerde tamamen kurutun. İhtiyacınız olduğunda demliğe bir avuç atıp üzerine sıcak su, tarçın ve karanfil ekleyerek 10 dk demlendirin.</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# SEKME 2: KOMPOST MODU (YENİ SMART COACH ENTEGRASYONU)
# ==========================================
with tab2:
    st.markdown('<div class="compost-coach-wrapper">', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="hero-card">
      <div style="position:relative;z-index:1">
        {HERO_SVG}
        <div class="hero-title">Smart Compost<br>Coach</div>
        <div class="hero-sub">Kompostunu takip et, fotoğrafla analiz et.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="c-card">
      <div class="c-card-head">
        <div>
          <div class="c-card-title">My Compost</div>
          <div class="c-card-sub">Kompostunun gelişimini takip et ve bakım önerilerini kişiselleştir.</div>
        </div>
        <div class="icon-chip">{SPROUT_SVG}</div>
      </div>
      <div class="compost-summary">
        <div class="summary-main">
          <div class="summary-label">Kompost Yaşı</div>
          <div class="summary-value">{age_d} gün</div>
          <div class="summary-note">{j_stage} dönemi</div>
        </div>
        <div class="summary-side">
          <div class="summary-label">Sonraki Çevirme</div>
          <div class="summary-value" style="font-size:22px;letter-spacing:-.04em;">{turning_message(until_t)}</div>
          <div class="summary-note">Son çevirme: {last_turn_message(since_t)}</div>
        </div>
      </div>
      <div class="c-card-title" style="font-size:15px;margin-top:16px;">Compost Journey</div>
      <div class="journey-row">
        <span class="journey-step {'active' if j_stage == 'Başlangıç' else ''}">Başlangıç</span>
        <span class="journey-step {'active' if j_stage == 'Aktif' else ''}">Aktif</span>
        <span class="journey-step {'active' if j_stage == 'Olgunlaşma' else ''}">Olgunlaşma</span>
        <span class="journey-step {'active' if j_stage == 'Hazır' else ''}">Hazır</span>
      </div>
      <div class="journey-track">
        <div class="journey-fill" style="width:{j_pct}%"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Kompost Bilgileri", use_container_width=True):
        edit_dialog()
        
    c1, c2 = st.columns(2)
    c1.button(st.session_state.c_type, use_container_width=True, disabled=True)
    c2.button(f"Yaklaşık {st.session_state.amount:.1f} kg", use_container_width=True, disabled=True)
    
    if st.button("📷 Kompostunu Analiz Et", type="primary", use_container_width=True):
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Lütfen uygulamanın secrets bölümüne GEMINI_API_KEY ekleyin.")
        else:
            analysis_dialog()

    if st.session_state.analysis_ready and st.session_state.ai_data:
        st.markdown('<div class="analysis-ready">Analiz tamamlandı. Sonuçları ayrı panelde inceleyebilirsin.</div>', unsafe_allow_html=True)
        if st.button("📊 Analiz Sonuçlarını İncele", use_container_width=True):
            results_dialog()

    st.markdown(f'<div class="goal-title-row" style="margin-top:20px; margin-bottom:6px;"><div class="goal-title">Bu Haftanın Hedefleri</div><div class="goal-progress">{g_done}/{g_tot} tamamlandı</div></div>', unsafe_allow_html=True)
    
    for idx, goal in enumerate(c_goals):
        k = f"goal_{idx}_{abs(hash(goal))}"
        curr = bool(st.session_state.goal_done.get(goal, False))
        chk = st.checkbox(goal, value=curr, key=k)
        if chk != curr:
            st.session_state.goal_done[goal] = chk
            if chk and goal == "Kompostu çevir":
                st.session_state.last_turn = date.today()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SEKME 3: EĞİTİM DESTEĞİ
# ==========================================
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("Öğren & Rehberlik Et (Eğitim Desteği)")
    st.markdown("Gönüllü eğitim rehberi, sıfır atık pratikleri ve döngüsel ekonomi bilgi bankası.<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="recipe-card bg-mint">
        <div class="recipe-title">♻️ Sıfır Atık Felsefesi ve Ayrıştırmanın Önemi</div>
        <div class="ingredient-list">
        <b>Neden Gıdayı Çöpe Atmamalıyız?</b><br>
        Dünyada üretilen gıdaların yaklaşık üçte biri tüketilmeden atık haline gelmektedir. Gıda atıkları çöpe gidip katı atık depolama sahalarında oksijensiz ortamda çürüdüklerinde, karbondioksitten 25 kat daha zararlı olan <b>metan gazı (CH₄)</b> üretirler. Gıda kaybı, küresel sera gazı emisyonlarının yaklaşık %8-10'undan sorumludur.<br><br>
        <b>Döngüsel Ekonomi Yaklaşımı:</b><br>
        Geleneksel "Al-Kullan-At" (Doğrusal) modeli yerine, gıdayı sistem içinde tutan "Azalt-Yeniden Kullan-Dönüştür" (Döngüsel) modelini benimsiyoruz. Amacımız gıdayı henüz atık haline gelmeden yakalamak ve kentsel karbon ayak izini azaltmaktır.
        </div>
    </div>
    
    <div class="recipe-card bg-blue">
        <div class="recipe-title">⚖️ Altın Kural: Kompost Dengesi (C:N Oranı)</div>
        <div class="ingredient-list">
        Sağlıklı ve kokusuz bir kompost üretimi için <b>Karbon (Kahverengi atıklar) / Azot (Yeşil atıklar)</b> dengesi hayati önem taşır. İdeal hacimsel oran <b>%60 Kahverengi, %40 Yeşil</b> malzemedir.<br><br>
        <ul>
            <li><b>🟢 Yeşiller (Nem, Azot ve Protein Kaynağı):</b> Meyve ve sebze artıkları, taze çimen, kahve telvesi, çay yaprakları. Süreci hızlandırır ancak fazla olursa koku ve balçıklaşmaya yol açar.</li>
            <li><b>🟤 Kahverengiler (Hava, Karbon ve Enerji Kaynağı):</b> Kuru yapraklar, dal parçaları, tuvalet kağıdı ruloları, talaş, parçalanmış kartonlar. Yığının hava almasını sağlar, fazla olursa süreci yavaşlatır.</li>
        </ul>
        <b>Nem ve Oksijen Kontrolü:</b> Kompostunuz bir sünger gibi nemli olmalı ancak sıkıldığında su damlatmamalıdır. Haftada bir karıştırarak mikroorganizmalar için gerekli oksijeni sağlamalısınız.
        </div>
    </div>
    
    <div class="recipe-card bg-pink">
        <div class="recipe-title">❌ Komposta Asla Atılmaması Gerekenler ve Sebepleri</div>
        <div class="ingredient-list">
        <ul>
            <li><b>Et, Kemik, Balık ve Yağlar:</b> Zararlı patojenleri, sinekleri ve kemirgenleri yığına çeker, anaerobik koku üretir.</li>
            <li><b>Süt Ürünleri (Peynir, Yoğurt, Süt):</b> Oksijen akışını tıkayarak kokulu çürümeye yol açar.</li>
            <li><b>Hastalık Bitkiler veya Yabani Ot Tohumları:</b> Ev tipi soğuk kompost yığınları bu zararlıları öldürecek yüksek sıcaklıklara (60°C+) her zaman ulaşamaz, bu nedenle hastalık bahçenize tekrar yayılabilir.</li>
            <li><b>Kedi/Köpek Dışkısı:</b> İnsan sağlığına zararlı kalıcı parazitler içerebilir.</li>
            <li><b>Narenciye ve Soğan Fazlası:</b> Solucanlara ve kompost içindeki yararlı bakterilere zarar verebilecek aşırı asidik bir ortam yaratır.</li>
        </ul>
        </div>
    </div>

    <div class="recipe-card bg-purple">
        <div class="recipe-title">🌍 Sürdürülebilirlik ve İleri Dönüşüm (Upcycling)</div>
        <div class="ingredient-list">
        <b>Geri Dönüşüm (Recycling) ve İleri Dönüşüm (Upcycling) Arasındaki Fark:</b><br>
        Geri dönüşüm, bir atığı yüksek enerji harcayarak parçalayıp tekrar ham maddeye dönüştürme işlemidir. İleri dönüşüm ise, atık durumundaki bir malzemeyi kalitesini ve estetik/işlevsel değerini artırarak doğrudan yeni bir ürüne çevirmektir. Meyve kabuklarından sirke veya cilt toniği üretmek tam bir ileri dönüşümdür.<br><br>
        <b>Yerel Ekolojik Fayda:</b><br>
        Gıdayı mikro ölçekte (evde veya mahalle pazarında) kurtarmak, atıkların şehir dışındaki tesislere taşınması sırasında oluşacak lojistik kaynaklı karbon emisyonlarını sıfıra indirir. Toprağa geri dönen her gram kompost, kimyasal gübre ihtiyacını azaltarak toprak ekosistemini canlandırır.
        </div>
    </div>
    """, unsafe_allow_html=True)
