"""Generate questions.json fixture for EcoGame quiz."""

import json

questions = []
answers = []

# Answer PK counter
apk = 1001

CREATED = "2025-01-01T00:00:00Z"


def add_mcq(qpk, text, category, diff, expl, source, options, correct_idx, article=None):
    global apk
    questions.append(
        {
            "model": "game.question",
            "pk": qpk,
            "fields": {
                "text_uz": text,
                "category": category,
                "difficulty": diff,
                "question_type": "MCQ",
                "explanation_uz": expl,
                "image": "",
                "time_limit": 30,
                "source": source,
                "related_article": article,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
            },
        }
    )
    for i, opt in enumerate(options):
        answers.append(
            {
                "model": "game.answer",
                "pk": apk,
                "fields": {
                    "question": qpk,
                    "text_uz": opt,
                    "is_correct": (i == correct_idx),
                    "order": i + 1,
                },
            }
        )
        apk += 1


def add_tf(qpk, text, category, diff, expl, source, correct_true, article=None):
    global apk
    questions.append(
        {
            "model": "game.question",
            "pk": qpk,
            "fields": {
                "text_uz": text,
                "category": category,
                "difficulty": diff,
                "question_type": "TRUE_FALSE",
                "explanation_uz": expl,
                "image": "",
                "time_limit": 20,
                "source": source,
                "related_article": article,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
            },
        }
    )
    answers.append(
        {
            "model": "game.answer",
            "pk": apk,
            "fields": {"question": qpk, "text_uz": "Ha", "is_correct": correct_true, "order": 1},
        }
    )
    apk += 1
    answers.append(
        {
            "model": "game.answer",
            "pk": apk,
            "fields": {
                "question": qpk,
                "text_uz": "Yo'q",
                "is_correct": not correct_true,
                "order": 2,
            },
        }
    )
    apk += 1


def add_scenario(qpk, text, category, diff, expl, source, options, correct_idx, article=None):
    global apk
    questions.append(
        {
            "model": "game.question",
            "pk": qpk,
            "fields": {
                "text_uz": text,
                "category": category,
                "difficulty": diff,
                "question_type": "SCENARIO",
                "explanation_uz": expl,
                "image": "",
                "time_limit": 45,
                "source": source,
                "related_article": article,
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
            },
        }
    )
    for i, opt in enumerate(options):
        answers.append(
            {
                "model": "game.answer",
                "pk": apk,
                "fields": {
                    "question": qpk,
                    "text_uz": opt,
                    "is_correct": (i == correct_idx),
                    "order": i + 1,
                },
            }
        )
        apk += 1


# ─────────────────────────────────────────────
# ENERGY — pk 1-30
# ─────────────────────────────────────────────
add_mcq(
    1,
    "O'zbekistonda bir yilda o'rtacha necha kun quyoshli bo'ladi?",
    "ENERGY",
    1,
    "O'zbekiston yiliga 300 kundan ortiq quyoshli kun bilan Markaziy Osiyoning eng quyoshli davlatlaridan biri. Bu quyosh energiyasini keng qo'llash uchun ulkan imkoniyat beradi.",
    "O'zbekiston Quyosh energiyasi instituti, 2022",
    ["150 kun", "200 kun", "250 kun", "300 kun"],
    3,
    article=4,
)

add_mcq(
    2,
    "Quyosh paneli qanday energiya hosil qiladi?",
    "ENERGY",
    1,
    "Fotovoltaik quyosh panellari quyosh nurini bevosita elektr energiyasiga aylantiradi. Bu jarayon fotovoltaik effekt orqali amalga oshiriladi.",
    "Energetika vazirligi, O'zbekiston, 2023",
    ["Issiqlik energiyasi", "Elektr energiyasi", "Kimyoviy energiya", "Mexanik energiya"],
    1,
)

add_mcq(
    3,
    "1 kVt quvvatli quyosh paneli yiliga qancha CO2 emissiyasini kamaytiradi?",
    "ENERGY",
    1,
    "Quyosh paneli an'anaviy elektr manbalari (ko'mir, gaz) o'rnini bosib, yiliga taxminan 1.5 tonna CO2 chiqarilishini oldini oladi.",
    "IRENA (Xalqaro qayta tiklanuvchi energiya agentligi), 2023",
    ["0.5 tonna", "1 tonna", "1.5 tonna", "3 tonna"],
    2,
    article=4,
)

add_mcq(
    4,
    "LED chiroq oddiy lambochkaga nisbatan necha foiz kam energiya sarflaydi?",
    "ENERGY",
    1,
    "LED texnologiyasi elektr energiyasining 75-80% ini yorug'likka aylantiradi, oddiy lambochkalar esa faqat 10% ini. Shuning uchun LED da 75-80% energiya tejaladi.",
    "Energiya samaradorligi markazi, Toshkent, 2023",
    ["20%", "50%", "75%", "90%"],
    2,
)

add_mcq(
    5,
    "O'zbekistonda elektr energiyasining asosiy manbai qaysi?",
    "ENERGY",
    2,
    "O'zbekistonda elektr energiyasining 80% dan ortig'i tabiiy gaz va ko'mirda ishlaydigan issiqlik elektr stansiyalarida ishlab chiqariladi.",
    "O'zbekiston Energetika vazirligi, 2023",
    ["Quyosh energiyasi", "Shamol energiyasi", "Issiqlik elektr stansiyalari", "Gidroelektr"],
    2,
)

add_mcq(
    6,
    "Uy-joy isitishda eng tejamkor usul qaysi?",
    "ENERGY",
    1,
    "Issiqlik nasosi (heat pump) elektr energiyasining har 1 kVh iga 3-5 kVh issiqlik beradi. Bu boshqa isitish usullariga nisbatan 3-5 marta samaraliroq.",
    "Qayta tiklanuvchi energiya assotsiatsiyasi, 2022",
    ["Elektr issitgich", "Gaz qozon", "Issiqlik nasosi", "Ko'mir"],
    2,
)

add_mcq(
    7,
    "O'zbekiston 2030 yilga qadar qayta tiklanuvchi energiya ulushini nechanchi foizga yetkazmoqchi?",
    "ENERGY",
    2,
    "O'zbekiston hukumati 2030 yilga qadar qayta tiklanuvchi energiya manbalari ulushini 25% ga yetkazishni rejalashtirib, 5 GVt quyosh va 3 GVt shamol energiyasini quradi.",
    "O'zbekiston Prezidentining 2022-yil farmonlari, Energetika vazirligi",
    ["10%", "15%", "20%", "25%"],
    3,
    article=4,
)

add_mcq(
    8,
    "Kerakmas joyda chiroqni yoqib qoldirish nima sababli ekologik muammo?",
    "ENERGY",
    1,
    "Ortiqcha elektr ishlatish elektr stansiyalarida ko'proq yoqilg'i yoqilishini talab qiladi, bu esa CO2 chiqarishni oshiradi va iqlim o'zgarishiga hissa qo'shadi.",
    "Ekologiya vazirligi, O'zbekiston, 2023",
    [
        "Lampochka tezroq buziladi",
        "Elektr stansiyalar ko'proq CO2 chiqaradi",
        "Suv sarfi ko'payadi",
        "Hech qanday ta'siri yo'q",
    ],
    1,
)

add_mcq(
    9,
    "Bio-gaz qanday manba asosida olinadi?",
    "ENERGY",
    2,
    "Bio-gaz organik moddalar (chorva mollarining go'ngi, o'simlik qoldiqlari, oziq-ovqat chiqindilari) anaerob parchalanishi natijasida hosil bo'ladigan metan aralashmasidir.",
    "FAO (BMT Oziq-ovqat va qishloq xo'jaligi tashkiloti), 2023",
    [
        "Neft qazib olish jarayonida",
        "Organik chiqindilarni anaerob parchalashda",
        "Kimyoviy sintez orqali",
        "Suv bug'lantirish natijasida",
    ],
    1,
)

add_mcq(
    10,
    "Shamol turbinasi nima hosil qiladi?",
    "ENERGY",
    2,
    "Shamol turbinalari shamol kinetik energiyasini mexanik energiyaga, so'ngra generator orqali elektr energiyasiga aylantiradi. CO2 chiqarmaydi.",
    "IRENA, Shamol energiyasi hisoboti, 2023",
    ["Issiqlik energiyasi", "Elektr energiyasi", "Kimyoviy energiya", "Bosimli suv"],
    1,
)

add_mcq(
    11,
    "Kichik GES (gidroelektrostansiya) qancha quvvatdan kichik stansiyaga aytiladi?",
    "ENERGY",
    3,
    "Xalqaro amaliyotda 10 MVt (megavatt) dan kam quvvatli stansiyalar kichik GES deb tasniflanadi. Ular daryolar va ariqlar yaqinida quriladi.",
    "Xalqaro energetika agentligi (IEA), 2023",
    ["1 MVt", "5 MVt", "10 MVt", "50 MVt"],
    2,
)

add_mcq(
    12,
    "Televizorni 'standby' rejimida qoldirish nima sababli noto'g'ri?",
    "ENERGY",
    1,
    "Standby rejimidagi elektronika kuniga 0.5-10 Vt sarflaydi. Uy bo'yicha bu yiliga 50-100 kVh gacha ko'tariladi va keraksiz elektr sarfiga olib keladi.",
    "Energiya samaradorligi bo'yicha xalqaro hamkorlik (CECP), 2022",
    ["Ekran buziladi", "Ovoz chiqaradi", "Elektr sarflashda davom etadi", "Internet aloqani uzadi"],
    2,
)

add_mcq(
    13,
    "Energiya samaradorligi 'A' sinfi nima anglatadi?",
    "ENERGY",
    2,
    "Evropa ittifoqining energiya belgilash tizimida 'A' sinfi (A+, A++) eng kam energiya sarflaydigan jihoz ekanini bildiradi. Bu xarid chog'ida muhim mezon.",
    "EU Energiya belgilash direktivi, 2021",
    [
        "Eng ko'p energiya sarflaydi",
        "Eng kam energiya sarflaydi",
        "O'rtacha energiya sarflaydi",
        "Xavfli jihozlar",
    ],
    1,
)

add_mcq(
    14,
    "Issiqlik elektr stansiyalari asosiy qanday issiqxona gazi chiqaradi?",
    "ENERGY",
    2,
    "Tabiiy gaz va ko'mir yoqilganda CO2 (karbonat angidrid) asosiy issiqxona gazi sifatida chiqariladi. Bu global isish va iqlim o'zgarishining bosh sababi.",
    "IPCC (Iqlim o'zgarishi bo'yicha hukumatlararo panel), 2023",
    ["Kislorod", "CO2 (karbonat angidrid)", "Azot", "Vodorod"],
    1,
    article=2,
)

add_mcq(
    15,
    "1 MWh (megavatt-soat) necha kWh (kilovatt-soat) ga teng?",
    "ENERGY",
    3,
    "Energiya o'lchov tizimida: 1 MVh = 1000 kVh. Oddiy uy oyiga 150-300 kVh sarflaydi, ya'ni 1 MVh taxminan bir uy uchun 3-6 oylik elektr.",
    "SI o'lchov tizimi, xalqaro standart",
    ["100 kVh", "500 kVh", "1000 kVh", "10000 kVh"],
    2,
)

add_mcq(
    16,
    "Quyosh isitish kollektori qanday maqsadda ishlatiladi?",
    "ENERGY",
    1,
    "Quyosh issiqlik kollektor (flat-plate yoki vakuum naychali) quyosh nurini issiqlikka aylantiradi va suv isitish yoki uy isitish uchun ishlatiladi. Elektr hosil qilmaydi.",
    "O'zbekiston Quyosh energiyasi instituti, 2022",
    ["Elektr hosil qilish", "Issiq suv va uy isitish", "Havo sovitish", "Shamol hosil qilish"],
    1,
)

add_mcq(
    17,
    "Fotovoltaik (FV) panellar qanday energiyani elektr energiyasiga aylantiradi?",
    "ENERGY",
    2,
    "Fotovoltaik effekt yarim o'tkazgich materiallar (kremniy) quyosh fotonlarini elektr energiyasiga aylantirishida asoslanadi. Bu jarayonni Albert Eynshteyn 1905-yilda tushuntirgan.",
    "NASA Yer kuzatish markazi, quyosh energiyasi bo'limi",
    ["Shamol energiyasini", "Issiqlik energiyasini", "Quyosh (yorug'lik) nurini", "Suv oqimini"],
    2,
)

add_mcq(
    18,
    "O'zbekistondagi eng katta suv elektr stansiyasi qaysi?",
    "ENERGY",
    3,
    "Charvak GES (1971) Chirchiq daryosida joylashgan bo'lib, 621.5 MVt quvvatga ega. U O'zbekistonning eng katta GES i hisoblanadi va katta Toshkent hududini ta'minlaydi.",
    "O'zenergo, rasmiy ma'lumotlar, 2023",
    ["Charvak GES", "Qayroqum GES", "Tuyamo'yin GES", "Andijan GES"],
    0,
)

add_mcq(
    19,
    "Termostat o'rnatish uy isitishiga qanday ta'sir qiladi?",
    "ENERGY",
    1,
    "Aqlli termostat haroratni avtomatik boshqarib, uy bo'sh paytda isitishni kamaytiradi. Bu isitish xarajatini 15-25% ga kamaytirishi mumkin.",
    "Energiya samaradorligi bo'yicha Yevropa agentligi (EEA), 2023",
    ["Havo tozalanadi", "Isitish xarajati kamayadi", "Suv tejaladi", "Chiqindi kamayadi"],
    1,
)

add_mcq(
    20,
    "Bio-gaz qurilmasi qanday sharoitda ishlaydi?",
    "ENERGY",
    2,
    "Bio-gaz qurilmasi (bioreaktor) organik moddalarni kislorodsiz (anaerob) muhitda parchalaydi. Kislorod bo'lsa, metan o'rniga CO2 hosil bo'ladi va jarayon samarasiz.",
    "FAO, Bioenergetika qo'llanmasi, 2022",
    [
        "Kislorod bilan boyitilgan muhitda",
        "Kislorodsiz, yopiq muhitda",
        "Yuqori haroratda",
        "UV nur ta'sirida",
    ],
    1,
)

add_mcq(
    21,
    "O'zbekistondagi Zarafshon shamol elektr stansiyasining quvvati necha MVt?",
    "ENERGY",
    3,
    "ACWA Power va Masdar kompaniyalari qurgan Zarafshon shamol elektr stansiyasi 1500 MVt (1.5 GVt) quvvatga ega bo'lib, Markaziy Osiyoning eng yirik shamol loyihasi.",
    "ACWA Power, Zarafshon loyihasi rasmiy ma'lumotlari, 2023",
    ["100 MVt", "500 MVt", "1500 MVt", "3000 MVt"],
    2,
    article=4,
)

# TRUE_FALSE — ENERGY
add_tf(
    22,
    "LED chiroqlar oddiy lambochkalarga nisbatan ko'proq elektr sarflaydi.",
    "ENERGY",
    1,
    "Aksincha, LED chiroqlar 75-80% kam energiya sarflaydi va 10-25 marta uzoqroq ishlaydi.",
    "Energiya samaradorligi markazi, 2023",
    False,
)

add_tf(
    23,
    "Quyosh panellari bulutli havoda ham elektr hosil qilishi mumkin.",
    "ENERGY",
    1,
    "Ha, bulutli havoda ham diffuz quyosh nuri panel orqali o'tib elektr hosil qiladi, faqat hosildorlik 10-25% ga tushadi.",
    "Fraunhofer Institut, Quyosh energiyasi bo'limi, 2023",
    True,
)

add_tf(
    24,
    "Shamol energiyasi ishlab chiqarish jarayonida CO2 chiqarmaydi.",
    "ENERGY",
    2,
    "Ha, shamol turbinalari ishlaganda CO2 chiqarmaydi. Faqat qurilish jarayonida material ishlab chiqarishda ozgina CO2 chiqadi.",
    "IRENA, Hayotiy tsikl tahlili, 2023",
    True,
)

add_tf(
    25,
    "Bio-gaz an'anaviy tabiiy gazga nisbatan iqlim uchun zararli.",
    "ENERGY",
    2,
    "Yo'q, bio-gaz organik moddalardan hosil bo'lib, CO2 aylanma (carbon neutral) hisoblanadi. Tabiiy gaz esa yangi CO2 manbaidan olinadi.",
    "BMT Iqlim o'zgarishi bo'yicha ramka konventsiyasi (UNFCCC), 2023",
    False,
)

add_tf(
    26,
    "Yadro energiyasi qayta tiklanuvchi energiya manbai hisoblanadi.",
    "ENERGY",
    3,
    "Yo'q, yadro energiyasi uran xom ashyosi chekli bo'lganligi sababli qayta tiklanuvchi emas, balki uglerodli bo'lmagan (low-carbon) manba sifatida tasniflanadi.",
    "IRENA, Energiya tasnifi, 2023",
    False,
)

add_tf(
    27,
    "Energiya tejash yangi elektr stansiyasi qurish kabi muhim muammo yechimi.",
    "ENERGY",
    2,
    "Ha, IEA ma'lumotlariga ko'ra, energiya samaradorligi eng arzon va tez ta'sir qiladigan 'yashil' manba — yangi quvvat qurish kerak bo'lmaydi.",
    "IEA, Energiya samaradorligi hisoboti, 2023",
    True,
)

# SCENARIO — ENERGY
add_scenario(
    28,
    "Uyingizda 100W oddiy lambochka o'rniga 10W LED o'rnatdingiz. Bu chiroq kuniga 5 soat yonadi. Bir yilda qancha kVh elektr tejaladi?",
    "ENERGY",
    2,
    "Tejalgan quvvat: 100-10=90W. 90W × 5soat/kun × 365kun = 164,250 Wh ≈ 164 kVh/yil. Bu taxminan uy uchun bir oylik elektr.",
    "Energiya samaradorligi hisob-kitobi",
    ["50 kVh", "100 kVh", "164 kVh", "250 kVh"],
    2,
)

add_scenario(
    29,
    "Uyingizga 2 kVt quvvatli quyosh paneli o'rnatdingiz. Kuniga o'rtacha 5 soat ishlaydi. Uy oyiga 150 kVh iste'mol qilsa, panel iste'molning necha foizini qoplaydi?",
    "ENERGY",
    3,
    "Panel oyiga: 2kVt × 5soat × 30kun = 300 kVh hosil qiladi. 300/150 × 100% = 200%. Panel uyni to'liq qoplaydigan va ortiqcha energiya ham hosil qiladigan darajada.",
    "Quyosh energiyasi hisob-kitobi standartlari",
    ["50%", "100%", "150%", "200%"],
    3,
)

add_scenario(
    30,
    "Mahallada 50 ta uy bor. Har bir uy LED chiroqlarga o'tgach, oyiga 25 kVh tejadi. Bir yilda mahalla necha tonna CO2 kamaytiradi? (1 kVh ≈ 0.5 kg CO2)",
    "ENERGY",
    2,
    "Yillik tejalgan elektr: 50uy × 25kVh × 12oy = 15,000 kVh. CO2: 15,000 × 0.5kg = 7,500 kg = 7.5 tonna CO2. Bu 340 ta daraxt ekishga teng.",
    "O'zbekiston Ekologiya va atrof-muhit vazirligi, 2023",
    ["3 tonna", "5 tonna", "7.5 tonna", "15 tonna"],
    2,
)

# ─────────────────────────────────────────────
# WATER — pk 31-60
# ─────────────────────────────────────────────
add_mcq(
    31,
    "Orol dengizi qaysi asrning 60-yillarida 68,000 km² maydonni egallagan?",
    "WATER",
    1,
    "Orol dengizi 20-asrning o'rtalarida dunyoning to'rtinchi yirik ko'li edi. 1960-yillarda 68,000 km² ni egallagan, lekin sug'orish uchun suv olinishi tufayli quriy boshlagan.",
    "UNESCO Orol dengizi bo'yicha hisobot, 2022",
    ["18-asr", "19-asr", "20-asr", "21-asr"],
    2,
    article=1,
)

add_mcq(
    32,
    "O'zbekistondagi eng uzun daryo qaysi?",
    "WATER",
    1,
    "Amudaryo Markaziy Osiyodagi eng uzun daryo bo'lib, umumiy uzunligi 2,540 km. U Pamir va Hindukush tog'laridan boshlanib, Orol dengiziga tomon oqadi.",
    "O'zbekiston geografiya ma'lumotlari, 2023",
    ["Sirdaryo", "Amudaryo", "Zarafshon", "Chirchiq"],
    1,
)

add_mcq(
    33,
    "Orol dengizining hozirgi hajmi asl hajmining necha foizini tashkil etadi?",
    "WATER",
    1,
    "Orol dengizi 1960-yillardan buyon 90% dan ortiq qurib ketgan. Bugungi kunda atigi 10% i qolgan — bu iqlim bilan bog'liq eng katta inqirozlardan biri.",
    "ASBP (Orol dengizini qutqarish xalqaro jamg'armasi), 2023",
    ["50%", "30%", "10%", "5%"],
    2,
    article=1,
)

add_mcq(
    34,
    "Orol dengizining qurishining asosiy sababi nima?",
    "WATER",
    2,
    "1960-70-yillarda sovet davrida paxta yetishtirishni ko'paytirish maqsadida Amudaryo va Sirdaryodan ko'p miqdorda suv olingan, natijada dengizga suv yetib bormay qolgan.",
    "BMT Atrof-muhit dasturi (UNEP), Orol dengizi fojiasi, 2022",
    ["Iqlim isishi", "Paxta dehqonchiligiga ko'p suv sarflash", "Zilzila", "Sanoat ifloslanishi"],
    1,
)

add_mcq(
    35,
    "Ichimlik suvini tayyorlashning to'g'ri usuli qaysi?",
    "WATER",
    1,
    "Ichimlik suvi tozalash, koagulyatsiya, filtratsiya va xlor bilan dezinfeksiya bosqichlaridan o'tkaziladi. Bu bakteriya va viruslarni yo'q qiladi.",
    "JSSV (O'zbekiston ichimlik suvi ta'minoti) me'yorlari, 2023",
    [
        "Daryo suvini to'g'ridan to'g'ri ichish",
        "Tozalash va dezinfeksiya qilish",
        "Qor suvini eritish",
        "Dengiz suvini iste'mol qilish",
    ],
    1,
)

add_mcq(
    36,
    "Suv 0°C da qotsa, uning hajmi qanday o'zgaradi?",
    "WATER",
    2,
    "Suv muzga aylanganda hajmi taxminan 9% ga kengayadi. Bu suv molekulalari orasidagi vodorod bog'larining o'ziga xos tuzilishi tufayli sodir bo'ladi.",
    "Kimyo va fizika asoslari, O'zbekiston ta'lim standarti",
    [
        "Hajm o'zgarmaydi",
        "Hajm 9% ga kengayadi",
        "Hajm 9% ga qisqaradi",
        "Hajm ikki barobarga kengayadi",
    ],
    1,
)

add_mcq(
    37,
    "Tish tozalayotganda jo'mrakni yopmaslik kuniga qancha suv behuda ketishiga olib keladi?",
    "WATER",
    1,
    "Ochiq jo'mrakdan minutiga 6-8 litr suv oqadi. Tish tozalash 2 minutni olsada, jo'mrak yopilmasa 12-16 litr suv behuda ketadi.",
    "Jahon sog'liqni saqlash tashkiloti (WHO), Suv tejash bo'yicha qo'llanma",
    ["1-2 litr", "5-10 litr", "15-20 litr", "50-100 litr"],
    1,
)

add_mcq(
    38,
    "Sug'orish O'zbekistonda suv iste'molining qancha qismini tashkil etadi?",
    "WATER",
    2,
    "O'zbekistonda sug'orish uchun sarflanadigan suv umumiy iste'molning taxminan 90% ini tashkil etadi. Bu dunyodagi eng yuqori ko'rsatkichlardan biri.",
    "Suv xo'jaligi vazirligi, O'zbekiston, 2023",
    ["30%", "50%", "75%", "90%"],
    3,
)

add_mcq(
    39,
    "Amudaryo qaysi suv havzasiga quyilishi kerak edi?",
    "WATER",
    3,
    "Amudaryo tarixan Orol dengiziga quyilgan. Lekin 1960-yillardan boshlab sug'orish uchun suv ko'p olinishi tufayli dengizga yetib bormay qo'ydi.",
    "O'rta Osiyo suv resurslarini boshqarish komissiyasi (ICWC), 2023",
    ["Kaspiy dengiziga", "Orol dengiziga", "Qora dengiziga", "Balxash ko'liga"],
    1,
)

add_mcq(
    40,
    "Quyidagilardan qaysi biri suvni tejash yo'li EMAS?",
    "WATER",
    1,
    "Noldan sug'orish (suv oqimini to'xtatmasdan) suvni ko'p sarflaydi. To'g'ri usullar: tomchi sug'orish, suv o'lchagich va qayta foydalanish.",
    "FAO, Suv samaradorligi bo'yicha qo'llanma, 2023",
    [
        "Tomchi sug'orish tizimini o'rnatish",
        "Suv o'lchagich o'rnatish",
        "Noldan sug'orish",
        "Yomg'ir suvini yig'ish",
    ],
    2,
)

add_mcq(
    41,
    "Orol dengizi qurib ketgandan so'ng nechta baliq turi yo'q bo'lib ketdi?",
    "WATER",
    2,
    "Orol dengizida 24 ta baliq turi yashagan. Sho'rlik oshgani va suv hajmi qisqargani tufayli barcha mahalliy baliq turlari yo'q bo'lib ketdi, baliqchilik sanoati inqirozga uchradi.",
    "FAO, Orol dengizi biologik xilma-xilligi hisoboti, 2021",
    ["5 tur", "15 tur", "24 tur", "50 tur"],
    2,
    article=1,
)

add_mcq(
    42,
    "Sirdaryo qaysi manbadan boshlanadi?",
    "WATER",
    2,
    "Sirdaryo Qirg'izistondagi Tyan-Shan tog'larida Qoradaryo va Norin daryolarining qo'shilishidan hosil bo'ladi. Umumiy uzunligi 3,018 km.",
    "O'zbekiston geografiya ensiklopediyasi, 2022",
    [
        "Pamir tog'laridan",
        "Qoradaryo va Norining qo'shilishidan",
        "Hisor tog'laridan",
        "Aral dengizidan",
    ],
    1,
)

add_mcq(
    43,
    "Ifloslangan suv orqali qaysi kasallik tarqalishi mumkin?",
    "WATER",
    1,
    "Vabo (cholera) Vibrio cholerae bakteriyasi bilan ifloslangan suv orqali tarqaladi. Daryo va ko'l suvini tozalamasdan ichish vaboga olib kelishi mumkin.",
    "Jahon sog'liqni saqlash tashkiloti (WHO), Suv xavfsizligi, 2023",
    ["Gripp", "Vabo (Cholera)", "O'pka saraton", "Tish chirishi"],
    1,
)

add_mcq(
    44,
    "O'zbekistonda aholi boshiga qayta tiklanadigan chuchuk suv resursi qancha?",
    "WATER",
    3,
    "O'zbekiston suv tanqisligi bo'yicha Markaziy Osiyo davlatlaridan biri. Aholi boshiga taxminan 1,700 m³/yil chuchuk suv to'g'ri keladi — bu suv tanqisligi chegarasiga yaqin.",
    "Jahon banki, Markaziy Osiyo suv resurslari hisoboti, 2022",
    ["500 m³", "1700 m³", "5000 m³", "10000 m³"],
    1,
)

add_mcq(
    45,
    "Tomchi sug'orish usulining asosiy afzalligi nima?",
    "WATER",
    1,
    "Tomchi sug'orish to'g'ridan-to'g'ri o'simlik ildiziga suv beradi, bug'lanish va oqimni minimallashtirib, an'anaviy usulga nisbatan 30-50% suv tejaydi.",
    "FAO, Tomchi sug'orish statistikasi, 2023",
    [
        "Sug'orish jarayoni tezroq",
        "30-50% suv tejaydi",
        "Hosil miqdori 2 barobarga oshadi",
        "O'g'it sarfi kamayadi",
    ],
    1,
)

add_mcq(
    46,
    "Zarafshon daryosi qaysi viloyatlardan o'tadi?",
    "WATER",
    2,
    "Zarafshon daryosi Tojikistondan boshlanib, O'zbekistonda Samarqand va Navoiy viloyatlaridan o'tadi. 'Samarqand' nomi ham bu daryo bilan bog'liq.",
    "O'zbekiston geografiya ma'lumotlari, 2023",
    [
        "Farg'ona va Toshkent",
        "Samarqand va Navoiy",
        "Qashqadaryo va Surxondaryo",
        "Buxoro va Xorazm",
    ],
    1,
)

add_mcq(
    47,
    "Suv molekulasining kimyoviy formulasi nima?",
    "WATER",
    3,
    "Suv molekulasi 2 ta vodorod atomi va 1 ta kislorod atomidan iborat: H₂O. Bu oddiy formula lekin suvning benzin, spirt kabi suyuqliklardan farqli xususiyatlarini belgilaydi.",
    "Umumiy kimyo darsligi, O'zbekiston oliy ta'lim standarti",
    ["HO", "H₂O", "H₃O", "HO₂"],
    1,
)

add_mcq(
    48,
    "O'zbekistonda yog'ingarchilik eng ko'p qaysi mintaqada kuzatiladi?",
    "WATER",
    2,
    "G'arbiy Tyan-Shan tog'larida (Toshkent viloyati tog'lari, Farg'ona tizmasi) yiliga 700-1000 mm yog'in tushadi. Tekislikda esa 100-300 mm atrofida.",
    "O'zgidrometmarkaz, Iqlim atlasi, 2022",
    ["Qizilqum cho'lida", "G'arbiy Tyan-Shan tog'larida", "Aral bo'yida", "Ustyurt platosida"],
    1,
)

add_mcq(
    49,
    "Suvni qayta foydalanishning to'g'ri misoli qaysi?",
    "WATER",
    1,
    "Sabzavot yuvgan suv organik bo'lib, o'simlik sug'orishga mutlaqo mos. Bu 'kulrang suv' qayta ishlatishning eng oson usuli va hech qanday tozalashni talab qilmaydi.",
    "BMT Suv dasturi (UN-Water), 2023",
    [
        "Yangi suv sotib olish",
        "Sabzavot yuvgan suvni bog' sug'orishda ishlatish",
        "Jo'mrakni doim ochiq qoldirish",
        "Katta idishda suv to'plash",
    ],
    1,
)

add_mcq(
    50,
    "Orol dengizidan ko'tarilgan tuz bo'ronlari necha km masofagacha yetib borishi mumkin?",
    "WATER",
    2,
    "Orol dengizi qurib ketgan tubidan ko'tarilgan tuz va pestitsid bo'ronlari shamol orqali 500 km masofagacha tarqalishi kuzatilgan. Bu qo'shni hududlar qishloq xo'jaligiga zarar keltiradi.",
    "ASBP, Orol dengizi ekologik muammolari, 2022",
    ["50 km", "200 km", "500 km", "2000 km"],
    2,
    article=1,
)

add_mcq(
    51,
    "Tomchi sug'orish texnologiyasini ixtiro qilgan mamlakat qaysi?",
    "WATER",
    3,
    "Tomchi sug'orish 1960-yillarda Isroil olimlari tomonidan ishlab chiqilgan. Bu ixtiro cho'l mamlakatida qishloq xo'jaligini rivojlantirishga imkon berdi.",
    "Isroil qishloq xo'jaligi tarixi, 2023",
    ["Frantsiya", "AQSh", "Isroil", "Hindiston"],
    2,
)

# TRUE_FALSE — WATER
add_tf(
    52,
    "Orol dengizi bir vaqtlar dunyoning to'rtinchi yirik ko'li hisoblangan.",
    "WATER",
    1,
    "Ha, Orol dengizi 1960-yillarda 68,000 km² maydon bilan dunyoning to'rtinchi yirik ko'li bo'lgan. Kaspiy, Yuqori va Viktoriya ko'llaridan keyin.",
    "UNESCO, Orol dengizi tarixi, 2022",
    True,
)

add_tf(
    53,
    "Yer yuzidagi barcha suvning taxminan 3% i chuchuk suv hisoblanadi.",
    "WATER",
    1,
    "Ha, Yer yuzidagi suvning atigi 2.5-3% i chuchuk suv. Lekin ularning ko'pi muzliklarda, er osti suvlarida — faqat 0.3% i daryolar va ko'llarda.",
    "USGS (AQSh geologiya xizmati), Dunyo suv resurslari, 2023",
    True,
)

add_tf(
    54,
    "Amudaryo hozirda Orol dengiziga yetib boradi.",
    "WATER",
    2,
    "Yo'q, Amudaryo suv ko'p olinishi sababli 1980-yillardan boshlab Orol dengiziga yetib bormay qoldi. Bu dengizning qurib ketishiga asosiy sabab bo'ldi.",
    "ASBP, Amudaryo oqim ma'lumotlari, 2022",
    False,
)

add_tf(
    55,
    "Suvni tejash orqali elektr energiyasi ham tejaladi.",
    "WATER",
    2,
    "Ha, suv tozalash, nasos qilish va isitish uchun katta elektr energiyasi kerak. 1 m³ suv tozalash uchun taxminan 0.3-0.5 kVh energiya sarflanadi.",
    "O'zbekiston suv ta'minoti tizimi energiya sarfi tahlili, 2023",
    True,
)

add_tf(
    56,
    "O'zbekiston Markaziy Osiyodagi suv resurslarining asosiy generatori hisoblanadi.",
    "WATER",
    3,
    "Yo'q, Markaziy Osiyodagi asosiy suv manbalari Tojikiston va Qirg'izistondagi tog' muzliklarida. O'zbekiston asosan quyi oqimda joylashgan suv iste'molchisi.",
    "ICWC, Markaziy Osiyo suv balansi, 2023",
    False,
)

add_tf(
    57,
    "Ochiq jo'mrakdan bir daqiqada taxminan 6-8 litr suv oqadi.",
    "WATER",
    1,
    "Ha, standart jo'mrakdan minutiga 6-8 litr suv oqadi. Tish tozalash, idish yuvish paytida jo'mrakni yopib qo'yish yiliga minglab litr suv tejaydi.",
    "WHO, Uy xo'jaligida suv iste'moli normalari, 2023",
    True,
)

# SCENARIO — WATER
add_scenario(
    58,
    "Oilangiz kuniga 200 litr suv iste'mol qiladi. Jo'mrakni tuzatib, kuniga 50 litr tejaysiz. Bir oyda necha litr suv tejaladi?",
    "WATER",
    2,
    "Tejamkorlik: 50 litr/kun × 30 kun = 1,500 litr/oy. Bu taxminan 1.5 tonna suv bo'lib, bir kishining ikki haftalik iste'moliga teng.",
    "Suv tejash hisob-kitobi asoslari",
    ["500 litr", "1000 litr", "1500 litr", "2000 litr"],
    2,
)

add_scenario(
    59,
    "Orol dengizi qurib ketishi natijasida Xorazm va Qoraqalpog'iston viloyatlarida iqlim qanday o'zgargan?",
    "WATER",
    2,
    "Katta suv havzasi yo'q bo'lganligi sababli iqlim keskin kontinental bo'lib ketdi: yoz harorati oshdi (+2-3°C), qish sovuqlashdi, yog'ingarchilik kamaydi.",
    "O'zgidrometmarkaz, Orol bo'yi iqlim o'zgarishlari, 2022",
    [
        "Yoz sovuqroq va qish iliqroq bo'ldi",
        "Yoz issiqroq va qish sovuqroq bo'ldi",
        "Yil bo'yi nam iqlim bo'ldi",
        "Iqlim o'zgarmadi",
    ],
    1,
    article=1,
)

add_scenario(
    60,
    "Fermer 1 gektar paxtaga tomchi sug'orish o'rnatdi. Oddiy sug'orish 8000 m³/ga suv sarflasa, tomchi sug'orish 40% tejasa, bir yilda necha m³ suv tejaydi?",
    "WATER",
    3,
    "Tejalgan suv: 8000 m³ × 40% = 3200 m³/yil/ga. Bu bir oilaning 10 yillik suv iste'moliga teng! Katta fermer xo'jaligi uchun bu ming dollar tejash demak.",
    "FAO, Tomchi sug'orish iqtisodiy tahlili, 2023",
    ["2000 m³", "3200 m³", "4000 m³", "6400 m³"],
    1,
)

# ─────────────────────────────────────────────
# FLORA — pk 61-90
# ─────────────────────────────────────────────
add_mcq(
    61,
    "Bir kattalashgan daraxt yiliga o'rtacha qancha CO2 shimib oladi?",
    "FLORA",
    1,
    "Katta daraxt yiliga taxminan 22 kg CO2 absorb qiladi. 1000 ta daraxt ekish 22 tonna CO2 ni atmosferadan tortib olishga teng — bu 5 ta avtomobilning yillik chiqarishiga teng.",
    "Arborday Foundation, Daraxt ekologiyasi, 2023",
    ["5 kg", "10 kg", "22 kg", "50 kg"],
    2,
    article=2,
)

add_mcq(
    62,
    "Fotosintez jarayonida o'simliklar quyosh nuridan nimalar hosil qiladi?",
    "FLORA",
    1,
    "Fotosintezda o'simliklar CO2 + suv + yorug'lik → glyukoza + kislorod reaksiyasini amalga oshiradi. Kislorod atmosferaga, glyukoza esa o'sish uchun ishlatiladi.",
    "Biologiya darsligi, O'zbekiston DTST, 2023",
    ["CO2 va azot", "Kislorod va glyukoza", "Suv va tuz", "Metan va kislorod"],
    1,
)

add_mcq(
    63,
    "O'rmonlarni ko'p miqdorda qirqib olish (deforestation) ekologiyaga qanday asosiy zarar yetkazadi?",
    "FLORA",
    1,
    "O'rmonlar CO2 ning asosiy yutuvchisi. Ular qirqilganda: 1) atmosferada CO2 ko'payadi, 2) yer siljishlari bo'ladi, 3) biologik xilma-xillik yo'qoladi.",
    "WWF, Deforestation hisoboti, 2023",
    ["Suv ko'payadi", "Atmosferada CO2 ko'payadi", "Hayvon ko'payadi", "Shamol kuchayadi"],
    1,
)

add_mcq(
    64,
    "O'zbekistondagi Zarafshon yong'oq o'rmoni qanday maqomga ega?",
    "FLORA",
    2,
    "Zarafshon davlat biosfera qo'riqxonasi 1975-yilda tashkil etilgan. UNESCO biosfera rezervatlar tarmog'iga kiritilgan bo'lib, noyob tog' eko-tizimini saqlaydi.",
    "O'zbekiston Ekologiya qo'mitasi, 2023",
    ["Milliy park", "Biosfera qo'riqxonasi", "Tabiiy yodgorlik", "Sanoat hududi"],
    1,
)

add_mcq(
    65,
    "Daraxt ekish uchun qaysi mavsumlar eng qulay?",
    "FLORA",
    1,
    "Bahor (mart-aprel) va kuz (oktyabr-noyabr) eng qulay mavsumlar. Bu paytlarda daraxtlar uxlash davrida bo'lib, ildiz tutish uchun mo'tadil harorat va namlik mavjud.",
    "O'zbekiston o'rmon xo'jaligi qo'llanmasi, 2022",
    ["Yoz va qish", "Bahor va kuz", "Faqat yoz", "Faqat qish"],
    1,
)

add_mcq(
    66,
    "O'zbekiston o'rmonlari mamlakatning qancha qismini egallaydi?",
    "FLORA",
    2,
    "O'zbekistonda o'rmon va butazorlar umumiy maydonning taxminan 8% ini tashkil etadi. Bu Yevropa o'rtacha 37% ga nisbatan juda kam, shuning uchun ko'kalamzorlashtirish muhim.",
    "O'zbekiston o'rmon xo'jaligi davlat qo'mitasi, 2023",
    ["1%", "8%", "20%", "35%"],
    1,
)

add_mcq(
    67,
    "O'zbekistondagi 'Yashil Makon' dasturining maqsadi nima?",
    "FLORA",
    1,
    "'Yashil Makon' — O'zbekiston Prezidentining 2021-yil farmoni bilan boshlangan dastur. Maqsad: 2026 yilga qadar 1 mlrd daraxt va buta o'simlik ekish, iqlimlashuvga hissa qo'shish.",
    "O'zbekiston Prezidentining 2021-yil farmoni, Ekologiya vazirligi",
    [
        "Yangi binolar qurish",
        "1 mlrd daraxt va buta ekish",
        "Ko'chalarni kengaytirish",
        "Sanoatni rivojlantirish",
    ],
    1,
)

add_mcq(
    68,
    "O'simliklar fotosintez uchun qaysi yorug'lik to'lqin uzunliklaridan ko'proq foydalanadi?",
    "FLORA",
    3,
    "Xlorofill asosan ko'k (430-450 nm) va qizil (640-680 nm) yorug'likni yutadi. Yashil yorug'lik aks ettiriladi, shuning uchun o'simliklar bizga yashil ko'rinadi.",
    "O'simlik fiziologiyasi, Oliy ta'lim darsligi, 2023",
    [
        "Yashil yorug'lik (500-560 nm)",
        "Ko'k va qizil yorug'lik",
        "Sariq yorug'lik (570-590 nm)",
        "To'q sariq yorug'lik",
    ],
    1,
)

add_mcq(
    69,
    "O'zbekistonda ko'kalamzorlashtirish uchun eng ko'p qaysi daraxtlar ekiladi?",
    "FLORA",
    2,
    "Terak (poplar) tez o'sgani va shimoliy mintaqalarda chidamliligi uchun, chinor esa katta soya berishi va uzoq umrliligi uchun O'zbekistonda ko'p ekiladi.",
    "O'zbekiston o'rmon xo'jaligi ilmiy-tadqiqot instituti, 2023",
    ["Qayin va eman", "Terak va chinor", "Archa va qayin", "Eman va o'rik"],
    1,
)

add_mcq(
    70,
    "Shaharlarda daraxt ekish shahar haroratini necha gradusga pasaytirishi mumkin?",
    "FLORA",
    1,
    "Shahar daraxtlari soya berish va suv bug'lantirish (evapotranspirasiya) orqali shahar haroratini 1-2°C ga, ba'zan 5°C gacha pasaytirishi mumkin.",
    "C40 Shaharlar iqlim rahbariyati, 2023",
    ["0.5°C", "1-2°C", "5°C", "10°C"],
    1,
    article=2,
)

add_mcq(
    71,
    "O'simliklar ildizlari orqali asosan nima oladi?",
    "FLORA",
    2,
    "Ildizlar tuproqdan suv va unda erigan mineral moddalar (azot, fosfor, kaliy va boshqalar) ni o'zlashtiradi. Bu moddalar o'sish va rivojlanish uchun zarur.",
    "O'simlik fiziologiyasi darsligi, 2023",
    ["Kislorod va CO2", "Suv va mineral moddalar", "Shakar va kraxmal", "Yorug'lik va issiqlik"],
    1,
)

add_mcq(
    72,
    "Daraxt qancha vaqt umr ko'rishi mumkin?",
    "FLORA",
    1,
    "Ko'plab daraxt turlari yuzlab, ba'zilari minglab yil umr ko'radi. Dunyodagi eng keksa daraxt — 5000 yillik Bristlecone Pine (AQSh). O'zbekistondagi chinorlar 500-700 yil umr ko'radi.",
    "Dendrologiya asoslari, 2023",
    ["10-20 yil", "50-100 yil", "100-1000 yil va undan ko'p", "Faqat 30-50 yil"],
    2,
)

add_mcq(
    73,
    "Dengiz tubida chuqur suvlarda o'simliklar fotosintez qila olmaydigan asosiy sabab nima?",
    "FLORA",
    2,
    "Yorug'lik dengizning taxminan 200 m chuqurligida so'nib qoladi. Fotosintez uchun yorug'lik kerak. Shuning uchun dengiz o'simliklari faqat 'fotic zona' (yorug' qavatda) yashaydi.",
    "Okeanografiya asoslari, 2023",
    ["Suv juda sovuq", "Yorug'lik yetmaydi", "Mineral moddalar yo'q", "Kislorod yo'q"],
    1,
)

add_mcq(
    74,
    "Chimyon tog'lari o'rmonida qaysi daraxt turi ustun?",
    "FLORA",
    3,
    "Chimyon (Toshkent viloyati) tog'larida archa (juniper) dominant tur hisoblanadi. Archa o'rmonlari O'zbekistonda 500,000 gektardan ortiq maydonni egallaydi.",
    "O'zbekiston o'rmon xo'jaligi instituti, 2023",
    ["Archa (juniper)", "Qayin", "Eman (oak)", "Terak"],
    0,
)

add_mcq(
    75,
    "Butun dunyodagi o'rmonlar yer kislorodining qancha qismini hosil qiladi?",
    "FLORA",
    2,
    "Yer yuzidagi o'rmonlar, ayniqsa tropik o'rmonlar, atmosfera kislorodining taxminan 28-30% ini ishlab chiqaradi. Okean fitoplanktonlari esa 50-80% ni hosil qiladi.",
    "NASA Yer kuzatish markazi, 2023",
    ["10%", "28-30%", "50%", "80%"],
    1,
)

add_mcq(
    76,
    "Daraxt ildizlari tuproq eroziyasini qanday to'xtatadi?",
    "FLORA",
    1,
    "Daraxt ildizlari tuproqni mexanik ravishda ushlab turadi, suv oqimini sekinlashtiradi va tuproq strukturasini mustahkamlaydi. Bu shamol va yomg'ir eroziyasiga qarshi eng samarali vosita.",
    "FAO, Tuproq eroziyasiga qarshi kurash, 2023",
    [
        "Kimyoviy moddalar chiqaradi",
        "Ildizlari tuproqni mahkam ushlab turadi",
        "Tuproqni qotiradi",
        "Suv to'siq hosil qiladi",
    ],
    1,
)

add_mcq(
    77,
    "Qizilqum cho'lida ko'kalamzorlashtirish uchun qaysi o'simliklar ekiladi?",
    "FLORA",
    2,
    "Saksovul (saxaul) va qandim cho'l sharoitiga moslashgan o'simliklar bo'lib, kamsuv va issiqqa chidamli. Ularni ekish cho'l tarqalishini to'xtatadi.",
    "O'zbekiston cho'llashtirish va qumlashtirish dasturi, 2023",
    ["Terak va chinor", "Saksovul va qandim", "Archa va qayin", "Eman va o'rik"],
    1,
)

add_mcq(
    78,
    "Bitta katta eman (oak) daraxti qancha hasharot turini boqishi mumkin?",
    "FLORA",
    3,
    "Ekologik tadqiqotlar ko'rsatishicha, bitta katta eman daraxti 280-500 dan ortiq hasharot turini oziqlanish, yashash va ko'payish uchun yashash joyi sifatida ta'minlaydi.",
    "Douglas Tallamy, Ona o'simliklar ekologiyasi, 2022",
    ["50 tur", "100 tur", "280-500 tur", "1000+ tur"],
    2,
)

add_mcq(
    79,
    "Fotosintezda CO2 dan hosil bo'ladigan asosiy organik modda qaysi?",
    "FLORA",
    2,
    "Fotosintez: 6CO₂ + 6H₂O → C₆H₁₂O₆ (glyukoza) + 6O₂. Glyukoza o'simlikning 'ovqati' bo'lib, energiya manbai va yangi hujayra qurilishiga xizmat qiladi.",
    "Biologiya: Hayot ilmi, O'zbekiston DTST, 2023",
    ["Azot", "Glyukoza", "Ozon", "Vodorod"],
    1,
)

add_mcq(
    80,
    "Shaharda daraxtlar qanday qo'shimcha ekologik vazifalarni bajaradi?",
    "FLORA",
    1,
    "Shahar daraxtlari: 1) soya va salqin beradi (issiqlik orolini pasaytiradi), 2) havo tozalaydi (chang, NO₂ va SO₂ ni yutadi), 3) shovqin kamaytiradi, 4) yomg'ir suvini ushlab qoladi.",
    "C40 Cities, Yashil infrastruktura, 2023",
    [
        "Faqat estetik ko'rinish uchun",
        "Soya, havo tozalash va shovqin kamaytirish",
        "Faqat CO2 yutish",
        "Faqat yomg'ir tutish",
    ],
    1,
    article=2,
)

add_mcq(
    81,
    "Evkalipt daraxti kuniga qancha suv iste'mol qiladi?",
    "FLORA",
    3,
    "Evkalipt tez o'suvchi daraxt bo'lib, kuniga 200-500 litr suv iste'mol qiladi. Shuning uchun quruq mintaqalarda ekish tavsiya qilinmaydi.",
    "CSIRO (Avstraliya ilmiy-tadqiqot tashkiloti), 2023",
    ["5-10 litr", "50 litr", "200-500 litr", "1000+ litr"],
    2,
)

# TRUE_FALSE — FLORA
add_tf(
    82,
    "O'simliklar fotosintez jarayonida kislorod chiqaradi.",
    "FLORA",
    1,
    "Ha, fotosintezda CO₂ va suv yorug'lik yordamida glyukoza va kislorodga aylanadi. Atmosferadagi kislorodning katta qismi o'simliklar tufayli mavjud.",
    "Biologiya asoslari, 2023",
    True,
)

add_tf(
    83,
    "O'rmonlarni qirqib olish iqlim o'zgarishiga hissa qo'shadi.",
    "FLORA",
    1,
    "Ha, o'rmonlar CO2 saqlaydi. Qirqilganda saqlangan CO2 atmosferaga chiqadi. Global deforestation yillik CO2 emissiyasining 10-15% ini tashkil etadi.",
    "IPCC, Yer foydalanish va iqlim hisoboti, 2022",
    True,
)

add_tf(
    84,
    "Kaktus ham fotosintez qiladi.",
    "FLORA",
    2,
    "Ha, kaktuslar CAM (Crassulacean Acid Metabolism) deb atalgan maxsus fotosintez turi bilan ishlaydi — kunduzi stomalarini yopadi, kechqurun CO2 yig'adi.",
    "O'simlik fiziologiyasi, 2023",
    True,
)

add_tf(
    85,
    "Daraxt ekish hududning er osti suv resurslarini kamaytiradi.",
    "FLORA",
    2,
    "Yo'q, daraxtlar ildizlari tuproq strukturasini yaxshilab, suv singishini (infiltratsiya) oshiradi, er osti suvlarini to'ldiradi va er osti suvini kamaytirmaydi.",
    "FAO, Daraxt va suv o'zaro ta'siri, 2023",
    False,
)

add_tf(
    86,
    "O'zbekistonda o'rmon maydoni mamlakatning 15% dan ortiq qismini egallaydi.",
    "FLORA",
    3,
    "Yo'q, O'zbekistonda o'rmon va butazorlar umumiy maydonning taxminan 8% ini tashkil etadi. Bu ko'rsatkich Yevropa o'rtachasidan (37%) ancha past.",
    "O'zbekiston o'rmon xo'jaligi qo'mitasi, 2023",
    False,
)

add_tf(
    87,
    "Bahor fasli daraxt ekish uchun eng qulay vaqtlardan biri.",
    "FLORA",
    1,
    "Ha, bahorda tuproq issig'i, namligi va ko'chat o'sishi uchun ideal sharoitlar mavjud. Mart-aprel oylari O'zbekistonda daraxt ekish uchun eng qulay davr.",
    "O'zbekiston o'rmon xo'jaligi qo'llanmasi, 2022",
    True,
)

# SCENARIO — FLORA
add_scenario(
    88,
    "Maktabdagi 500 o'quvchi har biri 2 tadan daraxt ekdi. Bu daraxtlar yiliga necha kg CO2 yutib oladi? (1 daraxt ≈ 22 kg CO2/yil)",
    "FLORA",
    2,
    "Jami daraxtlar: 500 × 2 = 1000 ta. CO2 yutish: 1000 × 22 kg = 22,000 kg/yil = 22 tonna CO2/yil. Bu 5 ta avtomobilning yillik chiqarishiga teng!",
    "Arborday Foundation hisob-kitobi",
    ["5,500 kg", "11,000 kg", "22,000 kg", "44,000 kg"],
    2,
    article=2,
)

add_scenario(
    89,
    "Shaharda 100 ta katta daraxt kesildi, 20 ta yangi kichik daraxt ekildi. Yillik CO2 yutish qanday o'zgardi? (katta daraxt=22 kg, kichik=2 kg)",
    "FLORA",
    2,
    "Oldingi: 100 × 22 = 2200 kg/yil. Keyingi: 20 × 2 = 40 kg/yil. Farq: 2200 - 40 = 2160 kg kamaydi. Bu ekologik jihatdan katta zarar — yangi daraxtlar 10 yildan keyin kattalar qatoriga kiradi.",
    "Shahar yashil infratuzilmasi tahlili",
    ["2160 kg kamaydi", "1000 kg kamaydi", "200 kg kamaydi", "O'zgarmadi"],
    0,
)

add_scenario(
    90,
    "Fermer dala chekkasiga 3 km uzunligida himoya daraxtzoqi ekmoqchi. Har 4 metrda 1 daraxt ekilsa, jami nechta daraxt kerak?",
    "FLORA",
    3,
    "Uzunlik: 3 km = 3000 m. Soni: 3000 / 4 = 750 ta daraxt. Bunday himoya daraxtzorlar qishloq xo'jaligi yerlarini shamol eroziyasidan saqlaydi.",
    "Agro-o'rmonchilik hisob-kitobi asoslari",
    ["500 ta", "750 ta", "1000 ta", "1500 ta"],
    1,
)

# ─────────────────────────────────────────────
# WASTE — pk 91-120
# ─────────────────────────────────────────────
add_mcq(
    91,
    "Bitta plastik shishani qayta ishlash necha soat elektr energiyasi tejaydi?",
    "WASTE",
    1,
    "1 ta plastik shishani qayta ishlash yangi plastik ishlab chiqarishga nisbatan taxminan 2 soatlik elektr energiyasini tejaydi. Bu 100W lambochkani 2 soat yoqishga yetadi.",
    "Plastik qayta ishlash sanoati ma'lumotlari, 2023",
    ["0.5 soat", "2 soat", "5 soat", "10 soat"],
    1,
    article=3,
)

add_mcq(
    92,
    "Plastik to'liq parchalanishi uchun taxminan qancha vaqt ketadi?",
    "WASTE",
    1,
    "Oddiy plastik (PET, HDPE) tabiatda 400-500 yil ichida parchalanadi. Bu vaqt ichida plastik mikroplastikga aylanib, tuproq va suvni ifloslantiradi.",
    "Plastik ifloslantirish koalitsiyasi, 2023",
    ["10 yil", "50 yil", "500 yil", "5000 yil"],
    2,
)

add_mcq(
    93,
    "1 tonna qog'ozni qayta ishlash nechta daraxtni kesishdan saqlab qoladi?",
    "WASTE",
    1,
    "1 tonna qayta ishlangan qog'oz 17 ta katta daraxtni, 26,500 litr suvni va 3.3 m³ poligon maydonini tejaydi.",
    "American Forest & Paper Association, 2023",
    ["5 ta", "10 ta", "17 ta", "50 ta"],
    2,
    article=3,
)

add_mcq(
    94,
    "Shisha qayta ishlash yangi shisha ishlab chiqarishga nisbatan necha foiz kam energiya sarflaydi?",
    "WASTE",
    2,
    "Qayta ishlangan shishadan yangi shisha tayyorlash yangi xom ashyodan ishlab chiqarishga nisbatan 30-35% kam energiya sarflaydi.",
    "Glass Packaging Institute, 2023",
    ["10%", "20%", "30%", "60%"],
    2,
)

add_mcq(
    95,
    "Chiqindilarni saralashning asosiy ekologik maqsadi nima?",
    "WASTE",
    1,
    "Saralash har xil turdagi chiqindilarni qayta ishlash va qayta foydalanish imkonini beradi. Bu xom ashyo sarfini, energiya iste'molini va poligon maydonini kamaytiradi.",
    "Ekologiya vazirligi, O'zbekiston, 2023",
    [
        "Shaharni tartibli ko'rinishga keltirish",
        "Chiqindilarni qayta ishlashga imkon berish",
        "Yong'in xavfini kamaytirish",
        "Poligon xarajatini qisqartirish",
    ],
    1,
)

add_mcq(
    96,
    "Batareyani oddiy axlatga tashlash nima uchun xavfli?",
    "WASTE",
    2,
    "Batareyalar qo'rg'oshin, simob, kadmiy va litiy kabi og'ir metallarni o'z ichiga oladi. Ular tuproqqa sinib, er osti suvlarini 400-500 yil mobaynida ifloslantirishi mumkin.",
    "Basel konventsiyasi, Xavfli chiqindilar, 2023",
    [
        "Portlash xavfi",
        "Og'ir metallar tuproq va suvni ifloslantiradi",
        "Yong'in chiqaradi",
        "Havo ifloslanadi",
    ],
    1,
)

add_mcq(
    97,
    "Elektron chiqindilar (e-waste) nima?",
    "WASTE",
    1,
    "E-waste — ishlatilmay qolgan elektron va elektr jihozlar: kompyuter, telefon, televizor, printer. Ular zararli metallar va kimyoviy moddalar o'z ichiga oladi.",
    "BMT E-waste statistikasi, 2023",
    [
        "Elektr toki bilan bog'liq har qanday narsa",
        "Eski elektron jihozlar: telefon, kompyuter, TV",
        "Faqat batareyalar",
        "Faqat simlar",
    ],
    1,
)

add_mcq(
    98,
    "O'zbekistonda yiliga taxminan qancha tonna qattiq maishiy chiqindi hosil bo'ladi?",
    "WASTE",
    2,
    "O'zbekistonda yiliga taxminan 5-6 million tonna qattiq maishiy chiqindi hosil bo'ladi. Shundan atigi 5-10% qayta ishlanadi, qolganlari poligonlarda ko'miladi.",
    "Ekologiya vazirligi, Chiqindilar boshqaruvi hisoboti, 2023",
    ["100,000 tonna", "1 million tonna", "5 million tonna", "20 million tonna"],
    2,
)

add_mcq(
    99,
    "Organik chiqindilardan (ovqat qoldiqlari) tayyorlanadigan natural o'g'it qanday ataladi?",
    "WASTE",
    1,
    "Kompost — organik moddalar aerob (kislorodli) sharoitda parchalanishi natijasida hosil bo'ladigan tabiiy o'g'it. U tuproqni boyitadi, suvni saqlaydi va kimyoviy o'g'it sarfini kamaytiradi.",
    "FAO, Kompostlash bo'yicha qo'llanma, 2023",
    [
        "Zaharli kimyoviy modda",
        "Kompost (tabiiy o'g'it)",
        "Ifloslantiruvchi kukun",
        "Kimyoviy reaktiv",
    ],
    1,
)

add_mcq(
    100,
    "O'zbekistonda chiqindilarni qayta ishlash sanoati qaysi shaharda eng ko'p rivojlangan?",
    "WASTE",
    2,
    "Toshkentda O'zbekistondagi chiqindi qayta ishlash korxonalarining ko'pi joylashgan. Shuningdek, Toshkent viloyatidagi Zangiota, Chirchiqda qayta ishlash zavodlari mavjud.",
    "O'zbekiston Ekologiya vazirligi, 2023",
    ["Samarqand", "Toshkent", "Buxoro", "Nukus"],
    1,
    article=3,
)

add_mcq(
    101,
    "1 martalik plastik qopni nima bilan almashtirish eng yaxshi?",
    "WASTE",
    1,
    "Ko'p martalik matoli sumka yoki savat ishlatish plastik qop iste'molini keskin kamaytiradi. 1 ta matoli sumka 700 ta plastik qopni almashtiradi.",
    "BMT Atrof-muhit dasturi (UNEP), Plastik ifloslantirish, 2023",
    [
        "Ko'p martalik matoli sumka",
        "Qo'shimcha plastik qop",
        "Qog'oz qop qo'lda",
        "Hech narsa olib yurmaslik",
    ],
    0,
)

add_mcq(
    102,
    "Kompyuter axlatga tashlanganda qanday zararli moddalar tuproqqa o'tishi mumkin?",
    "WASTE",
    2,
    "Kompyuterlar qo'rg'oshin (kondensatorlarda), simob (displeylarda), kadmiy (batareyalarda) va brom (plastik qutilarda) kabi og'ir metallar o'z ichiga oladi.",
    "WHO, E-waste va sog'liq, 2023",
    ["Faqat mis va temir", "Qo'rg'oshin, simob va kadmiy", "Faqat plastik", "Faqat shisha"],
    1,
)

add_mcq(
    103,
    "'Zero Waste' (Nol Chiqindi) tamoyilining to'g'ri tartibi qaysi?",
    "WASTE",
    3,
    "5R tamoyili: Refuse (rad etish) → Reduce (kamaytirish) → Reuse (qayta ishlatish) → Recycle (qayta ishlash) → Rot (kompostlash). Bu tartibda yuqoridagi usullar samaraliroq.",
    "Zero Waste International Alliance, 2023",
    [
        "Ishlatish, qayta ishlash, yo'q qilish",
        "Rad etish, kamaytirish, qayta ishlatish, qayta ishlash, kompostlash",
        "Yig'ish, yoqish, ko'mish",
        "Saralash, yoqish, tarqatish",
    ],
    1,
)

add_mcq(
    104,
    "Bioplastik an'anaviy plastikdan nimasi bilan farqlanadi?",
    "WASTE",
    1,
    "Bioplastik o'simlik xom ashyosidan (makkajo'xori, qand lavlagi) tayyorlanadi va mikroorganizmlar ta'sirida 3-6 oyda parchalanadi. Oddiy plastik 400-500 yil parchalanmaydi.",
    "European Bioplastics, 2023",
    ["Arzonroq ishlab chiqariladi", "Tez parchalanadi", "Yanada qattiqroq", "Ko'p rangli bo'ladi"],
    1,
)

add_mcq(
    105,
    "Quyidagi chiqindilardan qaysi biri eng tez parchalanadi?",
    "WASTE",
    2,
    "Meva po'stlog'i va boshqa organik chiqindilar 1-6 oy ichida parchalanadi. Qog'oz 2-6 hafta, temir 80-100 yil, shisha 4000+ yil, plastik 400-500 yil.",
    "Chiqindi parchalanishi jadvali, Ekologiya vazirligi",
    ["Shisha", "Plastik", "Meva po'stlog'i", "Temir"],
    2,
)

add_mcq(
    106,
    "LFG (Landfill Gas/Poligon gazi) nima?",
    "WASTE",
    3,
    "Poligonlardagi organik chiqindilar anaerob parchalanadi va taxminan 50% metan (CH₄), 50% CO₂ aralashmasini hosil qiladi. Metan CO₂ dan 25 marta kuchli issiqxona gazi.",
    "EPA (AQSh Atrof-muhit muhofaza agentligi), 2023",
    [
        "Qurilish chiqindisi gazlari",
        "Organik chiqindi parchalanishidan hosil bo'lgan metan",
        "Suyuq kimyoviy chiqindi",
        "Oziq-ovqat chiqindi bugi",
    ],
    1,
)

add_mcq(
    107,
    "Chiqindilarni kamaytirish uchun birinchi qadam nima?",
    "WASTE",
    1,
    "5R tamoyilida birinchi qadam — 'Refuse' (rad etish). Kerak bo'lmagan narsani sotib olmaslik yoki qabul qilmaslik eng samarali usul, chunki bu holda chiqindi hosil bo'lmaydi.",
    "Zero Waste International Alliance, 2023",
    [
        "Ko'proq qayta ishlash",
        "Ortiqcha narsa sotib olmaslik",
        "Katta axlatdon sotib olish",
        "Yoqib yuborish",
    ],
    1,
)

add_mcq(
    108,
    "O'zbekistonda yog'ochga arzon va ekologik alternativa bo'lishi mumkin bo'lgan o'simlik qaysi?",
    "WASTE",
    2,
    "Bambu tez o'suvchi o'simlik (kuniga 90 sm gacha) bo'lib, yog'ochdan mustahkamroq, 3-5 yilda kesishga tayyor va CO2 ni intensiv yutadi. Arid iqlimga ham moslashtirilgan navlari bor.",
    "Bambu sanoati xalqaro tashkiloti, 2023",
    ["Alyuminiy", "Bambu", "Mis", "Qo'rg'oshin"],
    1,
)

add_mcq(
    109,
    "Bitta shisha idishni qayta ishlash atmosferaga qancha CO2 chiqarishni oldini oladi?",
    "WASTE",
    3,
    "1 ta shisha idishni qayta ishlash yangi shisha ishlab chiqarishga nisbatan taxminan 300 g CO2 kamayishiga olib keladi. Bu elektr sarfi va xom ashyo kamayishi hisobida.",
    "Glass Packaging Institute, Hayotiy tsikl tahlili, 2023",
    ["50 g", "300 g", "1 kg", "5 kg"],
    1,
)

add_mcq(
    110,
    "O'zbekistonda eskirgan telefon va kompyuterni nima qilish kerak?",
    "WASTE",
    2,
    "E-chiqindilar ixtisoslashgan to'plash punktlariga topshirilishi shart. Bu zararli metallarning tuproqqa o'tishini oldini oladi va qayta ishlash imkonini beradi.",
    "O'zbekiston Ekologiya vazirligi, E-waste ko'rsatmasi, 2023",
    [
        "Oddiy axlatga tashlash",
        "Ixtisoslashgan to'plash punktlariga topshirish",
        "Yoqib yuborish",
        "Ko'mib qo'yish",
    ],
    1,
)

add_mcq(
    111,
    "O'zbekistonda 2030 yilgacha chiqindi qayta ishlashni necha foizga yetkazish rejalashtirilgan?",
    "WASTE",
    3,
    "O'zbekiston hukumatining rejasiga ko'ra, 2030 yilga qadar qattiq maishiy chiqindilarning 50% ini qayta ishlash maqsad qilingan. Hozircha atigi 5-10% qayta ishlanadi.",
    "O'zbekiston Ekologiya vazirligi, Chiqindilar boshqaruvi strategiyasi, 2023",
    ["15%", "25%", "50%", "80%"],
    2,
)

# TRUE_FALSE — WASTE
add_tf(
    112,
    "Plastik sumkalar qayta ishlanishi mumkin.",
    "WASTE",
    1,
    "Ha, PE (polietilen) plastik sumkalar texnik jihatdan qayta ishlanishi mumkin. Lekin ularni oddiy axlatga tashlamang — maxsus to'plash punktlariga topshiring.",
    "Plastik qayta ishlash sanoati, 2023",
    True,
)

add_tf(
    113,
    "Batareyani oddiy axlatga tashlab yuborish xavfsiz.",
    "WASTE",
    1,
    "Yo'q! Batareyalar og'ir metallar (qo'rg'oshin, kadmiy, simob) o'z ichiga oladi. Tuproq va suvga o'tib 400+ yil mobaynida ifloslantiradi.",
    "Basel konventsiyasi, 2023",
    False,
)

add_tf(
    114,
    "Bitta plastik shishaning tabiatda parchalanishi uchun 500 yildan ortiq vaqt kerak.",
    "WASTE",
    2,
    "Ha, PET plastik tabiatda 400-500 yil ichida to'liq parchalanadi. Bu davrda u mikro va nanoplastiklarga bo'linib, oziq-zanjirga kirib boradi.",
    "Plastik ifloslantirish koalitsiyasi, 2023",
    True,
    article=3,
)

add_tf(
    115,
    "Kompost qilish organik chiqindilarni foydali o'g'itga aylantiradi.",
    "WASTE",
    2,
    "Ha, to'g'ri kompostlash ovqat qoldiqlari va o'simlik chiqindilarini 2-3 oyda tuproqni boyituvchi humused o'g'itga aylantiradi.",
    "FAO, Organik chiqindilar boshqaruvi, 2023",
    True,
)

add_tf(
    116,
    "Shisha to'liq qayta ishlanishi mumkin va bu jarayon cheksiz takrorlanishi mumkin.",
    "WASTE",
    3,
    "Ha, shisha qayta ishlaganda sifati yo'qolmaydi (metall va qog'ozdan farqli). Nazariy jihatdan cheksiz marta qayta ishlanishi mumkin.",
    "Glass Packaging Institute, 2023",
    True,
)

add_tf(
    117,
    "Qayta ishlash (recycling) uchun chiqindilarni oldindan saralash kerak.",
    "WASTE",
    1,
    "Ha, aralashgan chiqindilar qayta ishlash zavodida saralanishi kerak, bu qo'shimcha xarajat. Uyda saralash jarayonni arzonlashtiradi va samaradorlikni oshiradi.",
    "Chiqindi boshqaruvi sanoati, 2023",
    True,
)

# SCENARIO — WASTE
add_scenario(
    118,
    "Oilangiz oyiga 30 ta plastik shisha iste'mol qiladi. Barchasini qayta ishlashga bersa, bir yilda necha soat elektr tejaladi? (1 shisha = 2 soat elektr tejaydi)",
    "WASTE",
    2,
    "Yilik saqlangan shishalar: 30 shisha/oy × 12 oy = 360 shisha. Tejilgan elektr: 360 × 2 soat = 720 soat. Bu oddiy lampochkaning qariyb bir oylik ishi!",
    "Plastik qayta ishlash iqtisodiy tahlili",
    ["180 soat", "360 soat", "720 soat", "1440 soat"],
    2,
    article=3,
)

add_scenario(
    119,
    "Maktab 100 kg qog'oz chiqindisini qayta ishlashga topshirdi. Nechta daraxt saqlanib qoldi? (1 tonna qog'oz = 17 daraxt)",
    "WASTE",
    2,
    "100 kg = 0.1 tonna. 0.1 × 17 = 1.7 daraxt saqlanib qoladi. Butun maktab yilida 1 tonna qog'oz topshirsa — 17 daraxt!",
    "American Forest & Paper Association hisob-kitobi",
    ["0.5 ta daraxt", "1.7 ta daraxt", "5 ta daraxt", "17 ta daraxt"],
    1,
)

add_scenario(
    120,
    "Shahar poligoniga oyiga 4000 tonna chiqindi keladi. 40% organik bo'lsa, kompostlash dasturini joriy qilsa, poligon hajmi necha tonnaga kamayadi?",
    "WASTE",
    3,
    "Organik chiqindi: 4000 × 40% = 1600 tonna/oy. Kompostlash bu miqdorni to'liq yo'naltirib, poligon hajmini 1600 tonna ga kamaytiradi. Bu poligon xizmat muddatini uzaytiradi.",
    "Chiqindilarni boshqarish texnologiyalari, 2023",
    ["800 tonna", "1200 tonna", "1600 tonna", "2000 tonna"],
    2,
)

# ─────────────────────────────────────────────
# FAUNA — pk 121-150
# ─────────────────────────────────────────────
add_mcq(
    121,
    "O'zbekiston Qizil kitobiga nechta hayvon turi kiritilgan?",
    "FAUNA",
    1,
    "O'zbekistonning Qizil kitobiga 184 ta hayvon turi kiritilgan, jumladan sut emizuvchilar, qushlar, reptiliyalar, baliqlar va hasharotlar.",
    "O'zbekiston Qizil kitobi, 5-nashr, 2022",
    ["50 tur", "100 tur", "184 tur", "300 tur"],
    2,
    article=5,
)

add_mcq(
    122,
    "Jayron (Gazella subgutturosa) qaysi hayvon turkumiga kiradi?",
    "FAUNA",
    1,
    "Jayron — tuyoqlilar turkumining juft tuyoqlilar tartibiga kiruvchi antilopa. U O'zbekiston Qizil kitobiga kiritilgan noyob hayvon.",
    "O'zbekiston hayvonot dunyosi, 2023",
    ["Yovvoyi cho'chqa (suidae)", "Antilopa (bovidae)", "Bo'ri (canidae)", "Ot (equidae)"],
    1,
)

add_mcq(
    123,
    "Quyidagi hayvonlardan qaysi biri O'zbekiston Qizil kitobida?",
    "FAUNA",
    1,
    "Jayron O'zbekiston Qizil kitobida noyob va himoyaga muhtoj tur sifatida kiritilgan. Populyatsiyasi so'nggi yillarda Qizilqum qo'riqxonasida tiklanmoqda.",
    "O'zbekiston Qizil kitobi, 2022",
    ["Uy mushuki", "Qo'y", "Jayron", "Mol sigir"],
    2,
    article=5,
)

add_mcq(
    124,
    "O'zbekistonda suv qushlari uchun muhim yashash joyi qaysi?",
    "FAUNA",
    2,
    "Aydarkul ko'li (Navoiy viloyati) va Arnasoy ko'llari suv qushlari uchun Markaziy Osiyoning eng muhim qishlash joylaridan biri. Yuz minglab qush bu yerda qishlaydi.",
    "Wetlands International, Markaziy Osiyo suv qushlari, 2023",
    [
        "Amudaryo deltasi faqat",
        "Aydarkul va Arnasoy ko'llari",
        "Qizilqum cho'li",
        "Toshkent suv ombori",
    ],
    1,
)

add_mcq(
    125,
    "Oziq-zanjir (food chain) nima?",
    "FAUNA",
    1,
    "Oziq-zanjir — tirik organizmlar orasidagi oziq-ovqat bog'liqligini ko'rsatuvchi tizim. Masalan: o'simlik → quyon → tulki → bo'ri. Har bir halqa oldingilarni iste'mol qiladi.",
    "Ekologiya asoslari, O'zbekiston DTST, 2023",
    ["Parazitizm", "Raqobat", "Oziq-zanjir", "Simbioz"],
    2,
)

add_mcq(
    126,
    "O'zbekiston Qizil kitobidagi sut emizuvchilar ichida qaysi yirik yirtqich bor?",
    "FAUNA",
    2,
    "Qoplayon (Panthera pardus, leopard) O'zbekiston Qizil kitobiga kiritilgan. Surxondaryo va Hisor tog'larida uchraydi, lekin soni juda kam — bir necha o'n ta.",
    "O'zbekiston Qizil kitobi, 2022",
    ["Tuyaqush", "Qoplayon (leopard)", "Timsoh", "Pingvin"],
    1,
    article=5,
)

add_mcq(
    127,
    "Hayvonlarning mavsumiy ko'chishi qanday ataladi?",
    "FAUNA",
    1,
    "Migratsiya — hayvonlar (qushlar, baliqlar, sut emizuvchilar) ning yashash sharoiti, oziq va ko'payish maqsadida mavsumiy ravishda bir hududdan boshqasiga ko'chishi.",
    "Hayvonot ekologiyasi, 2023",
    ["Hibernas", "Migratsiya", "Ko'payish", "Uyqu davri"],
    1,
)

add_mcq(
    128,
    "Archa o'rmonlari qaysi tog' hayvonlari uchun asosiy yashash joyi?",
    "FAUNA",
    2,
    "Tog' archa o'rmonlari argali (tog' qo'yi), qor qoploni (irbis) va boshqa tog' hayvonlari uchun oziq va boshpana beradi. O'rmonlar kamayishi bu turlar uchun katta xavf.",
    "WWF O'zbekiston, Tog' ekotizimi, 2023",
    [
        "Suv qushlari",
        "Tog' qo'yi (argali) va qor qoploni",
        "Cho'l kaltakesaklari",
        "Dengiz balig'lari",
    ],
    1,
)

add_mcq(
    129,
    "Yo'q bo'lib ketish xavfidagi hayvonlarni saqlash uchun nima tashkil etiladi?",
    "FAUNA",
    1,
    "Tabiat qo'riqxonalari (davlat qo'riqxonalari, milliy parklar, biosfera rezervatlari) noyob tur yashash muhitini saqlaydi va inson faoliyatidan himoya qiladi.",
    "IUCN, Himoyalangan hududlar, 2023",
    ["Sanoat zavodi", "Tabiat qo'riqxonasi", "Yo'l qurilishi", "Ko'chmas mulk"],
    1,
)

add_mcq(
    130,
    "Oziq-zanjirda bitta turning yo'q bo'lishi ekotizimga qanday ta'sir qiladi?",
    "FAUNA",
    2,
    "Kaskat ta'sir (trophic cascade): bir turning yo'q bo'lishi butun oziq-zanjirni buzadi. Masalan, bo'ri yo'q bo'lsa kiyik ko'payadi, kiyik o'simliklarni qirtishlaydi, eroziya boshlanadi.",
    "Yellowstone wolflar qayta keltirilishi tadqiqoti, 2023",
    [
        "Faqat yirik hayvonlarga ta'sir qiladi",
        "Bir turning yo'q bo'lishi butun ekotizimni o'zgartirishi mumkin",
        "Faqat estetik muammo",
        "Hech qanday ta'siri yo'q",
    ],
    1,
)

add_mcq(
    131,
    "Usturt platosida noyob hayvon — Usturt qoplig'ochi (saiga antilopa/ufloni) qaysi xususiyati bilan ajraladi?",
    "FAUNA",
    3,
    "Saiga antilopa (Saiga tatarica) noyob burun tuzilishi bilan ajralib turadi — katta, haziq buruni qishda sovuq havoni isitadi. Kritik xavf ostidagi tur: 95% kamaygan.",
    "IUCN Qizil ro'yxati, Saiga tatarica, 2023",
    ["Qanotlari bor", "Noyob katta burun tuzilishi", "Dengizda yashaydi", "Tunda ko'rishi yaxshi"],
    1,
)

add_mcq(
    132,
    "Baliqlar qanday nafas oladi?",
    "FAUNA",
    1,
    "Baliqlar jabra (gill) orqali nafas oladi. Jabra suvdagi erigan kislorodni qonga o'tkazadi. Baliqlar suvdan tashqarida nafas ola olmaydi (maxsus o'pkali baliqlar bundan mustasno).",
    "Zoologiya asoslari, 2023",
    ["O'pka orqali", "Teri orqali", "Jabra orqali", "Og'iz orqali"],
    2,
)

add_mcq(
    133,
    "O'zbekistondagi 'Zarafshon' qo'riqxonasi qaysi noyob tur himoyasi uchun tashkil etilgan?",
    "FAUNA",
    2,
    "Zarafshon davlat qo'riqxonasi (1975) qunduz (Castor fiber) populyatsiyasini saqlash uchun asos solingan. Bu Markaziy Osiyodagi qunduzning so'nggi yashash joylaridan biri.",
    "O'zbekiston Ekologiya vazirligi, Qo'riqxonalar tarmog'i, 2023",
    ["Jayron", "Qunduz", "Qoplayon", "Qo'ng'ir ayiq"],
    1,
)

add_mcq(
    134,
    "Qushlar migratsiyasining asosiy sabablari nima?",
    "FAUNA",
    1,
    "Qushlar oziq yetarli bo'lgan joylarga, ko'payish uchun qulay muhitga va qishni iliq iqlimda o'tkazishga migratsiya qiladi. Mavsumiy o'zgarish asosiy omil.",
    "Ornitoilogiya asoslari, 2023",
    [
        "Oziq va yashash muhitini yaxshilash",
        "Faqat yirtqichlardan qochish",
        "O'yin-kulgu maqsadida",
        "Tasodifiy harakat",
    ],
    0,
)

add_mcq(
    135,
    "O'zbek jayroni populyatsiyasi so'nggi 50 yilda qanday o'zgargan?",
    "FAUNA",
    2,
    "Jayron populyatsiyasi ov, yashash muhitining yo'qolishi va podaning uzilishi tufayli so'nggi 50 yilda 80% dan ortiq kamaygan. Hozirda qo'riqxonalarda 10,000-15,000 ta bor.",
    "O'zbekiston Qizil kitobi, 2022; IUCN, 2023",
    [
        "Deyarli o'zgarmagan",
        "Ikki barobarga ko'paygan",
        "80% dan ortiq kamaygan",
        "To'liq yo'q bo'lib ketgan",
    ],
    2,
    article=5,
)

add_mcq(
    136,
    "Qizilqum biosfera qo'riqxonasida qaysi hayvon turlari himoyalanadi?",
    "FAUNA",
    3,
    "Qizilqum davlat biosfera qo'riqxonasida jayron, ufloni (saiga), qoraquloq (caracal), saksovul to'ti kabi cho'l turlari himoyalanadi.",
    "Qizilqum biosfera qo'riqxonasi, rasmiy ma'lumotlar, 2023",
    [
        "Qunduz va qoplayon",
        "Jayron, ufloni va qoraquluq",
        "Qo'ng'ir ayiq va bo'ri",
        "Timsoh va kayman",
    ],
    1,
)

add_mcq(
    137,
    "Biodiversitet (biologik xilma-xillik) nima?",
    "FAUNA",
    1,
    "Biodiversitet — muayyan hududdagi yoki butun Yerdagi tirik organizmlar (o'simlik, hayvon, mikroorganizm), ularning genofondlari va ekotizimlari xilma-xilligi.",
    "Biologik xilma-xillik to'g'risidagi konventsiya (CBD), 2023",
    [
        "Bitta turning ko'p bo'lishi",
        "Barcha tirik organizmlar xilma-xilligi",
        "Bir xil o'simliklarning ko'payishi",
        "Faqat noyob turlar",
    ],
    1,
)

add_mcq(
    138,
    "Hasharotlar ekotizimdagi qaysi muhim vazifalarni bajaradi?",
    "FAUNA",
    2,
    "Hasharotlar: 1) o'simliklarni changlatadi (83% o'simlik turi ularsiz ko'paymaydi), 2) chirindi va go'ngni parchalaydi, 3) oziq-zanjirda asosiy halqa vazifasini o'taydi.",
    "Entomologiya jamiyati xalqaro hisoboti, 2023",
    [
        "Faqat zararli",
        "Changlatish, tuproqni boyitish, oziq-zanjirda muhim rol",
        "Hech qanday roli yo'q",
        "Faqat noqulaylik keltirish",
    ],
    1,
)

add_mcq(
    139,
    "Global qor qoploni (irbis, snow leopard) populyatsiyasi qancha deb baholanadi?",
    "FAUNA",
    3,
    "Dunyo bo'yicha qor qoploni populyatsiyasi 4,000-6,500 ta deb taxmin qilinadi. O'zbekistonda Hisor va Pamir-Oloy tog'larida bir necha o'n ta uchraydi.",
    "Snow Leopard Trust, Global soni, 2023",
    ["100 dan kamroq", "500 dan kamroq", "4000-6500", "10,000 dan ko'proq"],
    2,
)

add_mcq(
    140,
    "Tabiat qo'riqxonasi va milliy bog' o'rtasidagi asosiy farq nima?",
    "FAUNA",
    2,
    "Tabiat qo'riqxonasida inson kirishi va faoliyati qat'iyan cheklangan (faqat ilmiy tadqiqot). Milliy bog'da esa turizm, tarbiyaviy faoliyat ruxsat etiladi.",
    "O'zbekiston Ekologiya vazirligi, Himoyalangan hududlar qonunchilig, 2023",
    [
        "Farqi yo'q",
        "Qo'riqxonaga kirish cheklangan, milliy bog'da turizm ruxsat",
        "Milliy bog' kattaroq",
        "Qo'riqxonada maxsus oziq beriladi",
    ],
    1,
)

add_mcq(
    141,
    "O'zbekistonda nechta davlat tabiat qo'riqxonasi mavjud?",
    "FAUNA",
    1,
    "O'zbekistonda 9 ta davlat tabiat qo'riqxonasi bor: Zarafshon, Nurota, Qizilqum, Badai-Tugay, Hisor, Zomin, Chatqol, Surxon va Arnasoy.",
    "O'zbekiston Ekologiya vazirligi, 2023",
    ["3 ta", "6 ta", "9 ta", "15 ta"],
    2,
    article=5,
)

# TRUE_FALSE — FAUNA
add_tf(
    142,
    "Jayron O'zbekistonda yo'q bo'lib ketish xavfi ostidagi tur hisoblanadi.",
    "FAUNA",
    1,
    "Ha, jayron O'zbekiston Qizil kitobida 'himoyaga muhtoj' tur sifatida ro'yxatda. Ularning soni so'nggi o'n yilliklarda keskin kamaygan.",
    "O'zbekiston Qizil kitobi, 5-nashr, 2022",
    True,
)

add_tf(
    143,
    "Yirtqich hayvonlar ekotizimdagi oziq-zanjirda muhim rol o'ynaydi.",
    "FAUNA",
    1,
    "Ha, yirtqichlar o'ljalar sonini boshqarib, o'simliklar va boshqa resurslarni haddan tashqari iste'mol qilinishidan saqlaydi. Ular 'kaskat ta'sir' orqali butun ekotizimni tartibga soladi.",
    "Ekologiya asoslari, 2023",
    True,
)

add_tf(
    144,
    "O'zbekiston Qizil kitobiga kiritilgan turlarning barchasini ov qilish man etilgan.",
    "FAUNA",
    2,
    "Ha, O'zbekiston qonunchiligiga ko'ra Qizil kitobdagi barcha turlarni ov qilish, tutish va sotish qat'iyan man etilgan. Buzganlar jinoiy javobgarlikka tortiladi.",
    "O'zbekiston 'Qizil kitob' to'g'risida qonun, 2002",
    True,
    article=5,
)

add_tf(
    145,
    "Hasharotlarning yo'q bo'lib ketishi o'simliklarning ko'payishiga ta'sir qilmaydi.",
    "FAUNA",
    2,
    "Yo'q! Dunyo o'simliklarining 80% dan ortig'i changlatish uchun hasharotlarga muhtoj. Ari, kapalak va boshqa changlatuvchilar yo'q bo'lsa, ko'plab o'simliklar yo'q bo'lib ketadi.",
    "FAO, Changlatuvchilar va oziq-ovqat xavfsizligi, 2023",
    False,
)

add_tf(
    146,
    "Dengiz toshbaqalari plastik sumkani meduza deb adashtirib yeyishi mumkin.",
    "FAUNA",
    3,
    "Ha, plastik sumkalar dengizda meduza kabi suzib yuradi. Toshbaqalar ularni yutishi natijasida ich-ichakda tiqilib qoladi va o'lib ketadi. Bu dengiz hayvonlari uchun katta xavf.",
    "WWF, Plastik dengiz ifloslantirishi, 2023",
    True,
)

add_tf(
    147,
    "Hayvonlarning yashash muhitini saqlash ularni himoya qilishning eng samarali usuli.",
    "FAUNA",
    1,
    "Ha, yashash muhiti yo'q bo'lsa, hatto eng yaxshi himoya choralar ham samarasiz. 'Habitat loss' global darajada biologik xilma-xillikni yo'qotishning asosiy sababi.",
    "IUCN, Biologik xilma-xillikni yo'qotish omillari, 2023",
    True,
)

# SCENARIO — FAUNA
add_scenario(
    148,
    "Qo'riqxonada 50 ta jayron bor. Himoya olib borish natijasida populyatsiya yiliga 10% o'sadi. 3 yildan keyin nechta jayron bo'ladi?",
    "FAUNA",
    2,
    "Yillik o'sish: 50 × (1.10)³ = 50 × 1.331 = 66.5 ≈ 67 ta. Geometrik o'sish kichik populyatsiyalar uchun juda muhim — har bir individ qimmatli.",
    "Populyatsion ekologiya hisob-kitobi",
    ["55 ta", "60 ta", "67 ta", "80 ta"],
    2,
    article=5,
)

add_scenario(
    149,
    "Ekotizimda bo'rilar yo'q qilingach, kiyiklar soni 3 barobarga oshdi. Kiyiklar o'simliklarni qirtishladi, tuproq eroziyasi boshlandi. Bu qanday ekologik hodisa?",
    "FAUNA",
    2,
    "Bu 'trofik kaskad' (trophic cascade) — oziq-zanjirdagi o'zgarish boshqa darajalarga tarqalishi. Yellowstoneda bo'ri qaytarilganda daryo o'zagi ham o'zgardi (ekotizim muhandisligi).",
    "William Ripple, Yellowstone bo'ri tadqiqoti, 2012; Nature, 2023",
    [
        "To'g'ridan-to'g'ri ta'sir",
        "Trofik kaskad (kaskad ta'siri)",
        "Ijobiy ta'sir",
        "Qisqa muddatli ta'sir",
    ],
    1,
)

add_scenario(
    150,
    "Saiga antilopa populyatsiyasi 1990-yilda 1,000,000 bo'lgan. 2006-yilga kelib 95% kamaygan. Nechta qolgan?",
    "FAUNA",
    3,
    "Kamaygan: 1,000,000 × 95% = 950,000. Qolgan: 1,000,000 - 950,000 = 50,000 ta. Bu iqlim o'zgarishi, ov va yashash muhitining buzilishi oqibati.",
    "IUCN, Saiga tatarica, Populyatsiya dinamikasi, 2023",
    ["5,000 ta", "50,000 ta", "100,000 ta", "500,000 ta"],
    1,
)

# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────
fixture = questions + answers
with open("fixtures/questions.json", "w", encoding="utf-8") as f:
    json.dump(fixture, f, ensure_ascii=False, indent=2)

print(f"Generated {len(questions)} questions and {len(answers)} answers")
print(f"Total entries: {len(fixture)}")
print(f"Answer PKs: 1001 to {apk - 1}")

# Validate counts
cats = {}
types = {}
diffs = {}
for q in questions:
    c = q["fields"]["category"]
    t = q["fields"]["question_type"]
    d = q["fields"]["difficulty"]
    cats[c] = cats.get(c, 0) + 1
    types[t] = types.get(t, 0) + 1
    diffs[d] = diffs.get(d, 0) + 1

print(f"\nCategories: {cats}")
print(f"Types: {types}")
print(f"Difficulties: {diffs}")
related = sum(1 for q in questions if q["fields"]["related_article"] is not None)
print(f"Questions with related_article: {related}")
