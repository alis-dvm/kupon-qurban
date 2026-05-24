# 🕌 Kupon Qurban Digital v2.0
## Mushollah Ar Rohman — Perum BRI, Cepu

Aplikasi web berbasis Streamlit untuk mengelola kupon pengambilan daging qurban secara digital.
Dilengkapi **3 metode scan QR Code**, validasi petugas, log aktivitas, dan laporan otomatis.

---

## 🚀 Cara Menjalankan

### 1. Install dependensi Python
```bash
pip install -r requirements.txt
```

> ✅ **Tidak perlu sudo atau instalasi sistem apapun.**
> Fitur Foto QR menggunakan OpenCV yang otomatis terinstall via pip.

### 3. Jalankan aplikasi
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

## 📋 Fitur Lengkap

| No | Menu | Fungsi |
|----|------|--------|
| 1 | **🏠 Dashboard** | Statistik real-time, progress bar pengambilan, 10 aktivitas terakhir, log scan terbaru |
| 2 | **👥 Data Penerima** | Tambah manual, edit, hapus, import massal via CSV |
| 3 | **🎫 Generate Kupon** | Buat kupon digital otomatis 1 klik untuk semua penerima |
| 4 | **📋 Data Kupon** | Lihat semua kupon, filter, download QR Code & gambar kupon siap cetak |
| 5 | **📷 Validasi / Scan** | **3 metode scan QR** → konfirmasi pengambilan → status otomatis update |
| 6 | **📊 Laporan** | Ringkasan, export CSV, log semua aktivitas scan |
| 7 | **⚙️ Pengaturan** | Ganti password admin, info status library |

---

## 📷 3 Metode Scan QR Code

### 🎥 Tab 1 — Scan Live (Real-Time)
- Menggunakan library `streamlit-qrcode-scanner`
- Kamera aktif langsung, arahkan ke QR Code
- Hasil muncul **otomatis tanpa klik** apapun
- ✅ **Direkomendasikan** untuk petugas di lapangan (HP/tablet)

### 📸 Tab 2 — Foto QR Code
- Menggunakan `st.camera_input()` + `pyzbar`
- Klik tombol foto → sistem decode QR otomatis
- Cocok jika kamera real-time kurang stabil
- ✅ **Backup terbaik** jika Scan Live lambat

### ⌨️ Tab 3 — Input Manual
- Ketik atau tempel ID Kupon langsung
- Tersedia shortcut: pilih dari dropdown daftar kupon belum diambil
- ✅ **Fallback** jika kamera tidak tersedia sama sekali

---

## 🔄 Alur Penggunaan

```
1. Login Admin
        ↓
2. Input Data Penerima
   → Tambah manual (satu per satu)
   → atau Import CSV (massal)
        ↓
3. Generate Kupon
   → Klik "Generate Kupon Sekarang"
   → Sistem buat 1 kupon per penerima otomatis
        ↓
4. Bagikan Kupon ke Penerima
   → Download gambar kupon (siap cetak)
   → atau kirim digital via WhatsApp/media sosial
        ↓
5. Hari Pembagian — Buka menu Validasi / Scan
   → Pilih metode: Scan Live / Foto / Manual
   → Sistem tampilkan data penerima
   → Klik "Konfirmasi Pengambilan"
        ↓
6. Status otomatis berubah: Baru Dibuat → Sudah Diambil ✅
   → Tercatat di log dengan metode & nama petugas
```

---

## 📂 Format ID Kupon

```
QBN-YYYY-XXXX
│    │    └── Nomor urut 4 digit (0001, 0042, dst.)
│    └─────── Tahun otomatis (2026, 2027, dst.)
└──────────── Prefix Qurban
```

Contoh: `QBN-2026-0001`, `QBN-2026-0042`

---

## 📥 Format Import CSV

```csv
Ahmad Fauzan, 0812-3456-7890, Jl. Maju Km. 7, RT 01/RW 02
Siti Aisyah, 0813-1234-5678, Jl. Melati No. 15, RT 02/RW 03
Budi Santoso, 0814-9876-5432, Jl. Sejahtera No. 3, RT 03/RW 01
```

Kolom (tanpa baris header): `nama, no_hp, alamat, rt_rw`

---

## 📡 Log Scan

Setiap aktivitas scan tersimpan otomatis di tabel `log_scan`:

| Kolom | Keterangan |
|-------|-----------|
| `id_kupon` | ID kupon yang divalidasi |
| `aksi` | KONFIRMASI atau RESET |
| `status_sebelum` | Status sebelum aksi |
| `status_sesudah` | Status setelah aksi |
| `petugas` | Nama petugas yang melakukan scan |
| `metode` | `scan-live` / `scan-foto` / `manual` |
| `waktu` | Timestamp otomatis |

Log bisa dilihat dan diexport di menu **Laporan → Log Scan**.

---

## 🗄️ Database

Menggunakan **SQLite** (`qurban_arrohman.db`) — file lokal, tidak perlu server.

**Tabel:**
- `users` — akun admin
- `penerima` — daftar calon penerima
- `kupon` — kupon digital dengan status
- `log_scan` — riwayat semua aktivitas scan *(baru v2.0)*

---

## 📦 Dependensi

| Package | Versi Min | Fungsi |
|---------|-----------|--------|
| `streamlit` | 1.32.0 | Framework web app |
| `qrcode[pil]` | 7.4.2 | Generate QR Code |
| `Pillow` | 10.0.0 | Proses gambar kupon |
| `pandas` | 2.0.0 | Olah data tabel |
| `opencv-python-headless` | 4.8.0 | Decode QR dari foto (tanpa sudo) |
| `numpy` | 1.24.0 | Array gambar untuk OpenCV |
| `streamlit-qrcode-scanner` | 0.0.4 | Scan QR real-time |

---

## 💡 Tips Penggunaan di Lapangan

- Gunakan **HP atau tablet** untuk petugas validasi (Scan Live lebih mudah)
- Buka di browser HP, akses `http://<IP-komputer>:8501`
- Pastikan **cahaya cukup** saat scan foto
- Jika scan gagal, gunakan **Input Manual** sebagai backup
- Nama petugas diisi otomatis dari nama login admin

---

## 📞 Info

- **Mushollah:** Ar Rohman
- **Lokasi:** Perum BRI, Cepu
- **Versi:** 2.0.0
- **Changelog v2.0:** Tambah 3 metode scan QR, log_scan table, UI scan result box
- **Changelog v2.1:** Ganti pyzbar→OpenCV untuk decode QR foto (tidak butuh sudo)
