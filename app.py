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

    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) {
            flex-direction: row !important; flex-wrap: nowrap !important; overflow-x: hidden !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) > div[data-testid="column"] {
            width: 19% !important; min-width: 19% !important; flex: 1 1 19% !important; padding: 0 2px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) button {
            padding: 0px !important; min-height: 20px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(3)) button p {
            font-size: 9px !important; line-height: 1 !important;
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

    /* Sekme 2 İçindeki Özel Yapılar */
    .compost-coach-wrapper {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

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
    cleaned = resp.text.strip().replace("```json", "").replace("```", "").strip()
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
