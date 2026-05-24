import streamlit as st
import sqlite3
import qrcode
import io
import base64
import pandas as pd
from datetime import datetime
import hashlib
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ── QR Decode: OpenCV (UTAMA — tidak butuh sudo/libzbar0) ─────────
try:
    import cv2
    OPENCV_OK = True
except Exception:
    OPENCV_OK = False

# ── QR Decode: pyzbar (OPSIONAL — butuh sudo apt install libzbar0) ─
try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    PYZBAR_OK = True
except Exception:
    PYZBAR_OK = False

# Setidaknya satu decoder harus tersedia
FOTO_SCAN_OK = OPENCV_OK or PYZBAR_OK

# ── Live QR Scanner component ────────────────────────────────────
try:
    from streamlit_qrcode_scanner import qrcode_scanner
    SCANNER_OK = True
except Exception:
    SCANNER_OK = False

# ═══════════════════════════════════════════════════════════════
#  KONFIGURASI
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Kupon Qurban Digital – Mushollah Ar Rohman",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

TAHUN        = datetime.now().year
DB_PATH      = "qurban_arrohman.db"
MASJID       = "Mushollah Ar Rohman"
LOKASI       = "Perum BRI, Cepu"
PREFIX_KUPON = f"QBN-{TAHUN}"

# ═══════════════════════════════════════════════════════════════
#  CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important}

[data-testid="stSidebar"]{background:linear-gradient(180deg,#0D47A1 0%,#1565C0 60%,#1976D2 100%)!important}
[data-testid="stSidebar"] *{color:white!important}
[data-testid="stSidebar"] .stRadio label{
  background:rgba(255,255,255,.08);border-radius:8px;
  padding:8px 12px!important;transition:background .2s}
[data-testid="stSidebar"] .stRadio label:hover{background:rgba(255,255,255,.18)!important}

.metric-card{background:linear-gradient(135deg,#1565C0,#1E88E5);color:white;
  padding:1.3rem 1rem;border-radius:14px;text-align:center;
  box-shadow:0 6px 20px rgba(21,101,192,.25);margin-bottom:.5rem}
.metric-card.green{background:linear-gradient(135deg,#2E7D32,#43A047);
  box-shadow:0 6px 20px rgba(46,125,50,.25)}
.metric-card.orange{background:linear-gradient(135deg,#E65100,#FB8C00);
  box-shadow:0 6px 20px rgba(230,81,0,.25)}
.metric-card.purple{background:linear-gradient(135deg,#4A148C,#7B1FA2);
  box-shadow:0 6px 20px rgba(74,20,140,.25)}
.metric-card.teal{background:linear-gradient(135deg,#00695C,#00897B);
  box-shadow:0 6px 20px rgba(0,105,92,.25)}
.metric-icon{font-size:1.8rem}
.metric-value{font-size:2.4rem;font-weight:800;line-height:1.1}
.metric-label{font-size:.82rem;opacity:.92;margin-top:2px}

.badge-baru{background:#DBEAFE;color:#1D4ED8;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:700}
.badge-diambil{background:#DCFCE7;color:#15803D;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:700}
.badge-gagal{background:#FEE2E2;color:#991B1B;padding:3px 12px;border-radius:20px;font-size:.78rem;font-weight:700}

.section-title{font-size:1.6rem;font-weight:800;color:#0D47A1;margin-bottom:.25rem}
.section-sub{color:#607D8B;font-size:.92rem;margin-bottom:1.5rem}

.kupon-preview{border:2px solid #1565C0;border-radius:14px;padding:1.2rem;
  background:linear-gradient(135deg,#E3F2FD,#FFFFFF);
  box-shadow:0 4px 16px rgba(21,101,192,.12)}

.alert-success{background:#DCFCE7;border-left:4px solid #16A34A;
  padding:.8rem 1rem;border-radius:8px;color:#15803D;margin:.5rem 0}
.alert-warning{background:#FEF9C3;border-left:4px solid #CA8A04;
  padding:.8rem 1rem;border-radius:8px;color:#854D0E;margin:.5rem 0}
.alert-danger{background:#FEE2E2;border-left:4px solid #DC2626;
  padding:.8rem 1rem;border-radius:8px;color:#991B1B;margin:.5rem 0}
.alert-info{background:#E0F2FE;border-left:4px solid #0284C7;
  padding:.8rem 1rem;border-radius:8px;color:#075985;margin:.5rem 0}

/* ── Scanner box ── */
.scan-box{border:3px dashed #1565C0;border-radius:16px;padding:1.5rem;
  background:linear-gradient(135deg,#EFF6FF,#F8FAFC);text-align:center}
.scan-result-box{background:#F0FDF4;border:2px solid #22C55E;border-radius:12px;
  padding:1rem 1.5rem;margin:.8rem 0}
.scan-id{font-size:1.8rem;font-weight:800;color:#0D47A1;letter-spacing:.05em;
  font-family:monospace}

#MainMenu,footer,header{visibility:hidden}
.stButton>button{border-radius:8px!important;font-weight:600!important}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE NOT NULL,
            password     TEXT NOT NULL,
            nama_lengkap TEXT,
            role         TEXT DEFAULT 'admin'
        );
        CREATE TABLE IF NOT EXISTS penerima (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nama       TEXT NOT NULL,
            no_hp      TEXT,
            alamat     TEXT,
            rt_rw      TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS kupon (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            id_kupon     TEXT UNIQUE NOT NULL,
            penerima_id  INTEGER NOT NULL,
            status       TEXT DEFAULT 'Baru Dibuat',
            created_at   TEXT DEFAULT (datetime('now','localtime')),
            diambil_at   TEXT,
            diambil_oleh TEXT,
            catatan      TEXT,
            FOREIGN KEY (penerima_id) REFERENCES penerima(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS log_scan (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            id_kupon       TEXT NOT NULL,
            aksi           TEXT,
            status_sebelum TEXT,
            status_sesudah TEXT,
            petugas        TEXT,
            waktu          TEXT DEFAULT (datetime('now','localtime')),
            catatan        TEXT,
            metode         TEXT DEFAULT 'manual'
        );
    """)
    pw = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username,password,nama_lengkap,role) VALUES(?,?,?,?)",
              ("admin", pw, "Administrator", "admin"))
    conn.commit()


# ─── Auth ─────────────────────────────────────────────────────
def db_login(username, password):
    pw = hashlib.sha256(password.encode()).hexdigest()
    return get_conn().execute(
        "SELECT id,username,nama_lengkap,role FROM users WHERE username=? AND password=?",
        (username, pw)
    ).fetchone()


# ─── Penerima ─────────────────────────────────────────────────
def db_get_all_penerima():
    return pd.read_sql_query("SELECT * FROM penerima ORDER BY id", get_conn())

def db_add_penerima(nama, no_hp, alamat, rt_rw):
    c = get_conn()
    c.execute("INSERT INTO penerima(nama,no_hp,alamat,rt_rw) VALUES(?,?,?,?)",
              (nama, no_hp, alamat, rt_rw))
    c.commit()

def db_update_penerima(pid, nama, no_hp, alamat, rt_rw):
    c = get_conn()
    c.execute("UPDATE penerima SET nama=?,no_hp=?,alamat=?,rt_rw=? WHERE id=?",
              (nama, no_hp, alamat, rt_rw, pid))
    c.commit()

def db_delete_penerima(pid):
    c = get_conn()
    c.execute("DELETE FROM penerima WHERE id=?", (pid,))
    c.commit()


# ─── Kupon ────────────────────────────────────────────────────
def db_generate_all_kupon():
    conn = get_conn()
    c    = conn.cursor()
    c.execute("SELECT id FROM penerima WHERE id NOT IN (SELECT penerima_id FROM kupon)")
    pending = c.fetchall()
    c.execute(f"SELECT COUNT(*) FROM kupon WHERE id_kupon LIKE '{PREFIX_KUPON}-%'")
    offset = c.fetchone()[0]
    for i,(pid,) in enumerate(pending):
        id_kupon = f"{PREFIX_KUPON}-{offset+i+1:04d}"
        c.execute("INSERT INTO kupon(id_kupon,penerima_id) VALUES(?,?)", (id_kupon, pid))
    conn.commit()
    return len(pending)

def db_get_all_kupon():
    return pd.read_sql_query("""
        SELECT k.id,k.id_kupon,p.nama AS penerima,p.no_hp,p.alamat,p.rt_rw,
               k.status,k.created_at,k.diambil_at,k.diambil_oleh,k.catatan
        FROM kupon k JOIN penerima p ON k.penerima_id=p.id ORDER BY k.id
    """, get_conn())

def db_get_kupon_by_id(id_kupon):
    return get_conn().execute("""
        SELECT k.id,k.id_kupon,p.nama,p.no_hp,p.alamat,p.rt_rw,
               k.status,k.created_at,k.diambil_at,k.diambil_oleh,k.catatan
        FROM kupon k JOIN penerima p ON k.penerima_id=p.id
        WHERE k.id_kupon=?
    """, (id_kupon.upper().strip(),)).fetchone()

def db_konfirmasi(id_kupon, petugas, catatan="", metode="manual"):
    conn = get_conn()
    # get current status
    row = conn.execute("SELECT status FROM kupon WHERE id_kupon=?", (id_kupon,)).fetchone()
    old_status = row[0] if row else "-"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE kupon SET status='Sudah Diambil',diambil_at=?,diambil_oleh=?,catatan=? WHERE id_kupon=?",
        (now, petugas, catatan, id_kupon)
    )
    conn.execute(
        "INSERT INTO log_scan(id_kupon,aksi,status_sebelum,status_sesudah,petugas,catatan,metode) VALUES(?,?,?,?,?,?,?)",
        (id_kupon, "KONFIRMASI", old_status, "Sudah Diambil", petugas, catatan, metode)
    )
    conn.commit()

def db_reset_kupon(id_kupon, petugas="admin"):
    conn = get_conn()
    row  = conn.execute("SELECT status FROM kupon WHERE id_kupon=?", (id_kupon,)).fetchone()
    old  = row[0] if row else "-"
    conn.execute(
        "UPDATE kupon SET status='Baru Dibuat',diambil_at=NULL,diambil_oleh=NULL,catatan=NULL WHERE id_kupon=?",
        (id_kupon,)
    )
    conn.execute(
        "INSERT INTO log_scan(id_kupon,aksi,status_sebelum,status_sesudah,petugas,metode) VALUES(?,?,?,?,?,?)",
        (id_kupon, "RESET", old, "Baru Dibuat", petugas, "manual")
    )
    conn.commit()

def db_delete_all_kupon():
    get_conn().execute("DELETE FROM kupon"); get_conn().commit()

def db_get_log(limit=100):
    return pd.read_sql_query(
        f"SELECT * FROM log_scan ORDER BY id DESC LIMIT {limit}", get_conn()
    )

def db_stats():
    c  = get_conn()
    tp = c.execute("SELECT COUNT(*) FROM penerima").fetchone()[0]
    tk = c.execute("SELECT COUNT(*) FROM kupon").fetchone()[0]
    sd = c.execute("SELECT COUNT(*) FROM kupon WHERE status='Sudah Diambil'").fetchone()[0]
    bd = c.execute("SELECT COUNT(*) FROM kupon WHERE status='Baru Dibuat'").fetchone()[0]
    bk = c.execute("SELECT COUNT(*) FROM penerima WHERE id NOT IN (SELECT penerima_id FROM kupon)").fetchone()[0]
    return tp, tk, sd, bd, bk


# ═══════════════════════════════════════════════════════════════
#  QR CODE UTILITIES
# ═══════════════════════════════════════════════════════════════
def make_qr_bytes(data, color="#1565C0"):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=8, border=3)
    qr.add_data(data); qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color="white")
    buf = io.BytesIO(); img.save(buf,"PNG"); return buf.getvalue()


def decode_qr_from_image(pil_img):
    """Decode QR code dari PIL Image.
    Prioritas: OpenCV (tanpa sudo) -> pyzbar (butuh libzbar0) -> None
    """
    arr = np.array(pil_img.convert("RGB"))

    # Metode 1: OpenCV (tidak butuh sudo/libzbar0)
    if OPENCV_OK:
        try:
            bgr  = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            det  = cv2.QRCodeDetector()
            data, _, _ = det.detectAndDecode(bgr)
            if data and data.strip():
                return data.strip()
            # Coba dengan gambar diperbesar untuk QR kecil
            big  = cv2.resize(bgr, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            data2, _, _ = det.detectAndDecode(big)
            if data2 and data2.strip():
                return data2.strip()
        except Exception:
            pass

    # Metode 2: pyzbar (fallback jika libzbar0 tersedia)
    if PYZBAR_OK:
        try:
            results = pyzbar_decode(arr)
            if results:
                return results[0].data.decode("utf-8").strip()
        except Exception:
            pass

    return None


def _try_font(path, size):
    try: return ImageFont.truetype(path, size)
    except: return None

def _get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        f = _try_font(p, size)
        if f: return f
    return ImageFont.load_default()


def make_kupon_image(id_kupon, nama_penerima):
    W, H = 680, 380
    img  = Image.new("RGB", (W,H), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,W,90], fill="#0D47A1")
    draw.ellipse([-30,-30,80,80],fill="#1565C0")
    draw.ellipse([W-80,-30,W+30,80],fill="#1565C0")
    f_h = _get_font(17,True); f_s = _get_font(11)
    draw.text((W//2,30),"KUPON PENGAMBILAN DAGING QURBAN",fill="white",font=f_h,anchor="mm")
    draw.text((W//2,55),f"{MASJID}  ·  {LOKASI}  ·  Tahun {TAHUN}",fill="#BBDEFB",font=f_s,anchor="mm")
    qr_img = Image.open(io.BytesIO(make_qr_bytes(id_kupon,"#0D47A1"))).resize((210,210))
    img.paste(qr_img,(35,105))
    draw.line([(260,100),(260,320)],fill="#BBDEFB",width=2)
    f_lbl = _get_font(11); f_id = _get_font(26,True); f_nm = _get_font(18,True); f_i = _get_font(13)
    draw.text((280,110),"ID KUPON",fill="#607D8B",font=f_lbl)
    draw.text((280,128),id_kupon,fill="#0D47A1",font=f_id)
    draw.rectangle([278,174,430,176],fill="#E3F2FD")
    draw.text((280,185),"NAMA PENERIMA",fill="#607D8B",font=f_lbl)
    draw.text((280,203),nama_penerima,fill="#212121",font=f_nm)
    draw.rectangle([278,245,430,247],fill="#E3F2FD")
    draw.text((280,258),"Scan QR Code atau tunjukkan ID Kupon",fill="#455A64",font=f_i)
    draw.text((280,278),"kepada petugas saat hari pengambilan.",fill="#455A64",font=f_i)
    draw.rectangle([0,330,W,H],fill="#E3F2FD")
    draw.rectangle([0,330,W,333],fill="#1565C0")
    draw.text((W//2,354),"⚠  Kupon ini hanya berlaku untuk 1 (satu) kali pengambilan  ⚠",
              fill="#0D47A1",font=f_s,anchor="mm")
    draw.rectangle([2,2,W-2,H-2],outline="#0D47A1",width=3)
    buf = io.BytesIO(); img.save(buf,"PNG"); return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
#  SHARED HELPER: proses kupon setelah ID diketahui
# ═══════════════════════════════════════════════════════════════
def _render_kupon_detail_and_confirm(id_kupon, petugas, metode="manual"):
    """Tampilkan detail kupon dan form konfirmasi pengambilan."""
    row = db_get_kupon_by_id(id_kupon)
    if not row:
        st.markdown(f"""
        <div class="alert-danger">
            ❌ <b>Kupon tidak ditemukan!</b><br>
            ID <code>{id_kupon}</code> tidak ada dalam database.
        </div>""", unsafe_allow_html=True)
        return

    _, id_k, nama, no_hp, alamat, rt_rw, status, created_at, diambil_at, diambil_oleh, catatan = row

    # ── Tampilkan info ──
    col_qr, col_info = st.columns([1,2])
    with col_qr:
        st.image(make_qr_bytes(id_k), width=190)
    with col_info:
        badge = "badge-diambil" if status=="Sudah Diambil" else "badge-baru"
        st.markdown(f"""
        <div class="kupon-preview">
          <div style="font-size:.75rem;color:#607D8B;text-transform:uppercase;letter-spacing:.08em;">ID Kupon</div>
          <div class="scan-id">{id_k}</div>
          <div style="margin-top:.6rem;font-size:.85rem;color:#607D8B;">Penerima</div>
          <div style="font-size:1.1rem;font-weight:800;">{nama}</div>
          <div style="font-size:.85rem;color:#455A64;margin-top:.3rem;">
            📞 {no_hp or '-'} &nbsp;|&nbsp; 📍 {alamat or '-'} {rt_rw or ''}
          </div>
          <div style="margin-top:.8rem;">
            Status: <span class="{badge}">{status}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Status ──
    if status == "Sudah Diambil":
        st.markdown(f"""
        <div class="alert-danger">
            ⚠️ <b>KUPON INI SUDAH DIAMBIL!</b><br>
            Waktu : {diambil_at}<br>
            Petugas : {diambil_oleh or '-'}<br>
            Catatan : {catatan or '-'}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            ✅ <b>Data sesuai. Kupon belum diambil.</b>
            Klik tombol konfirmasi untuk menyelesaikan pengambilan.
        </div>""", unsafe_allow_html=True)

        catatan_inp = st.text_input(
            "Catatan (opsional)",
            placeholder="Contoh: Diwakilkan oleh...",
            key=f"cat_{id_k}_{metode}"
        )
        if st.button("✅  Konfirmasi Pengambilan", type="primary",
                     use_container_width=True, key=f"konfirm_{id_k}_{metode}"):
            if not petugas.strip():
                st.warning("⚠️ Isi nama petugas terlebih dahulu!")
            else:
                db_konfirmasi(id_k, petugas.strip(), catatan_inp, metode)
                st.success(f"🎉 **{nama}** — pengambilan berhasil dikonfirmasi! "
                           f"Status berubah menjadi **SUDAH DIAMBIL**. (via {metode})")
                st.balloons()
                # Reset scanner state
                for k in ["scan_live_result","scan_foto_result","scan_manual_result"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: LOGIN
# ═══════════════════════════════════════════════════════════════
def page_login():
    _, col, _ = st.columns([1,1.2,1])
    with col:
        st.markdown(f"""
        <div style="text-align:center;padding:2rem 0 1rem">
            <div style="font-size:4.5rem">🕌</div>
            <div style="font-size:1.6rem;font-weight:800;color:#0D47A1;margin-top:.5rem">{MASJID}</div>
            <div style="color:#607D8B;font-size:.9rem">{LOKASI}</div>
            <hr style="border-color:#E3F2FD;margin:1rem 0">
            <div style="font-size:1.1rem;font-weight:700;color:#333">🎫 Kupon Qurban Digital {TAHUN}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            username = st.text_input("👤 Username", placeholder="admin")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••")
            masuk    = st.form_submit_button("🔑 Masuk", type="primary", use_container_width=True)
            if masuk:
                if not username or not password:
                    st.error("Username dan password wajib diisi.")
                else:
                    result = db_login(username, password)
                    if result:
                        st.session_state.update({"logged_in":True,"user_id":result[0],
                                                 "username":result[1],"user_nama":result[2],"role":result[3]})
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")

        st.markdown("""<div style="text-align:center;color:#90A4AE;font-size:.78rem;margin-top:.8rem">
            Default → username: <b>admin</b> | password: <b>admin123</b></div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DASHBOARD
# ═══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown('<div class="section-title">🏠 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{MASJID} · {LOKASI} · Kupon Qurban {TAHUN}</div>',
                unsafe_allow_html=True)
    tp,tk,sd,bd,bk = db_stats()

    c1,c2,c3,c4,c5 = st.columns(5)
    for col,icon,val,lbl,cls in [
        (c1,"👥",tp,"Total Penerima",""),
        (c2,"🎫",tk,"Total Kupon",""),
        (c3,"✅",sd,"Sudah Diambil","green"),
        (c4,"⏳",bd,"Belum Diambil","orange"),
        (c5,"📋",bk,"Belum Ada Kupon","purple"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card {cls}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    cl,cr = st.columns([3,1])
    with cl:
        st.markdown("### 📊 Progress Pengambilan")
        if tk>0:
            st.progress(sd/tk, text=f"{sd}/{tk} kupon diambil ({sd/tk*100:.1f}%)")
        else:
            st.info("Belum ada kupon.")
    with cr:
        st.metric("Sisa Kupon", bd)

    st.markdown("---")
    cl2,cr2 = st.columns(2)
    with cl2:
        st.markdown("### 🕐 10 Pengambilan Terakhir")
        df = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID", p.nama AS "Penerima",
                   k.diambil_at AS "Waktu", k.diambil_oleh AS "Petugas"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Sudah Diambil' ORDER BY k.diambil_at DESC LIMIT 10
        """, get_conn())
        st.dataframe(df,use_container_width=True,hide_index=True) if not df.empty else st.info("Belum ada.")

    with cr2:
        st.markdown("### 📡 Log Scan Terbaru")
        df2 = pd.read_sql_query("""
            SELECT id_kupon AS "ID Kupon", aksi AS "Aksi", petugas AS "Petugas",
                   metode AS "Metode", waktu AS "Waktu"
            FROM log_scan ORDER BY id DESC LIMIT 10
        """, get_conn())
        st.dataframe(df2,use_container_width=True,hide_index=True) if not df2.empty else st.info("Belum ada log.")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DATA PENERIMA
# ═══════════════════════════════════════════════════════════════
def page_data_penerima():
    st.markdown('<div class="section-title">👥 Data Penerima</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Kelola daftar calon penerima kupon qurban.</div>',
                unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["📋 Daftar","➕ Tambah","📥 Import CSV"])

    with tab1:
        df = db_get_all_penerima()
        if df.empty:
            st.info("Belum ada penerima.")
        else:
            has = set(r[0] for r in get_conn().execute("SELECT penerima_id FROM kupon").fetchall())
            df["Kupon"] = df["id"].apply(lambda x:"✅" if x in has else "❌")
            st.markdown(f"**Total: {len(df)} penerima**")
            st.dataframe(df[["id","nama","no_hp","alamat","rt_rw","Kupon","created_at"]].rename(
                columns={"id":"No","nama":"Nama","no_hp":"No. HP",
                         "alamat":"Alamat","rt_rw":"RT/RW","created_at":"Terdaftar"}
            ), use_container_width=True, hide_index=True)

            st.markdown("### ✏️ Edit / Hapus")
            opts = {f"#{r['id']} – {r['nama']}":r["id"] for _,r in df.iterrows()}
            sel  = st.selectbox("Pilih penerima",list(opts.keys()))
            pid  = opts[sel]; row = df[df["id"]==pid].iloc[0]
            c1,c2 = st.columns(2)
            with c1:
                en  = st.text_input("Nama",value=row["nama"])
                ehp = st.text_input("No. HP",value=row["no_hp"] or "")
            with c2:
                ea  = st.text_input("Alamat",value=row["alamat"] or "")
                er  = st.text_input("RT/RW",value=row["rt_rw"] or "")
            b1,b2,_ = st.columns([1,1,3])
            with b1:
                if st.button("💾 Simpan",type="primary"):
                    db_update_penerima(pid,en,ehp,ea,er)
                    st.success("Diperbarui!"); st.rerun()
            with b2:
                if st.button("🗑️ Hapus",type="secondary"):
                    db_delete_penerima(pid); st.success("Dihapus!"); st.rerun()

    with tab2:
        with st.form("form_tambah",clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1:
                nama  = st.text_input("Nama *",placeholder="Ahmad Fauzan")
                no_hp = st.text_input("No. HP",placeholder="0812-3456-7890")
            with c2:
                alamat = st.text_input("Alamat",placeholder="Jl. Sejahtera No. 3")
                rt_rw  = st.text_input("RT/RW",placeholder="RT 01/RW 02")
            if st.form_submit_button("➕ Tambah",type="primary"):
                if not nama.strip(): st.error("Nama wajib diisi!")
                else:
                    db_add_penerima(nama.strip(),no_hp,alamat,rt_rw)
                    st.success(f"'{nama}' ditambahkan!"); st.rerun()

    with tab3:
        st.info("Format CSV: `nama, no_hp, alamat, rt_rw` (tanpa header)")
        up = st.file_uploader("Upload CSV",type=["csv"])
        if up:
            try:
                df_i = pd.read_csv(up,header=None)
                df_i.columns=["nama","no_hp","alamat","rt_rw"][:len(df_i.columns)]
                st.dataframe(df_i,hide_index=True)
                if st.button("✅ Import",type="primary"):
                    for _,r in df_i.iterrows():
                        db_add_penerima(str(r.get("nama","")).strip(),
                                        str(r.get("no_hp","")),str(r.get("alamat","")),str(r.get("rt_rw","")))
                    st.success(f"{len(df_i)} penerima diimport!"); st.rerun()
            except Exception as e:
                st.error(f"Gagal: {e}")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: GENERATE KUPON
# ═══════════════════════════════════════════════════════════════
def page_generate_kupon():
    st.markdown('<div class="section-title">🎫 Generate Kupon</div>', unsafe_allow_html=True)
    tp,tk,sd,bd,bk = db_stats()
    c1,c2,c3 = st.columns(3)
    for col,icon,val,lbl,cls in [
        (c1,"👥",tp,"Total Penerima",""),
        (c2,"📋",bk,"Belum Punya Kupon","orange"),
        (c3,"🎫",tk,"Total Kupon","green"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card {cls}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if tp == 0:
        st.warning("Tambahkan penerima terlebih dahulu.")
    elif bk == 0:
        st.markdown('<div class="alert-success">✅ Semua penerima sudah punya kupon!</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="alert-warning">📋 {bk} penerima belum punya kupon.</div>',
                    unsafe_allow_html=True)
        st.markdown("")
        if st.button("🎫  Generate Kupon Sekarang",type="primary",use_container_width=True):
            with st.spinner("Membuat kupon..."):
                n = db_generate_all_kupon()
            st.success(f"🎉 {n} kupon berhasil dibuat!"); st.balloons(); st.rerun()

    if tk > 0:
        st.markdown("---")
        with st.expander("⚠️ Zona Berbahaya"):
            st.warning("Hapus semua kupon (tidak bisa dibatalkan).")
            k = st.text_input("Ketik HAPUS untuk konfirmasi")
            if st.button("🗑️ Hapus Semua",type="secondary"):
                if k.strip().upper()=="HAPUS":
                    db_delete_all_kupon(); st.success("Dihapus!"); st.rerun()
                else: st.error("Konfirmasi tidak sesuai.")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DATA KUPON
# ═══════════════════════════════════════════════════════════════
def page_data_kupon():
    st.markdown('<div class="section-title">📋 Data Kupon</div>', unsafe_allow_html=True)
    df = db_get_all_kupon()
    if df.empty:
        st.info("Belum ada kupon."); return

    cf1,cf2 = st.columns([3,1])
    with cf1: search = st.text_input("🔍 Cari ID/Nama","")
    with cf2: fs = st.selectbox("Status",["Semua","Baru Dibuat","Sudah Diambil"])

    filt = df.copy()
    if search:
        filt = filt[filt["id_kupon"].str.contains(search,case=False,na=False)|
                    filt["penerima"].str.contains(search,case=False,na=False)]
    if fs!="Semua": filt = filt[filt["status"]==fs]

    st.markdown(f"**{len(filt)} dari {len(df)} kupon**")
    st.dataframe(filt[["id_kupon","penerima","no_hp","alamat","status","created_at","diambil_at","diambil_oleh"]].rename(
        columns={"id_kupon":"ID Kupon","penerima":"Penerima","no_hp":"No. HP","alamat":"Alamat",
                 "status":"Status","created_at":"Dibuat","diambil_at":"Diambil","diambil_oleh":"Petugas"}
    ), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🖨️ Lihat & Cetak Kupon")
    opts = {f"{r['id_kupon']} – {r['penerima']}":r["id_kupon"] for _,r in filt.iterrows()}
    if not opts: return
    sel = st.selectbox("Pilih Kupon",list(opts.keys()))
    id_k = opts[sel]; row = db_get_kupon_by_id(id_k)
    if not row: return
    _,id_k,nama,no_hp,alamat,rt_rw,status,created_at,diambil_at,diambil_oleh,catatan = row

    cA,cB = st.columns([1,2])
    with cA:
        st.image(make_qr_bytes(id_k),caption=f"QR: {id_k}",width=200)
        st.download_button("⬇️ QR Code",make_qr_bytes(id_k),f"qr_{id_k}.png","image/png")
    with cB:
        badge = "badge-diambil" if status=="Sudah Diambil" else "badge-baru"
        st.markdown(f"""
        <div class="kupon-preview">
          <div class="scan-id">{id_k}</div>
          <div style="font-weight:700;font-size:1.1rem">{nama}</div>
          <div style="color:#455A64;font-size:.85rem">📞 {no_hp or '-'} | 📍 {alamat or '-'}</div>
          <div style="margin-top:.6rem">Status: <span class="{badge}">{status}</span></div>
          <div style="color:#90A4AE;font-size:.78rem">Dibuat: {created_at}</div>
        </div>""", unsafe_allow_html=True)
        if status=="Sudah Diambil":
            st.markdown(f'<div class="alert-success">✅ Diambil: {diambil_at} | 👤 {diambil_oleh}</div>',
                        unsafe_allow_html=True)
        kupon_img = make_kupon_image(id_k, nama)
        c1,c2 = st.columns(2)
        with c1:
            st.download_button("🖨️ Download Kupon",kupon_img,f"kupon_{id_k}.png",
                               "image/png",type="primary",use_container_width=True)
        with c2:
            if status=="Sudah Diambil":
                if st.button("↩️ Reset",use_container_width=True):
                    db_reset_kupon(id_k,st.session_state.get("user_nama","admin"))
                    st.success("Reset!"); st.rerun()

    st.markdown("**Preview Kupon:**")
    st.image(make_kupon_image(id_k,nama),use_container_width=False,width=680)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: VALIDASI / SCAN ← FITUR UTAMA
# ═══════════════════════════════════════════════════════════════
def page_validasi():
    st.markdown('<div class="section-title">📷 Validasi / Scan Kupon</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Konfirmasi pengambilan qurban dengan 3 metode: Scan Live, Foto QR, atau Input Manual.</div>',
                unsafe_allow_html=True)

    # ── Nama Petugas (global di atas tab) ──
    col_pt, col_st = st.columns([3,1])
    with col_pt:
        petugas = st.text_input(
            "👤 Nama Petugas *",
            value=st.session_state.get("user_nama",""),
            placeholder="Nama petugas yang bertugas hari ini",
            key="petugas_input"
        )
    with col_st:
        _, tk, sd, bd, _ = db_stats()
        st.metric("Sisa Kupon", bd, f"/{tk} total")

    st.markdown("---")

    # ══════════════════════════════════════════
    #  TAB 1 · SCAN LIVE (html5-qrcode)
    #  TAB 2 · FOTO QR  (pyzbar)
    #  TAB 3 · INPUT MANUAL
    # ══════════════════════════════════════════
    tabs = st.tabs(["🎥  Scan Live (Kamera Real-Time)",
                    "📸  Foto QR Code",
                    "⌨️  Input Manual"])

    # ────────────────────────────────────────
    #  TAB 1 : SCAN LIVE
    # ────────────────────────────────────────
    with tabs[0]:
        if SCANNER_OK:
            st.markdown("""
            <div class="alert-info">
                📱 <b>Scan Live:</b> Arahkan kamera ke QR Code pada kupon.
                Hasil scan akan muncul otomatis di bawah.
            </div>""", unsafe_allow_html=True)

            qr_result = qrcode_scanner(key="live_scanner_main")

            if qr_result:
                st.session_state["scan_live_result"] = qr_result
                st.markdown(f"""
                <div class="scan-result-box">
                    <div style="color:#15803D;font-size:.8rem;font-weight:700;
                                text-transform:uppercase;letter-spacing:.1em">
                        ✅ QR Terdeteksi!
                    </div>
                    <div class="scan-id">{qr_result}</div>
                </div>""", unsafe_allow_html=True)

            saved = st.session_state.get("scan_live_result","")
            if saved:
                st.markdown("### 📋 Hasil Scan")
                _render_kupon_detail_and_confirm(saved, petugas, metode="scan-live")
        else:
            st.markdown("""
            <div class="alert-warning">
                ⚠️ Komponen scanner real-time tidak tersedia.<br>
                Install: <code>pip install streamlit-qrcode-scanner</code><br>
                Gunakan tab <b>Foto QR Code</b> atau <b>Input Manual</b>.
            </div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────
    #  TAB 2 : FOTO QR (camera_input + pyzbar)
    # ────────────────────────────────────────
    with tabs[1]:
        st.markdown("""
        <div class="alert-info">
            📸 <b>Ambil foto</b> QR Code menggunakan kamera perangkat Anda.
            Sistem akan otomatis membaca dan memvalidasi kupon.
        </div>""", unsafe_allow_html=True)

        if not FOTO_SCAN_OK:
            st.warning("Library decoder QR tidak tersedia. Install: `pip install opencv-python-headless`")
        else:
            col_cam, col_tip = st.columns([2,1])
            with col_cam:
                st.markdown('<div class="scan-box">', unsafe_allow_html=True)
                foto = st.camera_input("📷 Arahkan kamera ke QR Code lalu klik ambil foto",
                                       key="camera_qr_foto")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_tip:
                st.markdown("""
                **💡 Tips agar berhasil:**
                - Pastikan QR Code terlihat jelas
                - Pegang ponsel/kamera dengan stabil
                - Jarak ideal: 15–30 cm dari QR Code
                - Cahaya cukup, hindari pantulan cahaya
                - Pastikan seluruh QR Code masuk frame
                """)

            if foto:
                with st.spinner("🔍 Membaca QR Code..."):
                    pil_img   = Image.open(foto)
                    qr_text   = decode_qr_from_image(pil_img)

                if qr_text:
                    st.session_state["scan_foto_result"] = qr_text
                    st.markdown(f"""
                    <div class="scan-result-box">
                        <div style="color:#15803D;font-size:.8rem;font-weight:700;
                                    text-transform:uppercase;letter-spacing:.1em">
                            ✅ QR Berhasil Dibaca!
                        </div>
                        <div class="scan-id">{qr_text}</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="alert-danger">
                        ❌ <b>QR Code tidak terbaca.</b><br>
                        Coba ambil foto ulang dengan posisi lebih dekat dan cahaya lebih terang.
                    </div>""", unsafe_allow_html=True)

            saved_foto = st.session_state.get("scan_foto_result","")
            if saved_foto:
                st.markdown("### 📋 Hasil Scan Foto")
                _render_kupon_detail_and_confirm(saved_foto, petugas, metode="scan-foto")
                if st.button("🔄 Scan QR Lain", key="clear_foto"):
                    del st.session_state["scan_foto_result"]; st.rerun()

    # ────────────────────────────────────────
    #  TAB 3 : INPUT MANUAL
    # ────────────────────────────────────────
    with tabs[2]:
        st.markdown("""
        <div class="alert-info">
            ⌨️ <b>Input Manual:</b> Ketik atau tempel ID Kupon dari kupon fisik/digital.
        </div>""", unsafe_allow_html=True)

        c_in, c_btn = st.columns([4,1])
        with c_in:
            id_input = st.text_input(
                "🔢 ID Kupon",
                placeholder="Contoh: QBN-2026-0001",
                key="manual_id_input"
            )
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            cari = st.button("🔍 Cari", type="primary", use_container_width=True)

        if cari and id_input.strip():
            st.session_state["scan_manual_result"] = id_input.strip().upper()

        # Shortcut: pilih dari daftar yang belum diambil
        with st.expander("📋 Pilih dari daftar kupon belum diambil"):
            df_bd = pd.read_sql_query("""
                SELECT k.id_kupon,p.nama,p.no_hp FROM kupon k
                JOIN penerima p ON k.penerima_id=p.id
                WHERE k.status='Baru Dibuat' ORDER BY k.id
            """, get_conn())
            if df_bd.empty:
                st.success("🎉 Semua kupon sudah diambil!")
            else:
                opts_bd = {f"{r['id_kupon']} – {r['nama']}":r["id_kupon"]
                           for _,r in df_bd.iterrows()}
                pick = st.selectbox("Pilih kupon",["-- Pilih --"]+list(opts_bd.keys()),
                                    key="pick_from_list")
                if pick != "-- Pilih --":
                    if st.button("✅ Gunakan Ini", type="primary"):
                        st.session_state["scan_manual_result"] = opts_bd[pick]
                        st.rerun()

        saved_man = st.session_state.get("scan_manual_result","")
        if saved_man:
            st.markdown(f"""
            <div class="scan-result-box">
                <div style="color:#075985;font-size:.8rem;font-weight:700;
                            text-transform:uppercase;letter-spacing:.1em">
                    🔍 ID Kupon
                </div>
                <div class="scan-id">{saved_man}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("### 📋 Detail Kupon")
            _render_kupon_detail_and_confirm(saved_man, petugas, metode="manual")
            if st.button("🔄 Cari Kupon Lain", key="clear_manual"):
                del st.session_state["scan_manual_result"]; st.rerun()

    # ── Daftar status bawah ──
    st.markdown("---")
    cl,cr = st.columns(2)
    with cl:
        st.markdown("### ⏳ Belum Diambil")
        df_bd2 = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID",p.nama AS "Penerima",p.no_hp AS "No. HP"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Baru Dibuat' ORDER BY k.id
        """, get_conn())
        if df_bd2.empty: st.success("🎉 Semua sudah diambil!")
        else:
            st.info(f"**{len(df_bd2)}** kupon belum diambil.")
            st.dataframe(df_bd2,use_container_width=True,hide_index=True)

    with cr:
        st.markdown("### ✅ Sudah Diambil")
        df_sd = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID",p.nama AS "Penerima",
                   k.diambil_at AS "Waktu",k.diambil_oleh AS "Petugas"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Sudah Diambil' ORDER BY k.diambil_at DESC
        """, get_conn())
        if df_sd.empty: st.info("Belum ada.")
        else:
            st.info(f"**{len(df_sd)}** kupon sudah diambil.")
            st.dataframe(df_sd,use_container_width=True,hide_index=True)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: LAPORAN
# ═══════════════════════════════════════════════════════════════
def page_laporan():
    st.markdown('<div class="section-title">📊 Laporan</div>', unsafe_allow_html=True)
    tp,tk,sd,bd,bk = db_stats()

    tab1,tab2 = st.tabs(["📈 Ringkasan","📡 Log Scan"])

    with tab1:
        c1,c2 = st.columns([1,2])
        with c1:
            st.markdown(f"### Ringkasan {TAHUN}")
            st.dataframe(pd.DataFrame({
                "Keterangan":["Total Penerima","Total Kupon","Sudah Diambil","Belum Diambil","Belum Punya Kupon"],
                "Jumlah":[tp,tk,sd,bd,bk]
            }), hide_index=True, use_container_width=True)
        with c2:
            if tk>0:
                pct=sd/tk
                st.progress(pct,text=f"{pct*100:.1f}% kupon sudah diambil")

        df_all = db_get_all_kupon()
        if not df_all.empty:
            csv = df_all.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV",csv,
                               f"laporan_kupon_{TAHUN}_{datetime.now().strftime('%Y%m%d')}.csv",
                               "text/csv",type="primary")
            st.dataframe(df_all,use_container_width=True,hide_index=True)

    with tab2:
        st.markdown("### 📡 Log Semua Aktivitas Scan")
        df_log = db_get_log(500)
        if df_log.empty:
            st.info("Belum ada aktivitas scan.")
        else:
            # filter by metode
            metodes = ["Semua"] + list(df_log["metode"].unique())
            fm = st.selectbox("Filter Metode",metodes)
            show = df_log if fm=="Semua" else df_log[df_log["metode"]==fm]
            st.markdown(f"**{len(show)} log**")
            st.dataframe(show,use_container_width=True,hide_index=True)
            csv2 = show.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export Log CSV",csv2,"log_scan.csv","text/csv")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: PENGATURAN
# ═══════════════════════════════════════════════════════════════
def page_pengaturan():
    st.markdown('<div class="section-title">⚙️ Pengaturan</div>', unsafe_allow_html=True)
    tab1,tab2 = st.tabs(["🔑 Ganti Password","ℹ️ Info Aplikasi"])

    with tab1:
        with st.form("form_pw"):
            op = st.text_input("Password Lama",type="password")
            np_ = st.text_input("Password Baru",type="password")
            cp = st.text_input("Konfirmasi Baru",type="password")
            if st.form_submit_button("💾 Simpan",type="primary"):
                if np_!=cp: st.error("Tidak cocok!")
                elif len(np_)<6: st.error("Min 6 karakter!")
                else:
                    if not db_login(st.session_state["username"],op): st.error("Password lama salah!")
                    else:
                        h = hashlib.sha256(np_.encode()).hexdigest()
                        get_conn().execute("UPDATE users SET password=? WHERE username=?",
                                          (h,st.session_state["username"])); get_conn().commit()
                        st.success("Password diubah!")

    with tab2:
        # Scanner status
        st.markdown(f"""
        ### Info Aplikasi
        | | |
        |---|---|
        | **Mushollah** | {MASJID} |
        | **Lokasi** | {LOKASI} |
        | **Tahun** | {TAHUN} |
        | **Versi** | 2.0.0 |
        | **Scan Live** | {'✅ Aktif' if SCANNER_OK else '❌ Tidak Tersedia'} |
        | **Scan Foto (OpenCV/pyzbar)** | {'✅ Aktif (OpenCV)' if OPENCV_OK else ('✅ Aktif (pyzbar)' if PYZBAR_OK else '❌ Tidak Tersedia')} |

        ### Metode Scan yang Tersedia
        - 🎥 **Scan Live** — kamera real-time via `streamlit-qrcode-scanner`
        - 📸 **Scan Foto** — foto kamera lalu QR didekode otomatis via OpenCV (tanpa sudo)
        - ⌨️ **Input Manual** — ketik ID Kupon langsung
        """)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR & ROUTER
# ═══════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:1.2rem 0 .5rem">
            <div style="font-size:3rem">🕌</div>
            <div style="font-weight:800;font-size:1rem;margin-top:.4rem">{MASJID}</div>
            <div style="font-size:.78rem;opacity:.8">{LOKASI}</div>
            <div style="font-size:.75rem;opacity:.7;margin-top:.2rem">Kupon Qurban {TAHUN}</div>
        </div>
        <hr style="border-color:rgba(255,255,255,.2);margin:.5rem 0">
        """, unsafe_allow_html=True)

        menu = st.radio("Navigasi",[
            "🏠  Dashboard",
            "👥  Data Penerima",
            "🎫  Generate Kupon",
            "📋  Data Kupon",
            "📷  Validasi / Scan",
            "📊  Laporan",
            "⚙️  Pengaturan",
        ], label_visibility="collapsed")

        st.markdown("<hr style='border-color:rgba(255,255,255,.2)'>", unsafe_allow_html=True)
        tp,tk,sd,bd,_ = db_stats()
        st.markdown(f"""
        <div style="font-size:.78rem;opacity:.85;line-height:2">
            👥 Penerima: <b>{tp}</b><br>
            🎫 Kupon: <b>{tk}</b><br>
            ✅ Diambil: <b>{sd}</b><br>
            ⏳ Sisa: <b>{bd}</b><br>
            📡 Scan: {'✅' if SCANNER_OK else '⚠️'} Live | {'✅' if FOTO_SCAN_OK else '⚠️'} Foto
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr style='border-color:rgba(255,255,255,.2)'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:.78rem;opacity:.8'>👤 {st.session_state.get('user_nama','Admin')}</div>",
                    unsafe_allow_html=True)
        if st.button("🚪 Logout",use_container_width=True,type="secondary"):
            st.session_state.clear(); st.rerun()
    return menu


def main():
    init_db()
    if not st.session_state.get("logged_in"):
        page_login(); return

    menu = sidebar()
    if   "Dashboard"    in menu: page_dashboard()
    elif "Penerima"     in menu: page_data_penerima()
    elif "Generate"     in menu: page_generate_kupon()
    elif "Data Kupon"   in menu: page_data_kupon()
    elif "Validasi"     in menu: page_validasi()
    elif "Laporan"      in menu: page_laporan()
    elif "Pengaturan"   in menu: page_pengaturan()

if __name__ == "__main__":
    main()
