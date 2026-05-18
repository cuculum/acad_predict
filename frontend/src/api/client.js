// ============================================================
// CLIENT.JS — API Logic (Versi Diperbaiki, referensi: api.js Zein)
// ============================================================

import axios from "axios";

// ✅ SAMA — Cara baca env variable dan fallback URL sudah benar
const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8001";

// ✅ SAMA — axios.create() dengan baseURL dan timeout sudah benar
// ❌ BEDA — Kamu tidak menyertakan headers 'Content-Type': 'application/json'
// Ini penting agar POST request (postIPKTarget) bisa diterima backend dengan benar
const apiClient = axios.create({
  baseURL,
  timeout: 15000,
  // ❌ MILIKMU: tidak ada headers → bisa menyebabkan POST request gagal
  // ✅ PERBAIKAN: tambahkan headers berikut seperti milik Zein
  headers: {
    "Content-Type": "application/json",
  },
});

// ✅ SAMA — Struktur interceptors.response sudah benar (ada handler sukses & error)
apiClient.interceptors.response.use(
  (response) => {
    // ✅ SAMA — langsung return response.data (unwrap data dari axios)
    return response.data;
  },
  (error) => {
    // ✅ SAMA — urutan prioritas pesan error sudah benar
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      // ❌ MILIKMU: fallback "Unknown error"
      // ✅ PERBAIKAN: ganti menjadi "Terjadi kesalahan pada server." agar konsisten dengan Zein
      "Terjadi kesalahan pada server.";

    // ❌ MILIKMU: return Promise.reject(message) — menolak dengan STRING biasa
    // ✅ PERBAIKAN: harus return Promise.reject(new Error(message)) — menolak dengan objek Error
    // Kenapa penting? Karena objek Error punya .stack trace untuk debugging,
    // dan komponen React biasanya mengecek error.message, bukan string langsung
    return Promise.reject(new Error(message));
  }
);

// =============================================================
// API FUNCTIONS — Perbaikan pada endpoint URL
// =============================================================

// ❌ MILIKMU: '/students/${nim}' → path salah, tidak ada prefix /api/
// ✅ PERBAIKAN: '/api/student/${nim}' — sesuai route backend milik Zein
// Catatan: 'student' (singular), bukan 'students' (plural)
export const getStudent = (nim) => {
  // return apiClient.get(`/students/${nim}`); // ❌ LAMA (salah path)
  return apiClient.get(`/api/student/${nim}`); // ✅ BENAR
};

// ❌ MILIKMU: '/predict/${nim}' → path salah, tidak ada prefix /api/
// ✅ PERBAIKAN: '/api/predict/${nim}'
export const getPredict = (nim) => {
  // return apiClient.get(`/predict/${nim}`); // ❌ LAMA (salah path)
  return apiClient.get(`/api/predict/${nim}`); // ✅ BENAR
};

// ❌ MILIKMU: '/students' → path salah, tidak ada prefix /api/
// ✅ PERBAIKAN: '/api/students'
// ✅ SAMA — penggunaan { params } untuk query string sudah benar
// ❌ BEDA — Kamu tidak memberi default value params = {}
// Zein menulis (params = {}) agar tidak error jika dipanggil tanpa argumen
export const getStudents = (params = {}) => {
  // return apiClient.get("/students", { params }); // ❌ LAMA (salah path)
  return apiClient.get("/api/students", { params }); // ✅ BENAR
};

// ✅ SAMA — endpoint '/health' sudah benar, tidak perlu prefix /api/
export const getHealth = () => {
  return apiClient.get("/health"); // ✅ BENAR
};

// ❌ MILIKMU: '/students/${nim}/ipk-target' → path salah, tidak ada prefix /api/
// ✅ PERBAIKAN: '/api/ipk-target/${nim}' — struktur path juga berbeda, ikuti milik Zein
export const postIPKTarget = (nim, payload) => {
  // return apiClient.post(`/students/${nim}/ipk-target`, payload); // ❌ LAMA (salah path & struktur)
  return apiClient.post(`/api/ipk-target/${nim}`, payload); // ✅ BENAR
};

export default apiClient;

// ============================================================
// RINGKASAN PERBEDAAN (untuk laporan ke dosen):
// ============================================================
//
// No | Bagian                  | Milikmu (❌)                        | Milik Zein (✅)
// ---|-------------------------|-------------------------------------|------------------------------------
// 1  | axios.create headers    | Tidak ada                           | Ada 'Content-Type': 'application/json'
// 2  | Promise.reject          | reject(message) → String            | reject(new Error(message)) → Error object
// 3  | Fallback error message  | "Unknown error"                     | "Terjadi kesalahan pada server."
// 4  | getStudent endpoint     | /students/:nim                      | /api/student/:nim
// 5  | getPredict endpoint     | /predict/:nim                       | /api/predict/:nim
// 6  | getStudents endpoint    | /students                           | /api/students
// 7  | getStudents default arg | params (tanpa default)              | params = {} (ada default value)
// 8  | postIPKTarget endpoint  | /students/:nim/ipk-target           | /api/ipk-target/:nim
// ============================================================
