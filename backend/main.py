"""
=============================================================================
FILE   : main.py 
TUJUAN : Menunjukkan kesalahan pada kode  + versi perbaikannya
         ✅ = kode yang BENAR (mengacu pada kode punya saya)
         ❌ = kode teman yang SALAH / kurang tepat
         💬 = penjelasan kesalahan
=============================================================================
"""

# ── BAGIAN 1: IMPORT ─────────────────────────────────────────────────────────

# ❌ KODE  (SALAH):
# from utils import load_students_json, save_students_json, predict_student, analyze_ipk_target
#
# 💬 PENJELASAN KESALAHAN:
#    Teman mengimpor semua fungsi dari satu file "utils.py".
#    Padahal struktur proyek yang benar memisahkan setiap fungsi ke dalam
#    modul yang berbeda di dalam folder "utils/":
#      - utils/predictor.py     → fungsi predict_student
#      - utils/data_generator.py → fungsi save_students_json
#      - utils/ipk_target.py    → fungsi analyze_ipk_target
#    Jika file utils.py tidak ada, kode teman akan langsung error saat dijalankan.

# ✅ PERBAIKAN (mengacu kode saya):
import json
import os
import sys
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.predictor import predict_student          # ✅ modul terpisah
from utils.data_generator import save_students_json  # ✅ modul terpisah
from utils.ipk_target import analyze_ipk_target      # ✅ modul terpisah


# ── BAGIAN 2: INISIALISASI APP ────────────────────────────────────────────────

app = FastAPI(
    title="Academic Performance Prediction API",
    description="Sistem Prediksi Performa Akademik Mahasiswa",
    version="1.0.0",
)

# ❌ KODE TEMAN (KURANG LENGKAP):
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# 💬 PENJELASAN KESALAHAN:
#    Teman tidak menyertakan "allow_credentials=True".
#    Jika frontend mengirim request dengan cookie atau header Authorization,
#    server akan menolaknya karena credentials tidak diizinkan.

# ✅ PERBAIKAN:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # ✅ ditambahkan
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── BAGIAN 3: LOADING DATA ────────────────────────────────────────────────────

STUDENTS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students.json")

# ❌ KODE TEMAN (KURANG TEPAT):
# students_cache = load_students_json()
#
# 💬 PENJELASAN KESALAHAN:
#    Teman memuat data langsung di level modul (saat file diimport).
#    Masalahnya ada dua:
#    1. Jika file students.json tidak ada, program langsung crash tanpa fallback.
#    2. Tidak ada mekanisme generate data otomatis jika file belum tersedia.
#    Cara yang benar adalah menggunakan lazy-loading + auto-generate.

# ✅ PERBAIKAN: gunakan dictionary cache + auto-generate jika file tidak ada
_students_cache: dict[str, dict] = {}

def load_students() -> dict[str, dict]:
    """Load students dari JSON; generate otomatis jika file belum ada."""
    global _students_cache
    if _students_cache:
        return _students_cache  # sudah di-cache, langsung kembalikan

    if not os.path.exists(STUDENTS_JSON_PATH):
        print("students.json tidak ditemukan – generating...")
        save_students_json(STUDENTS_JSON_PATH)  # ✅ auto-generate

    with open(STUDENTS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    _students_cache = {s["nim"]: s for s in data}
    print(f"Loaded {len(_students_cache)} students.")
    return _students_cache

# ✅ Startup event untuk memuat data saat server pertama kali jalan
@app.on_event("startup")
async def startup_event():
    load_students()


# ── BAGIAN 4: MODEL PYDANTIC ──────────────────────────────────────────────────

# ❌ KODE TEMAN (SALAH – TYPE DATA MATKUL TERSULIT):
# class IPKTargetRequest(BaseModel):
#     target_ipk: float
#     kebiasaan_belajar: str
#     gaya_belajar: str
#     beban_sks_direncanakan: int
#     matkul_tersulit: str          # ← ❌ SALAH! seharusnya List[str]
#
# 💬 PENJELASAN KESALAHAN:
#    "matkul_tersulit" bertipe str, artinya hanya bisa menerima SATU mata kuliah.
#    Padahal fungsi analyze_ipk_target() mengharapkan sebuah LIST mata kuliah.
#    Jika frontend mengirim ["Matematika", "Fisika"], server akan error karena
#    tipe tidak cocok. Ini adalah kesalahan FATAL yang langsung menyebabkan crash.

# ✅ PERBAIKAN:
class IPKTargetRequest(BaseModel):
    target_ipk: float
    kebiasaan_belajar: str
    gaya_belajar: str
    beban_sks_direncanakan: int
    matkul_tersulit: List[str]    # ✅ BENAR: list of string, bisa banyak matkul


# ── BAGIAN 5: ENDPOINT /health ────────────────────────────────────────────────

# ❌ KODE TEMAN (NAMA KEY BERBEDA):
# @app.get("/health")
# def health_check():
#     return {"status": "ok", "total_mahasiswa": len(students_cache)}
#
# 💬 PENJELASAN KESALAHAN:
#    Key yang dikembalikan adalah "total_mahasiswa", padahal seharusnya
#    "total_students". Jika frontend membaca key "total_students" dan
#    server mengembalikan "total_mahasiswa", data tidak akan terbaca.

# ✅ PERBAIKAN:
@app.get("/health")
def health_check():
    students = load_students()
    return {"status": "ok", "total_students": len(students)}  # ✅ key yang benar


# ── BAGIAN 6: ENDPOINT GET /api/students ─────────────────────────────────────

# ❌ KODE TEMAN (TIGA MASALAH SEKALIGUS):
# @app.get("/api/students")
# def list_students(
#     page: int = Query(1, ge=1),
#     limit: int = Query(10, ge=1),   # ← ❌ default 10, seharusnya 20
#     prodi: Optional[str] = None,
#     search: Optional[str] = None
# ):
#     students = list(students_cache.values())
#     if prodi:
#         students = [s for s in students if s["prodi"].lower() == prodi.lower()]
#         # ↑ ❌ tidak mengecek prodi_key, sehingga filter tidak lengkap
#     if search:
#         students = [s for s in students if search.lower() in s["nama"].lower() or search in s["nim"]]
#     start = (page - 1) * limit
#     end = start + limit
#     return {
#         "page": page,
#         "limit": limit,
#         "total": len(students),
#         "data": students[start:end]   # ← ❌ key "data", seharusnya "students"
#                                       # ← ❌ tidak ada "total_pages"
#                                       # ← ❌ mengembalikan seluruh objek, bukan field ringkas
#     }
#
# 💬 PENJELASAN KESALAHAN:
#    1. Default limit=10 seharusnya 20.
#    2. Filter prodi tidak mengecek field "prodi_key", padahal data bisa
#       disimpan dengan prodi_key (contoh: "TI", "SI"). Akibatnya filter
#       tidak bekerja untuk semua kasus.
#    3. Response key "data" seharusnya "students" agar konsisten dengan
#       kontrak API yang digunakan frontend.
#    4. Tidak ada field "total_pages" padahal frontend butuh ini untuk
#       menampilkan pagination.
#    5. Mengembalikan seluruh objek student (boros bandwidth), seharusnya
#       hanya field-field ringkas yang dibutuhkan di halaman daftar.

# ✅ PERBAIKAN:
@app.get("/api/students")
def list_students(
    page: int = 1,
    limit: int = 20,                     # ✅ default 20
    prodi: Optional[str] = None,
    search: Optional[str] = None,
):
    students = load_students()
    items = list(students.values())

    if prodi:
        # ✅ cek prodi_key (uppercase) DAN prodi (lowercase) agar filter lengkap
        items = [s for s in items if s["prodi_key"].upper() == prodi.upper() or
                 s["prodi"].lower() == prodi.lower()]

    if search:
        s_lower = search.lower()
        items = [s for s in items if s_lower in s["nim"] or s_lower in s["nama"].lower()]

    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    page_items = items[start:end]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,  # ✅ ditambahkan
        "students": [                                   # ✅ key "students" bukan "data"
            {
                # ✅ hanya kembalikan field ringkas, bukan seluruh objek
                "nim": s["nim"],
                "nama": s["nama"],
                "prodi": s["prodi"],
                "prodi_key": s["prodi_key"],
                "angkatan": s["angkatan"],
                "jenis_kelamin": s["jenis_kelamin"],
                "semester_aktif": s["semester_aktif"],
                "ipk_kumulatif": s["ipk_kumulatif"],
            }
            for s in page_items
        ],
    }


# ── BAGIAN 7: ENDPOINT GET /api/student/{nim} ────────────────────────────────

# ❌ KODE TEMAN (PESAN ERROR KURANG INFORMATIF):
# @app.get("/api/student/{nim}")
# def get_student(nim: str):
#     student = students_cache.get(nim)
#     if not student:
#         raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
#     return student
#
# 💬 PENJELASAN KESALAHAN:
#    Secara fungsional hampir sama, tapi pesan error tidak menyertakan NIM
#    yang dicari. Ketika debug, pesan "Mahasiswa tidak ditemukan" tidak
#    memberi tahu NIM mana yang bermasalah.

# ✅ PERBAIKAN:
@app.get("/api/student/{nim}")
def get_student(nim: str):
    students = load_students()
    student = students.get(nim)
    if not student:
        # ✅ pesan error menyertakan NIM agar mudah di-debug
        raise HTTPException(status_code=404, detail=f"Mahasiswa dengan NIM {nim} tidak ditemukan.")
    return student


# ── BAGIAN 8: ENDPOINT GET /api/predict/{nim} ────────────────────────────────

# ❌ KODE TEMAN (DUA KESALAHAN SEKALIGUS):
# @app.get("/api/predict/{nim}")
# def predict(nim: str):
#     student = students_cache.get(nim)
#     if not student:
#         raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
#     prediction = predict_student(student)
#     return {"student": student, "prediction": prediction}  # ← ❌ struktur salah
#                                                            # ← ❌ tidak ada cek lulus
#
# 💬 PENJELASAN KESALAHAN:
#    1. Struktur response salah: teman mengembalikan nested object
#       {"student": {...}, "prediction": {...}}, padahal seharusnya flat object
#       di mana semua field student + prediksi ada di level yang sama.
#       Frontend yang mengakses "response.prediksi" akan gagal karena
#       response teman tidak punya field tersebut.
#
#    2. Tidak ada pengecekan apakah mahasiswa sudah lulus (semester_aktif >= 6).
#       Akibatnya predict_student() tetap dipanggil untuk mahasiswa yang sudah
#       lulus, padahal seharusnya langsung dikembalikan dengan status "lulus"
#       dan prediksi = null.

# ✅ PERBAIKAN:
@app.get("/api/predict/{nim}")
def predict(nim: str):
    students = load_students()
    student = students.get(nim)
    if not student:
        raise HTTPException(status_code=404, detail=f"Mahasiswa dengan NIM {nim} tidak ditemukan.")

    # ✅ siapkan base response sebagai flat object (bukan nested)
    base = {
        "nim": student["nim"],
        "nama": student["nama"],
        "prodi": student["prodi"],
        "prodi_key": student["prodi_key"],
        "angkatan": student["angkatan"],
        "jenis_kelamin": student["jenis_kelamin"],
        "semester_aktif": student["semester_aktif"],
        "ipk_kumulatif": student["ipk_kumulatif"],
        "riwayat_semester": student["riwayat_semester"],
    }

    # ✅ cek apakah mahasiswa sudah lulus (tidak perlu diprediksi lagi)
    if student.get("semester_aktif", 0) >= 6:
        base["status"] = "lulus"
        base["prediksi"] = None
        return base

    # ✅ jika masih aktif, baru panggil predict_student
    base["status"] = "aktif"
    base["prediksi"] = predict_student(student)
    return base


# ── BAGIAN 9: ENDPOINT POST /api/ipk-target/{nim} ────────────────────────────

# ❌ KODE TEMAN (DUA KESALAHAN FATAL):
# @app.post("/api/ipk-target/{nim}")
# def ipk_target(nim: str, request: IPKTargetRequest):
#     student = students_cache.get(nim)
#     if not student:
#         raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
#     analysis = analyze_ipk_target(nim, request)   # ← ❌ signature SALAH
#     return analysis
#
# 💬 PENJELASAN KESALAHAN:
#    1. Signature pemanggilan analyze_ipk_target() SALAH.
#       Teman memanggil: analyze_ipk_target(nim, request)
#       Seharusnya     : analyze_ipk_target(student, prediksi, target_ipk,
#                                           kebiasaan_belajar, gaya_belajar,
#                                           beban_sks, matkul_tersulit)
#       Ini adalah error FATAL — program pasti crash karena jumlah dan tipe
#       argumen tidak cocok dengan fungsi yang didefinisikan di utils/ipk_target.py.
#
#    2. Tidak ada langkah memanggil predict_student() terlebih dahulu.
#       Fungsi analyze_ipk_target() membutuhkan data prediksi (hasil dari
#       predict_student) sebagai salah satu parameternya. Tanpa ini,
#       analisis target IPK tidak akan berjalan dengan benar.

# ✅ PERBAIKAN:
@app.post("/api/ipk-target/{nim}")
def ipk_target(nim: str, req: IPKTargetRequest):
    students = load_students()
    student = students.get(nim)
    if not student:
        raise HTTPException(status_code=404, detail=f"Mahasiswa dengan NIM {nim} tidak ditemukan.")

    # ✅ Langkah 1: dapatkan prediksi terlebih dahulu
    prediksi = predict_student(student)

    # ✅ Langkah 2: gunakan prediksi + data request untuk analisis target IPK
    #    dengan parameter yang sesuai signature fungsi analyze_ipk_target()
    result = analyze_ipk_target(
        student=student,
        prediksi=prediksi,
        target_ipk=req.target_ipk,
        kebiasaan_belajar=req.kebiasaan_belajar,
        gaya_belajar=req.gaya_belajar,
        beban_sks=req.beban_sks_direncanakan,
        matkul_tersulit=req.matkul_tersulit,
    )
    return result


# ── BAGIAN 10: ENTRYPOINT ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)


# =============================================================================
# RINGKASAN KESALAHAN KODE TEMAN
# =============================================================================
#
#  No  | Lokasi                        | Jenis Kesalahan       | Dampak
# -----|-------------------------------|-----------------------|------------------
#  1   | Import utils                  | Struktur modul salah  | Error saat import
#  2   | CORS middleware               | allow_credentials     | Request ditolak
#  3   | Loading data                  | Tidak ada fallback    | Crash jika file
#      |                               | auto-generate         | JSON tidak ada
#  4   | IPKTargetRequest.matkul       | str → List[str]       | Error runtime
#  5   | /health response key          | "total_mahasiswa"     | Frontend tidak baca
#  6   | /api/students default limit   | 10 → 20               | Tampilan berbeda
#  7   | /api/students filter prodi    | Tidak cek prodi_key   | Filter tidak lengkap
#  8   | /api/students response        | Key "data" + tidak    | Frontend tidak baca
#      |                               | ada total_pages       |
#  9   | /api/predict response         | Nested bukan flat     | Frontend tidak baca
#  10  | /api/predict logika lulus     | Tidak ada cek lulus   | Fungsionalitas hilang
#  11  | /api/ipk-target signature     | Parameter salah       | CRASH (fatal error)
#  12  | /api/ipk-target predict step  | Tidak ada predict dulu| Analisis tidak akurat
#
# =============================================================================
