import streamlit as st
import pandas as pd
import json
import os
import re
import base64
import calendar
import random
from datetime import datetime

st.set_page_config(page_title="Armada Starbucks Vardiya", layout="wide", initial_sidebar_state="collapsed")

SAVE_FILE = os.path.expanduser("~/Desktop/starbucks_armada_data.json")

STARBUCKS_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%">
  <circle cx="250" cy="250" r="248" fill="#006241"/>
  <circle cx="250" cy="250" r="195" fill="#006241" stroke="#ffffff" stroke-width="6"/>
  <polygon points="250,90 258,114 282,114 262,128 270,152 250,138 230,152 238,128 218,114 242,114" fill="#ffffff"/>
  <path d="M250 135 L285 160 L275 200 L225 200 L215 160 Z" fill="#ffffff"/>
  <path d="M225 160 L250 178 L275 160 L268 195 L232 195 Z" fill="#006241"/>
  <path d="M250 185 C230 185 215 200 215 225 C215 248 230 268 250 268 C270 268 285 248 285 225 C285 200 270 185 250 185 Z" fill="#ffffff"/>
  <ellipse cx="238" cy="218" rx="6" ry="4" fill="#006241"/>
  <ellipse cx="262" cy="218" rx="6" ry="4" fill="#006241"/>
  <path d="M246 226 L250 236 L254 226" stroke="#006241" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M242 245 Q250 252 258 245" stroke="#006241" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M250 268 C240 280 235 305 235 350 L265 350 C265 305 260 280 250 268 Z" fill="#ffffff"/>
  <path d="M195 210 Q210 260 205 320 Q200 380 250 425 Q300 380 295 320 Q290 260 305 210 C290 240 280 280 280 320 Q270 380 250 400 Q230 380 220 320 C220 280 210 240 195 210 Z" fill="#ffffff"/>
  <path d="M140 230 Q125 280 145 340 Q165 400 220 440 C175 410 150 360 148 300 Q146 255 160 220 Z" fill="#ffffff"/>
  <path d="M360 230 Q375 280 355 340 Q335 400 280 440 C325 410 350 360 352 300 Q354 255 340 220 Z" fill="#ffffff"/>
  <path d="M115 250 Q105 290 120 330 Q135 370 175 410 C145 380 125 340 125 295 Q125 265 130 240 Z" fill="#ffffff"/>
  <path d="M385 250 Q395 290 380 330 Q365 370 325 410 C355 380 375 340 375 295 Q375 265 370 240 Z" fill="#ffffff"/>
</svg>"""

logo_b64 = base64.b64encode(STARBUCKS_LOGO_SVG.encode("utf-8")).decode("utf-8")
LOGO_DATA_URI = f"data:image/svg+xml;base64,{logo_b64}"

st.markdown(f"""
<style>
    .stApp {{
        background-color: #080c14;
        color: #f8fafc;
    }}
    .bg-watermark {{
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 620px;
        height: 620px;
        background-image: url('{LOGO_DATA_URI}');
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: 0.07;
        pointer-events: none;
        z-index: 0;
    }}
    .header-container {{
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 20px;
        padding: 12px 20px;
        border-bottom: 2px solid #1e293b;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 12px;
    }}
    .logo-img {{
        width: 58px;
        height: 58px;
        border-radius: 50%;
        box-shadow: 0 4px 16px rgba(0, 98, 65, 0.8);
    }}
    .header-title {{
        color: #ffffff;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
    }}
    .header-sub {{
        color: #008248;
        font-size: 13px;
        font-weight: 700;
        margin: 2px 0 0 0;
    }}
</style>
<div class="bg-watermark"></div>
<div class="header-container">
    <img src="{LOGO_DATA_URI}" class="logo-img" alt="Logo">
    <div>
        <h1 class="header-title">Armada Starbucks Vardiya & Aylık Raporlama Yönetimi</h1>
        <p class="header-sub">DYNAMIC STORE MANAGEMENT & SHIFT SCHEDULING SYSTEM</p>
    </div>
</div>
""", unsafe_allow_html=True)

EMPLOYEES = [
    {"name": "Onur Kaynak", "tip": "SM", "role": "Müdür", "quota": 180},
    {"name": "Banu Sezer", "tip": "SSV", "role": "Müdür", "quota": 180},
    {"name": "Göktuğ Gökdemir", "tip": "SSV", "role": "Müdür", "quota": 180},
    {"name": "Ceyda Işık", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Yusuf Efe Aydoğmuş", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Cansu Elibüyük", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Elif Karaca", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Vahti Ünal", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Cansu Yüksel", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Hayrunnisa Erdoğan", "tip": "PT", "role": "Barista", "quota": 112},
    {"name": "Ebrar Sena Akkaya", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Ahmet Emre Demren", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Buse Kayabalı", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Ayça Yiğit", "tip": "FT", "role": "Barista", "quota": 180},
    {"name": "Emir Altunbulak", "tip": "PT", "role": "Barista", "quota": 112},
]

DAY_NAMES_TR = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
MONTH_NAMES_TR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

A_MGR = "07:30-16:00"
K_MGR = "15:30-00:00"
MID_MGR = "09:00-17:30"

A_FT = "07:30-16:00"
K_FT = "15:30-00:00"
ARA_12 = "12:00-20:30"
ARA_10 = "10:00-18:30"

A_PT = "07:30-15:30"
K_PT = "16:00-00:00"
OFF  = "OFF"

def calculate_net_hours(shift_str):
    s = str(shift_str).strip().upper()
    if not s or s in ["OFF", "BOŞ", "-", "0", "NONE"]:
        return 0.0
    if "RAPOR" in s or "İZİN" in s:
        return 7.5
    match = re.search(r'(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})', s)
    if match:
        h1, m1, h2, m2 = map(int, match.groups())
        start_min = h1 * 60 + m1
        end_min = h2 * 60 + m2
        if end_min <= start_min:
            end_min += 24 * 60
        gross = (end_min - start_min) / 60.0
        return max(0.0, gross - 1.0)
    return 0.0

def categorize_shift(s):
    s_upper = str(s).upper()
    if not s_upper or s_upper in ["OFF", "BOŞ", "NONE"]: return "OFF"
    if "RAPOR" in s_upper: return "Rapor"
    if "İZİN" in s_upper: return "İzin"
    match = re.search(r'(\d{1,2})[:.](\d{2})', s_upper)
    if match:
        h = int(match.group(1))
        if h < 9: return "Açılış"
        elif 9 <= h < 14: return "Ara"
        else: return "Kapanış"
    return "Özel Vardiya"

def format_hour(h):
    h = round(float(h), 2)
    if h.is_integer():
        return f"{int(h)}s"
    return f"{h:.1f}s"

def generate_intelligent_store_schedule(year, month, seed=None):
    if seed is None:
        seed = year * 100 + month
    rng = random.Random(seed)
    
    num_days = calendar.monthrange(year, month)[1]
    
    days_info = []
    for day in range(1, num_days + 1):
        weekday_idx = datetime(year, month, day).weekday()
        days_info.append({
            "day": day,
            "weekday_idx": weekday_idx,
            "weekday_name": DAY_NAMES_TR[weekday_idx],
            "col_name": f"{DAY_NAMES_TR[weekday_idx]} ({day})"
        })
        
    mgr_names = ["Onur Kaynak", "Banu Sezer", "Göktuğ Gökdemir"]
    ft_names = [e["name"] for e in EMPLOYEES if e["tip"] == "FT"]
    
    full_schedule = {emp["name"]: [OFF] * num_days for emp in EMPLOYEES}
    
    # 1. Dinamik Müdür Rotasyonu (Her gün 1 Açılış, 1 Kapanış, 3. müdür çalışıyorsa 09:00-17:30)
    # Haftalık 1 gün dönüşümlü OFF
    for d in range(num_days):
        w = days_info[d]["weekday_idx"]
        # Müdür OFF günleri rotasyonu
        if w == 2: # Çarşamba -> Banu OFF
            full_schedule[mgr_names[0]][d] = A_MGR if (d % 2 == 0) else K_MGR
            full_schedule[mgr_names[1]][d] = OFF
            full_schedule[mgr_names[2]][d] = K_MGR if (d % 2 == 0) else A_MGR
        elif w == 3: # Perşembe -> Onur OFF
            full_schedule[mgr_names[0]][d] = OFF
            full_schedule[mgr_names[1]][d] = A_MGR if (d % 2 == 0) else K_MGR
            full_schedule[mgr_names[2]][d] = K_MGR if (d % 2 == 0) else A_MGR
        elif w == 4: # Cuma -> Göktuğ OFF
            full_schedule[mgr_names[0]][d] = A_MGR if (d % 2 == 0) else K_MGR
            full_schedule[mgr_names[1]][d] = K_MGR if (d % 2 == 0) else A_MGR
            full_schedule[mgr_names[2]][d] = OFF
        else:
            # 3 Müdür de çalışıyor: 1 Açılış, 1 Kapanış, 1 Ara Yönetici (09:00-17:30)
            roles = [A_MGR, MID_MGR, K_MGR]
            shift_order = [(d + 0) % 3, (d + 1) % 3, (d + 2) % 3]
            for m_idx in range(3):
                full_schedule[mgr_names[m_idx]][d] = roles[shift_order[m_idx]]
                
    # 2. PT Baristalar (Emir ve Hayrunnisa - Tam 16 Gün * 7s = 112s)
    pt_days_emir = set(range(0, min(num_days, 32), 2)[:16])
    pt_days_hayru = set(range(1, min(num_days, 32), 2)[:16])
    
    for d in pt_days_emir:
        w = days_info[d]["weekday_idx"]
        full_schedule["Emir Altunbulak"][d] = A_PT if w in [0, 2, 5] else K_PT
        
    for d in pt_days_hayru:
        w = days_info[d]["weekday_idx"]
        full_schedule["Hayrunnisa Erdoğan"][d] = A_PT if w in [1, 3, 6] else K_PT
        
    # 3. FT Baristalar (Dinamik & Karışık Dağılım Motoru)
    # Her gün: Tam 3 Barista Açılış. Hafta içi 4 Barista Kapanış, Hafta sonu 5 Barista Kapanış (Müdürle toplam 6).
    # Kalan personeller 10:00 ve 12:00 araçısı.
    for d in range(num_days):
        w = days_info[d]["weekday_idx"]
        is_weekend = (w in [5, 6])
        
        # Günün PT durumu
        pt_openers = [p for p in ["Emir Altunbulak", "Hayrunnisa Erdoğan"] if full_schedule[p][d] == A_PT]
        pt_closers = [p for p in ["Emir Altunbulak", "Hayrunnisa Erdoğan"] if full_schedule[p][d] == K_PT]
        
        needed_ft_open = 3 - len(pt_openers)
        needed_ft_close = (5 if is_weekend else 4) - len(pt_closers)
        
        # Her gün dönüşümlü 1-2 kişiye haftalık OFF verilir
        avail_ft = []
        for idx, ft_name in enumerate(ft_names):
            if (d + idx * 2) % 7 != 0:
                avail_ft.append(ft_name)
        
        rng.shuffle(avail_ft)
        
        # Açılış Baristaları (Denetim Kuralı: Ceyda & Yusuf hafta içi aynı gün açılış olamaz)
        openers_today = []
        for b in avail_ft:
            if len(openers_today) < needed_ft_open:
                if not is_weekend and b == "Yusuf Efe Aydoğmuş" and "Ceyda Işık" in openers_today:
                    continue
                if not is_weekend and b == "Ceyda Işık" and "Yusuf Efe Aydoğmuş" in openers_today:
                    continue
                openers_today.append(b)
                full_schedule[b][d] = A_FT
                
        # Kapanış Baristaları
        closers_today = []
        remaining_ft = [b for b in avail_ft if b not in openers_today]
        for b in remaining_ft:
            if len(closers_today) < needed_ft_close:
                closers_today.append(b)
                full_schedule[b][d] = K_FT
                
        # Fazla Baristalar ➔ Çift Aracı (10:00 ve 12:00)
        extras = [b for b in remaining_ft if b not in closers_today]
        if len(extras) >= 1:
            full_schedule[extras[0]][d] = ARA_12
        if len(extras) >= 2:
            full_schedule[extras[1]][d] = ARA_10
        if len(extras) >= 3:
            for extra_b in extras[2:]:
                full_schedule[extra_b][d] = OFF
                
    # 28 günden sonraki günlerde personelin 180s/112s kotasını korumak için dengeleme
    if num_days > 28:
        for p_name, shifts in full_schedule.items():
            emp_info = next(e for e in EMPLOYEES if e["name"] == p_name)
            max_limit = emp_info["quota"]
            curr_hours = sum(calculate_net_hours(s) for s in shifts)
            if curr_hours > max_limit:
                diff_shifts = int((curr_hours - max_limit) / (7.0 if emp_info["tip"] == "PT" else 7.5))
                for extra_day in range(28, num_days):
                    if diff_shifts > 0 and shifts[extra_day] not in [OFF, ""]:
                        shifts[extra_day] = OFF
                        diff_shifts -= 1

    # Haftalara Böl
    weeks_dict = {}
    total_weeks = (num_days + 6) // 7
    for w in range(total_weeks):
        start_d = w * 7
        end_d = min((w + 1) * 7, num_days)
        w_name = f"{w+1}. Hafta ({start_d+1}-{end_d})"
        
        df_w = pd.DataFrame({
            "Partner": [e["name"] for e in EMPLOYEES],
            "TİP": [e["tip"] for e in EMPLOYEES]
        })
        for d_idx in range(start_d, end_d):
            col_name = days_info[d_idx]["col_name"]
            df_w[col_name] = [full_schedule[emp["name"]][d_idx] for emp in EMPLOYEES]
        weeks_dict[w_name] = df_w
        
    return weeks_dict

def load_all_store():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_month_store(month_key, weeks_dict):
    store = load_all_store()
    store[month_key] = {w: df.to_dict(orient="records") for w, df in weeks_dict.items()}
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")

c_y, c_m, c_gen = st.columns([1, 1.5, 2.5])
with c_y:
    sel_year = st.selectbox("Yıl", [2026, 2027], index=0)
with c_m:
    sel_month = st.selectbox("Ay", range(1, 13), index=datetime.now().month - 1, format_func=lambda x: MONTH_NAMES_TR[x-1])

month_key = f"{sel_year}_{sel_month:02d}"

if "app_store" not in st.session_state:
    st.session_state.app_store = load_all_store()

if month_key not in st.session_state.app_store:
    st.session_state.app_store[month_key] = {
        w: df.to_dict(orient="records") 
        for w, df in generate_intelligent_store_schedule(sel_year, sel_month).items()
    }
    save_month_store(month_key, {w: pd.DataFrame(d) for w, d in st.session_state.app_store[month_key].items()})

with c_gen:
    st.write("")
    if st.button("🎲 Yeni Karışık / Dinamik Vardiya Üret", use_container_width=True, type="primary"):
        new_seed = random.randint(1, 999999)
        new_w = generate_intelligent_store_schedule(sel_year, sel_month, seed=new_seed)
        save_month_store(month_key, new_w)
        st.session_state.app_store[month_key] = {w: df.to_dict(orient="records") for w, df in new_w.items()}
        st.success(f"{MONTH_NAMES_TR[sel_month-1]} {sel_year} için tamamen yeni ve karışık vardiya oluşturuldu!")
        st.rerun()

current_month_weeks = {w: pd.DataFrame(data) for w, data in st.session_state.app_store[month_key].items()}
WEEKS_KEYS = list(current_month_weeks.keys())

st.subheader(f"🛠️ {MONTH_NAMES_TR[sel_month-1]} {sel_year} - Manuel Düzenleme Paneli")

c1, c2, c3 = st.columns([1.5, 1.5, 1.5])
with c1:
    sel_week = st.selectbox("Hafta Seç", WEEKS_KEYS, key="dyn_week")
with c2:
    sel_emp = st.selectbox("Partner Seç", [e["name"] for e in EMPLOYEES], key="dyn_emp")

current_df = current_month_weeks[sel_week]
day_cols = [c for c in current_df.columns if c not in ["Partner", "TİP", "Haftalık Saat"]]

with c3:
    sel_day = st.selectbox("Gün Seç", day_cols, key="dyn_day")

emp_idx = current_df[current_df["Partner"] == sel_emp].index[0]
curr_val = str(current_df.at[emp_idx, sel_day])
p_tip = next(e["tip"] for e in EMPLOYEES if e["name"] == sel_emp)

st.markdown(f"**Şu Anki Durum:** `{curr_val}` ({p_tip})")

b1, b2, b3, b4, b5, b6 = st.columns(6)
with b1:
    if st.button("🔴 OFF Yap", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = "OFF"
        save_month_store(month_key, current_month_weeks)
        st.rerun()

with b2:
    if st.button("☀️ Açılış", use_container_width=True):
        val = A_PT if p_tip == "PT" else A_FT
        current_month_weeks[sel_week].at[emp_idx, sel_day] = val
        save_month_store(month_key, current_month_weeks)
        st.rerun()

with b3:
    if st.button("☕ Ara (12:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = ARA_12
        save_month_store(month_key, current_month_weeks)
        st.rerun()

with b4:
    if st.button("☕ Ara (10:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = ARA_10
        save_month_store(month_key, current_month_weeks)
        st.rerun()

with b5:
    if st.button("🌙 Kapanış", use_container_width=True):
        val = K_PT if p_tip == "PT" else K_FT
        current_month_weeks[sel_week].at[emp_idx, sel_day] = val
        save_month_store(month_key, current_month_weeks)
        st.rerun()

with b6:
    if st.button("👔 Müd. Ara (09:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = MID_MGR
        save_month_store(month_key, current_month_weeks)
        st.rerun()

st.subheader(f"📅 {MONTH_NAMES_TR[sel_month-1]} {sel_year} - Haftalık Vardiya Çizelgeleri")
tabs = st.tabs(WEEKS_KEYS)

for idx, week in enumerate(WEEKS_KEYS):
    with tabs[idx]:
        df_w = current_month_weeks[week].copy()
        d_cols = [c for c in df_w.columns if c not in ["Partner", "TİP", "Haftalık Saat"]]
        
        weekly_hours = []
        for _, row in df_w.iterrows():
            w_sum = sum(calculate_net_hours(row[d]) for d in d_cols)
            weekly_hours.append(format_hour(w_sum))
        df_w["Haftalık Saat"] = weekly_hours
        
        def highlight_roles(row):
            styles = [""] * len(row)
            if row["TİP"] in ["SM", "SSV"]:
                styles[0] = "background-color: #1e3a8a; color: #ffffff; font-weight: bold;"
                styles[1] = "background-color: #1e3a8a; color: #ffffff; font-weight: bold;"
            elif row["TİP"] == "PT":
                styles[0] = "background-color: #fef08a; color: #854d0e; font-weight: bold;"
                styles[1] = "background-color: #fef08a; color: #854d0e; font-weight: bold;"
            return styles

        st.dataframe(
            df_w.style.apply(highlight_roles, axis=1),
            use_container_width=True,
            hide_index=True
        )

all_days_series = {emp["name"]: [] for emp in EMPLOYEES}
for week in WEEKS_KEYS:
    df_w = current_month_weeks[week]
    d_cols = [c for c in df_w.columns if c not in ["Partner", "TİP", "Haftalık Saat"]]
    for _, row in df_w.iterrows():
        p_name = row["Partner"]
        for d in d_cols:
            all_days_series[p_name].append((d, str(row[d])))

st.subheader(f"📊 {MONTH_NAMES_TR[sel_month-1]} {sel_year} - Aylık Partner Çalışma ve Vardiya Raporu")

report_rows = []
for emp in EMPLOYEES:
    p_name = emp["name"]
    p_tip = emp["tip"]
    shifts = all_days_series[p_name]
    
    total_hours = 0.0
    cnt_acilis = 0
    cnt_ara = 0
    cnt_kapanis = 0
    cnt_off = 0
    cnt_izin = 0
    cnt_rapor = 0
    
    for _, s in shifts:
        h = calculate_net_hours(s)
        total_hours += h
        cat = categorize_shift(s)
        if cat == "Açılış": cnt_acilis += 1
        elif cat == "Ara": cnt_ara += 1
        elif cat == "Kapanış": cnt_kapanis += 1
        elif cat == "OFF": cnt_off += 1
        elif cat == "İzin": cnt_izin += 1
        elif cat == "Rapor": cnt_rapor += 1
        
    limit = emp["quota"]
    
    if total_hours > limit:
        diff = total_hours - limit
        status = f"🚨 +{format_hour(diff)} Kota Aşımı!"
    elif total_hours < limit:
        diff = limit - total_hours
        status = f"ℹ️ -{format_hour(diff)} Eksik"
    else:
        status = "✅ Tam Kota"
        
    report_rows.append({
        "Partner": p_name,
        "TİP": p_tip,
        "Açılış": cnt_acilis,
        "Ara": cnt_ara,
        "Kapanış": cnt_kapanis,
        "OFF": cnt_off,
        "Toplam Net Saat": format_hour(total_hours),
        "Aylık Hedef": format_hour(limit),
        "Durum": status
    })

report_df = pd.DataFrame(report_rows)

def style_report_table(row):
    styles = [""] * len(row)
    if row["TİP"] in ["SM", "SSV"]:
        styles[0] = "background-color: #1e3a8a; color: #ffffff; font-weight: bold;"
        styles[1] = "background-color: #1e3a8a; color: #ffffff; font-weight: bold;"
    elif row["TİP"] == "PT":
        styles[0] = "background-color: #fef08a; color: #854d0e; font-weight: bold;"
        styles[1] = "background-color: #fef08a; color: #854d0e; font-weight: bold;"
    
    if "Kota Aşımı" in str(row["Durum"]):
        styles[8] = "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
    elif "Tam Kota" in str(row["Durum"]):
        styles[8] = "background-color: #dcfce7; color: #166534; font-weight: bold;"
    return styles

st.dataframe(
    report_df.style.apply(style_report_table, axis=1),
    use_container_width=True,
    hide_index=True
)

st.subheader("📄 Resmi Aylık Rapor Çıktısı (PDF & Yazdırma)")

def get_report_html():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Armada Starbucks Vardiya Raporu - {MONTH_NAMES_TR[sel_month-1]} {sel_year}</title>
    <style>
        @page {{ size: A4 landscape; margin: 8mm; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0f172a; font-size: 8pt; padding: 10px; }}
        h1 {{ color: #006241; font-size: 15pt; margin: 0 0 4px 0; text-align: center; }}
        p.sub {{ text-align: center; color: #64748b; font-size: 8.5pt; margin: 0 0 10px 0; }}
        h2 {{ color: #1e3a8a; font-size: 10pt; margin: 12px 0 5px 0; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 3px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 4px; text-align: center; }}
        th {{ background-color: #f1f5f9; font-weight: bold; color: #0f172a; }}
        .mgr {{ background-color: #1e3a8a; color: #ffffff; font-weight: bold; }}
        .pt {{ background-color: #fef08a; color: #854d0e; font-weight: bold; }}
        .alert {{ background-color: #fee2e2; color: #991b1b; font-weight: bold; }}
        .ok {{ background-color: #dcfce7; color: #166534; font-weight: bold; }}
        @media print {{
            .no-print {{ display: none; }}
        }}
    </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom: 12px; text-align: right;">
            <button onclick="window.print()" style="padding: 8px 16px; background-color: #006241; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">🖨️ PDF Olarak Kaydet / Yazdır</button>
        </div>
        <h1>☕ Armada Starbucks - {MONTH_NAMES_TR[sel_month-1]} {sel_year} Aylık Vardiya & Performans Raporu</h1>
        <p class="sub">Çalışma Çizelgesi ve İstatistik Özeti (1 Saat Mola Düşümlü Net Saatler)</p>
        
        <h2>📊 Aylık Partner Çalışma ve İstatistik Tablosu</h2>
        <table>
            <thead>
                <tr>
                    <th>Partner</th><th>TİP</th><th>Açılış</th><th>Ara</th><th>Kapanış</th><th>OFF</th><th>Toplam Net Saat</th><th>Aylık Kota</th><th>Durum</th>
                </tr>
            </thead>
            <tbody>
    """
    for _, r in report_df.iterrows():
        p_cls = "mgr" if r["TİP"] in ["SM", "SSV"] else ("pt" if r["TİP"] == "PT" else "")
        d_cls = "alert" if "Kota Aşımı" in str(r["Durum"]) else ("ok" if "Tam Kota" in str(r["Durum"]) else "")
        html_content += f"""
        <tr>
            <td class="{p_cls}">{r['Partner']}</td><td class="{p_cls}">{r['TİP']}</td><td>{r['Açılış']}</td><td>{r['Ara']}</td><td>{r['Kapanış']}</td><td>{r['OFF']}</td><td><b>{r['Toplam Net Saat']}</b></td><td>{r['Aylık Hedef']}</td><td class="{d_cls}">{r['Durum']}</td>
        </tr>
        """
    html_content += "</tbody></table>"
    
    for week in WEEKS_KEYS:
        df_w = current_month_weeks[week]
        cols = [c for c in df_w.columns if c != "Haftalık Saat"]
        html_content += f"<h2>📅 {week}</h2><table><thead><tr>"
        for c in cols:
            html_content += f"<th>{c}</th>"
        html_content += "</tr></thead><tbody>"
        for _, r in df_w.iterrows():
            p_cls = "mgr" if r["TİP"] in ["SM", "SSV"] else ("pt" if r["TİP"] == "PT" else "")
            html_content += f"<tr><td class='{p_cls}'>{r['Partner']}</td><td class='{p_cls}'>{r['TİP']}</td>"
            for c in cols[2:]:
                html_content += f"<td>{r[c]}</td>"
            html_content += "</tr>"
        html_content += "</tbody></table>"
        
    html_content += """
    </body>
    </html>
    """
    return html_content

report_html = get_report_html()
b64 = base64.b64encode(report_html.encode("utf-8")).decode("utf-8")
st.markdown(
    f'<a href="data:text/html;base64,{b64}" target="_blank" download="Armada_Starbucks_{MONTH_NAMES_TR[sel_month-1]}_{sel_year}_Rapor.html" style="display:inline-block;padding:10px 22px;background-color:#006241;color:white;text-decoration:none;border-radius:6px;font-weight:bold;">📥 Resmi Raporu Aç ve PDF Olarak Yazdır / Kaydet</a>',
    unsafe_allow_html=True
)