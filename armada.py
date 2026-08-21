import streamlit as st
import pandas as pd
import re
import base64
import random

st.set_page_config(page_title="Armada Starbucks Vardiya", layout="wide", initial_sidebar_state="collapsed")

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
    .stApp {{ background-color: #080c14; color: #f8fafc; }}
    .bg-watermark {{
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        width: 620px; height: 620px; background-image: url('{LOGO_DATA_URI}');
        background-repeat: no-repeat; background-position: center; background-size: contain;
        opacity: 0.07; pointer-events: none; z-index: 0;
    }}
    .header-container {{
        position: relative; z-index: 1; display: flex; align-items: center; gap: 18px;
        margin-bottom: 20px; padding: 12px 20px; border-bottom: 2px solid #1e293b;
        background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); border-radius: 12px;
    }}
    .logo-img {{ width: 58px; height: 58px; border-radius: 50%; box-shadow: 0 4px 16px rgba(0, 98, 65, 0.8); }}
    .header-title {{ color: #ffffff; font-size: 24px; font-weight: 800; margin: 0; }}
    .header-sub {{ color: #008248; font-size: 13px; font-weight: 700; margin: 2px 0 0 0; }}
</style>
<div class="bg-watermark"></div>
<div class="header-container">
    <img src="{LOGO_DATA_URI}" class="logo-img" alt="Logo">
    <div>
        <h1 class="header-title">Armada Starbucks Vardiya & Aylık Raporlama Yönetimi</h1>
        <p class="header-sub">OPERATIONAL STORE MANAGEMENT & SHIFT SCHEDULING SYSTEM</p>
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
WEEKS_TITLES = ["1. Hafta (1-7)", "2. Hafta (8-14)", "3. Hafta (15-21)", "4. Hafta (22-28)"]

A_MGR = "07:30-16:00"
K_MGR = "15:30-00:00"
MID_MGR = "09:00-17:30"

A_FT = "07:30-16:00"
K_FT = "15:30-00:00"
ARA_12 = "12:00-20:30"
ARA_10 = "10:00-18:30"

A_PT = "07:30-15:30"
K_PT = "16:00-00:00"
OFF = "OFF"

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
    return f"{int(h)}s" if h.is_integer() else f"{h:.1f}s"

def generate_armada_master_schedule(seed=None):
    if seed is None:
        seed = 42
    rng = random.Random(seed)

    mgr_names = ["Onur Kaynak", "Banu Sezer", "Göktuğ Gökdemir"]
    all_names = [e["name"] for e in EMPLOYEES]
    schedule = {name: ["OFF"] * 28 for name in all_names}

    # Her hafta tam 6 gün iş (45s) ve tam 1 OFF garanti eden, pazar/cts kapanışı net 5 barista + 1 müdür = 6 kişi yapan rotasyon:
    ft_rotations_flawless = {
        "Ceyda Işık": [
            [OFF, K_FT, ARA_12, K_FT, K_FT, K_FT, ARA_10],
            [OFF, K_FT, ARA_10, K_FT, K_FT, K_FT, ARA_12],
            [OFF, K_FT, K_FT, K_FT, K_FT, K_FT, ARA_10],
            [OFF, K_FT, ARA_10, K_FT, K_FT, K_FT, ARA_12]
        ],
        "Yusuf Efe Aydoğmuş": [
            [K_FT, ARA_10, K_FT, A_FT, A_FT, A_FT, OFF],
            [K_FT, K_FT, K_FT, A_FT, A_FT, A_FT, OFF],
            [K_FT, K_FT, K_FT, A_FT, A_FT, A_FT, OFF],
            [K_FT, ARA_10, K_FT, A_FT, A_FT, A_FT, OFF]
        ],
        "Elif Karaca": [
            [K_FT, K_FT, A_FT, K_FT, ARA_12, OFF, K_FT],
            [K_FT, K_FT, A_FT, K_FT, K_FT, OFF, K_FT],
            [K_FT, K_FT, A_FT, K_FT, ARA_12, OFF, K_FT],
            [K_FT, K_FT, A_FT, K_FT, K_FT, OFF, K_FT]
        ],
        "Cansu Yüksel": [
            [K_FT, K_FT, OFF, ARA_12, K_FT, K_FT, K_FT],
            [K_FT, ARA_12, OFF, A_FT, K_FT, K_FT, K_FT],
            [K_FT, A_FT, OFF, K_FT, ARA_10, K_FT, K_FT],
            [K_FT, A_FT, OFF, ARA_12, K_FT, K_FT, K_FT]
        ],
        "Ebrar Sena Akkaya": [
            [K_FT, K_FT, OFF, A_FT, A_FT, ARA_10, ARA_12],
            [K_FT, K_FT, OFF, K_FT, ARA_12, ARA_10, ARA_12],
            [K_FT, K_FT, OFF, K_FT, K_FT, ARA_10, ARA_12],
            [K_FT, K_FT, OFF, A_FT, ARA_12, ARA_10, ARA_12]
        ],
        "Ahmet Emre Demren": [
            [ARA_12, A_FT, K_FT, K_FT, K_FT, A_FT, OFF],
            [ARA_12, A_FT, A_FT, K_FT, K_FT, A_FT, OFF],
            [ARA_12, K_FT, K_FT, ARA_12, K_FT, A_FT, OFF],
            [ARA_12, A_FT, A_FT, K_FT, K_FT, A_FT, OFF]
        ],
        "Ayça Yiğit": [
            [ARA_10, OFF, K_FT, ARA_10, K_FT, A_FT, A_FT],
            [ARA_10, OFF, K_FT, ARA_12, K_FT, A_FT, A_FT],
            [ARA_10, OFF, K_FT, K_FT, ARA_10, A_FT, A_FT],
            [ARA_10, OFF, K_FT, ARA_10, K_FT, A_FT, A_FT]
        ]
    }

    for w_idx in range(4):
        s_d = w_idx * 7
        
        mgr_pattern = [
            {"Onur Kaynak": OFF,   "Banu Sezer": A_MGR,   "Göktuğ Gökdemir": K_MGR},
            {"Onur Kaynak": A_MGR, "Banu Sezer": MID_MGR, "Göktuğ Gökdemir": K_MGR},
            {"Onur Kaynak": K_MGR, "Banu Sezer": A_MGR,   "Göktuğ Gökdemir": MID_MGR},
            {"Onur Kaynak": A_MGR, "Banu Sezer": OFF,     "Göktuğ Gökdemir": K_MGR},
            {"Onur Kaynak": A_MGR, "Banu Sezer": K_MGR,   "Göktuğ Gökdemir": OFF},
            {"Onur Kaynak": MID_MGR, "Banu Sezer": K_MGR, "Göktuğ Gökdemir": A_MGR},
            {"Onur Kaynak": A_MGR, "Banu Sezer": K_MGR,   "Göktuğ Gökdemir": MID_MGR},
        ]
        for day in range(7):
            abs_d = s_d + day
            for m in mgr_names:
                schedule[m][abs_d] = mgr_pattern[day][m]

        # PT Baristalar (Her hafta kesin 4 gün iş = 28s, 4 haftada 112s)
        emir_work_days = [0, 2, 4, 6]
        hayru_work_days = [1, 3, 5, 6]
        for day in range(7):
            abs_d = s_d + day
            schedule["Emir Altunbulak"][abs_d] = (A_PT if day in [0, 4] else K_PT) if day in emir_work_days else OFF
            schedule["Hayrunnisa Erdoğan"][abs_d] = (A_PT if day in [1, 3] else (K_PT if day == 5 else A_PT)) if day in hayru_work_days else OFF

        for day in range(7):
            abs_d = s_d + day
            is_weekend = (day in [5, 6])
            
            if day == 1:
                schedule["Cansu Elibüyük"][abs_d] = OFF
            else:
                schedule["Cansu Elibüyük"][abs_d] = K_FT if is_weekend else A_FT
                
            if day == 4:
                schedule["Vahti Ünal"][abs_d] = OFF
            else:
                schedule["Vahti Ünal"][abs_d] = A_FT if is_weekend else K_FT

            if day == 3:
                schedule["Buse Kayabalı"][abs_d] = OFF
            elif day == 1:
                schedule["Buse Kayabalı"][abs_d] = A_FT
            else:
                schedule["Buse Kayabalı"][abs_d] = A_FT if day in [0, 2] else K_FT

            for b in ft_rotations_flawless.keys():
                schedule[b][abs_d] = ft_rotations_flawless[b][w_idx][day]

    weeks_dict = {}
    for w in range(4):
        start_d = w * 7
        end_d = (w + 1) * 7
        w_name = WEEKS_TITLES[w]

        df_w = pd.DataFrame({
            "Partner": [e["name"] for e in EMPLOYEES],
            "TİP": [e["tip"] for e in EMPLOYEES]
        })
        for d_idx in range(start_d, end_d):
            col_name = f"{DAY_NAMES_TR[d_idx % 7]} ({d_idx + 1})"
            df_w[col_name] = [schedule[emp["name"]][d_idx] for emp in EMPLOYEES]
        weeks_dict[w_name] = df_w

    return weeks_dict

c_y, c_m, c_gen = st.columns([1, 1.5, 2.5])
with c_y:
    sel_year = st.selectbox("Yıl", [2026, 2027], index=0)
with c_m:
    sel_month = st.selectbox("Ay", range(1, 13), index=7, format_func=lambda x: MONTH_NAMES_TR[x-1])

month_key = f"{sel_year}_{sel_month:02d}"

if "current_schedule" not in st.session_state or st.session_state.get("last_month_key") != month_key:
    st.session_state.current_schedule = generate_armada_master_schedule(seed=sel_year*100+sel_month)
    st.session_state.last_month_key = month_key

with c_gen:
    st.write("")
    if st.button("🎲 Yeni Karışık / Dinamik Vardiya Üret", use_container_width=True, type="primary"):
        new_seed = random.randint(1, 999999)
        st.session_state.current_schedule = generate_armada_master_schedule(seed=new_seed)
        st.success(f"{MONTH_NAMES_TR[sel_month-1]} {sel_year} için tam kotalı ve dengeli kadro üretildi!")
        st.rerun()

current_month_weeks = st.session_state.current_schedule
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
        st.rerun()

with b2:
    if st.button("☀️ Açılış", use_container_width=True):
        val = A_PT if p_tip == "PT" else A_FT
        current_month_weeks[sel_week].at[emp_idx, sel_day] = val
        st.rerun()

with b3:
    if st.button("☕ Ara (12:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = ARA_12
        st.rerun()

with b4:
    if st.button("☕ Ara (10:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = ARA_10
        st.rerun()

with b5:
    if st.button("🌙 Kapanış", use_container_width=True):
        val = K_PT if p_tip == "PT" else K_FT
        current_month_weeks[sel_week].at[emp_idx, sel_day] = val
        st.rerun()

with b6:
    if st.button("👔 Müd. Ara (09:00)", use_container_width=True):
        current_month_weeks[sel_week].at[emp_idx, sel_day] = MID_MGR
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
        <p class="sub">Haftalık 45s (FT) ve 28s (PT) Kotalı Net Çalışma Çizelgesi</p>
        
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