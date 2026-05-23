import streamlit as st
import sqlite3
import qrcode
import io
import base64
import pandas as pd
from datetime import datetime
import hashlib
from PIL import Image, ImageDraw, ImageFont
import os

# ═══════════════════════════════════════════════════════════════
#  KONFIGURASI APLIKASI
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
#  CSS STYLING
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Import font ── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 60%, #1976D2 100%) !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stRadio > div { gap: 4px; }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px 12px !important;
        transition: background 0.2s;
        cursor: pointer;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.18) !important;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: linear-gradient(135deg, #1565C0 0%, #1E88E5 100%);
        color: white;
        padding: 1.3rem 1rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(21,101,192,0.25);
        margin-bottom: 0.5rem;
    }
    .metric-card.green {
        background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%);
        box-shadow: 0 6px 20px rgba(46,125,50,0.25);
    }
    .metric-card.orange {
        background: linear-gradient(135deg, #E65100 0%, #FB8C00 100%);
        box-shadow: 0 6px 20px rgba(230,81,0,0.25);
    }
    .metric-card.purple {
        background: linear-gradient(135deg, #4A148C 0%, #7B1FA2 100%);
        box-shadow: 0 6px 20px rgba(74,20,140,0.25);
    }
    .metric-icon  { font-size: 1.8rem; }
    .metric-value { font-size: 2.4rem; font-weight: 800; line-height: 1.1; }
    .metric-label { font-size: 0.82rem; opacity: 0.92; margin-top: 2px; }

    /* ── Status Badge ── */
    .badge-baru {
        background:#DBEAFE; color:#1D4ED8;
        padding:3px 12px; border-radius:20px;
        font-size:0.78rem; font-weight:700;
    }
    .badge-diambil {
        background:#DCFCE7; color:#15803D;
        padding:3px 12px; border-radius:20px;
        font-size:0.78rem; font-weight:700;
    }

    /* ── Section Header ── */
    .section-title {
        font-size: 1.6rem; font-weight: 800;
        color: #0D47A1; margin-bottom: 0.25rem;
    }
    .section-sub {
        color: #607D8B; font-size: 0.92rem; margin-bottom: 1.5rem;
    }

    /* ── Kupon Card ── */
    .kupon-preview {
        border: 2px solid #1565C0;
        border-radius: 14px;
        padding: 1.2rem;
        background: linear-gradient(135deg, #E3F2FD 0%, #FFFFFF 100%);
        box-shadow: 0 4px 16px rgba(21,101,192,0.12);
    }

    /* ── Alert custom ── */
    .alert-success {
        background:#DCFCE7; border-left:4px solid #16A34A;
        padding:0.8rem 1rem; border-radius:8px; color:#15803D;
    }
    .alert-warning {
        background:#FEF9C3; border-left:4px solid #CA8A04;
        padding:0.8rem 1rem; border-radius:8px; color:#854D0E;
    }
    .alert-danger {
        background:#FEE2E2; border-left:4px solid #DC2626;
        padding:0.8rem 1rem; border-radius:8px; color:#991B1B;
    }

    /* ── Button tweaks ── */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* ── Hide Streamlit default ── */
    #MainMenu, footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def get_conn():
    """Single SQLite connection (Streamlit caches it)."""
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password      TEXT NOT NULL,
            nama_lengkap  TEXT,
            role          TEXT DEFAULT 'admin'
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
    """)
    # Default admin
    pw_hash = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute(
        "INSERT OR IGNORE INTO users (username, password, nama_lengkap, role) VALUES (?,?,?,?)",
        ("admin", pw_hash, "Administrator", "admin")
    )
    conn.commit()


# ─── Auth ───────────────────────────────────────────────────────
def db_login(username: str, password: str):
    conn = get_conn()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    row = conn.execute(
        "SELECT id, username, nama_lengkap, role FROM users WHERE username=? AND password=?",
        (username, pw_hash)
    ).fetchone()
    return row


# ─── Penerima ────────────────────────────────────────────────────
def db_get_all_penerima() -> pd.DataFrame:
    conn = get_conn()
    return pd.read_sql_query("SELECT * FROM penerima ORDER BY id", conn)


def db_add_penerima(nama, no_hp, alamat, rt_rw):
    conn = get_conn()
    conn.execute("INSERT INTO penerima (nama, no_hp, alamat, rt_rw) VALUES (?,?,?,?)",
                 (nama, no_hp, alamat, rt_rw))
    conn.commit()


def db_update_penerima(pid, nama, no_hp, alamat, rt_rw):
    conn = get_conn()
    conn.execute("UPDATE penerima SET nama=?, no_hp=?, alamat=?, rt_rw=? WHERE id=?",
                 (nama, no_hp, alamat, rt_rw, pid))
    conn.commit()


def db_delete_penerima(pid):
    conn = get_conn()
    conn.execute("DELETE FROM penerima WHERE id=?", (pid,))
    conn.commit()


# ─── Kupon ──────────────────────────────────────────────────────
def db_generate_all_kupon() -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM penerima WHERE id NOT IN (SELECT penerima_id FROM kupon)")
    pending = c.fetchall()
    c.execute(f"SELECT COUNT(*) FROM kupon WHERE id_kupon LIKE '{PREFIX_KUPON}-%'")
    offset = c.fetchone()[0]
    for i, (pid,) in enumerate(pending):
        id_kupon = f"{PREFIX_KUPON}-{offset + i + 1:04d}"
        c.execute("INSERT INTO kupon (id_kupon, penerima_id) VALUES (?,?)", (id_kupon, pid))
    conn.commit()
    return len(pending)


def db_get_all_kupon() -> pd.DataFrame:
    conn = get_conn()
    return pd.read_sql_query("""
        SELECT k.id, k.id_kupon, p.nama AS penerima, p.no_hp, p.alamat, p.rt_rw,
               k.status, k.created_at, k.diambil_at, k.diambil_oleh, k.catatan
        FROM kupon k
        JOIN penerima p ON k.penerima_id = p.id
        ORDER BY k.id
    """, conn)


def db_get_kupon_by_id(id_kupon: str):
    conn = get_conn()
    return conn.execute("""
        SELECT k.id, k.id_kupon, p.nama, p.no_hp, p.alamat, p.rt_rw,
               k.status, k.created_at, k.diambil_at, k.diambil_oleh, k.catatan
        FROM kupon k
        JOIN penerima p ON k.penerima_id = p.id
        WHERE k.id_kupon = ?
    """, (id_kupon.upper().strip(),)).fetchone()


def db_konfirmasi(id_kupon, petugas, catatan=""):
    conn = get_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "UPDATE kupon SET status='Sudah Diambil', diambil_at=?, diambil_oleh=?, catatan=? WHERE id_kupon=?",
        (now, petugas, catatan, id_kupon)
    )
    conn.commit()


def db_reset_kupon(id_kupon):
    conn = get_conn()
    conn.execute(
        "UPDATE kupon SET status='Baru Dibuat', diambil_at=NULL, diambil_oleh=NULL, catatan=NULL WHERE id_kupon=?",
        (id_kupon,)
    )
    conn.commit()


def db_delete_all_kupon():
    conn = get_conn()
    conn.execute("DELETE FROM kupon")
    conn.commit()


def db_stats():
    conn = get_conn()
    c = conn.cursor()
    tp  = c.execute("SELECT COUNT(*) FROM penerima").fetchone()[0]
    tk  = c.execute("SELECT COUNT(*) FROM kupon").fetchone()[0]
    sd  = c.execute("SELECT COUNT(*) FROM kupon WHERE status='Sudah Diambil'").fetchone()[0]
    bd  = c.execute("SELECT COUNT(*) FROM kupon WHERE status='Baru Dibuat'").fetchone()[0]
    bk  = c.execute(
        "SELECT COUNT(*) FROM penerima WHERE id NOT IN (SELECT penerima_id FROM kupon)"
    ).fetchone()[0]
    return tp, tk, sd, bd, bk


# ═══════════════════════════════════════════════════════════════
#  QR CODE & KUPON IMAGE
# ═══════════════════════════════════════════════════════════════
def make_qr_bytes(data: str, color="#1565C0") -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color=color, back_color="white")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _try_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return None


def _get_font(size, bold=False):
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    candidates_reg = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    candidates = candidates_bold if bold else candidates_reg
    for path in candidates:
        f = _try_font(path, size)
        if f:
            return f
    return ImageFont.load_default()


def make_kupon_image(id_kupon, nama_penerima) -> bytes:
    """Buat gambar kupon yang bisa dicetak / dikirim digital."""
    W, H = 680, 380
    img  = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # ── Background header ──
    draw.rectangle([0, 0, W, 90], fill="#0D47A1")
    # Decorative circles
    draw.ellipse([-30, -30, 80, 80], fill="#1565C0")
    draw.ellipse([W-80, -30, W+30, 80], fill="#1565C0")

    # ── Header text ──
    f_header = _get_font(17, bold=True)
    f_sub    = _get_font(11)
    draw.text((W//2, 30), "KUPON PENGAMBILAN DAGING QURBAN", fill="white",
              font=f_header, anchor="mm")
    draw.text((W//2, 55), f"{MASJID}  ·  {LOKASI}  ·  Tahun {TAHUN}",
              fill="#BBDEFB", font=f_sub, anchor="mm")
    draw.text((W//2, 75), "─" * 60, fill="#42A5F5", font=f_sub, anchor="mm")

    # ── QR Code ──
    qr_bytes = make_qr_bytes(id_kupon, "#0D47A1")
    qr_img   = Image.open(io.BytesIO(qr_bytes)).resize((210, 210))
    img.paste(qr_img, (35, 105))

    # ── Separator line ──
    draw.line([(260, 100), (260, 320)], fill="#BBDEFB", width=2)

    # ── Coupon info ──
    f_label  = _get_font(11)
    f_id     = _get_font(26, bold=True)
    f_nama   = _get_font(18, bold=True)
    f_info   = _get_font(13)

    draw.text((280, 110), "ID KUPON", fill="#607D8B", font=f_label)
    draw.text((280, 128), id_kupon,  fill="#0D47A1", font=f_id)

    draw.rectangle([278, 174, 430, 176], fill="#E3F2FD")

    draw.text((280, 185), "NAMA PENERIMA", fill="#607D8B", font=f_label)
    draw.text((280, 203), nama_penerima,  fill="#212121", font=f_nama)

    draw.rectangle([278, 245, 430, 247], fill="#E3F2FD")

    draw.text((280, 258), "Scan QR Code atau tunjukkan ID Kupon",
              fill="#455A64", font=f_info)
    draw.text((280, 278), "kepada petugas saat hari pengambilan.",
              fill="#455A64", font=f_info)

    # ── Footer ──
    draw.rectangle([0, 330, W, H], fill="#E3F2FD")
    draw.rectangle([0, 330, W, 333], fill="#1565C0")
    f_footer = _get_font(11)
    draw.text((W//2, 354),
              "⚠  Kupon ini hanya berlaku untuk 1 (satu) kali pengambilan  ⚠",
              fill="#0D47A1", font=f_footer, anchor="mm")

    # ── Border ──
    draw.rectangle([2, 2, W-2, H-2], outline="#0D47A1", width=3)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: LOGIN
# ═══════════════════════════════════════════════════════════════
def page_login():
    col_L, col_M, col_R = st.columns([1, 1.2, 1])
    with col_M:
        st.markdown("""
        <div style="text-align:center; padding:2rem 0 1rem;">
            <div style="font-size:4.5rem; line-height:1;">🕌</div>
            <div style="font-size:1.6rem; font-weight:800; color:#0D47A1; margin-top:.5rem;">
                Mushollah Ar Rohman
            </div>
            <div style="color:#607D8B; font-size:.9rem;">Perum BRI, Cepu</div>
            <hr style="border-color:#E3F2FD; margin:1rem 0;">
            <div style="font-size:1.1rem; font-weight:700; color:#333;">
                🎫 Kupon Qurban Digital
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="admin")
            password = st.text_input("🔒 Password", type="password", placeholder="••••••••")
            masuk    = st.form_submit_button("🔑 Masuk", type="primary", use_container_width=True)

            if masuk:
                if not username or not password:
                    st.error("Username dan password wajib diisi.")
                else:
                    result = db_login(username, password)
                    if result:
                        st.session_state.update({
                            "logged_in": True,
                            "user_id":   result[0],
                            "username":  result[1],
                            "user_nama": result[2],
                            "role":      result[3],
                        })
                        st.rerun()
                    else:
                        st.error("❌ Username atau password salah!")

        st.markdown("""
        <div style="text-align:center; color:#90A4AE; font-size:.78rem; margin-top:.8rem;">
            Login default → username: <b>admin</b> | password: <b>admin123</b>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DASHBOARD
# ═══════════════════════════════════════════════════════════════
def page_dashboard():
    st.markdown(f'<div class="section-title">🏠 Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{MASJID} · {LOKASI} · Kupon Qurban {TAHUN}</div>',
                unsafe_allow_html=True)

    tp, tk, sd, bd, bk = db_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "👥", tp,  "Total Penerima",      ""),
        (c2, "🎫", tk,  "Total Kupon",          ""),
        (c3, "✅", sd,  "Sudah Diambil",        "green"),
        (c4, "⏳", bd,  "Belum Diambil",        "orange"),
        (c5, "📋", bk,  "Belum Ada Kupon",      "purple"),
    ]
    for col, icon, val, label, cls in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card {cls}">
                <div class="metric-icon">{icon}</div>
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Progress bar
    col_prog, col_info = st.columns([3, 1])
    with col_prog:
        st.markdown("### 📊 Progress Pengambilan Qurban")
        if tk > 0:
            pct = sd / tk
            st.progress(pct, text=f"{sd} dari {tk} kupon sudah diambil  ({pct*100:.1f}%)")
        else:
            st.info("Belum ada kupon. Silakan generate kupon terlebih dahulu.")

    with col_info:
        st.metric("Sisa Kupon", bd, f"-{sd} sudah diambil" if sd else "")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🕐 10 Pengambilan Terakhir")
        conn = get_conn()
        df_last = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID Kupon", p.nama AS "Penerima",
                   k.diambil_at AS "Waktu", k.diambil_oleh AS "Petugas"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Sudah Diambil'
            ORDER BY k.diambil_at DESC LIMIT 10
        """, conn)
        if df_last.empty:
            st.info("Belum ada pengambilan.")
        else:
            st.dataframe(df_last, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown("### ⏳ Kupon Belum Diambil (10 teratas)")
        conn = get_conn()
        df_pending = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID Kupon", p.nama AS "Penerima", p.no_hp AS "No. HP"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Baru Dibuat'
            ORDER BY k.id LIMIT 10
        """, conn)
        if df_pending.empty:
            st.success("🎉 Semua kupon sudah diambil!")
        else:
            st.dataframe(df_pending, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DATA PENERIMA
# ═══════════════════════════════════════════════════════════════
def page_data_penerima():
    st.markdown('<div class="section-title">👥 Data Penerima</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Kelola daftar calon penerima kupon qurban.</div>',
                unsafe_allow_html=True)

    tab_list, tab_tambah, tab_import = st.tabs(
        ["📋 Daftar Penerima", "➕ Tambah Penerima", "📥 Import CSV"]
    )

    # ── Tab: Daftar ──
    with tab_list:
        df = db_get_all_penerima()
        if df.empty:
            st.info("Belum ada data penerima. Silakan tambah di tab 'Tambah Penerima'.")
        else:
            conn = get_conn()
            has_kupon = set(
                r[0] for r in conn.execute("SELECT penerima_id FROM kupon").fetchall()
            )
            df["Kupon"] = df["id"].apply(lambda x: "✅" if x in has_kupon else "❌")

            st.markdown(f"**Total: {len(df)} penerima**")
            st.dataframe(
                df[["id", "nama", "no_hp", "alamat", "rt_rw", "Kupon", "created_at"]].rename(
                    columns={"id": "No", "nama": "Nama", "no_hp": "No. HP",
                             "alamat": "Alamat", "rt_rw": "RT/RW", "created_at": "Terdaftar"}
                ),
                use_container_width=True, hide_index=True
            )

            st.markdown("---")
            st.markdown("### ✏️ Edit / Hapus Penerima")
            opts = {f"#{r['id']} – {r['nama']}": r["id"] for _, r in df.iterrows()}
            sel  = st.selectbox("Pilih penerima", list(opts.keys()), key="sel_edit")
            pid  = opts[sel]
            row  = df[df["id"] == pid].iloc[0]

            c1, c2 = st.columns(2)
            with c1:
                en  = st.text_input("Nama",   value=row["nama"],      key="en")
                ehp = st.text_input("No. HP", value=row["no_hp"] or "", key="ehp")
            with c2:
                ea  = st.text_input("Alamat", value=row["alamat"] or "", key="ea")
                er  = st.text_input("RT/RW",  value=row["rt_rw"]  or "", key="er")

            cb1, cb2, _ = st.columns([1, 1, 3])
            with cb1:
                if st.button("💾 Simpan", type="primary", key="btn_edit"):
                    db_update_penerima(pid, en, ehp, ea, er)
                    st.success(f"Data '{en}' berhasil diperbarui!")
                    st.rerun()
            with cb2:
                if st.button("🗑️ Hapus", type="secondary", key="btn_del"):
                    db_delete_penerima(pid)
                    st.success("Penerima dihapus.")
                    st.rerun()

    # ── Tab: Tambah ──
    with tab_tambah:
        st.markdown("### Tambah Penerima Baru")
        with st.form("form_tambah_penerima", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nama  = st.text_input("Nama Lengkap *", placeholder="Ahmad Fauzan")
                no_hp = st.text_input("No. HP",         placeholder="0812-3456-7890")
            with c2:
                alamat = st.text_input("Alamat",  placeholder="Jl. Sejahtera No. 3")
                rt_rw  = st.text_input("RT/RW",   placeholder="RT 01/RW 02")
            sub = st.form_submit_button("➕ Tambah Penerima", type="primary")
            if sub:
                if not nama.strip():
                    st.error("Nama tidak boleh kosong!")
                else:
                    db_add_penerima(nama.strip(), no_hp, alamat, rt_rw)
                    st.success(f"✅ Penerima '{nama}' berhasil ditambahkan!")
                    st.rerun()

    # ── Tab: Import CSV ──
    with tab_import:
        st.markdown("### Import Data dari CSV")
        st.info("""
        **Format CSV (tanpa header):**  
        `nama, no_hp, alamat, rt_rw`  
        Contoh: `Siti Aisyah, 0813-1234-5678, Jl. Melati No. 15, RT 02/RW 03`
        """)
        uploaded = st.file_uploader("Upload file CSV", type=["csv"])
        if uploaded:
            try:
                df_imp = pd.read_csv(uploaded, header=None)
                cols   = ["nama", "no_hp", "alamat", "rt_rw"]
                df_imp.columns = cols[:len(df_imp.columns)]
                st.markdown(f"**Preview: {len(df_imp)} baris**")
                st.dataframe(df_imp, hide_index=True)

                if st.button("✅ Import Semua Data", type="primary"):
                    cnt = 0
                    for _, r in df_imp.iterrows():
                        db_add_penerima(
                            str(r.get("nama", "")).strip(),
                            str(r.get("no_hp", "")),
                            str(r.get("alamat", "")),
                            str(r.get("rt_rw", ""))
                        )
                        cnt += 1
                    st.success(f"✅ {cnt} penerima berhasil diimport!")
                    st.rerun()
            except Exception as e:
                st.error(f"Gagal membaca CSV: {e}")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: GENERATE KUPON
# ═══════════════════════════════════════════════════════════════
def page_generate_kupon():
    st.markdown('<div class="section-title">🎫 Generate Kupon</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Buat kupon digital secara otomatis untuk setiap penerima.</div>',
                unsafe_allow_html=True)

    tp, tk, sd, bd, bk = db_stats()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{tp}</div>
            <div class="metric-label">Total Penerima</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card orange">
            <div class="metric-icon">📋</div>
            <div class="metric-value">{bk}</div>
            <div class="metric-label">Belum Punya Kupon</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card green">
            <div class="metric-icon">🎫</div>
            <div class="metric-value">{tk}</div>
            <div class="metric-label">Total Kupon Dibuat</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if tp == 0:
        st.warning("⚠️ Belum ada data penerima. Tambahkan penerima terlebih dahulu di menu Data Penerima.")
    elif bk == 0:
        st.markdown("""
        <div class="alert-success">
            ✅ <b>Semua penerima sudah memiliki kupon!</b>
            Tidak ada kupon baru yang perlu dibuat.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-warning">
            📋 Terdapat <b>{bk} penerima</b> yang belum memiliki kupon.
            Klik tombol di bawah untuk membuat kupon secara otomatis.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        if st.button("🎫  Generate Kupon Sekarang", type="primary", use_container_width=True):
            with st.spinner("⚙️  Sistem membuat kupon digital secara otomatis..."):
                n = db_generate_all_kupon()
            st.success(f"🎉 Berhasil membuat {n} kupon digital!")
            st.balloons()
            st.rerun()

    # Reset zona
    if tk > 0:
        st.markdown("---")
        with st.expander("⚠️ Zona Berbahaya – Hapus Semua Kupon"):
            st.warning("Tindakan ini akan **menghapus semua kupon** dan tidak bisa dibatalkan.")
            konfirm = st.text_input("Ketik **HAPUS** untuk konfirmasi", key="konfirm_hapus")
            if st.button("🗑️ Hapus Semua Kupon", type="secondary"):
                if konfirm.strip().upper() == "HAPUS":
                    db_delete_all_kupon()
                    st.success("Semua kupon berhasil dihapus.")
                    st.rerun()
                else:
                    st.error("Konfirmasi tidak sesuai.")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: DATA KUPON
# ═══════════════════════════════════════════════════════════════
def page_data_kupon():
    st.markdown('<div class="section-title">📋 Data Kupon</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Lihat, cetak, atau kirim digital kupon qurban.</div>',
                unsafe_allow_html=True)

    df = db_get_all_kupon()
    if df.empty:
        st.info("Belum ada kupon. Generate kupon terlebih dahulu di menu Generate Kupon.")
        return

    # ── Filter ──
    cf1, cf2, cf3 = st.columns([3, 2, 1])
    with cf1:
        search = st.text_input("🔍 Cari ID Kupon / Nama Penerima", "")
    with cf2:
        filter_status = st.selectbox("Filter Status", ["Semua", "Baru Dibuat", "Sudah Diambil"])
    with cf3:
        st.markdown("<br>", unsafe_allow_html=True)
        total_shown = st.empty()

    filt = df.copy()
    if search:
        mask = (filt["id_kupon"].str.contains(search, case=False, na=False) |
                filt["penerima"].str.contains(search, case=False, na=False))
        filt = filt[mask]
    if filter_status != "Semua":
        filt = filt[filt["status"] == filter_status]

    total_shown.metric("Ditampilkan", len(filt))

    # ── Table ──
    display_df = filt[["id_kupon", "penerima", "no_hp", "alamat", "status",
                        "created_at", "diambil_at", "diambil_oleh"]].rename(columns={
        "id_kupon": "ID Kupon", "penerima": "Penerima", "no_hp": "No. HP",
        "alamat": "Alamat", "status": "Status", "created_at": "Dibuat",
        "diambil_at": "Diambil", "diambil_oleh": "Petugas"
    })
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Detail & Print ──
    st.markdown("---")
    st.markdown("### 🖨️ Lihat & Cetak / Kirim Digital Kupon")

    opts = {f"{r['id_kupon']} – {r['penerima']}": r["id_kupon"]
            for _, r in filt.iterrows()}
    if not opts:
        st.warning("Tidak ada kupon yang sesuai filter.")
        return

    sel_kupon = st.selectbox("Pilih Kupon", list(opts.keys()))
    id_kupon  = opts[sel_kupon]
    row       = db_get_kupon_by_id(id_kupon)

    if row:
        _, id_k, nama, no_hp, alamat, rt_rw, status, created_at, diambil_at, diambil_oleh, catatan = row

        colA, colB = st.columns([1, 2])

        with colA:
            qr_bytes = make_qr_bytes(id_k)
            st.image(qr_bytes, caption=f"QR: {id_k}", width=210)
            st.download_button(
                "⬇️ Download QR Code", data=qr_bytes,
                file_name=f"qr_{id_k}.png", mime="image/png"
            )

        with colB:
            badge = ("badge-diambil" if status == "Sudah Diambil" else "badge-baru")
            st.markdown(f"""
            <div class="kupon-preview">
                <div style="font-size:.8rem; color:#607D8B; text-transform:uppercase; letter-spacing:.08em;">ID Kupon</div>
                <div style="font-size:1.5rem; font-weight:800; color:#0D47A1; margin-bottom:.5rem;">{id_k}</div>
                <div style="font-size:.8rem; color:#607D8B;">Penerima</div>
                <div style="font-size:1.1rem; font-weight:700; margin-bottom:.4rem;">{nama}</div>
                <div style="font-size:.85rem; color:#455A64;">📞 {no_hp or '-'}</div>
                <div style="font-size:.85rem; color:#455A64;">📍 {alamat or '-'} {rt_rw or ''}</div>
                <div style="margin-top:.8rem;">
                    Status: <span class="{badge}">{status}</span>
                </div>
                <div style="font-size:.8rem; color:#90A4AE; margin-top:.4rem;">Dibuat: {created_at}</div>
            </div>
            """, unsafe_allow_html=True)

            if status == "Sudah Diambil":
                st.markdown(f"""
                <div class="alert-success" style="margin-top:.8rem;">
                    ✅ Diambil: {diambil_at}<br>
                    👤 Petugas: {diambil_oleh or '-'}<br>
                    📝 Catatan: {catatan or '-'}
                </div>
                """, unsafe_allow_html=True)

            # Download kupon lengkap
            st.markdown("<br>", unsafe_allow_html=True)
            kupon_img = make_kupon_image(id_k, nama)
            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                st.download_button(
                    "🖨️ Download Kupon (Cetak)",
                    data=kupon_img,
                    file_name=f"kupon_{id_k}.png",
                    mime="image/png",
                    type="primary",
                    use_container_width=True
                )
            with c_dl2:
                if status == "Sudah Diambil":
                    if st.button("↩️ Reset Status", use_container_width=True):
                        db_reset_kupon(id_k)
                        st.success("Status kupon direset ke 'Baru Dibuat'.")
                        st.rerun()

        # Preview kupon image
        st.markdown("---")
        st.markdown("**Preview Kupon:**")
        st.image(kupon_img, use_container_width=False, width=680)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: VALIDASI / SCAN
# ═══════════════════════════════════════════════════════════════
def page_validasi():
    st.markdown('<div class="section-title">📷 Validasi / Scan Kupon</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Konfirmasi pengambilan qurban dengan scan QR atau input manual ID Kupon.</div>',
                unsafe_allow_html=True)

    # Petugas
    petugas = st.text_input(
        "👤 Nama Petugas *",
        value=st.session_state.get("user_nama", ""),
        placeholder="Nama petugas yang bertugas hari ini"
    )

    st.markdown("---")

    col_input, col_stat = st.columns([3, 1])
    with col_input:
        id_input = st.text_input(
            "🔢 Input Manual ID Kupon",
            placeholder="Contoh: QBN-2026-0001",
            key="id_input_scan"
        )
    with col_stat:
        _, tk, sd, bd, _ = db_stats()
        st.metric("Sisa", bd, f"{sd} sudah diambil")

    btn_cari = st.button("🔍 Cari Kupon", type="primary")

    if btn_cari:
        if not id_input.strip():
            st.warning("Masukkan ID Kupon terlebih dahulu.")
        else:
            row = db_get_kupon_by_id(id_input.strip())
            if not row:
                st.markdown(f"""
                <div class="alert-danger">
                    ❌ Kupon dengan ID <b>{id_input.strip().upper()}</b> tidak ditemukan dalam sistem!
                </div>
                """, unsafe_allow_html=True)
            else:
                _, id_k, nama, no_hp, alamat, rt_rw, status, created_at, diambil_at, diambil_oleh, catatan = row

                st.markdown("---")
                st.markdown("### 📋 Data Kupon Ditemukan")

                cA, cB = st.columns([1, 2])
                with cA:
                    qr_b = make_qr_bytes(id_k)
                    st.image(qr_b, width=180)

                with cB:
                    st.markdown(f"""
                    **ID Kupon:** `{id_k}`  
                    **Penerima:** {nama}  
                    **No. HP:** {no_hp or '-'}  
                    **Alamat:** {alamat or '-'} {rt_rw or ''}
                    """)

                if status == "Sudah Diambil":
                    st.markdown(f"""
                    <div class="alert-danger">
                        ⚠️ <b>KUPON INI SUDAH DIAMBIL!</b><br>
                        Waktu pengambilan : {diambil_at}<br>
                        Dikonfirmasi oleh : {diambil_oleh or '-'}<br>
                        Catatan            : {catatan or '-'}
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.markdown("""
                    <div class="alert-success">
                        ✅ <b>Data sesuai. Kupon belum diambil.</b><br>
                        Konfirmasi pengambilan di bawah.
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### ✅ Konfirmasi Pengambilan")
                    catatan_inp = st.text_input(
                        "Catatan (opsional)",
                        placeholder="Contoh: Diwakilkan oleh...",
                        key="catatan_konfirm"
                    )

                    if st.button("✅  Konfirmasi Pengambilan", type="primary", use_container_width=True):
                        if not petugas.strip():
                            st.warning("⚠️ Mohon isi nama petugas terlebih dahulu!")
                        else:
                            db_konfirmasi(id_k, petugas.strip(), catatan_inp)
                            st.success(
                                f"🎉 Pengambilan oleh **{nama}** berhasil dikonfirmasi! "
                                f"Status kupon **{id_k}** berubah menjadi **SUDAH DIAMBIL**."
                            )
                            st.balloons()
                            st.rerun()

    # ── Daftar Belum Diambil ──
    st.markdown("---")
    col_ta, col_tb = st.columns(2)

    with col_ta:
        st.markdown("### ⏳ Kupon Belum Diambil")
        conn = get_conn()
        df_bd = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID Kupon", p.nama AS "Penerima", p.no_hp AS "No. HP"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Baru Dibuat' ORDER BY k.id
        """, conn)
        if df_bd.empty:
            st.success("🎉 Semua kupon sudah diambil!")
        else:
            st.info(f"Masih ada **{len(df_bd)}** kupon belum diambil.")
            st.dataframe(df_bd, use_container_width=True, hide_index=True)

    with col_tb:
        st.markdown("### ✅ Kupon Sudah Diambil")
        conn = get_conn()
        df_sd = pd.read_sql_query("""
            SELECT k.id_kupon AS "ID Kupon", p.nama AS "Penerima",
                   k.diambil_at AS "Waktu", k.diambil_oleh AS "Petugas"
            FROM kupon k JOIN penerima p ON k.penerima_id=p.id
            WHERE k.status='Sudah Diambil' ORDER BY k.diambil_at DESC
        """, conn)
        if df_sd.empty:
            st.info("Belum ada pengambilan.")
        else:
            st.info(f"**{len(df_sd)}** kupon sudah diambil.")
            st.dataframe(df_sd, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: LAPORAN
# ═══════════════════════════════════════════════════════════════
def page_laporan():
    st.markdown('<div class="section-title">📊 Laporan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Ringkasan dan export data kupon qurban.</div>',
                unsafe_allow_html=True)

    tp, tk, sd, bd, bk = db_stats()

    # Summary table
    df_sum = pd.DataFrame({
        "Keterangan": ["Total Penerima", "Total Kupon", "Sudah Diambil",
                        "Belum Diambil", "Belum Punya Kupon"],
        "Jumlah": [tp, tk, sd, bd, bk]
    })
    col_s, col_p = st.columns([1, 2])
    with col_s:
        st.markdown(f"### 📈 Ringkasan {TAHUN}")
        st.dataframe(df_sum, use_container_width=True, hide_index=True)
    with col_p:
        st.markdown("### 📊 Persentase Pengambilan")
        if tk > 0:
            pct = sd / tk
            st.progress(pct, text=f"{pct*100:.1f}% kupon sudah diambil")
            st.markdown(f"""
            | Metric | Nilai |
            |---|---|
            | Persentase Sudah Diambil | `{pct*100:.1f}%` |
            | Persentase Belum Diambil | `{(1-pct)*100:.1f}%` |
            """)
        else:
            st.info("Belum ada kupon.")

    st.markdown("---")

    # Export
    df_all = db_get_all_kupon()
    if not df_all.empty:
        st.markdown("### 📥 Export Data")
        csv = df_all.to_csv(index=False).encode("utf-8")
        tanggal = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            "⬇️ Download Laporan CSV",
            data=csv,
            file_name=f"laporan_kupon_qurban_{TAHUN}_{tanggal}.csv",
            mime="text/csv",
            type="primary"
        )
        st.markdown("### 📋 Data Lengkap Kupon")
        st.dataframe(df_all, use_container_width=True, hide_index=True)
    else:
        st.info("Belum ada data kupon.")


# ═══════════════════════════════════════════════════════════════
#  HALAMAN: PENGATURAN
# ═══════════════════════════════════════════════════════════════
def page_pengaturan():
    st.markdown('<div class="section-title">⚙️ Pengaturan</div>', unsafe_allow_html=True)

    tab_pw, tab_info = st.tabs(["🔑 Ganti Password", "ℹ️ Info Aplikasi"])

    with tab_pw:
        st.markdown("### Ganti Password Admin")
        with st.form("form_ganti_pw"):
            old_pw  = st.text_input("Password Lama",            type="password")
            new_pw  = st.text_input("Password Baru",            type="password")
            conf_pw = st.text_input("Konfirmasi Password Baru", type="password")
            sub     = st.form_submit_button("💾 Simpan Password", type="primary")
            if sub:
                if new_pw != conf_pw:
                    st.error("Password baru tidak cocok!")
                elif len(new_pw) < 6:
                    st.error("Password minimal 6 karakter!")
                else:
                    result = db_login(st.session_state["username"], old_pw)
                    if not result:
                        st.error("Password lama salah!")
                    else:
                        conn = get_conn()
                        new_hash = hashlib.sha256(new_pw.encode()).hexdigest()
                        conn.execute(
                            "UPDATE users SET password=? WHERE username=?",
                            (new_hash, st.session_state["username"])
                        )
                        conn.commit()
                        st.success("✅ Password berhasil diubah!")

    with tab_info:
        st.markdown(f"""
        ### Informasi Aplikasi

        | | |
        |---|---|
        | **Aplikasi** | Kupon Qurban Digital |
        | **Versi**    | 1.0.0 |
        | **Mushollah**| {MASJID} |
        | **Lokasi**   | {LOKASI} |
        | **Tahun**    | {TAHUN} |
        | **Prefix ID**| {PREFIX_KUPON}-XXXX |
        | **Database** | SQLite (lokal) |

        ---
        ### Panduan Singkat
        1. **Login Admin** → masuk dengan akun admin
        2. **Data Penerima** → input/import daftar calon penerima
        3. **Generate Kupon** → klik Generate untuk buat kupon otomatis
        4. **Data Kupon** → lihat, cetak, atau kirim digital kupon
        5. **Validasi/Scan** → input ID kupon untuk konfirmasi pengambilan
        6. **Laporan** → export data ke CSV
        """)


# ═══════════════════════════════════════════════════════════════
#  SIDEBAR & MAIN ROUTER
# ═══════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:1.2rem 0 .5rem;">
            <div style="font-size:3rem; line-height:1;">🕌</div>
            <div style="font-weight:800; font-size:1rem; margin-top:.4rem;">{MASJID}</div>
            <div style="font-size:.78rem; opacity:.8;">{LOKASI}</div>
            <div style="font-size:.75rem; opacity:.7; margin-top:.2rem;">Kupon Qurban {TAHUN}</div>
        </div>
        <hr style="border-color:rgba(255,255,255,.2); margin:.5rem 0;">
        """, unsafe_allow_html=True)

        menu = st.radio(
            "Navigasi",
            ["🏠  Dashboard",
             "👥  Data Penerima",
             "🎫  Generate Kupon",
             "📋  Data Kupon",
             "📷  Validasi / Scan",
             "📊  Laporan",
             "⚙️  Pengaturan"],
            label_visibility="collapsed"
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,.2);'>", unsafe_allow_html=True)

        # Quick stats
        tp, tk, sd, bd, _ = db_stats()
        st.markdown(f"""
        <div style="font-size:.78rem; opacity:.85; line-height:2;">
            👥 Penerima: <b>{tp}</b><br>
            🎫 Kupon: <b>{tk}</b><br>
            ✅ Diambil: <b>{sd}</b><br>
            ⏳ Sisa: <b>{bd}</b>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:rgba(255,255,255,.2);'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:.78rem; opacity:.8;">
            👤 {st.session_state.get('user_nama', 'Admin')}
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()

    return menu


def main():
    init_db()

    if not st.session_state.get("logged_in"):
        page_login()
        return

    menu = sidebar()

    if   "Dashboard"     in menu: page_dashboard()
    elif "Data Penerima" in menu: page_data_penerima()
    elif "Generate"      in menu: page_generate_kupon()
    elif "Data Kupon"    in menu: page_data_kupon()
    elif "Validasi"      in menu: page_validasi()
    elif "Laporan"       in menu: page_laporan()
    elif "Pengaturan"    in menu: page_pengaturan()


if __name__ == "__main__":
    main()
