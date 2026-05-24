# 🕌 Kupon Qurban Digital
## Mushollah Ar Rohman — Perum BRI, Cepu

Aplikasi web berbasis **Streamlit** untuk mengelola kupon pengambilan daging qurban secara digital.
Dilengkapi 3 metode scan QR Code, kategori penerima, jam pengambilan, validasi petugas, log aktivitas, dan laporan otomatis.

**Versi saat ini: `v2.5.0`**

---

## 🚀 Cara Menjalankan

### 1. Install dependensi Python
```bash
pip install -r requirements.txt
```

> ✅ **Tidak perlu `sudo` atau instalasi sistem apapun.**
> Fitur Foto QR menggunakan OpenCV yang terinstall otomatis via pip.

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
| 1 | **🏠 Dashboard** | Statistik real-time, progress bar, 10 pengambilan terakhir (+ tanggal & jam), log scan terbaru |
| 2 | **👥 Data Penerima** | Tambah manual dengan kategori, edit, hapus, import massal via CSV |
| 3 | **🎫 Generate Kupon** | Buat kupon digital otomatis 1 klik untuk semua penerima |
| 4 | **📋 Data Kupon** | Lihat daftar, filter, kolom **Tgl Pengambilan** & **Jam** terpisah, download QR & gambar kupon |
| 5 | **📷 Validasi / Scan** | 3 metode scan QR → konfirmasi pengambilan → status & waktu otomatis terupdate |
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

Kategori tampil di: tabel daftar penerima, form tambah, form edit, tabel data kupon, dan kolom CSV.

---

## 🕐 Kolom Jam Pengambilan

Waktu pengambilan (`diambil_at`) ditampilkan secara **terpisah** di seluruh UI:

| Tampilan | Format |
|----------|--------|
| **Tgl Pengambilan** | `2026-05-24` |
| **Jam** | `22:56` (WIB) |

Diterapkan di:
- Tabel **Data Kupon** — kolom Tgl Pengambilan + Jam
- **Card detail kupon** — 📅 Tanggal dan 🕐 Jam WIB
- **Popup validasi scan** — saat kupon sudah diambil
- **Dashboard** — kolom Tanggal + Jam di tabel "10 Pengambilan Terakhir"

> Kupon yang **belum diambil** menampilkan `—` di kolom Tgl & Jam (tidak error).

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
   → Tambah manual satu per satu (isi nama, HP, alamat, RT/RW, kategori)
   → atau Import CSV massal (kolom kategori opsional)
        ↓
3. Generate Kupon
   → Klik "Generate Kupon Sekarang"
   → Sistem membuat 1 kupon per penerima secara otomatis (format QBN-YYYY-XXXX)
        ↓
4. Bagikan Kupon ke Penerima
   → Download gambar kupon (siap cetak / kirim digital via WhatsApp)
        ↓
5. Hari Pembagian — Buka menu Validasi / Scan
   → Isi nama petugas
   → Pilih metode: Scan Live / Foto / Manual
   → Sistem tampilkan data & status kupon
   → Klik "Konfirmasi Pengambilan"
        ↓
6. Status otomatis berubah: Baru Dibuat → Sudah Diambil ✅
   → Tercatat di log: tanggal, jam, petugas, metode scan
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
| `waktu` | Timestamp otomatis — tanggal & jam (datetime lokal) |
| `catatan` | Catatan opsional dari petugas |

Log bisa dilihat dan diexport CSV di menu **Laporan → Log Scan**.

---

## 🗄️ Database

Menggunakan **SQLite** (`qurban_arrohman.db`) — file lokal, tidak perlu server atau koneksi internet.

| Tabel | Kolom Utama | Keterangan |
|-------|-------------|-----------|
| `users` | username, password, role | Akun admin |
| `penerima` | nama, no_hp, alamat, rt_rw, **kategori** | Data penerima kupon |
| `kupon` | id_kupon, penerima_id, status, **diambil_at**, diambil_oleh | Kupon digital |
| `log_scan` | id_kupon, aksi, petugas, metode, waktu | Riwayat aktivitas scan |

> Migrasi kolom `kategori` berjalan **otomatis** saat aplikasi dijalankan. Data lama tidak hilang.

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
- Sidebar bisa dilipat dengan klik tombol **‹** dan dibuka kembali dengan klik tombol **›** di tepi kiri layar

---

## ⚠️ Catatan: Pesan "sudo is disabled"

Jika muncul pesan **"Sudo is disabled on this machine"**, **abaikan saja** —
tidak perlu menjalankan perintah `sudo apt-get install libzbar0`.
Aplikasi ini menggunakan **OpenCV** untuk decode QR foto,
yang terinstall otomatis via `pip install -r requirements.txt` tanpa perlu sudo.

---

## 📜 Changelog

### v2.5.0 — 25 Mei 2026
**Revisi Sidebar Toggle & Tambah Jam Pengambilan**

- 🐛 **[Fix]** Tombol expand sidebar (panah **›**) tidak bisa diklik setelah sidebar dilipat
  - **Root cause:** CSS `header{visibility:hidden}` menyembunyikan seluruh elemen header termasuk tombol toggle
  - **Solusi:** Ganti pendekatan — hide elemen header secara spesifik (`stToolbar`, `stDecoration`, `stStatusWidget`); header dibuat transparan & tinggi 0 tapi tetap ada di DOM
  - Tombol expand `[data-testid="collapsedControl"]` kini `position:fixed` dengan `z-index:999999` — selalu tampil & bisa diklik
  - Hover effect: tombol melebar sedikit + shadow lebih dalam sebagai feedback visual
  - Tombol collapse (chevron di dalam sidebar) juga diberi style putih transparan yang konsisten
- ✨ **[Baru]** Kolom **Jam Pengambilan** tampil terpisah dari tanggal di seluruh UI
  - `diambil_at` (format `2026-05-24 22:56:12`) dipecah menjadi **Tgl Pengambilan** + **Jam** (HH:MM)
  - Diterapkan di: tabel Data Kupon, card detail kupon, popup validasi scan, tabel Dashboard "10 Pengambilan Terakhir"
  - Kupon belum diambil: kolom Tgl & Jam tampil `—` (tidak error, guard NaN/NULL)
- 🔧 **[Ubah]** Fungsi `db_get_all_kupon()` kini otomatis menambah kolom `tgl_pengambilan` & `jam_pengambilan`

---

### v2.4.0 — 25 Mei 2026 *(digabung ke v2.5.0)*

> Versi ini tidak dirilis tersendiri; perubahan dikerjakan bersamaan dengan v2.5.0.

---

### v2.3.0 — 24 Mei 2026
**Kategori Penerima & Perbaikan UI Sidebar/Logout**

- ✨ **[Baru]** Field **Kategori Penerima** di menu Data Penerima
  - Pilihan: `Shohibul Qurban`, `Warga`, `Panitia`, `Lainnya`
  - Pilih "Lainnya" → muncul field teks untuk isi kategori custom (contoh: Muallaf, Dhuafa)
  - Tampil di tabel daftar penerima, form tambah, form edit, tabel Data Kupon, dan kolom CSV
  - Migrasi kolom `kategori` berjalan otomatis — data lama tidak hilang
- 🐛 **[Fix]** Sidebar toggle button (panah collapse) diberi warna & border agar terlihat jelas *(disempurnakan di v2.5.0)*
- 🐛 **[Fix]** Tombol Logout kini terlihat jelas dan mencolok
  - Kotak info "Logged in as + nama user" di atas tombol
  - Tombol dengan border putih; hover berubah **merah** sebagai sinyal keluar
- ✨ **[Baru]** Kolom `kategori` ikut tampil di tabel Data Kupon

---

### v2.2.0 — 24 Mei 2026
**Perbaikan Bug Dashboard (DeltaGenerator)**

- 🐛 **[Fix]** Blok debug `DeltaGenerator(...)` muncul di bawah tulisan "Belum ada" di Dashboard
  - **Root cause:** ternary expression `st.dataframe() if cond else st.info()` mengembalikan objek `DeltaGenerator` yang ikut dirender
  - **Solusi:** Ganti ke blok `if/else` biasa di bagian "10 Pengambilan Terakhir" dan "Log Scan Terbaru"

---

### v2.1.0 — 24 Mei 2026
**Hapus Ketergantungan `sudo`**

- 🔧 **[Ubah]** Ganti `pyzbar` (butuh `sudo apt install libzbar0`) → **OpenCV** sebagai decoder QR foto utama
  - `pyzbar` dipertahankan sebagai fallback opsional jika sudah terinstall
  - Decode QR foto kini mencoba 2× (normal + diperbesar 2×) untuk akurasi lebih baik pada QR kecil
- 🔧 **[Ubah]** `requirements.txt`: tambah `opencv-python-headless`, pindah `pyzbar` ke komentar opsional
- 📝 **[Docs]** README ditambah seksi "Catatan: sudo is disabled" dan langkah install yang lebih ringkas

---

### v2.0.0 — 23 Mei 2026
**Fitur Scan QR Code & Log Aktivitas**

- ✨ **[Baru]** Menu **Validasi / Scan** dengan 3 metode:
  - 🎥 **Scan Live** — real-time via `streamlit-qrcode-scanner`
  - 📸 **Foto QR** — ambil foto → decode otomatis via `pyzbar`
  - ⌨️ **Input Manual** — ketik ID Kupon + shortcut dropdown daftar belum diambil
- ✨ **[Baru]** Tabel `log_scan` — rekam semua aksi KONFIRMASI & RESET beserta metode, petugas, waktu
- ✨ **[Baru]** Tab **Log Scan** di menu Laporan — filter by metode, export CSV
- ✨ **[Baru]** Dashboard: panel "Log Scan Terbaru" (10 log terakhir)
- ✨ **[Baru]** Helper `_render_kupon_detail_and_confirm()` — digunakan bersama antar semua tab scan
- ✨ **[Baru]** Scan result box — tampilan ID kupon terdeteksi yang jelas & berwarna
- 🔧 **[Ubah]** `db_konfirmasi()` & `db_reset_kupon()` otomatis catat ke `log_scan`
- 🎨 **[UI]** CSS: `.scan-box`, `.scan-result-box`, `.scan-id`, `.alert-info`
- 📝 **[Docs]** README diperbarui lengkap: 3 metode scan, tabel log_scan, alur penggunaan

---

### v1.0.0 — 23 Mei 2026
**Rilis Pertama**

- ✨ **[Baru]** Login admin dengan autentikasi SHA-256
- ✨ **[Baru]** Dashboard — statistik total penerima, kupon, sudah/belum diambil, progress bar
- ✨ **[Baru]** Data Penerima — tambah manual, edit, hapus, import CSV
- ✨ **[Baru]** Generate Kupon — format `QBN-YYYY-XXXX`, otomatis 1 kupon/penerima
- ✨ **[Baru]** Data Kupon — lihat daftar, filter, download QR Code & gambar kupon siap cetak
- ✨ **[Baru]** Gambar kupon (680×380px) dengan nama penerima, ID, dan QR Code berwarna
- ✨ **[Baru]** Validasi — input manual ID Kupon → konfirmasi pengambilan
- ✨ **[Baru]** Laporan — ringkasan & export CSV
- ✨ **[Baru]** Pengaturan — ganti password admin
- ✨ **[Baru]** Database SQLite lokal (`qurban_arrohman.db`) — tabel: users, penerima, kupon
- 🎨 **[UI]** Sidebar biru gradien, metric cards warna-warni, badge status Baru/Sudah Diambil
- 📝 **[Docs]** README awal: instalasi, alur, format kupon

---

## 📞 Info Aplikasi

| | |
|---|---|
| **Mushollah** | Ar Rohman |
| **Lokasi** | Perum BRI, Cepu |
| **Versi** | 2.5.0 |
| **Database** | SQLite (lokal, `qurban_arrohman.db`) |
| **Framework** | Streamlit |
| **Bahasa** | Python 3.10+ |
