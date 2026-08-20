import streamlit as st
import pandas as pd
import json
import os
import re
import base64

st.set_page_config(page_title="Armada Starbucks", layout="wide", initial_sidebar_state="collapsed")

SAVE_FILE = os.path.expanduser("~/Desktop/starbucks_armada_data.json")

st.markdown('''
<style>
    .stApp {
        background-color: #080c14;
        background-image: linear-gradient(rgba(8, 12, 20, 0.88), rgba(8, 12, 20, 0.94)),
                          url("data:image/svg+xml;base64,NDA0OiBOb3QgRm91bmQ=");
        background-repeat: no-repeat;
        background-position: center 40%;
        background-size: 580px;
        background-attachment: fixed;
        color: #f8fafc;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 20px;
        padding: 12px 20px;
        border-bottom: 2px solid #1e293b;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 12px;
    }
    .logo-img {
        width: 62px;
        height: 62px;
        border-radius: 50%;
        box-shadow: 0 4px 16px rgba(0, 98, 65, 0.8);
    }
    .header-title {
        color: #ffffff;
        font-size: 25px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-sub {
        color: #008248;
        font-size: 13px;
        font-weight: 700;
        margin: 2px 0 0 0;
        letter-spacing: 0.5px;
    }
</style>
''', unsafe_allow_html=True)

EMPLOYEES = [
    {"name": "Onur Kaynak", "tip": "SM", "role_title": "Store Manager", "target_monthly": 180},
    {"name": "Banu Sezer", "tip": "SSV", "role_title": "Shift Supervisor", "target_monthly": 180},
    {"name": "Göktuğ Gökdemir", "tip": "SSV", "role_title": "Shift Supervisor", "target_monthly": 180},
    {"name": "Cansu Elibüyük", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Elif Karaca", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Vahti Ünal", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Cansu Yüksel", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Hayrunnisa Erdoğan", "tip": "PT", "role_title": "Barista (PT)", "target_monthly": 112},
    {"name": "Ebrar Sena Akkaya", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Ahmet Emre Demren", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Buse Kayabalı", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Ayça Yiğit", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Emir Altunbulak", "tip": "PT", "role_title": "Barista (PT)", "target_monthly": 112},
    {"name": "Ceyda Işık", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
    {"name": "Yusuf Efe Aydoğmuş", "tip": "FT", "role_title": "Barista", "target_monthly": 180},
]

WEEK_DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
WEEKS = ["1. Hafta (1-7)", "2. Hafta (8-14)", "3. Hafta (15-21)", "4. Hafta (22-28)"]

A_FT = "07:30-16:00"
K_FT = "15:30-00:00"
ARA  = "12:00-20:30"
A_PT = "07:30-15:30"
K_PT = "16:00-00:00"
OFF  = "OFF"

def calculate_net_hours(shift_str):
    s = str(shift_str).strip().upper()
    if not s or s in ["OFF", "BOŞ", "-", "0", "NONE"]:
        return 0.0
    if "RAPOR" in s or "İZİN" in s or "DOĞUM" in s:
        return 7.5
    match = re.search(r"(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})", s)
    if match:
        h1, m1, h2, m2 = map(int, match.groups())
        start_min = h1 * 60 + m1
        end_min = h2 * 60 + m2
        if end_min <= start_min:
            end_min += 24 * 60
        gross_hours = (end_min - start_min) / 60.0
        return max(0.0, gross_hours - 1.0)
    return 0.0

def categorize_shift(s):
    s_upper = str(s).upper()
    if not s_upper or s_upper in ["OFF", "BOŞ", "NONE"]: return "OFF"
    if "RAPOR" in s_upper: return "Rapor"
    if "İZİN" in s_upper or "DOĞUM" in s_upper: return "İzin"
    match = re.search(r"(\d{1,2})[:.](\d{2})", s_upper)
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

def generate_perfect_armada_schedule():
    pats = {
        "Onur Kaynak": [
            A_FT, A_FT, K_FT, K_FT, OFF, A_FT, A_FT,
            K_FT, K_FT, OFF, A_FT, A_FT, A_FT, K_FT,
            A_FT, K_FT, K_FT, OFF, A_FT, A_FT, A_FT,
            K_FT, OFF, A_FT, A_FT, A_FT, K_FT, K_FT
        ],
        "Banu Sezer": [
            K_FT, K_FT, OFF, A_FT, A_FT, K_FT, K_FT,
            A_FT, A_FT, A_FT, OFF, K_FT, K_FT, K_FT,
            OFF, A_FT, A_FT, A_FT, K_FT, K_FT, K_FT,
            K_FT, K_FT, K_FT, OFF, A_FT, A_FT, A_FT
        ],
        "Göktuğ Gökdemir": [
            OFF, A_FT, A_FT, A_FT, K_FT, K_FT, K_FT,
            K_FT, K_FT, K_FT, OFF, A_FT, A_FT, A_FT,
            A_FT, A_FT, OFF, K_FT, K_FT, K_FT, A_FT,
            OFF, A_FT, A_FT, A_FT, K_FT, K_FT, K_FT
        ],
        "Hayrunnisa Erdoğan": [
            A_PT, OFF, A_PT, OFF, A_PT, K_PT, OFF,
            OFF, A_PT, A_PT, OFF, K_PT, OFF, K_PT,
            K_PT, OFF, K_PT, OFF, A_PT, A_PT, OFF,
            OFF, A_PT, OFF, A_PT, OFF, K_PT, K_PT
        ],
        "Emir Altunbulak": [
            OFF, K_PT, OFF, K_PT, OFF, A_PT, A_PT,
            A_PT, OFF, A_PT, OFF, K_PT, K_PT, OFF,
            OFF, OFF, K_PT, K_PT, OFF, A_PT, A_PT,
            A_PT, A_PT, OFF, K_PT, OFF, OFF, K_PT
        ],
        "Cansu Elibüyük": [
            A_FT, A_FT, A_FT, OFF, K_FT, K_FT, K_FT,
            OFF, ARA,  A_FT, A_FT, A_FT, K_FT, K_FT,
            K_FT, K_FT, OFF, A_FT, A_FT, ARA,  K_FT,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT
        ],
        "Elif Karaca": [
            K_FT, K_FT, OFF, A_FT, A_FT, A_FT, ARA,
            ARA,  K_FT, K_FT, OFF, A_FT, A_FT, A_FT,
            A_FT, A_FT, A_FT, OFF, K_FT, K_FT, ARA,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT
        ],
        "Vahti Ünal": [
            ARA,  K_FT, K_FT, K_FT, OFF, A_FT, A_FT,
            A_FT, A_FT, ARA,  K_FT, K_FT, OFF, A_FT,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT,
            A_FT, ARA,  K_FT, K_FT, K_FT, OFF, A_FT
        ],
        "Cansu Yüksel": [
            A_FT, A_FT, ARA,  K_FT, K_FT, OFF, A_FT,
            OFF,  A_FT, A_FT, A_FT, ARA,  K_FT, K_FT,
            K_FT, K_FT, K_FT, OFF, A_FT, A_FT, ARA,
            A_FT, A_FT, OFF,  ARA,  K_FT, K_FT, K_FT
        ],
        "Ebrar Sena Akkaya": [
            K_FT, OFF, A_FT, A_FT, A_FT, ARA,  K_FT,
            A_FT, A_FT, OFF,  ARA,  K_FT, K_FT, K_FT,
            OFF,  A_FT, A_FT, A_FT, ARA,  K_FT, K_FT,
            ARA,  K_FT, K_FT, OFF, A_FT, A_FT, A_FT
        ],
        "Ahmet Emre Demren": [
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT,
            A_FT, A_FT, A_FT, OFF, ARA,  K_FT, K_FT,
            K_FT, K_FT, OFF, A_FT, A_FT, ARA,  K_FT,
            OFF, ARA,  A_FT, A_FT, A_FT, K_FT, K_FT
        ],
        "Buse Kayabalı": [
            A_FT, A_FT, A_FT, ARA,  OFF, K_FT, K_FT,
            K_FT, OFF, A_FT, A_FT, A_FT, ARA,  K_FT,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT,
            A_FT, ARA,  K_FT, K_FT, OFF, A_FT, A_FT
        ],
        "Ayça Yiğit": [
            K_FT, K_FT, K_FT, OFF, ARA,  A_FT, A_FT,
            A_FT, ARA,  K_FT, K_FT, OFF, A_FT, A_FT,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT,
            A_FT, A_FT, ARA,  K_FT, K_FT, K_FT, OFF
        ],
        "Ceyda Işık": [
            K_FT, K_FT, OFF, A_FT, A_FT, K_FT, K_FT,
            OFF,  A_FT, A_FT, A_FT, ARA,  K_FT, K_FT,
            A_FT, A_FT, ARA,  K_FT, K_FT, OFF, K_FT,
            OFF,  A_FT, A_FT, ARA,  K_FT, K_FT, K_FT
        ],
        "Yusuf Efe Aydoğmuş": [
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, K_FT,
            K_FT, K_FT, OFF, A_FT, A_FT, A_FT, ARA,
            OFF, A_FT, A_FT, ARA,  K_FT, K_FT, OFF,
            A_FT, A_FT, A_FT, ARA, K_FT, K_FT, K_FT
        ]
    }
    
    monthly_data = {}
    for w_idx, week in enumerate(WEEKS):
        df_w = pd.DataFrame({
            "Partner": [e["name"] for e in EMPLOYEES],
            "TİP": [e["tip"] for e in EMPLOYEES]
        })
        for d_idx, d in enumerate(WEEK_DAYS):
            col_name = f"{d} ({w_idx*7 + d_idx + 1})"
            shifts_col = []
            for emp in EMPLOYEES:
                shifts_col.append(pats[emp["name"]][w_idx*7 + d_idx])
            df_w[col_name] = shifts_col
        monthly_data[week] = df_w
    return monthly_data

def save_current_data(data):
    try:
        dict_to_save = {w: df.to_dict(orient="records") for w, df in data.items()}
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(dict_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Kayıt hatası: {e}")

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data_dict = json.load(f)
                return {w: pd.DataFrame(df_raw) for w, df_raw in data_dict.items()}
        except Exception:
            pass
    return generate_perfect_armada_schedule()

if "monthly_shifts" not in st.session_state:
    st.session_state.monthly_shifts = load_data()

st.markdown('''
<div class="header-container">
    <img src="data:image/svg+xml;base64,NDA0OiBOb3QgRm91bmQ=" class="logo-img" alt="Starbucks Logo">
    <div>
        <h1 class="header-title">Armada Starbucks Vardiya & Aylık Raporlama Yönetimi</h1>
        <p class="header-sub">STORE MANAGEMENT & SHIFT SCHEDULING SYSTEM</p>
    </div>
</div>
''', unsafe_allow_html=True)

st.subheader("🛠️ Manuel Vardiya & İzin Düzenleme")

c1, c2, c3 = st.columns([1.5, 1.5, 1.5])
with c1:
    sel_week = st.selectbox("Hafta Seç", WEEKS, key="dyn_week")
with c2:
    sel_emp = st.selectbox("Partner Seç", [e["name"] for e in EMPLOYEES], key="dyn_emp")

current_df = st.session_state.monthly_shifts[sel_week]
day_cols = [c for c in current_df.columns if c not in ["Partner", "TİP", "Haftalık Saat"]]

with c3:
    sel_day = st.selectbox("Gün Seç", day_cols, key="dyn_day")

emp_idx = current_df[current_df["Partner"] == sel_emp].index[0]
curr_val = str(current_df.at[emp_idx, sel_day])

st.markdown(f"**Şu Anki Durum:** `{curr_val}`")

b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    if st.button("🔴 OFF (İzin) Yap", use_container_width=True):
        st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = "OFF"
        save_current_data(st.session_state.monthly_shifts)
        st.rerun()

with b2:
    if st.button("☀️ Açılış (07:30)", use_container_width=True):
        val = A_PT if next(e["tip"] for e in EMPLOYEES if e["name"] == sel_emp) == "PT" else A_FT
        st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = val
        save_current_data(st.session_state.monthly_shifts)
        st.rerun()

with b3:
    if st.button("☕ Ara (12:00)", use_container_width=True):
        st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = ARA
        save_current_data(st.session_state.monthly_shifts)
        st.rerun()

with b4:
    if st.button("🌙 Kapanış", use_container_width=True):
        val = K_PT if next(e["tip"] for e in EMPLOYEES if e["name"] == sel_emp) == "PT" else K_FT
        st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = val
        save_current_data(st.session_state.monthly_shifts)
        st.rerun()

with b5:
    if st.button("📋 Rapor / İzin", use_container_width=True):
        st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = "YILLIK İZİN"
        save_current_data(st.session_state.monthly_shifts)
        st.rerun()

with st.form("custom_edit_form", clear_on_submit=False):
    c_in, c_btn = st.columns([3, 1])
    with c_in:
        custom_val = st.text_input("Veya Özel Saat Yaz (Örn: 09:00-18:00, 10:00-19:00):", value=curr_val)
    with c_btn:
        st.write("")
        custom_save = st.form_submit_button("💾 Özel Saati Kaydet", type="primary", use_container_width=True)
        if custom_save:
            st.session_state.monthly_shifts[sel_week].at[emp_idx, sel_day] = custom_val.strip()
            save_current_data(st.session_state.monthly_shifts)
            st.rerun()

st.subheader("📅 Haftalık Vardiya Çizelgeleri")
tabs = st.tabs(WEEKS)

for idx, week in enumerate(WEEKS):
    with tabs[idx]:
        df_w = st.session_state.monthly_shifts[week].copy()
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
for week in WEEKS:
    df_w = st.session_state.monthly_shifts[week]
    d_cols = [c for c in df_w.columns if c not in ["Partner", "TİP", "Haftalık Saat"]]
    for _, row in df_w.iterrows():
        p_name = row["Partner"]
        for d in d_cols:
            all_days_series[p_name].append((d, str(row[d])))

st.subheader("📊 Aylık Partner Çalışma ve Vardiya Raporu")

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
        
    limit = 112 if p_tip == "PT" else 180
    
    if total_hours > limit:
        diff = total_hours - limit
        status = f"🚨 +{format_hour(diff)} Kota Aşımı (Maks {limit}s)!"
    elif total_hours < limit:
        diff = limit - total_hours
        status = f"ℹ️ -{format_hour(diff)} Eksik"
    else:
        status = "✅ Tam Kota"
        
    report_rows.append({
        "Partner": p_name,
        "TİP": p_tip,
        "Açılış Sayısı": cnt_acilis,
        "Ara Vardiya Sayısı": cnt_ara,
        "Kapanış Sayısı": cnt_kapanis,
        "OFF Gün": cnt_off,
        "İzin": cnt_izin,
        "Rapor": cnt_rapor,
        "Toplam Çalışılan Saat": format_hour(total_hours),
        "Aylık Kota": format_hour(limit),
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
        styles[10] = "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
    elif "Tam Kota" in str(row["Durum"]):
        styles[10] = "background-color: #dcfce7; color: #166534; font-weight: bold;"
    return styles

st.dataframe(
    report_df.style.apply(style_report_table, axis=1),
    use_container_width=True,
    hide_index=True
)

st.subheader("📄 Resmi Aylık Rapor Çıktısı (PDF & Yazdırma)")

def get_report_html():
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Armada Starbucks Vardiya Raporu</title>
    <style>
        @page { size: A4 landscape; margin: 8mm; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0f172a; font-size: 8pt; padding: 10px; }
        h1 { color: #006241; font-size: 15pt; margin: 0 0 4px 0; text-align: center; }
        p.sub { text-align: center; color: #64748b; font-size: 8.5pt; margin: 0 0 10px 0; }
        h2 { color: #1e3a8a; font-size: 10pt; margin: 12px 0 5px 0; border-bottom: 1.5px solid #cbd5e1; padding-bottom: 3px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 10px; }
        th, td { border: 1px solid #cbd5e1; padding: 4px; text-align: center; }
        th { background-color: #f1f5f9; font-weight: bold; color: #0f172a; }
        .mgr { background-color: #1e3a8a; color: #ffffff; font-weight: bold; }
        .pt { background-color: #fef08a; color: #854d0e; font-weight: bold; }
        .alert { background-color: #fee2e2; color: #991b1b; font-weight: bold; }
        .ok { background-color: #dcfce7; color: #166534; font-weight: bold; }
        @media print {
            .no-print { display: none; }
        }
    </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom: 12px; text-align: right;">
            <button onclick="window.print()" style="padding: 8px 16px; background-color: #006241; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">🖨️ PDF Olarak Kaydet / Yazdır</button>
        </div>
        <h1>☕ Armada Starbucks - Aylık Vardiya & Performans Raporu</h1>
        <p class="sub">4 Haftalık Çalışma Çizelgesi ve İstatistik Özeti (1 Saat Mola Düşümlü Net Saatler)</p>
        
        <h2>📊 Aylık Partner Çalışma ve İstatistik Tablosu</h2>
        <table>
            <thead>
                <tr>
                    <th>Partner</th><th>TİP</th><th>Açılış</th><th>Ara</th><th>Kapanış</th><th>OFF</th><th>İzin</th><th>Rapor</th><th>Toplam Net Saat</th><th>Aylık Kota</th><th>Durum</th>
                </tr>
            </thead>
            <tbody>
    '''
    for _, r in report_df.iterrows():
        p_cls = "mgr" if r["TİP"] in ["SM", "SSV"] else ("pt" if r["TİP"] == "PT" else "")
        d_cls = "alert" if "Kota Aşımı" in str(r["Durum"]) else ("ok" if "Tam Kota" in str(r["Durum"]) else "")
        html_content += f'''
        <tr>
            <td class="{p_cls}">{r['Partner']}</td><td class="{p_cls}">{r['TİP']}</td><td>{r['Açılış Sayısı']}</td><td>{r['Ara Vardiya Sayısı']}</td><td>{r['Kapanış Sayısı']}</td><td>{r['OFF Gün']}</td><td>{r['İzin']}</td><td>{r['Rapor']}</td><td><b>{r['Toplam Çalışılan Saat']}</b></td><td>{r['Aylık Kota']}</td><td class="{d_cls}">{r['Durum']}</td>
        </tr>
        '''
    html_content += "</tbody></table>"
    
    for week in WEEKS:
        df_w = st.session_state.monthly_shifts[week]
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
        
    html_content += '''
    </body>
    </html>
    '''
    return html_content

report_html = get_report_html()
b64 = base64.b64encode(report_html.encode("utf-8")).decode("utf-8")
st.markdown(
    f'<a href="data:text/html;base64,{b64}" target="_blank" download="Armada_Starbucks_Aylik_Rapor.html" style="display:inline-block;padding:10px 22px;background-color:#006241;color:white;text-decoration:none;border-radius:6px;font-weight:bold;">📥 Resmi Raporu Aç ve PDF Olarak Yazdır / Kaydet</a>',
    unsafe_allow_html=True
)
