import streamlit as st
import pandas as pd
import json
import os
import random
import re
import base64
from datetime import datetime

# ============================================================
# AYARLAR
# ============================================================

st.set_page_config(
    page_title="Armada Starbucks Vardiya",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SAVE_FILE = os.path.expanduser(
    "~/Desktop/starbucks_armada_data.json"
)

DAY_NAMES = [
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
]

MONTH_NAMES = [
    "Ocak", "Şubat", "Mart", "Nisan",
    "Mayıs", "Haziran", "Temmuz", "Ağustos",
    "Eylül", "Ekim", "Kasım", "Aralık"
]

WEEKS = [
    "1. Hafta",
    "2. Hafta",
    "3. Hafta",
    "4. Hafta",
]

OFF = "OFF"

# ============================================================
# VARDİYALAR
# ============================================================

A_FT = "07:30-16:00"
K_FT = "15:30-00:00"

A_PT = "07:30-15:30"
K_PT = "16:00-00:00"

ARA_10 = "10:00-18:30"
ARA_12 = "12:00-20:30"

MUDUR_ARA = "09:00-17:30"

# ============================================================
# PERSONEL
# ============================================================

EMPLOYEES = [
    ("Onur Kaynak", "SM"),
    ("Banu Sezer", "SSV"),
    ("Göktuğ Gökdemir", "SSV"),

    ("Ceyda Işık", "FT"),
    ("Yusuf Efe Aydoğmuş", "FT"),
    ("Cansu Elibüyük", "FT"),
    ("Elif Karaca", "FT"),
    ("Vahti Ünal", "FT"),
    ("Cansu Yüksel", "FT"),
    ("Ebrar Sena Akkaya", "FT"),
    ("Ahmet Emre Demren", "FT"),
    ("Buse Kayabalı", "FT"),
    ("Ayça Yiğit", "FT"),

    ("Hayrunnisa Erdoğan", "PT"),
    ("Emir Altunbulak", "PT"),
]

ALL_EMPLOYEES = [x[0] for x in EMPLOYEES]

FT_NAMES = [
    name for name, tip in EMPLOYEES
    if tip == "FT"
]

MGR_NAMES = [
    "Onur Kaynak",
    "Banu Sezer",
    "Göktuğ Gökdemir",
]

SSV_NAMES = [
    "Banu Sezer",
    "Göktuğ Gökdemir",
]

PT_NAMES = [
    "Emir Altunbulak",
    "Hayrunnisa Erdoğan",
]

FT_MGR_NAMES = MGR_NAMES + FT_NAMES

# ============================================================
# NET SAAT HESABI
# ============================================================

def calculate_hours(shift):

    if shift is None:
        return 0.0

    shift = str(shift).strip()

    if shift == OFF:
        return 0.0

    if shift in ["İZİN", "RAPOR"]:
        return 7.5

    match = re.search(
        r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})",
        shift
    )

    if not match:
        return 0.0

    h1, m1, h2, m2 = map(
        int,
        match.groups()
    )

    start = h1 * 60 + m1
    end = h2 * 60 + m2

    if end <= start:
        end += 1440

    gross = (end - start) / 60

    # 1 saat mola
    return gross - 1


# ============================================================
# VARDİYA TİPİ
# ============================================================

def shift_type(shift):

    if shift == OFF:
        return "OFF"

    if not isinstance(shift, str):
        return "OTHER"

    if "07:30" in shift:
        return "OPEN"

    if "15:30" in shift or "16:00" in shift:
        return "CLOSE"

    if "09:00" in shift:
        return "MID"

    if "10:00" in shift or "12:00" in shift:
        return "ARA"

    return "OTHER"


def is_open(shift):
    return shift_type(shift) == "OPEN"


def is_close(shift):
    return shift_type(shift) == "CLOSE"


# ============================================================
# OFF DAĞITIMI
# ============================================================

def generate_off_days(rng):

    """
    13 FT/Müdür için:
    - Her kişi haftada tam 1 OFF
    - Günlük maksimum 2 OFF
    - Çarşamba mümkün olduğunca boş tutulur
    """

    names = FT_MGR_NAMES.copy()
    rng.shuffle(names)

    # Günlük kapasite
    capacity = {
        day: 2
        for day in range(7)
    }

    # Çarşamba yoğun gün:
    # mümkünse yalnızca 1 OFF
    capacity[2] = 1

    result = {}

    # Özel çalışanların OFF'larını
    # mümkün olduğunca kuralları destekleyecek şekilde dağıt.
    preferred = {
        "Cansu Elibüyük": [0, 1, 3, 4],
        "Vahti Ünal": [0, 1, 3, 4],
        "Buse Kayabalı": [0, 1, 3, 4],
        "Ceyda Işık": [0, 1, 3, 4, 5, 6],
        "Yusuf Efe Aydoğmuş": [0, 1, 3, 4, 5, 6],
    }

    # Önce özel kişiler
    special = [
        "Cansu Elibüyük",
        "Vahti Ünal",
        "Buse Kayabalı",
        "Ceyda Işık",
        "Yusuf Efe Aydoğmuş",
    ]

    for name in special:

        candidates = preferred.get(
            name,
            list(range(7))
        ).copy()

        rng.shuffle(candidates)

        selected = None

        for day in candidates:

            if capacity[day] > 0:

                selected = day
                break

        if selected is None:
            raise RuntimeError(
                "OFF dağılımı çözülemedi."
            )

        result[name] = selected
        capacity[selected] -= 1

    # Kalan kişiler
    remaining = [
        n for n in names
        if n not in result
    ]

    for name in remaining:

        candidates = list(range(7))
        rng.shuffle(candidates)

        selected = None

        for day in candidates:

            if capacity[day] > 0:

                selected = day
                break

        if selected is None:
            raise RuntimeError(
                "Günlük OFF kapasitesi doldu."
            )

        result[name] = selected
        capacity[selected] -= 1

    return result


# ============================================================
# HAFTALIK ÜRETİCİ
# ============================================================

def create_empty_schedule():

    return {
        name: [None] * 28
        for name in ALL_EMPLOYEES
    }


# ============================================================
# FT VARDİYA ÜRETİMİ
# ============================================================

def create_ft_shifts(
    name,
    off_day,
    rng,
):

    """
    Çalışma günlerinde temel olarak 3 Açılış / 3 Kapanış.
    Ergonomi daha sonra kontrol edilir.
    """

    shifts = [None] * 7

    work_days = [
        d for d in range(7)
        if d != off_day
    ]

    open_days = set(
        rng.sample(work_days, 3)
    )

    for day in work_days:

        if day in open_days:
            shifts[day] = A_FT
        else:
            shifts[day] = K_FT

    return shifts


# ============================================================
# ONUR
# ============================================================

def create_onur_shifts(
    off_day,
    rng,
):

    shifts = [None] * 7

    work_days = [
        d for d in range(7)
        if d != off_day
    ]

    close_day = rng.choice(work_days)

    for day in work_days:

        if day == close_day:
            shifts[day] = K_FT
        else:
            shifts[day] = A_FT

    return shifts


# ============================================================
# SSV
# ============================================================

def create_ssv_shifts(
    off_day,
    rng,
):

    shifts = [None] * 7

    work_days = [
        d for d in range(7)
        if d != off_day
    ]

    open_days = set(
        rng.sample(work_days, 3)
    )

    for day in work_days:

        if day in open_days:
            shifts[day] = A_FT
        else:
            shifts[day] = K_FT

    return shifts


# ============================================================
# ERGONOMİ DÜZELTME
# ============================================================

def fix_ergonomics(
    schedule,
    locked,
):

    """
    Kapanış -> ertesi gün Açılış yasaktır.

    ÖNEMLİ:
    OFF hücresine ASLA dokunulmaz.
    """

    for day in range(1, 28):

        for name in ALL_EMPLOYEES:

            previous = schedule[name][day - 1]
            current = schedule[name][day]

            if not is_close(previous):
                continue

            if not is_open(current):
                continue

            # OFF kilitliyse hiçbir şekilde değiştirme.
            if schedule[name][day] == OFF:
                continue

            # Sonraki gün çalışma günü.
            if name in PT_NAMES:
                schedule[name][day] = K_PT

            elif name in MGR_NAMES:
                schedule[name][day] = MUDUR_ARA

            else:
                schedule[name][day] = ARA_12


# ============================================================
# ELİBÜYÜK / BUSE / VAHTİ
# ============================================================

def apply_special_rules(
    schedule,
    off_map,
):

    for week in range(4):

        start = week * 7

        # ----------------------------------------------------
        # ELİBÜYÜK
        # ----------------------------------------------------

        elif_off = off_map[
            "Cansu Elibüyük"
        ]

        for d in range(7):

            idx = start + d

            if d == elif_off:
                schedule[
                    "Cansu Elibüyük"
                ][idx] = OFF

            elif d < 5:
                schedule[
                    "Cansu Elibüyük"
                ][idx] = A_FT

            else:
                schedule[
                    "Cansu Elibüyük"
                ][idx] = K_FT

        # ----------------------------------------------------
        # VAHTİ
        # ----------------------------------------------------

        vahti_off = off_map[
            "Vahti Ünal"
        ]

        for d in range(7):

            idx = start + d

            if d == vahti_off:
                schedule[
                    "Vahti Ünal"
                ][idx] = OFF

            elif d < 5:
                schedule[
                    "Vahti Ünal"
                ][idx] = K_FT

            else:
                schedule[
                    "Vahti Ünal"
                ][idx] = A_FT

        # ----------------------------------------------------
        # BUSE
        # ----------------------------------------------------

        buse_off = off_map[
            "Buse Kayabalı"
        ]

        for d in range(7):

            idx = start + d

            if d == buse_off:

                schedule[
                    "Buse Kayabalı"
                ][idx] = OFF

            elif d == elif_off:

                # Elibüyük OFF olduğunda
                # Buse kesin açılış.
                schedule[
                    "Buse Kayabalı"
                ][idx] = A_FT

            elif d in [0, 2, 5]:

                schedule[
                    "Buse Kayabalı"
                ][idx] = A_FT

            else:

                schedule[
                    "Buse Kayabalı"
                ][idx] = K_FT


# ============================================================
# CEYDA / EFE
# ============================================================

def fix_ceyda_efe(
    schedule,
):

    """
    Hafta içi Ceyda ve Efe aynı gün
    Açılış yapamaz.
    """

    for day in range(28):

        if day % 7 >= 5:
            continue

        ceyda = schedule[
            "Ceyda Işık"
        ][day]

        efe = schedule[
            "Yusuf Efe Aydoğmuş"
        ][day]

        if not (
            is_open(ceyda)
            and is_open(efe)
        ):
            continue

        # Birini Ara yap.
        # OFF hücresine dokunulmaz çünkü
        # burada iki hücre de çalışma günü.
        schedule[
            "Yusuf Efe Aydoğmuş"
        ][day] = ARA_12


# ============================================================
# MÜDÜR - SSV
# ============================================================

def apply_manager_ssv_rule(
    schedule,
):

    """
    Müdür Açılış + bir SSV Kapanış ise
    diğer SSV = 09:00-17:30.
    """

    for day in range(28):

        manager = schedule[
            "Onur Kaynak"
        ][day]

        banu = schedule[
            "Banu Sezer"
        ][day]

        goktug = schedule[
            "Göktuğ Gökdemir"
        ][day]

        if not is_open(manager):
            continue

        if (
            is_close(banu)
            and goktug != OFF
        ):
            schedule[
                "Göktuğ Gökdemir"
            ][day] = MUDUR_ARA

        elif (
            is_close(goktug)
            and banu != OFF
        ):
            schedule[
                "Banu Sezer"
            ][day] = MUDUR_ARA


# ============================================================
# PT ÜRETİMİ
# ============================================================

def create_pt_schedule(
    name,
    week,
    rng,
):

    """
    Her hafta 4 gün çalışma.
    4 hafta x 4 gün = 16 iş günü.
    16 x 7 = 112 net saat.
    """

    patterns = [
        [0, 2, 4, 6],
        [0, 1, 3, 5],
        [1, 2, 4, 6],
        [0, 2, 3, 5],
    ]

    work_days = patterns[
        (week + (
            1 if name == "Hayrunnisa Erdoğan"
            else 0
        )) % len(patterns)
    ]

    shifts = [OFF] * 7

    for d in work_days:

        if d in [0, 2, 4]:
            shifts[d] = A_PT
        else:
            shifts[d] = K_PT

    return shifts


# ============================================================
# AYLIK VARDİYA ÜRET
# ============================================================

def generate_schedule(
    seed=None,
):

    if seed is None:
        seed = random.randint(
            1,
            999999999
        )

    rng = random.Random(seed)

    schedule = create_empty_schedule()

    # ========================================================
    # 4 HAFTA
    # ========================================================

    for week in range(4):

        start = week * 7

        # ----------------------------------------------------
        # OFF HARİTASI
        # ----------------------------------------------------

        off_map = generate_off_days(
            rng
        )

        # ----------------------------------------------------
        # FT / MÜDÜR OFF
        # ----------------------------------------------------

        for name in FT_MGR_NAMES:

            off_day = off_map[name]

            schedule[name][
                start + off_day
            ] = OFF

        # ----------------------------------------------------
        # ONUR
        # ----------------------------------------------------

        onur_off = off_map[
            "Onur Kaynak"
        ]

        onur_shifts = create_onur_shifts(
            onur_off,
            rng
        )

        for d in range(7):

            if d == onur_off:
                continue

            schedule[
                "Onur Kaynak"
            ][start + d] = onur_shifts[d]

        # ----------------------------------------------------
        # SSV
        # ----------------------------------------------------

        for name in SSV_NAMES:

            shifts = create_ssv_shifts(
                off_map[name],
                rng
            )

            for d in range(7):

                if d == off_map[name]:
                    continue

                schedule[name][
                    start + d
                ] = shifts[d]

        # ----------------------------------------------------
        # DİĞER FT
        # ----------------------------------------------------

        for name in FT_NAMES:

            if name in [
                "Cansu Elibüyük",
                "Vahti Ünal",
                "Buse Kayabalı",
            ]:
                continue

            shifts = create_ft_shifts(
                name,
                off_map[name],
                rng
            )

            for d in range(7):

                if d == off_map[name]:
                    continue

                schedule[name][
                    start + d
                ] = shifts[d]

        # ----------------------------------------------------
        # PT
        # ----------------------------------------------------

        for name in PT_NAMES:

            shifts = create_pt_schedule(
                name,
                week,
                rng
            )

            for d in range(7):

                schedule[name][
                    start + d
                ] = shifts[d]

        # ----------------------------------------------------
        # ÖZEL KURALLAR
        # ----------------------------------------------------

        apply_special_rules(
            schedule,
            off_map
        )

    # ========================================================
    # SON DÜZELTMELER
    # ========================================================

    fix_ceyda_efe(
        schedule
    )

    apply_manager_ssv_rule(
        schedule
    )

    fix_ergonomics(
        schedule,
        locked=set()
    )

    # Özel kurallar ergonomi sonrasında
    # tekrar kontrol edilir.
    apply_manager_ssv_rule(
        schedule
    )

    # ========================================================
    # OFF'ları tekrar kilitle
    # ========================================================

    # OFF sayısı ve özel kuralların değişmediğini
    # doğrulamak için kontrol motoru.
    errors = validate_schedule(
        schedule
    )

    if errors:

        # Bazı kombinasyonlar rastgele seçimden
        # dolayı ergonomiyle çakışabilir.
        # Yeni seed ile tekrar denenecek.
        raise RuntimeError(
            "\n".join(errors)
        )

    return schedule


# ============================================================
# SAĞLAM ÜRETİM
# ============================================================

def generate_valid_schedule():

    for attempt in range(10000):

        try:

            seed = random.randint(
                1,
                999999999
            )

            schedule = generate_schedule(
                seed
            )

            return schedule

        except RuntimeError:
            continue

    raise RuntimeError(
        "10000 denemede geçerli vardiya üretilemedi."
    )


# ============================================================
# DOĞRULAMA
# ============================================================

def validate_schedule(
    schedule,
):

    errors = []

    # ========================================================
    # KOTA
    # ========================================================

    for name in FT_MGR_NAMES:

        total = sum(
            calculate_hours(
                schedule[name][d]
            )
            for d in range(28)
        )

        if abs(total - 180.0) > 0.01:

            errors.append(
                f"{name}: aylık {total:.1f}s "
                f"oldu, 180.0s olmalı."
            )

    for name in PT_NAMES:

        total = sum(
            calculate_hours(
                schedule[name][d]
            )
            for d in range(28)
        )

        if abs(total - 112.0) > 0.01:

            errors.append(
                f"{name}: aylık {total:.1f}s "
                f"oldu, 112.0s olmalı."
            )

        work_days = sum(
            schedule[name][d] != OFF
            for d in range(28)
        )

        if work_days != 16:

            errors.append(
                f"{name}: {work_days} iş günü "
                f"oldu, 16 olmalı."
            )

    # ========================================================
    # FT/MÜDÜR HAFTALIK OFF
    # ========================================================

    for name in FT_MGR_NAMES:

        for week in range(4):

            start = week * 7
            end = start + 7

            off_count = sum(
                schedule[name][d] == OFF
                for d in range(start, end)
            )

            if off_count != 1:

                errors.append(
                    f"{name}: "
                    f"{week + 1}. hafta "
                    f"{off_count} OFF."
                )

    # ========================================================
    # GÜNLÜK OFF <= 2
    # SADECE FT + MÜDÜR
    # ========================================================

    for day in range(28):

        count = sum(
            schedule[name][day] == OFF
            for name in FT_MGR_NAMES
        )

        if count > 2:

            errors.append(
                f"{day + 1}. gün "
                f"FT/Müdür OFF={count}; "
                f"maksimum 2."
            )

    # ========================================================
    # ELİBÜYÜK
    # ========================================================

    for day in range(28):

        weekday = day % 7
        shift = schedule[
            "Cansu Elibüyük"
        ][day]

        if shift == OFF:
            continue

        expected = (
            A_FT
            if weekday < 5
            else K_FT
        )

        if shift != expected:

            errors.append(
                f"Elibüyük {day + 1}. gün "
                f"{shift}; beklenen "
                f"{expected}."
            )

    # ========================================================
    # ELİBÜYÜK OFF -> BUSE AÇILIŞ
    # ========================================================

    for day in range(28):

        if schedule[
            "Cansu Elibüyük"
        ][day] == OFF:

            if schedule[
                "Buse Kayabalı"
            ][day] != A_FT:

                errors.append(
                    f"{day + 1}. gün "
                    "Elibüyük OFF iken "
                    "Buse Açılış değil."
                )

    # ========================================================
    # VAHTİ
    # ========================================================

    for day in range(28):

        weekday = day % 7

        shift = schedule[
            "Vahti Ünal"
        ][day]

        if shift == OFF:
            continue

        expected = (
            K_FT
            if weekday < 5
            else A_FT
        )

        if shift != expected:

            errors.append(
                f"Vahti {day + 1}. gün "
                f"{shift}; beklenen "
                f"{expected}."
            )

    # ========================================================
    # CEYDA + EFE
    # ========================================================

    for day in range(28):

        if day % 7 >= 5:
            continue

        if (
            is_open(
                schedule[
                    "Ceyda Işık"
                ][day]
            )
            and
            is_open(
                schedule[
                    "Yusuf Efe Aydoğmuş"
                ][day]
            )
        ):

            errors.append(
                f"{day + 1}. gün "
                "Ceyda ve Efe aynı anda Açılış."
            )

    # ========================================================
    # ERGONOMİ
    # ========================================================

    for name in ALL_EMPLOYEES:

        for day in range(1, 28):

            previous = schedule[
                name
            ][day - 1]

            current = schedule[
                name
            ][day]

            if (
                is_close(previous)
                and
                is_open(current)
            ):

                errors.append(
                    f"{name}: "
                    f"{day}. gün Kapanış -> "
                    f"{day + 1}. gün Açılış."
                )

    # ========================================================
    # ONUR
    # ========================================================

    for week in range(4):

        start = week * 7
        end = start + 7

        values = schedule[
            "Onur Kaynak"
        ][start:end]

        if values.count(OFF) != 1:

            errors.append(
                f"Onur {week + 1}. hafta "
                "tam 1 OFF olmalı."
            )

        if values.count(K_FT) != 1:

            errors.append(
                f"Onur {week + 1}. hafta "
                "tam 1 Kapanış olmalı."
            )

    return errors


# ============================================================
# DATAFRAME
# ============================================================

def schedule_to_dataframe(
    schedule,
    week,
):

    start = week * 7

    rows = []

    for name, tip in EMPLOYEES:

        row = {
            "Partner": name,
            "TİP": tip,
        }

        for d in range(7):

            day_number = start + d + 1

            row[
                f"{DAY_NAMES[d]} ({day_number})"
            ] = schedule[name][
                start + d
            ]

        total = sum(
            calculate_hours(
                schedule[name][start + d]
            )
            for d in range(7)
        )

        row["Haftalık Saat"] = round(
            total,
            1
        )

        rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# JSON KAYIT
# ============================================================

def save_schedule(
    month_key,
    schedule,
):

    data = {
        month_key: schedule
    }

    os.makedirs(
        os.path.dirname(SAVE_FILE),
        exist_ok=True
    )

    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def load_schedule(
    month_key,
):

    if not os.path.exists(
        SAVE_FILE
    ):
        return None

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data.get(
            month_key
        )

    except Exception:
        return None


# ============================================================
# LOGO
# ============================================================

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 500 500">

<circle
cx="250"
cy="250"
r="245"
fill="#006241"/>

<circle
cx="250"
cy="250"
r="190"
fill="none"
stroke="white"
stroke-width="8"/>

<text
x="250"
y="280"
text-anchor="middle"
font-size="130"
font-family="Arial"
font-weight="bold"
fill="white">
S
</text>

</svg>
"""

logo_b64 = base64.b64encode(
    LOGO_SVG.encode()
).decode()

LOGO_URI = (
    "data:image/svg+xml;base64,"
    + logo_b64
)

st.markdown(
    f"""
<style>

.stApp {{
    background:#080c14;
}}

.header {{
    display:flex;
    align-items:center;
    gap:18px;
    padding:15px 20px;
    margin-bottom:20px;
    background:#0f172a;
    border-radius:12px;
    border-bottom:2px solid #006241;
}}

.logo {{
    width:60px;
    height:60px;
}}

.title {{
    font-size:24px;
    font-weight:800;
    color:white;
}}

.subtitle {{
    font-size:12px;
    color:#00a862;
    font-weight:700;
}}

</style>

<div class="header">

<img
class="logo"
src="{LOGO_URI}"
>

<div>

<div class="title">
Armada Starbucks Vardiya Yönetimi
</div>

<div class="subtitle">
SHIFT SCHEDULING & OPERATIONAL MANAGEMENT
</div>

</div>

</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# TARİH
# ============================================================

col1, col2, col3 = st.columns(
    [1, 1.5, 2]
)

with col1:

    year = st.selectbox(
        "Yıl",
        [2026, 2027, 2028],
        index=0
    )

with col2:

    month = st.selectbox(
        "Ay",
        range(1, 13),
        index=datetime.now().month - 1,
        format_func=lambda x:
            MONTH_NAMES[x - 1]
    )

month_key = (
    f"{year}-{month:02d}"
)

# ============================================================
# SESSION
# ============================================================

if "schedule" not in st.session_state:

    loaded = load_schedule(
        month_key
    )

    if loaded:

        st.session_state.schedule = loaded

    else:

        try:

            st.session_state.schedule = (
                generate_valid_schedule()
            )

            save_schedule(
                month_key,
                st.session_state.schedule
            )

        except Exception as e:

            st.error(
                f"Vardiya üretilemedi: {e}"
            )

            st.stop()


# ============================================================
# YENİ VARDİYA
# ============================================================

with col3:

    if st.button(
        "🎲 Yeni Dinamik Vardiya Üret",
        use_container_width=True,
        type="primary"
    ):

        try:

            new_schedule = (
                generate_valid_schedule()
            )

            st.session_state.schedule = (
                new_schedule
            )

            save_schedule(
                month_key,
                new_schedule
            )

            st.success(
                "Tüm kuralları geçen yeni vardiya üretildi."
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Yeni vardiya üretilemedi: {e}"
            )


schedule = st.session_state.schedule


# ============================================================
# KURAL DURUMU
# ============================================================

errors = validate_schedule(
    schedule
)

if errors:

    st.error(
        "⚠️ Vardiya şu anda kuralları geçmiyor."
    )

    with st.expander(
        "Hataları Göster"
    ):

        for error in errors:
            st.write(
                "❌",
                error
            )

else:

    st.success(
        "✅ Vardiya üretimi tüm ana kuralları geçiyor."
    )


# ============================================================
# HAFTALIK TABLOLAR
# ============================================================

st.subheader(
    f"📅 {MONTH_NAMES[month - 1]} {year}"
)

tabs = st.tabs(
    WEEKS
)

for week_index, tab in enumerate(tabs):

    with tab:

        df = schedule_to_dataframe(
            schedule,
            week_index
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# AYLIK RAPOR
# ============================================================

st.subheader(
    "📊 Aylık Rapor"
)

report = []

for name, tip in EMPLOYEES:

    shifts = schedule[name]

    total = sum(
        calculate_hours(x)
        for x in shifts
    )

    opens = sum(
        is_open(x)
        for x in shifts
    )

    closes = sum(
        is_close(x)
        for x in shifts
    )

    offs = sum(
        x == OFF
        for x in shifts
    )

    target = (
        112.0
        if tip == "PT"
        else 180.0
    )

    status = (
        "✅ Tam Kota"
        if abs(total - target) < 0.01
        else f"❌ {total:.1f}s"
    )

    report.append({
        "Partner": name,
        "TİP": tip,
        "Açılış": opens,
        "Kapanış": closes,
        "OFF": offs,
        "Net Saat": round(total, 1),
        "Hedef": target,
        "Durum": status,
    })

report_df = pd.DataFrame(
    report
)

st.dataframe(
    report_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MANUEL DÜZENLEME
# ============================================================

st.subheader(
    "🛠️ Manuel Düzenleme"
)

c1, c2, c3 = st.columns(3)

with c1:

    selected_employee = st.selectbox(
        "Partner",
        ALL_EMPLOYEES
    )

with c2:

    selected_day = st.number_input(
        "Gün",
        min_value=1,
        max_value=28,
        value=1
    )

with c3:

    current_shift = schedule[
        selected_employee
    ][selected_day - 1]

    st.write(
        f"Mevcut: **{current_shift}**"
    )


st.warning(
    "🔒 OFF hücresi vardiya butonları tarafından "
    "ezilemez."
)

b1, b2, b3, b4, b5 = st.columns(5)

with b1:

    if st.button(
        "🔴 OFF",
        use_container_width=True
    ):

        schedule[
            selected_employee
        ][selected_day - 1] = OFF

        save_schedule(
            month_key,
            schedule
        )

        st.rerun()


with b2:

    if st.button(
        "☀️ Açılış",
        use_container_width=True
    ):

        if current_shift != OFF:

            if selected_employee in PT_NAMES:
                value = A_PT
            else:
                value = A_FT

            schedule[
                selected_employee
            ][selected_day - 1] = value

            save_schedule(
                month_key,
                schedule
            )

            st.rerun()


with b3:

    if st.button(
        "☕ Ara 12:00",
        use_container_width=True
    ):

        if current_shift != OFF:

            schedule[
                selected_employee
            ][selected_day - 1] = ARA_12

            save_schedule(
                month_key,
                schedule
            )

            st.rerun()


with b4:

    if st.button(
        "☕ Ara 10:00",
        use_container_width=True
    ):

        if current_shift != OFF:

            schedule[
                selected_employee
            ][selected_day - 1] = ARA_10

            save_schedule(
                month_key,
                schedule
            )

            st.rerun()


with b5:

    if st.button(
        "🌙 Kapanış",
        use_container_width=True
    ):

        if current_shift != OFF:

            if selected_employee in PT_NAMES:
                value = K_PT
            else:
                value = K_FT

            schedule[
                selected_employee
            ][selected_day - 1] = value

            save_schedule(
                month_key,
                schedule
            )

            st.rerun()


# ============================================================
# SON DOĞRULAMA
# ============================================================

st.subheader(
    "🔍 Sistem Doğrulaması"
)

errors = validate_schedule(
    schedule
)

if not errors:

    st.success(
        "🟢 TÜM KURALLAR GEÇERLİ"
    )

    st.write(
        """
        • FT/Müdür aylık net kota: 180 saat  
        • PT aylık net kota: 112 saat  
        • FT/Müdür haftalık OFF: tam 1  
        • FT/Müdür günlük OFF: maksimum 2  
        • PT OFF'ları günlük 2 OFF sınırına dahil değil  
        • Elibüyük hafta içi Açılış  
        • Elibüyük hafta sonu Kapanış  
        • Elibüyük OFF → Buse Açılış  
        • Vahti hafta içi Kapanış  
        • Vahti hafta sonu Açılış  
        • Ceyda/Efe hafta içi aynı anda Açılış değil  
        • Kapanış → ertesi gün Açılış yok  
        • Onur haftada 1 OFF + 1 Kapanış  
        • Müdür Açılış + SSV Kapanış → diğer SSV 09:00  
        """
    )

else:

    st.error(
        f"{len(errors)} adet kural ihlali var."
    )

    for error in errors:

        st.write(
            "❌",
            error
        )


# ============================================================
# CSV İNDİR
# ============================================================

csv_df = report_df.copy()

csv_data = csv_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 Aylık Raporu CSV İndir",
    data=csv_data,
    file_name=(
        f"Armada_Starbucks_"
        f"{MONTH_NAMES[month - 1]}_"
        f"{year}.csv"
    ),
    mime="text/csv",
    use_container_width=True
)