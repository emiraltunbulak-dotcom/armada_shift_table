import random

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

WEEKEND_DAYS = {5, 6}
WEDNESDAY = 2
OPEN_SET = {A_MGR, A_FT, A_PT, MID_MGR}
CLOSE_SET = {K_MGR, K_FT, K_PT}
ARA_SET = {ARA_10, ARA_12, MID_MGR}


def segments_from_offdays(work_days_all, excluded):
    """work_days_all: sorted list 0..6. excluded: set of days (off/ara) that break chains.
    Returns ordered list of contiguous segments (lists of day indices)."""
    segs = []
    cur = []
    for d in range(7):
        if d in excluded:
            if cur:
                segs.append(cur)
                cur = []
            continue
        cur.append(d)
    if cur:
        segs.append(cur)
    return segs


def plan_person_week(schedule, person, s_d, off_day, ara_day, target_open=3, target_close=3):
    """Assign OPEN/CLOSE for all working days of `person` in week starting at s_d,
    guaranteeing no CLOSE->OPEN transition (checking the *real* previous day,
    including across the week boundary)."""
    excluded = set()
    if off_day is not None:
        excluded.add(off_day)
    if ara_day is not None:
        excluded.add(ara_day)

    segs = segments_from_offdays(list(range(7)), excluded)
    remaining_open, remaining_close = target_open, target_close

    for seg_idx, seg in enumerate(segs):
        first_day = seg[0]
        abs_first = s_d + first_day
        must_all_close = False
        if seg_idx == 0:
            prev_real = schedule[person][abs_first - 1] if abs_first > 0 else None
            if prev_real in CLOSE_SET:
                must_all_close = True
        # else: this segment starts right after an OFF/ARA day (or is the very
        # first day of week0 with no history) -> free to open

        if must_all_close:
            n_open = 0
        else:
            n_open = min(remaining_open, len(seg))
        n_close = len(seg) - n_open

        for i, d in enumerate(seg):
            abs_d = s_d + d
            if i < n_open:
                schedule[person][abs_d] = A_FT
                remaining_open = max(0, remaining_open - 1)
            else:
                schedule[person][abs_d] = K_FT
                remaining_close = max(0, remaining_close - 1)

    if off_day is not None:
        schedule[person][s_d + off_day] = OFF
    # ara_day is written by the caller (needs cross-check against ARA_SET first)


def generate_armada_master_schedule(seed=None):
    if seed is None:
        seed = 42
    rng = random.Random(seed)

    mgr_names = ["Onur Kaynak", "Banu Sezer", "Göktuğ Gökdemir"]
    ft_baristas = [
        "Cansu Elibüyük", "Buse Kayabalı", "Vahti Ünal", "Ceyda Işık",
        "Yusuf Efe Aydoğmuş", "Elif Karaca", "Cansu Yüksel", "Ebrar Sena Akkaya",
        "Ahmet Emre Demren", "Ayça Yiğit"
    ]
    other_ft = ["Ceyda Işık", "Yusuf Efe Aydoğmuş", "Elif Karaca", "Cansu Yüksel",
                "Ebrar Sena Akkaya", "Ahmet Emre Demren", "Ayça Yiğit"]
    flex_ft = ["Buse Kayabalı"] + other_ft
    pt_baristas = ["Emir Altunbulak", "Hayrunnisa Erdoğan"]
    all_names = mgr_names + ft_baristas + pt_baristas

    schedule = {name: ["OFF"] * 28 for name in all_names}
    hard_open = set()  # (person, abs_d) - bu günler asla kapanışa çevrilemez

    # ------------------------------------------------------------------
    # Sabit haftalık müdür şablonu (her 4 hafta için aynı):
    #  - Onur (SM): Pzt OFF, Sal-Cts açılış, Pazar KAPANIŞ (rule12: SM haftada
    #    1 kapanış). Kapanıştan açılışa hiç geçiş yok.
    #  - Banu (SSV): Salı OFF; Çar aracı@9(rule8: Onur açık+Göktuğ kapanış->
    #    diğer SSV aracı), Per/Cum/Cts açılış, Paz/Pzt kapanış.
    #  - Göktuğ (SSV): Perşembe OFF; Cum-Çar açılış, Çarşamba kapanış (rule8
    #    tetikleyicisi).
    # ------------------------------------------------------------------
    mgr_pattern = [
        {"Onur Kaynak": OFF,   "Banu Sezer": K_MGR,   "Göktuğ Gökdemir": A_MGR},     # Pzt
        {"Onur Kaynak": A_MGR, "Banu Sezer": OFF,     "Göktuğ Gökdemir": A_MGR},     # Sal
        {"Onur Kaynak": A_MGR, "Banu Sezer": MID_MGR, "Göktuğ Gökdemir": K_MGR},     # Çar (rule8)
        {"Onur Kaynak": A_MGR, "Banu Sezer": A_MGR,   "Göktuğ Gökdemir": OFF},       # Per
        {"Onur Kaynak": A_MGR, "Banu Sezer": A_MGR,   "Göktuğ Gökdemir": A_MGR},     # Cum
        {"Onur Kaynak": A_MGR, "Banu Sezer": A_MGR,   "Göktuğ Gökdemir": A_MGR},     # Cts
        {"Onur Kaynak": K_MGR, "Banu Sezer": K_MGR,   "Göktuğ Gökdemir": A_MGR},     # Paz
    ]

    for w_idx in range(4):
        s_d = w_idx * 7
        for day in range(7):
            abs_d = s_d + day
            for m in mgr_names:
                schedule[m][abs_d] = mgr_pattern[day][m]

        # PT (değişmedi)
        emir_work_days = [0, 2, 4, 6]
        hayru_work_days = [1, 2, 3, 5]
        for day in range(7):
            abs_d = s_d + day
            schedule["Emir Altunbulak"][abs_d] = (A_PT if day in [0, 4, 6] else K_PT) if day in emir_work_days else OFF
            # Sal, Çar = açılış (blok) / Per, Cts = kapanış (blok) -> Çar(kapanış)
            # sonrası Per(açılış) gibi bir kapanış->açılış geçişi oluşmaz.
            schedule["Hayrunnisa Erdoğan"][abs_d] = (A_PT if day in [1, 2] else K_PT) if day in hayru_work_days else OFF

        # Elibüyük & Vahti (sabit kurallar)
        weekdays = [0, 1, 2, 3, 4]
        elib_off = rng.choice(weekdays)
        vahti_off = rng.choice([d for d in weekdays if d != elib_off])

        for day in range(7):
            abs_d = s_d + day
            is_weekend = day in WEEKEND_DAYS
            if day == elib_off:
                schedule["Cansu Elibüyük"][abs_d] = OFF
            elif is_weekend:
                schedule["Cansu Elibüyük"][abs_d] = K_FT
            else:
                schedule["Cansu Elibüyük"][abs_d] = A_FT

            if day == vahti_off:
                schedule["Vahti Ünal"][abs_d] = OFF
            elif is_weekend:
                schedule["Vahti Ünal"][abs_d] = A_FT
            else:
                schedule["Vahti Ünal"][abs_d] = K_FT

        # Diğer FT + Buse (esnek havuz)
        # NOT: PT partnerler (Emir, Hayrunnisa) yapısal olarak haftada 3-4 gün
        # çalışmıyor; bu onlar için "izin" değil, part-time programının doğal
        # sonucu. "Günde en fazla 2 kişi OFF" kuralı FT + SSV + SM için
        # (13 kişi) uygulanır, PT dahil edilmez.
        off_count = [0] * 7
        for day in range(7):
            abs_d = s_d + day
            off_count[day] = sum(1 for n in mgr_names + ["Cansu Elibüyük", "Vahti Ünal"]
                                  if schedule[n][abs_d] == OFF)

        forced_work = {"Buse Kayabalı": {elib_off}}

        pool_order = flex_ft[:]
        rng.shuffle(pool_order)
        person_off = {}
        for person in pool_order:
            forbidden = forced_work.get(person, set())
            candidates = sorted(
                [d for d in range(7) if d not in forbidden],
                key=lambda d: (off_count[d] >= 2, d == WEDNESDAY, off_count[d], rng.random())
            )
            chosen = next((d for d in candidates if off_count[d] < 2), candidates[0])
            person_off[person] = chosen
            off_count[chosen] += 1

        ara_volunteer = flex_ft[w_idx % len(flex_ft)]
        ara_day_for = {}
        for person in flex_ft:
            if person != ara_volunteer:
                continue
            forced_d = elib_off if person == "Buse Kayabalı" else None
            work_days = [d for d in range(7)
                         if d != person_off[person] and d != 6 and d != forced_d]  # Pazar & zorunlu gün hariç
            rng.shuffle(work_days)
            chosen_ara = None
            for d in work_days:
                abs_d = s_d + d
                prev = schedule[person][abs_d - 1] if abs_d > 0 else None
                if prev not in ARA_SET:
                    chosen_ara = d
                    break
            if chosen_ara is not None:
                ara_day_for[person] = chosen_ara

        # Buse: Elibüyük'ün izin günü ZORUNLU açılış -> önce sabitle
        if "Buse Kayabalı" in flex_ft:
            schedule["Buse Kayabalı"][s_d + elib_off] = A_FT
            hard_open.add(("Buse Kayabalı", s_d + elib_off))

        for person in flex_ft:
            off_day = person_off[person]
            ara_day = ara_day_for.get(person)
            t_open, t_close = 3, 3
            forced_day = elib_off if person == "Buse Kayabalı" else None
            if forced_day is not None:
                t_open -= 1  # o gün zaten açılış olarak sayıldı
            if ara_day is not None:
                # aracı bir çalışma gününü kapladığı için hedeflerden birini düşür
                if t_open >= t_close:
                    t_open -= 1
                else:
                    t_close -= 1

            # forced_day'i segment planlamasından hariç tut (zaten yazıldı)
            plan_excluded_extra = {forced_day} if forced_day is not None else set()

            # Küçük bir sar: plan_person_week fonksiyonunu forced_day'i de
            # "off" gibi hariç tutacak ama OFF yazmayacak şekilde çağırmak için
            # ufak bir yardımcı kopya kullanıyoruz.
            _plan_person_week_with_forced(schedule, person, s_d, off_day, ara_day,
                                           forced_day, t_open, t_close)

            if ara_day is not None:
                idx = flex_ft.index(person)
                schedule[person][s_d + ara_day] = ARA_12 if idx % 2 == 0 else ARA_10

            if forced_day is not None:
                # Zorunlu açılış günü (Buse -> Elibüyük izinli) bir önceki
                # gerçek günü kapanış->açılış ihlaline sokabilir; geriye
                # doğru kısa bir düzeltme uygula.
                p = s_d + forced_day - 1
                steps = 0
                while p >= 0 and schedule[person][p] in CLOSE_SET and steps < 3:
                    schedule[person][p] = A_FT
                    p -= 1
                    steps += 1

        # Ceyda & Efe aynı gün açılış olmasın (son kontrol / düzeltme)
        for day in range(7):
            abs_d = s_d + day
            if schedule["Ceyda Işık"][abs_d] == A_FT and schedule["Yusuf Efe Aydoğmuş"][abs_d] == A_FT:
                # Kapanışa çevirmek güvenli mi? Ertesi gün zaten açılışsa
                # (kapanış->açılış oluşur) o kişiyi seçme, diğerini dene.
                def safe_to_close(person):
                    nxt = schedule[person][abs_d + 1] if abs_d + 1 < 28 else None
                    return nxt not in OPEN_SET
                if safe_to_close("Yusuf Efe Aydoğmuş"):
                    schedule["Yusuf Efe Aydoğmuş"][abs_d] = K_FT
                elif safe_to_close("Ceyda Işık"):
                    schedule["Ceyda Işık"][abs_d] = K_FT
                else:
                    # ikisi de ertesi gün açılış - en az riskli seçenek
                    schedule["Yusuf Efe Aydoğmuş"][abs_d] = K_FT

    # ------------------------------------------------------------------
    # Son güvenlik geçişi: 28 günlük zaman çizelgesinde kalan olası
    # kapanış->açılış ihlallerini (ör. haftalar arası sınırda oluşanlar)
    # açılış gününü kapanışa çevirerek düzeltir. Elibüyük & Vahti bu
    # kontrolün dışındadır (kendi sabit kurallarının doğal sonucu).
    # ------------------------------------------------------------------
    exempt = {"Cansu Elibüyük", "Vahti Ünal"}
    for n in all_names:
        if n in exempt:
            continue
        for d in range(1, 28):
            if (n, d) in hard_open:
                continue
            if schedule[n][d - 1] in CLOSE_SET and schedule[n][d] in OPEN_SET:
                if n in mgr_names:
                    schedule[n][d] = K_MGR
                elif n in pt_baristas:
                    schedule[n][d] = K_PT
                else:
                    schedule[n][d] = K_FT

    return schedule


def _plan_person_week_with_forced(schedule, person, s_d, off_day, ara_day, forced_day, t_open, t_close):
    excluded = set()
    if off_day is not None:
        excluded.add(off_day)
    if ara_day is not None:
        excluded.add(ara_day)
    if forced_day is not None:
        excluded.add(forced_day)

    segs = segments_from_offdays(list(range(7)), excluded)
    remaining_open, remaining_close = t_open, t_close

    for seg_idx, seg in enumerate(segs):
        first_day = seg[0]
        abs_first = s_d + first_day
        must_all_close = False
        if seg_idx == 0:
            prev_real = schedule[person][abs_first - 1] if abs_first > 0 else None
            if prev_real in CLOSE_SET:
                must_all_close = True
        n_open = 0 if must_all_close else min(remaining_open, len(seg))
        n_close = len(seg) - n_open
        for i, d in enumerate(seg):
            abs_d = s_d + d
            if i < n_open:
                schedule[person][abs_d] = A_FT
                remaining_open = max(0, remaining_open - 1)
            else:
                schedule[person][abs_d] = K_FT
                remaining_close = max(0, remaining_close - 1)

    if off_day is not None:
        schedule[person][s_d + off_day] = OFF