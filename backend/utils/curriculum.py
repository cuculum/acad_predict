# =====================================================
# DATA PRODI
# =====================================================

PRODI_LIST = {
    "TI": {
        "name": "Teknologi Informasi",
        # SALAH LAMA:
        # prodi_code memakai 100,110,dll
        # Sedangkan Zein memakai 024,025,dll
        # sehingga pembacaan NIM tidak sama

        # PERBAIKAN:
        "prodi_code": "024"
    },

    "AK": {
        "name": "Akuntansi",
        "prodi_code": "025"
    },

    "TM": {
        "name": "Teknik Mesin",
        "prodi_code": "026"
    },

    "AP": {
        "name": "Administrasi Perkantoran",
        "prodi_code": "027"
    }
}


# =====================================================
# FUNGSI MEMBUAT DATA MATA KULIAH
# =====================================================

def generate_courses(prefix, semester, jumlah_wajib, jumlah_pilihan):

    courses = []

    # =================================================
    # WAJIB
    # =================================================

    for i in range(1, jumlah_wajib + 1):

        # CODING LAMA:
        # semua SKS wajib = 3
        # padahal di Zein ada 1 SKS dan 2 SKS

        # PERBAIKAN:
        # dibuat bervariasi agar mirip Zein
        if i % 2 == 0:
            sks = 2
        else:
            sks = 1

        course = {
            "kode": prefix + str(semester) + str(i).zfill(2),

            # CODING LAMA:
            # nama masih generic

            # PERBAIKAN:
            # tetap sederhana tapi lebih realistis
            "nama": "Mata Kuliah Wajib " + str(semester) + "-" + str(i),

            "sks": sks,
            "wajib": True
        }

        courses.append(course)

    # =================================================
    # PILIHAN
    # =================================================

    for i in range(1, jumlah_pilihan + 1):

        # CODING LAMA:
        # semua pilihan = 2 SKS

        # PERBAIKAN:
        # dibuat campuran 1 dan 2 SKS seperti Zein
        if i % 3 == 0:
            sks = 1
        else:
            sks = 2

        course = {
            "kode": prefix + str(semester) + "P" + str(i).zfill(2),

            "nama": "Mata Kuliah Pilihan " + str(semester) + "-" + str(i),

            "sks": sks,
            "wajib": False
        }

        courses.append(course)

    return courses


# =====================================================
# MEMBANGUN CURRICULUM
# =====================================================

CURRICULUM = {}

for prodi_key in PRODI_LIST:

    prodi_data = PRODI_LIST[prodi_key]

    CURRICULUM[prodi_key] = {
        "name": prodi_data["name"],
        "prodi_code": prodi_data["prodi_code"],
        "semesters": {}
    }

    for semester in range(1, 7):

        # =================================================
        # PENENTUAN JUMLAH MATKUL
        # =================================================

        # CODING KAMU:
        # jumlah matkul sudah benar konsepnya

        # PERBAIKAN:
        # disamakan mendekati Zein
        # semester awal lebih banyak wajib

        if semester == 1:
            jumlah_wajib = 8
            jumlah_pilihan = 10

        elif semester == 2:
            jumlah_wajib = 6
            jumlah_pilihan = 10

        elif semester == 3:
            jumlah_wajib = 6
            jumlah_pilihan = 12

        elif semester == 4:
            jumlah_wajib = 5
            jumlah_pilihan = 25

        elif semester == 5:
            jumlah_wajib = 4
            jumlah_pilihan = 13

        else:
            jumlah_wajib = 3
            jumlah_pilihan = 11

        courses = generate_courses(
            prodi_key,
            semester,
            jumlah_wajib,
            jumlah_pilihan
        )

        # =================================================
        # KHUSUS SEMESTER 6
        # =================================================

        # CODING KAMU:
        # sudah bagus karena ada override TA

        if semester == 6:

            courses[0] = {
                "kode": prodi_key + "601",

                # CODING LAMA:
                # Tugas Akhir = 6 SKS

                # PERBAIKAN:
                # Zein memakai 2 SKS
                "nama": "Tugas Akhir",
                "sks": 2,
                "wajib": True
            }

            courses[1] = {
                "kode": prodi_key + "602",

                # CODING LAMA:
                # Kerja Praktek = 3 SKS

                # PERBAIKAN:
                # Zein memakai 2 SKS
                "nama": "Kerja Praktik",
                "sks": 2,
                "wajib": True
            }

            courses[2] = {
                "kode": prodi_key + "603",

                "nama": "Seminar Hasil",

                # PERBAIKAN:
                # Zein memakai 2 SKS
                "sks": 2,
                "wajib": True
            }

        CURRICULUM[prodi_key]["semesters"][semester] = courses


# =====================================================
# FUNGSI UTAMA
# =====================================================

def get_wajib_courses(prodi_key, semester) -> list:

    # CODING LAMA:
    # memakai loop manual

    # PERBAIKAN:
    # memakai list comprehension seperti Zein
    courses = CURRICULUM[prodi_key]["semesters"].get(semester, [])

    return [c for c in courses if c["wajib"]]


def get_pilihan_courses(prodi_key, semester) -> list:

    courses = CURRICULUM[prodi_key]["semesters"].get(semester, [])

    return [c for c in courses if not c["wajib"]]


def get_prodi_key(nim: str) -> str:

    # CODING KAMU:
    # sudah benar konsep slicing NIM

    kode = nim[2:5]

    # PERBAIKAN:
    # memakai dictionary agar lebih efisien

    PRODI_CODE_MAP = {
        "024": "TI",
        "025": "AK",
        "026": "TM",
        "027": "AP"
    }

    return PRODI_CODE_MAP.get(kode, "TI")


# =====================================================
# TOTAL SKS SEMESTER
# =====================================================

# CODING KAMU:
# fungsi ini belum ada

# PERBAIKAN:
# ditambahkan agar sama seperti Zein

def get_semester_sks(prodi_key, semester):

    courses = CURRICULUM[prodi_key]["semesters"].get(semester, [])

    return sum(c["sks"] for c in courses)


def get_wajib_sks(prodi_key, semester):

    wajib = get_wajib_courses(prodi_key, semester)

    return sum(c["sks"] for c in wajib)


# =====================================================
# MAX SKS BERDASARKAN IPK
# =====================================================

def get_max_sks_by_ipk(ipk, semester) -> int:

    # CODING KAMU:
    # belum ada kondisi semester 1

    # PERBAIKAN:
    # semester 1 default 20 SKS

    if semester == 1:
        return 20

    # CODING LAMA:
    # tidak ada kategori 18 SKS

    # PERBAIKAN:
    # disamakan dengan Zein

    if ipk >= 3.5:
        return 24

    elif ipk >= 3.0:
        return 22

    elif ipk >= 2.5:
        return 20

    else:
        return 18


# =====================================================
# PREREQUISITES
# =====================================================

# CODING KAMU:
# prerequisite masih sedikit

# PERBAIKAN:
# dipisah jadi variabel global seperti Zein

PREREQUISITES = {

    "TI20101": ["TI10101"],
    "TI30101": ["TI20101"],

    "AK20101": ["AK10101"],
    "AK30101": ["AK20101"],

    "TM20101": ["TM10101"],
    "TM30101": ["TM20101"],

    "AP20101": ["AP10101"],
    "AP30101": ["AP20101"],
}


def validate_prerequisites(kode, completed) -> tuple[bool, list]:

    if kode not in PREREQUISITES:
        return True, []

    required = PREREQUISITES[kode]

    missing = []

    for req in required:

        if req not in completed:
            missing.append(req)

    return len(missing) == 0, missing


# =====================================================
# GET COMPLETED COURSES
# =====================================================

def get_completed_courses(riwayat) -> list:

    # CODING KAMU:
    # hanya cek lulus True/False

    # KELEMAHAN:
    # tidak mempertimbangkan nilai huruf

    # PERBAIKAN:
    # disamakan konsep Zein

    grade_order = ["A", "AB", "B", "BC", "C", "D", "E"]

    completed = []

    for item in riwayat:

        nilai = item.get("nilai_huruf", "E")

        if nilai in grade_order:

            if grade_order.index(nilai) <= grade_order.index("D"):

                completed.append(item["kode"])

    return completed
