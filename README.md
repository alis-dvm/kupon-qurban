# 🕌 Kupon Qurban Digital
## Mushollah Ar Rohman — Perum BRI, Cepu

Aplikasi web berbasis **Streamlit** untuk mengelola kupon pengambilan daging qurban secara digital.
Dilengkapi 3 metode scan QR Code, kategori penerima, validasi petugas, log aktivitas, dan laporan otomatis.

**Versi saat ini: `v2.3.0`**

---

## 🚀 Cara Menjalankan

### 1. Install dependensi Python
```bash
pip install -r requirements.txt
```

> ✅ **Tidak perlu `sudo` atau instalasi sistem apapun.**
> Fitur Foto QR menggunakan OpenCV yang otomatis terinstall via pip.

### 2. Jalankan aplikasi
```bash
streamlit run app.py
```

Buka browser di: **http://localhost:8501**

---

## 🔑 Login Default

| Username | Password   |
|----------|------------|
| `admin`  | `admin123` |

> Segera ganti password setelah login pertama di menu **Pengaturan**.

---

## 📋 Fitur Lengkap

| No | Menu | Fungsi |
|----|------|--------|
| 1 | **🏠 Dashboard** | Statistik real-time, progress bar pengambilan, 10 aktivitas terakhir, log scan terbaru |
| 2 | **👥 Data Penerima** | Tambah manual dengan kategori, edit, hapus, import massal via CSV |
| 3 | **🎫 Generate Kupon** | Buat kupon digital otomatis 1 klik untuk semua penerima |
| 4 | **📋 Data Kupon** | Lihat semua kupon, filter status, download QR Code & gambar kupon siap cetak |
| 5 | **📷 Validasi / Scan** | 3 metode scan QR → konfirmasi pengambilan → status otomatis terupdate |
| 6 | **📊 Laporan** | Ringkasan statistik, export CSV, log semua aktivitas scan |
| 7 | **⚙️ Pengaturan** | Ganti password admin, info status library scanner |

---

## 🏷️ Kategori Penerima

Setiap penerima dapat diberi salah satu kategori berikut:

| Kategori | Keterangan |
|----------|-----------|
| **Shohibul Qurban** | Orang yang berkurban / pemilik hewan qurban |
| **Warga** | Warga sekitar (default) |
| **Panitia** | Anggota panitia qurban |
| **Lainnya** | Kategori custom — bisa diisi bebas (contoh: Muallaf, Dhuafa, dll.) |

Kategori tampil di tabel daftar penerima, form tambah, form edit, dan kolom CSV.

---

## 📷 3 Metode Scan QR Code

### 🎥 Tab 1 — Scan Live (Real-Time)
- Menggunakan library `streamlit-qrcode-scanner`
- Kamera aktif langsung, arahkan ke QR Code
- Hasil muncul **otomatis tanpa klik** apapun
- ✅ **Direkomendasikan** untuk petugas di lapangan (HP/tablet)

### 📸 Tab 2 — Foto QR Code
- Menggunakan `st.camera_input()` + OpenCV (`cv2.QRCodeDetector`)
- Klik tombol foto → sistem decode QR otomatis
- Jika QR kecil, otomatis coba ulang dengan gambar diperbesar 2×
- ✅ **Backup terbaik** jika Scan Live kurang stabil

### ⌨️ Tab 3 — Input Manual
- Ketik atau tempel ID Kupon langsung
- Shortcut: pilih dari dropdown daftar kupon yang belum diambil
- ✅ **Fallback** jika kamera tidak tersedia sama sekali

---

## 🔄 Alur Penggunaan

```
1. Login Admin
        ↓
2. Input Data Penerima
   → Tambah manual satu per satu (dengan kategori)
   → atau Import CSV massal (kolom kategori opsional)
        ↓
3. Generate Kupon
   → Klik "Generate Kupon Sekarang"
   → Sistem membuat 1 kupon per penerima secara otomatis
        ↓
4. Bagikan Kupon ke Penerima
   → Download gambar kupon (siap cetak / kirim digital via WhatsApp)
        ↓
5. Hari Pembagian — Buka menu Validasi / Scan
   → Pilih metode: Scan Live / Foto / Manual
   → Sistem tampilkan data & status kupon
   → Klik "Konfirmasi Pengambilan"
        ↓
6. Status otomatis berubah: Baru Dibuat → Sudah Diambil ✅
   → Tercatat di log: waktu, petugas, metode scan
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
Ahmad Fauzan, 0812-3456-7890, Jl. Maju Km. 7, RT 01/RW 02, Shohibul Qurban
Siti Aisyah, 0813-1234-5678, Jl. Melati No. 15, RT 02/RW 03, Warga
Budi Santoso, 0814-9876-5432, Jl. Sejahtera No. 3, RT 03/RW 01, Panitia
Dhuafa RT04, 0815-0000-1111, Jl. Damai No. 7, RT 04/RW 02, Dhuafa
```

Kolom (tanpa baris header): `nama, no_hp, alamat, rt_rw, kategori`

> Kolom `kategori` bersifat **opsional**. Jika tidak diisi, default otomatis **Warga**.

---

## 📡 Log Scan

Setiap aktivitas scan tersimpan otomatis di tabel `log_scan`:

| Kolom | Keterangan |
|-------|-----------|
| `id_kupon` | ID kupon yang divalidasi |
| `aksi` | `KONFIRMASI` atau `RESET` |
| `status_sebelum` | Status sebelum aksi dilakukan |
| `status_sesudah` | Status setelah aksi dilakukan |
| `petugas` | Nama petugas yang melakukan aksi |
| `metode` | `scan-live` / `scan-foto` / `manual` |
| `waktu` | Timestamp otomatis (datetime lokal) |
| `catatan` | Catatan opsional dari petugas |

Log bisa dilihat dan diexport CSV di menu **Laporan → Log Scan**.

---

## 🗄️ Database

Menggunakan **SQLite** (`qurban_arrohman.db`) — file lokal, tidak perlu server atau koneksi internet.

| Tabel | Keterangan |
|-------|-----------|
| `users` | Akun admin (username, password hash, role) |
| `penerima` | Data penerima kupon (nama, HP, alamat, RT/RW, **kategori**) |
| `kupon` | Kupon digital dengan status pengambilan |
| `log_scan` | Riwayat semua aktivitas validasi/scan |

> Migrasi kolom `kategori` berjalan **otomatis** saat aplikasi pertama kali dijalankan. Data lama tidak hilang.

---

## 📦 Dependensi

| Package | Versi Min | Fungsi |
|---------|-----------|--------|
| `streamlit` | 1.32.0 | Framework web app |
| `qrcode[pil]` | 7.4.2 | Generate QR Code |
| `Pillow` | 10.0.0 | Proses & render gambar kupon |
| `pandas` | 2.0.0 | Olah data tabel & CSV |
| `opencv-python-headless` | 4.8.0 | Decode QR dari foto (tanpa sudo) |
| `numpy` | 1.24.0 | Array gambar untuk OpenCV |
| `streamlit-qrcode-scanner` | 0.0.4 | Komponen scan QR real-time |

---

## 💡 Tips Penggunaan di Lapangan

- Gunakan **HP atau tablet** untuk petugas validasi — Scan Live lebih praktis
- Akses dari HP: buka browser → ketik `http://<IP-komputer>:8501`
- Pastikan **cahaya cukup** saat menggunakan Foto QR agar terbaca akurat
- Jika scan gagal 2× berturut-turut, alihkan ke **Input Manual**
- Nama petugas otomatis terisi dari nama akun yang login
- Tombol **Logout** berwarna merah saat hover — klik jika selesai bertugas

---

## ⚠️ Catatan: Pesan "sudo is disabled"

Jika muncul pesan **"Sudo is disabled on this machine"**, **abaikan saja** —
tidak perlu menjalankan perintah `sudo apt-get install libzbar0`.
Aplikasi ini menggunakan **OpenCV** untuk decode QR foto,
yang terinstall otomatis via `pip install -r requirements.txt` tanpa perlu sudo.

---

## 📜 Changelog

### v2.3.0 — 24 Mei 2026
**Revisi UI Sidebar & Tambah Kategori Penerima**
- ✨ **[Baru]** Field **Kategori Penerima** di Data Penerima
  - Pilihan: Shohibul Qurban, Warga, Panitia, Lainnya
  - Jika pilih "Lainnya" → muncul field teks untuk isi kategori sendiri (custom)
  - Tampil di tabel daftar, form tambah, form edit, dan kolom CSV
  - Migrasi database otomatis — data lama tidak hilang
- 🐛 **[Fix]** Sidebar toggle button (panah collapse/expand) kini terlihat jelas
  - Diberi warna biru dengan border putih; hover menjadi biru tua
  - Bisa diklik untuk **membuka kembali** sidebar setelah ditutup
- 🐛 **[Fix]** Tombol Logout kini terlihat jelas dan mencolok
  - Kotak info user (nama + label "Logged in as") di atas tombol logout
  - Tombol dengan border putih; hover berubah **merah** sebagai sinyal keluar
- ✨ **[Baru]** Kolom `kategori` ikut tampil di tabel Data Kupon

---

### v2.2.0 — 24 Mei 2026
**Perbaikan Bug Dashboard**
- 🐛 **[Fix]** Error DeltaGenerator muncul di bawah tulisan "Belum ada" di Dashboard
  - Penyebab: ternary expression `st.X() if cond else st.Y()` mengembalikan objek DeltaGenerator
  - Solusi: diganti ke blok `if/else` biasa pada bagian "10 Pengambilan Terakhir" dan "Log Scan Terbaru"

---

### v2.1.0 — 24 Mei 2026
**Hapus Ketergantungan `sudo`**
- 🔧 **[Ubah]** Ganti `pyzbar` (butuh `sudo apt install libzbar0`) → **OpenCV** sebagai decoder QR utama
  - `pyzbar` tetap sebagai fallback opsional jika sudah terinstall
  - Decode QR foto kini otomatis mencoba 2× (normal + gambar diperbesar 2×) untuk akurasi lebih baik
- 🔧 **[Ubah]** `requirements.txt` diperbarui: tambah `opencv-python-headless`, hapus `pyzbar` dari wajib
- 📝 **[Docs]** README ditambah catatan "sudo is disabled" dan panduan install yang lebih jelas

---

### v2.0.0 — 23 Mei 2026
**Fitur Scan QR Code & Log Aktivitas**
- ✨ **[Baru]** Menu **Validasi / Scan** dengan 3 metode:
  - 🎥 **Scan Live** — real-time via `streamlit-qrcode-scanner`
  - 📸 **Foto QR** — ambil foto kamera → decode otomatis via `pyzbar`
  - ⌨️ **Input Manual** — ketik ID Kupon + shortcut dropdown belum diambil
- ✨ **[Baru]** Tabel `log_scan` — rekam semua aksi KONFIRMASI & RESET beserta metode, petugas, waktu
- ✨ **[Baru]** Tab **Log Scan** di menu Laporan — bisa filter by metode & export CSV
- ✨ **[Baru]** Dashboard: panel "Log Scan Terbaru" (10 log terakhir)
- ✨ **[Baru]** Fungsi `_render_kupon_detail_and_confirm()` — shared helper antar semua tab scan
- ✨ **[Baru]** Scan result box — tampilan ID kupon terdeteksi yang jelas & berwarna
- 🔧 **[Ubah]** `db_konfirmasi()` & `db_reset_kupon()` kini otomatis catat ke `log_scan`
- 🎨 **[UI]** CSS tambahan: `.scan-box`, `.scan-result-box`, `.scan-id`, `.alert-info`
- 📝 **[Docs]** README diperbarui dengan panduan 3 metode scan dan tabel log_scan

---

### v1.0.0 — 23 Mei 2026
**Rilis Pertama**
- ✨ **[Baru]** Sistem login admin dengan autentikasi password (SHA-256 hash)
- ✨ **[Baru]** Menu **Dashboard** — statistik: total penerima, kupon, sudah/belum diambil, progress bar
- ✨ **[Baru]** Menu **Data Penerima** — tambah manual, edit, hapus, import CSV
- ✨ **[Baru]** Menu **Generate Kupon** — buat kupon otomatis format `QBN-YYYY-XXXX`
- ✨ **[Baru]** Menu **Data Kupon** — lihat daftar, filter, download QR Code & gambar kupon
- ✨ **[Baru]** Gambar kupon siap cetak (680×380px) dengan nama, ID, dan QR Code berwarna
- ✨ **[Baru]** Menu **Validasi** — input manual ID Kupon → konfirmasi pengambilan
- ✨ **[Baru]** Menu **Laporan** — ringkasan & export CSV
- ✨ **[Baru]** Menu **Pengaturan** — ganti password admin
- ✨ **[Baru]** Database SQLite lokal (`qurban_arrohman.db`) — 3 tabel: users, penerima, kupon
- 🎨 **[UI]** Desain sidebar biru gradien, metric cards warna-warni, badge status
- 📝 **[Docs]** README awal dengan panduan instalasi dan alur penggunaan

---

## 📞 Info Aplikasi

| | |
|---|---|
| **Mushollah** | Ar Rohman |
| **Lokasi** | Perum BRI, Cepu |
| **Versi** | 2.3.0 |
| **Database** | SQLite (lokal) |
| **Framework** | Streamlit |
