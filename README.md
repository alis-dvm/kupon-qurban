# 🕌 Kupon Qurban Digital – Mushollah Ar Rohman, Perum BRI, Cepu

Aplikasi web untuk mengelola kupon pengambilan daging qurban secara digital,
dilengkapi QR Code, validasi petugas, dan laporan otomatis.

---

## 🚀 Cara Menjalankan

### 1. Install dependensi

```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser di: **http://localhost:8501**

---

## 🔑 Login Default

| Username | Password  |
|----------|-----------|
| `admin`  | `admin123`|

> Segera ganti password setelah login pertama di menu **Pengaturan**.

---

## 📋 Fitur Aplikasi

| No | Menu | Fungsi |
|----|------|--------|
| 1 | **Dashboard** | Statistik real-time, progress pengambilan, aktivitas terbaru |
| 2 | **Data Penerima** | Tambah, edit, hapus, import CSV penerima kupon |
| 3 | **Generate Kupon** | Buat kupon digital otomatis untuk semua penerima |
| 4 | **Data Kupon** | Lihat semua kupon, download QR Code & gambar kupon siap cetak |
| 5 | **Validasi / Scan** | Input ID Kupon manual → konfirmasi pengambilan |
| 6 | **Laporan** | Ringkasan & export data CSV |
| 7 | **Pengaturan** | Ganti password admin |

---

## 🔄 Alur Penggunaan

```
Login Admin
    ↓
Input Data Penerima (manual / import CSV)
    ↓
Generate Kupon (otomatis — 1 kupon per penerima)
    ↓
Cek Data Kupon → Download / Cetak / Kirim Digital
    ↓
Hari Pembagian: Buka menu Validasi / Scan
    ↓
Input ID Kupon → Cari → Konfirmasi Pengambilan
    ↓
Status otomatis berubah: Baru Dibuat → Sudah Diambil ✅
```

---

## 📂 Format ID Kupon

```
QBN-YYYY-XXXX
QBN  = Qurban
YYYY = Tahun (otomatis)
XXXX = Nomor urut 4 digit
```

Contoh: `QBN-2026-0001`, `QBN-2026-0042`

---

## 📥 Format Import CSV

```
Ahmad Fauzan, 0812-3456-7890, Jl. Maju Km. 7, RT 01/RW 02
Siti Aisyah, 0813-1234-5678, Jl. Melati No. 15, RT 02/RW 03
Budi Santoso, 0814-9876-5432, Jl. Sejahtera No. 3, RT 03/RW 01
```

Kolom: `nama, no_hp, alamat, rt_rw` (tanpa baris header)

---

## 🗄️ Database

Menggunakan **SQLite** (`qurban_arrohman.db`) — file lokal, tidak perlu konfigurasi server.

---

## 📞 Info

- **Mushollah:** Ar Rohman
- **Lokasi:** Perum BRI, Cepu
- **Versi:** 1.0.0
