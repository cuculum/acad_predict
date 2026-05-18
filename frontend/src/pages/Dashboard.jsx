<?php
// ============================================================
//  config.php — Konfigurasi Koneksi Database
//  Versi: Perbaikan dari kode asli + penjelasan untuk dosen
// ============================================================


// ────────────────────────────────────────────────────────────
//  BAGIAN 1: DETEKSI ENVIRONMENT (LOKAL vs PRODUCTION)
//  ✅ BENAR — logika ini sudah tepat di kode asli Anda
// ────────────────────────────────────────────────────────────

if ($_SERVER['HTTP_HOST'] == 'localhost' || $_SERVER['HTTP_HOST'] == '127.0.0.1') {

    // ── Konfigurasi LOKAL ──────────────────────────────────
    define('DB_HOST', 'localhost');
    define('DB_USER', 'uxsf55g0_intantoko');
    define('DB_PASS', '300706tan');
    define('DB_NAME', 'uxsf55g0_toko_intan');
    define('BASE_URL', 'http://localhost/toko-intan/');   // ← TAMBAHAN: base URL lokal

} else {

    // ── Konfigurasi PRODUCTION (hosting) ──────────────────
    // ❌ MASALAH di kode asli: nilai placeholder 'GANTI_DENGAN_...'
    //    berbahaya jika lupa diganti sebelum upload ke hosting.
    //    Solusi: gunakan nilai nyata sejak awal, atau gunakan
    //    file .env yang tidak di-commit ke repository.
    define('DB_HOST', 'localhost');
    define('DB_USER', 'uxsf55g0_intantoko');   // ← Ganti dengan user DB di hosting Anda
    define('DB_PASS', '300706tan');             // ← Ganti dengan password DB di hosting
    define('DB_NAME', 'uxsf55g0_toko_intan');  // ← Ganti dengan nama DB di hosting
    define('BASE_URL', 'https://nama-domain-anda.com/'); // ← Ganti dengan URL hosting
}


// ────────────────────────────────────────────────────────────
//  BAGIAN 2: MEMBUAT KONEKSI DATABASE
//
//  ❌ MASALAH di kode asli:
//     Anda membungkus mysqli di dalam try-catch, tetapi
//     mysqli TIDAK melempar Exception secara default.
//     Artinya blok catch(){} tidak akan pernah terpanggil,
//     sehingga error koneksi tidak tertangkap dengan benar.
//
//  ✅ SOLUSI: Aktifkan mysqli_report() agar mysqli melempar
//     Exception, ATAU cek $conn->connect_error secara manual
//     (seperti yang sudah Anda tulis — sudah benar!),
//     tapi hapus try-catch yang tidak efektif itu.
//
//  Di bawah ini dua cara ditunjukkan sekaligus:
// ────────────────────────────────────────────────────────────

// ── Cara yang DIPERBAIKI (direkomendasikan) ────────────────

// Aktifkan agar mysqli bisa melempar Exception
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

try {
    $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

    // ✅ BENAR — pengecekan connect_error sudah ada di kode asli
    //    Dengan mysqli_report() di atas, baris ini sebenarnya
    //    sudah tidak diperlukan karena Exception otomatis dilempar,
    //    tapi tetap ditulis sebagai pengaman tambahan.
    if ($conn->connect_error) {
        die("Koneksi gagal: " . $conn->connect_error);
    }

    // ✅ BENAR — set_charset sudah ada di kode asli, bagus!
    $conn->set_charset("utf8mb4");

} catch (mysqli_sql_exception $e) {
    // ❌ Di kode asli: catch (Exception $e) — terlalu umum
    //    dan tidak akan tertangkap tanpa mysqli_report().
    //
    // ✅ PERBAIKAN: tangkap mysqli_sql_exception secara spesifik.
    //    Dengan ini, jika DB_USER/DB_PASS salah, error akan
    //    muncul dan tertangkap di sini.
    die("Koneksi database gagal: " . $e->getMessage());
}


// ────────────────────────────────────────────────────────────
//  RINGKASAN PERBAIKAN UNTUK DOSEN
// ────────────────────────────────────────────────────────────
//
//  No | Kode Asli                  | Perbaikan
//  ---+----------------------------+---------------------------
//  1  | try { new mysqli(...) }    | Tambah mysqli_report()
//     | catch (Exception $e)       | agar Exception benar-benar
//     |                            | dilempar oleh mysqli
//  ---+----------------------------+---------------------------
//  2  | 'GANTI_DENGAN_USERNAME_DB' | Ganti dengan nilai nyata
//     | (placeholder production)   | atau gunakan file .env
//  ---+----------------------------+---------------------------
//  3  | Tidak ada BASE_URL         | Tambah konstanta BASE_URL
//     |                            | untuk kemudahan routing
//  ---+----------------------------+---------------------------
//  4  | catch (Exception $e)       | Ganti dengan
//     |                            | catch (mysqli_sql_exception)
//     |                            | agar lebih spesifik
//
//  Bagian yang SUDAH BENAR di kode asli:
//  - Deteksi localhost vs production ✅
//  - Penggunaan define() untuk konstanta ✅
//  - $conn->connect_error check ✅
//  - set_charset("utf8mb4") ✅
// ────────────────────────────────────────────────────────────
?>
