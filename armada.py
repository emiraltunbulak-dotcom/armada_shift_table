import streamlit as st
import pandas as pd
import json
import os
import re
import base64
import random
from datetime import datetime

st.set_page_config(
    page_title="Armada Starbucks Vardiya",
    layout="wide",
    initial_sidebar_state="collapsed"
)

SAVE_FILE = os.path.expanduser("~/Desktop/starbucks_armada_data.json")


# ============================================================
# VARDİYA SABİTLERİ
# ============================================================

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


# ============================================================
# GÜNLER / AYLAR
# ============================================================

DAY_NAMES_TR = [
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar"
]

MONTH_NAMES_TR = [
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık"
]

WEEKS_TITLES = [
    "1. Hafta (1-7)",
    "2. Hafta (8-14)",
    "3. Hafta (15-21)",
    "4. Hafta (22-28)"
]


# ============================================================
# PERSONEL
# ============================================================

EMPLOYEES = [
    {
        "name": "Onur Kaynak",
        "tip": "SM",
        "role": "Müdür",
        "quota": 180
    },
    {
        "name": "Banu Sezer",
        "tip": "SSV",
        "role": "Müdür",
        "quota": 180
    },
    {
        "name": "Göktuğ Gökdemir",
        "tip": "SSV",
        "role": "Müdür",
        "quota": 180
    },
    {
        "name": "Ceyda Işık",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Yusuf Efe Aydoğmuş",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Cansu Elibüyük",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Elif Karaca",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Vahti Ünal",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Cansu Yüksel",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Hayrunnisa Erdoğan",
        "tip": "PT",
        "role": "Barista",
        "quota": 112
    },
    {
        "name": "Ebrar Sena Akkaya",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Ahmet Emre Demren",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Buse Kayabalı",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Ayça Yiğit",
        "tip": "FT",
        "role": "Barista",
        "quota": 180
    },
    {
        "name": "Emir Altunbulak",
        "tip": "PT",
        "role": "Barista",
        "quota": 112
    }
]


MGR_NAMES = [
    "Onur Kaynak",
    "Banu Sezer",
    "Göktuğ Gökdemir"
]


FT_NAMES = [
    "Cansu Elibüyük",
    "Buse Kayabalı",
    "Vahti Ünal",
    "Ceyda Işık",
    "Yusuf Efe Aydoğmuş",
    "Elif Karaca",
    "Cansu Yüksel",
    "Ebrar Sena Akkaya",
    "Ahmet Emre Demren",
    "Ayça Yiğit"
]


PT_NAMES = [
    "Emir Altunbulak",
    "Hayrunnisa Erdoğan"
]


ALL_NAMES = MGR_NAMES + FT_NAMES + PT_NAMES


# ============================================================
# VARDİYA YARDIMCI FONKSİYONLARI
# ============================================================

def calculate_net_hours(shift_str):

    s = str(shift_str).strip().upper()

    if not s or s in {
        "OFF",
        "BOŞ",
        "-",
        "0",
        "NONE"
    }:
        return 0.0

    if "RAPOR" in s or "İZİN" in s:
        return 7.5

    match = re.search(
        r"(\d{1,2})[:.](\d{2})\s*[-–]\s*(\d{1,2})[:.](\d{2})",
        s
    )

    if not match:
        return 0.0

    h1, m1, h2, m2 = map(
        int,
        match.groups()
    )

    start_min = h1 * 60 + m1
    end_min = h2 * 60 + m2

    if end_min <= start_min:
        end_min += 24 * 60

    gross = (end_min - start_min) / 60

    return max(
        0.0,
        gross - 1.0
    )


def categorize_shift(shift):

    s = str(shift).strip().upper()

    if not s or s in {
        "OFF",
        "BOŞ",
        "NONE"
    }:
        return "OFF"

    if "RAPOR" in s:
        return "Rapor"

    if "İZİN" in s:
        return "İzin"

    match = re.search(
        r"(\d{1,2})[:.](\d{2})",
        s
    )

    if not match:
        return "Özel Vardiya"

    hour = int(
        match.group(1)
    )

    if hour < 9:
        return "Açılış"

    if hour < 14:
        return "Ara"

    return "Kapanış"


def format_hour(hours):

    hours = round(
        float(hours),
        2
    )

    if hours.is_integer():
        return f"{int(hours)}s"

    return f"{hours:.1f}s"


def is_open(shift):

    return shift in {
        A_FT,
        A_PT,
        A_MGR
    }


def is_close(shift):

    return shift in {
        K_FT,
        K_PT,
        K_MGR
    }


def is_ara(shift):

    return shift in {
        ARA_10,
        ARA_12,
        MID_MGR
    }


def is_off(shift):

    return str(
        shift
    ).strip().upper() == "OFF"


# ============================================================
# ANA VARDİYA MOTORU
# ============================================================

def generate_armada_master_schedule(seed=None):

    rng = random.Random(
        seed if seed is not None else 42
    )

    schedule = {
        name: [OFF] * 28
        for name in ALL_NAMES
    }

    # --------------------------------------------------------
    # OFF GÜNLERİ
    # --------------------------------------------------------

    off_map = {

        "Cansu Elibüyük": 1,

        "Buse Kayabalı": 3,

        "Vahti Ünal": 4,

        "Ceyda Işık": 0,

        "Yusuf Efe Aydoğmuş": 4,

        "Elif Karaca": 6,

        "Cansu Yüksel": 5,

        "Ebrar Sena Akkaya": 1,

        "Ahmet Emre Demren": 5,

        "Ayça Yiğit": 6
    }


    # ========================================================
    # 4 HAFTA
    # ========================================================

    for week in range(4):

        base = week * 7


        # ====================================================
        # 1. MÜDÜRLER
        # ====================================================

        manager_pattern = [

            # PAZARTESİ
            {
                "Onur Kaynak": OFF,
                "Banu Sezer": A_MGR,
                "Göktuğ Gökdemir": K_MGR
            },

            # SALI - SEVKİYAT
            {
                "Onur Kaynak": A_MGR,
                "Banu Sezer": K_MGR,
                "Göktuğ Gökdemir": MID_MGR
            },

            # ÇARŞAMBA - YOĞUN
            {
                "Onur Kaynak": K_MGR,
                "Banu Sezer": A_MGR,
                "Göktuğ Gökdemir": MID_MGR
            },

            # PERŞEMBE - SEVKİYAT
            {
                "Onur Kaynak": A_MGR,
                "Banu Sezer": OFF,
                "Göktuğ Gökdemir": K_MGR
            },

            # CUMA
            {
                "Onur Kaynak": A_MGR,
                "Banu Sezer": K_MGR,
                "Göktuğ Gökdemir": OFF
            },

            # CUMARTESİ - SEVKİYAT + TEMİZLİK
            {
                "Onur Kaynak": MID_MGR,
                "Banu Sezer": K_MGR,
                "Göktuğ Gökdemir": A_MGR
            },

            # PAZAR - SEVKİYAT + TEMİZLİK
            {
                "Onur Kaynak": A_MGR,
                "Banu Sezer": K_MGR,
                "Göktuğ Gökdemir": MID_MGR
            }
        ]


        for day in range(7):

            abs_day = base + day

            for manager in MGR_NAMES:

                schedule[
                    manager
                ][abs_day] = manager_pattern[
                    day
                ][manager]


        # ====================================================
        # 2. PT PARTNERLER
        # ====================================================

        for day in range(7):

            abs_day = base + day


            # EMİR
            if day in {
                0,
                2,
                4,
                6
            }:

                if day in {
                    0,
                    4,
                    6
                }:

                    schedule[
                        "Emir Altunbulak"
                    ][abs_day] = A_PT

                else:

                    schedule[
                        "Emir Altunbulak"
                    ][abs_day] = K_PT

            else:

                schedule[
                    "Emir Altunbulak"
                ][abs_day] = OFF


            # HAYRUNNİSA
            if day in {
                1,
                2,
                3,
                5
            }:

                if day in {
                    1,
                    3,
                    5
                }:

                    schedule[
                        "Hayrunnisa Erdoğan"
                    ][abs_day] = A_PT

                else:

                    schedule[
                        "Hayrunnisa Erdoğan"
                    ][abs_day] = K_PT

            else:

                schedule[
                    "Hayrunnisa Erdoğan"
                ][abs_day] = OFF


        # ====================================================
        # 3. ELİBÜYÜK
        # ====================================================

        for day in range(7):

            abs_day = base + day

            if day == off_map[
                "Cansu Elibüyük"
            ]:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = OFF

            elif day < 5:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = A_FT

            else:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = K_FT


        # ====================================================
        # 4. VAHTİ
        # ====================================================

        for day in range(7):

            abs_day = base + day

            if day == off_map[
                "Vahti Ünal"
            ]:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = OFF

            elif day < 5:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = K_FT

            else:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = A_FT


        # ====================================================
        # 5. BUSE
        # ====================================================

        for day in range(7):

            abs_day = base + day


            if day == off_map[
                "Buse Kayabalı"
            ]:

                schedule[
                    "Buse Kayabalı"
                ][abs_day] = OFF


            elif day == off_map[
                "Cansu Elibüyük"
            ]:

                # Elibüyük izinliyse Buse açılış
                schedule[
                    "Buse Kayabalı"
                ][abs_day] = A_FT


            elif day in {
                0,
                2,
                5
            }:

                schedule[
                    "Buse Kayabalı"
                ][abs_day] = A_FT


            elif day in {
                4,
                6
            }:

                schedule[
                    "Buse Kayabalı"
                ][abs_day] = K_FT


            else:

                schedule[
                    "Buse Kayabalı"
                ][abs_day] = ARA_12


        # ====================================================
        # 6. DİĞER FT PARTNERLER
        # ====================================================

        other_ft = [
            "Ceyda Işık",
            "Yusuf Efe Aydoğmuş",
            "Elif Karaca",
            "Cansu Yüksel",
            "Ebrar Sena Akkaya",
            "Ahmet Emre Demren",
            "Ayça Yiğit"
        ]


        # OFF
        for name in other_ft:

            schedule[
                name
            ][
                base + off_map[name]
            ] = OFF


        # ----------------------------------------------------
        # VARDİYA DAĞITIMI
        # ----------------------------------------------------

        for name in other_ft:

            available_days = [
                day
                for day in range(7)
                if day != off_map[name]
            ]

            rng.shuffle(
                available_days
            )


            # 3 AÇILIŞ
            open_days = []

            for day in available_days:

                if len(open_days) >= 3:
                    break

                abs_day = base + day

                # Önceki gün kapanışsa açılış verme.
                if abs_day > 0:

                    if is_close(
                        schedule[
                            name
                        ][abs_day - 1]
                    ):
                        continue


                # Ceyda + Efe aynı açılış olamaz.
                if name == "Ceyda Işık":

                    if is_open(
                        schedule[
                            "Yusuf Efe Aydoğmuş"
                        ][abs_day]
                    ):
                        continue


                if name == "Yusuf Efe Aydoğmuş":

                    if is_open(
                        schedule[
                            "Ceyda Işık"
                        ][abs_day]
                    ):
                        continue


                open_days.append(day)


            # 2 KAPANIŞ
            close_days = []

            for day in available_days:

                if day in open_days:
                    continue

                if len(close_days) >= 2:
                    break

                close_days.append(day)


            # ARA
            remaining_days = [
                day
                for day in available_days
                if day not in open_days
                and day not in close_days
            ]


            ara_day = None

            for day in remaining_days:

                abs_day = base + day

                if abs_day > 0:

                    if is_ara(
                        schedule[
                            name
                        ][abs_day - 1]
                    ):
                        continue

                ara_day = day
                break


            # Eğer ara atanamadıysa kalan günü kullan.
            if (
                ara_day is None
                and remaining_days
            ):

                ara_day = remaining_days[0]


            # ATAMALAR
            for day in open_days:

                schedule[
                    name
                ][base + day] = A_FT


            for day in close_days:

                schedule[
                    name
                ][base + day] = K_FT


            if ara_day is not None:

                schedule[
                    name
                ][base + ara_day] = rng.choice(
                    [
                        ARA_10,
                        ARA_12
                    ]
                )


        # ====================================================
        # 7. CEYDA + EFE AÇILIŞ KONTROLÜ
        # ====================================================

        for day in range(7):

            abs_day = base + day

            ceyda_open = is_open(
                schedule[
                    "Ceyda Işık"
                ][abs_day]
            )

            efe_open = is_open(
                schedule[
                    "Yusuf Efe Aydoğmuş"
                ][abs_day]
            )


            if ceyda_open and efe_open:

                if day != off_map[
                    "Yusuf Efe Aydoğmuş"
                ]:

                    schedule[
                        "Yusuf Efe Aydoğmuş"
                    ][abs_day] = ARA_12


        # ====================================================
        # 8. ARKA ARKAYA ARA KONTROLÜ
        # ====================================================

        for name in FT_NAMES:

            for day in range(1, 7):

                abs_day = base + day

                current_shift = schedule[
                    name
                ][abs_day]

                previous_shift = schedule[
                    name
                ][abs_day - 1]


                if (
                    is_ara(current_shift)
                    and
                    is_ara(previous_shift)
                ):

                    if name == "Cansu Elibüyük":

                        if day < 5:

                            schedule[
                                name
                            ][abs_day] = A_FT

                        else:

                            schedule[
                                name
                            ][abs_day] = K_FT

                    elif day != off_map.get(
                        name,
                        -1
                    ):

                        schedule[
                            name
                        ][abs_day] = K_FT


        # ====================================================
        # 9. KAPANIŞ -> AÇILIŞ KONTROLÜ
        # ====================================================

        for name in FT_NAMES:

            if name in {
                "Cansu Elibüyük",
                "Vahti Ünal"
            }:
                continue


            for day in range(1, 7):

                abs_day = base + day

                previous_shift = schedule[
                    name
                ][abs_day - 1]

                current_shift = schedule[
                    name
                ][abs_day]


                if (
                    is_close(previous_shift)
                    and
                    is_open(current_shift)
                ):

                    if day != off_map.get(
                        name,
                        -1
                    ):

                        schedule[
                            name
                        ][abs_day] = ARA_12


        # ====================================================
        # 10. SEVKİYAT GÜNLERİ
        # ====================================================

        shipment_days = {
            1,
            3,
            5,
            6
        }


        for day in shipment_days:

            abs_day = base + day


            already_ara = any(
                is_ara(
                    schedule[name][abs_day]
                )
                for name in FT_NAMES
            )


            if already_ara:
                continue


            candidates = [
                name
                for name in FT_NAMES
                if name != "Cansu Elibüyük"
                and name != "Vahti Ünal"
                and not is_off(
                    schedule[name][abs_day]
                )
            ]


            rng.shuffle(
                candidates
            )


            for name in candidates:

                if abs_day > 0:

                    if is_ara(
                        schedule[
                            name
                        ][abs_day - 1]
                    ):
                        continue


                schedule[
                    name
                ][abs_day] = (
                    ARA_12
                    if day in {
                        1,
                        5,
                        6
                    }
                    else ARA_10
                )

                break


        # ====================================================
        # 11. GÜNLÜK MAX 2 OFF
        # ====================================================

        for day in range(7):

            abs_day = base + day

            off_people = [
                name
                for name in ALL_NAMES
                if is_off(
                    schedule[name][abs_day]
                )
            ]


            if len(off_people) > 2:

                candidates = [
                    name
                    for name in off_people
                    if name in other_ft
                ]

                rng.shuffle(
                    candidates
                )


                while (
                    len(off_people) > 2
                    and candidates
                ):

                    person = candidates.pop()

                    if day < 5:

                        schedule[
                            person
                        ][abs_day] = A_FT

                    else:

                        schedule[
                            person
                        ][abs_day] = K_FT

                    off_people.remove(
                        person
                    )


        # ====================================================
        # 12. ELİBÜYÜK / VAHTİ SON KONTROL
        # ====================================================

        for day in range(7):

            abs_day = base + day


            # ELİBÜYÜK
            if day == off_map[
                "Cansu Elibüyük"
            ]:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = OFF

                schedule[
                    "Buse Kayabalı"
                ][abs_day] = A_FT


            elif day < 5:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = A_FT


            else:

                schedule[
                    "Cansu Elibüyük"
                ][abs_day] = K_FT


            # VAHTİ
            if day == off_map[
                "Vahti Ünal"
            ]:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = OFF


            elif day < 5:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = K_FT


            else:

                schedule[
                    "Vahti Ünal"
                ][abs_day] = A_FT


    # ========================================================
    # KURAL KONTROLÜ
    # ========================================================

    violations = []


    for week in range(4):

        base = week * 7


        # ----------------------------------------------------
        # GÜNLÜK OFF
        # ----------------------------------------------------

        for day in range(7):

            abs_day = base + day

            off_count = sum(
                1
                for name in ALL_NAMES
                if is_off(
                    schedule[name][abs_day]
                )
            )


            if off_count > 2:

                violations.append(
                    f"{WEEKS_TITLES[week]} / "
                    f"{DAY_NAMES_TR[day]}: "
                    f"{off_count} OFF"
                )


        # ----------------------------------------------------
        # CEYDA + EFE
        # ----------------------------------------------------

        for day in range(7):

            abs_day = base + day

            if (
                is_open(
                    schedule[
                        "Ceyda Işık"
                    ][abs_day]
                )
                and
                is_open(
                    schedule[
                        "Yusuf Efe Aydoğmuş"
                    ][abs_day]
                )
            ):

                violations.append(
                    f"{WEEKS_TITLES[week]} / "
                    f"{DAY_NAMES_TR[day]}: "
                    f"Ceyda ve Efe birlikte açılış"
                )


        # ----------------------------------------------------
        # ELİBÜYÜK ARA
        # ----------------------------------------------------

        for day in range(7):

            abs_day = base + day

            if is_ara(
                schedule[
                    "Cansu Elibüyük"
                ][abs_day]
            ):

                violations.append(
                    f"{WEEKS_TITLES[week]} / "
                    f"{DAY_NAMES_TR[day]}: "
                    f"Elibüyük aracı"
                )


        # ----------------------------------------------------
        # ARKA ARKAYA ARA
        # ----------------------------------------------------

        for name in FT_NAMES:

            for day in range(1, 7):

                abs_day = base + day

                if (
                    is_ara(
                        schedule[name][abs_day]
                    )
                    and
                    is_ara(
                        schedule[name][abs_day - 1]
                    )
                ):

                    violations.append(
                        f"{WEEKS_TITLES[week]}: "
                        f"{name} arka arkaya aracı"
                    )


        # ----------------------------------------------------
        # KAPANIŞ -> AÇILIŞ
        # ----------------------------------------------------

        for name in FT_NAMES:

            for day in range(1, 7):

                abs_day = base + day

                if (
                    is_close(
                        schedule[name][abs_day - 1]
                    )
                    and
                    is_open(
                        schedule[name][abs_day]
                    )
                ):

                    if name not in {
                        "Cansu Elibüyük",
                        "Vahti Ünal"
                    }:

                        violations.append(
                            f"{WEEKS_TITLES[week]}: "
                            f"{name} kapanıştan açılışa geçti"
                        )


        # ----------------------------------------------------
        # ONUR SM 1 KAPANIŞ
        # ----------------------------------------------------

        onur_closing = sum(
            1
            for day in range(7)
            if is_close(
                schedule[
                    "Onur Kaynak"
                ][base + day]
            )
        )


        if onur_closing != 1:

            violations.append(
                f"{WEEKS_TITLES[week]}: "
                f"Onur SM kapanış sayısı "
                f"{onur_closing}"
            )


    st.session_state[
        "last_schedule_violations"
    ] = violations


    # ========================================================
    # DATAFRAME
    # ========================================================

    weeks_dict = {}


    for week in range(4):

        start = week * 7
        end = start + 7

        df = pd.DataFrame({

            "Partner": [
                employee["name"]
                for employee in EMPLOYEES
            ],

            "TİP": [
                employee["tip"]
                for employee in EMPLOYEES
            ]
        })


        for day in range(
            start,
            end
        ):

            column_name = (
                f"{DAY_NAMES_TR[day % 7]} "
                f"({day + 1})"
            )


            df[column_name] = [

                schedule[
                    employee["name"]
                ][day]

                for employee in EMPLOYEES
            ]


        weeks_dict[
            WEEKS_TITLES[week]
        ] = df


    return weeks_dict


# ============================================================
# DOSYA KAYIT SİSTEMİ
# ============================================================

def load_all_store():

    if not os.path.exists(
        SAVE_FILE
    ):
        return {}


    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_month_store(
    month_key,
    weeks_dict
):

    store = load_all_store()


    store[month_key] = {

        week: df.to_dict(
            orient="records"
        )

        for week, df
        in weeks_dict.items()
    }


    try:

        directory = os.path.dirname(
            SAVE_FILE
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )


        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                store,
                file,
                ensure_ascii=False,
                indent=2
            )


    except Exception as error:

        st.error(
            f"Kayıt hatası: {error}"
        )


# ============================================================
# BAŞLIK
# ============================================================

st.title(
    "☕ Armada Starbucks Vardiya Yönetimi"
)

st.caption(
    "Operasyonel vardiya planlama ve aylık raporlama sistemi"
)


# ============================================================
# YIL / AY
# ============================================================

col_year, col_month, col_generate = st.columns(
    [1, 1.5, 2.5]
)


with col_year:

    sel_year = st.selectbox(
        "Yıl",
        [2026, 2027],
        index=0
    )


with col_month:

    current_month = datetime.now().month

    sel_month = st.selectbox(
        "Ay",
        range(1, 13),
        index=current_month - 1,
        format_func=lambda x:
            MONTH_NAMES_TR[x - 1]
    )


month_key = (
    f"{sel_year}_{sel_month:02d}"
)


# ============================================================
# SESSION STORE
# ============================================================

if "app_store" not in st.session_state:

    st.session_state.app_store = (
        load_all_store()
    )


if month_key not in st.session_state.app_store:

    generated = (
        generate_armada_master_schedule(
            seed=sel_year * 100 + sel_month
        )
    )


    st.session_state.app_store[
        month_key
    ] = {

        week: df.to_dict(
            orient="records"
        )

        for week, df
        in generated.items()
    }


    save_month_store(
        month_key,
        generated
    )


# ============================================================
# YENİ VARDİYA ÜRET
# ============================================================

with col_generate:

    if st.button(
        "🎲 Yeni Karışık / Dinamik Vardiya Üret",
        use_container_width=True,
        type="primary"
    ):

        new_seed = random.randint(
            1,
            999999
        )


        generated = (
            generate_armada_master_schedule(
                seed=new_seed
            )
        )


        save_month_store(
            month_key,
            generated
        )


        st.session_state.app_store[
            month_key
        ] = {

            week: df.to_dict(
                orient="records"
            )

            for week, df
            in generated.items()
        }


        st.rerun()


# ============================================================
# DATAFRAME'LERİ YÜKLE
# ============================================================

current_month_weeks = {

    week: pd.DataFrame(data)

    for week, data
    in st.session_state
    .app_store[month_key]
    .items()
}


weeks_keys = list(
    current_month_weeks.keys()
)


# ============================================================
# KURAL DURUMU
# ============================================================

violations = st.session_state.get(
    "last_schedule_violations",
    []
)


if violations:

    st.warning(
        f"⚠️ {len(violations)} adet "
        f"kural kontrolü uyarısı var."
    )


    with st.expander(
        "Kural kontrollerini göster"
    ):

        for violation in violations:

            st.write(
                f"• {violation}"
            )

else:

    st.success(
        "✅ Vardiya tanımlı kurallardan geçti."
    )


# ============================================================
# MANUEL DÜZENLEME
# ============================================================

st.subheader(
    f"🛠️ "
    f"{MONTH_NAMES_TR[sel_month - 1]} "
    f"{sel_year} - Manuel Düzenleme"
)


c1, c2, c3 = st.columns(3)


with c1:

    sel_week = st.selectbox(
        "Hafta Seç",
        weeks_keys,
        key="dyn_week"
    )


with c2:

    sel_emp = st.selectbox(
        "Partner Seç",
        [
            employee["name"]
            for employee in EMPLOYEES
        ],
        key="dyn_emp"
    )


current_df = current_month_weeks[
    sel_week
]


day_cols = [

    column

    for column
    in current_df.columns

    if column not in {
        "Partner",
        "TİP",
        "Haftalık Saat"
    }
]


with c3:

    sel_day = st.selectbox(
        "Gün Seç",
        day_cols,
        key="dyn_day"
    )


emp_idx = current_df[
    current_df["Partner"] == sel_emp
].index[0]


current_value = str(
    current_df.at[
        emp_idx,
        sel_day
    ]
)


partner_type = next(

    employee["tip"]

    for employee
    in EMPLOYEES

    if employee["name"] == sel_emp
)


st.write(
    f"**Şu Anki Durum:** "
    f"`{current_value}` "
    f"({partner_type})"
)


def save_manual_change(
    new_value
):

    current_month_weeks[
        sel_week
    ].at[
        emp_idx,
        sel_day
    ] = new_value


    save_month_store(
        month_key,
        current_month_weeks
    )


    st.rerun()


b1, b2, b3, b4, b5, b6 = st.columns(6)


with b1:

    if st.button(
        "🔴 OFF Yap",
        use_container_width=True
    ):

        save_manual_change(
            OFF
        )


with b2:

    if st.button(
        "☀️ Açılış",
        use_container_width=True
    ):

        save_manual_change(

            A_PT
            if partner_type == "PT"
            else A_FT

        )


with b3:

    if st.button(
        "☕ Ara (12:00)",
        use_container_width=True
    ):

        save_manual_change(
            ARA_12
        )


with b4:

    if st.button(
        "☕ Ara (10:00)",
        use_container_width=True
    ):

        save_manual_change(
            ARA_10
        )


with b5:

    if st.button(
        "🌙 Kapanış",
        use_container_width=True
    ):

        save_manual_change(

            K_PT
            if partner_type == "PT"
            else K_FT

        )


with b6:

    if st.button(
        "👔 Müd. Ara (09:00)",
        use_container_width=True
    ):

        save_manual_change(
            MID_MGR
        )


# ============================================================
# HAFTALIK ÇİZELGE
# ============================================================

st.subheader(
    f"📅 "
    f"{MONTH_NAMES_TR[sel_month - 1]} "
    f"{sel_year} - Haftalık Vardiya Çizelgeleri"
)


tabs = st.tabs(
    weeks_keys
)


for index, week in enumerate(
    weeks_keys
):

    with tabs[index]:

        df = current_month_weeks[
            week
        ].copy()


        day_columns = [

            column

            for column
            in df.columns

            if column not in {
                "Partner",
                "TİP",
                "Haftalık Saat"
            }
        ]


        weekly_hours = []


        for _, row in df.iterrows():

            total = sum(

                calculate_net_hours(
                    row[column]
                )

                for column
                in day_columns

            )

            weekly_hours.append(
                format_hour(total)
            )


        df["Haftalık Saat"] = (
            weekly_hours
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
    f"📊 "
    f"{MONTH_NAMES_TR[sel_month - 1]} "
    f"{sel_year} - Aylık Partner Raporu"
)


all_days_series = {

    employee["name"]: []

    for employee
    in EMPLOYEES
}


for week in weeks_keys:

    df = current_month_weeks[
        week
    ]


    day_columns = [

        column

        for column
        in df.columns

        if column not in {
            "Partner",
            "TİP",
            "Haftalık Saat"
        }
    ]


    for _, row in df.iterrows():

        name = row[
            "Partner"
        ]


        for column in day_columns:

            all_days_series[
                name
            ].append(

                (
                    column,
                    str(row[column])
                )

            )


report_rows = []


for employee in EMPLOYEES:

    name = employee[
        "name"
    ]

    tip = employee[
        "tip"
    ]


    total_hours = 0.0

    opening_count = 0

    ara_count = 0

    closing_count = 0

    off_count = 0

    izin_count = 0

    rapor_count = 0


    for _, shift in (
        all_days_series[name]
    ):

        total_hours += (
            calculate_net_hours(
                shift
            )
        )


        category = (
            categorize_shift(
                shift
            )
        )


        if category == "Açılış":

            opening_count += 1

        elif category == "Ara":

            ara_count += 1

        elif category == "Kapanış":

            closing_count += 1

        elif category == "OFF":

            off_count += 1

        elif category == "İzin":

            izin_count += 1

        elif category == "Rapor":

            rapor_count += 1


    quota = employee[
        "quota"
    ]


    if total_hours > quota:

        difference = (
            total_hours - quota
        )

        status = (
            f"🚨 +"
            f"{format_hour(difference)} "
            f"Kota Aşımı!"
        )


    elif total_hours < quota:

        difference = (
            quota - total_hours
        )

        status = (
            f"ℹ️ -"
            f"{format_hour(difference)} "
            f"Eksik"
        )


    else:

        status = "✅ Tam Kota"


    report_rows.append({

        "Partner": name,

        "TİP": tip,

        "Açılış": opening_count,

        "Ara": ara_count,

        "Kapanış": closing_count,

        "OFF": off_count,

        "Toplam Net Saat":
            format_hour(
                total_hours
            ),

        "Aylık Hedef":
            format_hour(
                quota
            ),

        "Durum": status
    })


report_df = pd.DataFrame(
    report_rows
)


st.dataframe(
    report_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# HTML / PDF RAPOR
# ============================================================

def get_report_html():

    html = f"""
<!DOCTYPE html>

<html lang="tr">

<head>

<meta charset="utf-8">

<title>
Armada Starbucks Vardiya Raporu
</title>

<style>

@page {{
    size: A4 landscape;
    margin: 8mm;
}}

body {{
    font-family: Arial, sans-serif;
    color: #0f172a;
    font-size: 8pt;
}}

h1 {{
    text-align: center;
    font-size: 15pt;
}}

h2 {{
    font-size: 10pt;
    margin-top: 14px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
}}

th,
td {{
    border: 1px solid #cbd5e1;
    padding: 4px;
    text-align: center;
}}

th {{
    background: #f1f5f9;
}}

.no-print {{
    margin-bottom: 12px;
}}

@media print {{

    .no-print {{
        display: none;
    }}

}}

</style>

</head>

<body>

<div class="no-print">

<button onclick="window.print()">
PDF Olarak Kaydet / Yazdır
</button>

</div>

<h1>
☕ Armada Starbucks -
{MONTH_NAMES_TR[sel_month - 1]}
{sel_year}
Vardiya Raporu
</h1>

<h2>
Aylık Partner Raporu
</h2>

<table>

<thead>

<tr>

<th>Partner</th>
<th>TİP</th>
<th>Açılış</th>
<th>Ara</th>
<th>Kapanış</th>
<th>OFF</th>
<th>Toplam Net Saat</th>
<th>Aylık Hedef</th>
<th>Durum</th>

</tr>

</thead>

<tbody>
"""


    for _, row in report_df.iterrows():

        html += f"""
<tr>

<td>{row['Partner']}</td>

<td>{row['TİP']}</td>

<td>{row['Açılış']}</td>

<td>{row['Ara']}</td>

<td>{row['Kapanış']}</td>

<td>{row['OFF']}</td>

<td>{row['Toplam Net Saat']}</td>

<td>{row['Aylık Hedef']}</td>

<td>{row['Durum']}</td>

</tr>
"""


    html += """
</tbody>

</table>
"""


    for week in weeks_keys:

        df = current_month_weeks[
            week
        ]


        columns = list(
            df.columns
        )


        html += f"""
<h2>
{week}
</h2>

<table>

<thead>

<tr>
"""


        for column in columns:

            html += (
                f"<th>{column}</th>"
            )


        html += """
</tr>

</thead>

<tbody>
"""


        for _, row in df.iterrows():

            html += "<tr>"


            for column in columns:

                html += (
                    f"<td>"
                    f"{row[column]}"
                    f"</td>"
                )


            html += "</tr>"


        html += """
</tbody>

</table>
"""


    html += """
</body>
</html>
"""


    return html


report_html = get_report_html()


encoded_report = base64.b64encode(
    report_html.encode(
        "utf-8"
    )
).decode(
    "utf-8"
)


st.markdown(
    f"""
<a
href="data:text/html;base64,{encoded_report}"
target="_blank"
style="
display:inline-block;
padding:10px 22px;
background:#006241;
color:white;
text-decoration:none;
border-radius:6px;
font-weight:bold;
"
>
📥 Resmi Raporu Aç / PDF Olarak Kaydet
</a>
""",
    unsafe_allow_html=True
)