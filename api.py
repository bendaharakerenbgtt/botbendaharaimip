from flask import Flask, request, jsonify
import io
import contextlib
import os
from datetime import datetime

from scraper import (
    ambil_data,
    cek_kas,
    rekap_kas,
    rekap_kas_rapih,
    ambil_bulan
)
from ai_gemini import tanya_ilmi, bersihkan_format_markdown


app = Flask(__name__)


# ==========================
# SIMPAN LOG PERTANYAAN USER
# ==========================

def simpan_log_pertanyaan(pesan_user):
    if not pesan_user or not pesan_user.strip():
        return
    try:
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("log_pertanyaan.txt", "a", encoding="utf-8") as f:
            f.write(f"[{waktu}] {pesan_user.strip()}\n")
    except Exception as e:
        print("Gagal menyimpan log:", e)


def ambil_log_pertanyaan(jumlah=20):
    if not os.path.exists("log_pertanyaan.txt"):
        return "Belum ada riwayat pertanyaan tercatat."
    try:
        with open("log_pertanyaan.txt", "r", encoding="utf-8") as f:
            baris = f.readlines()
        baris_terakhir = baris[-jumlah:]
        return "".join(baris_terakhir)
    except Exception as e:
        return f"Gagal membaca log: {e}"


# ==========================
# FORMAT OUTPUT
# ==========================

def capture_output(func, *args):

    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        func(*args)

    return output.getvalue()



# ==========================
# LOAD DATA TERBARU
# ==========================

def get_database():

    anggota, transaksi = ambil_data()

    return anggota, transaksi



# ==========================
# COMMAND HELP
# ==========================

def bantuan():

    return """
Assalamu'alaikum! Akang/Teteh, saya **Ilmi** (Asisten Resmi IMIP) 🤖✨

Format Perintah Kas:

1. Cek kas anggota
kas [NIM] [bulan]
Contoh: kas 2490343138 agustus

2. Rekap kas biasa
rekap kas [bulan]
Contoh: rekap kas agustus

3. Rekap kas rapih
rekap kas rapih [bulan]
Contoh: rekap kas rapih agustus

4. Tanya Ilmi AI (Tanya apa saja seputar IMIP)
Sertakan kata "ilmi" dalam pesan kamu!
Contoh: ilmi siapa ketua IMIP tahun ini?
"""



# ==========================
# CEK KAS
# ==========================

def proses_cek_kas(
        nim,
        bulan,
        anggota,
        transaksi
):


    hasil = capture_output(
        cek_kas,
        nim,
        bulan,
        anggota,
        transaksi
    )


    return hasil



# ==========================
# REKAP KAS BIASA
# ==========================

def proses_rekap(
        bulan,
        anggota,
        transaksi
):


    hasil = capture_output(
        rekap_kas,
        bulan,
        anggota,
        transaksi
    )


    return hasil



# ==========================
# REKAP KAS RAPIH
# ==========================

def proses_rekap_rapih(
        bulan,
        anggota,
        transaksi
):


    hasil = capture_output(
        rekap_kas_rapih,
        bulan,
        anggota,
        transaksi
    )


    return hasil





# ==========================
# HEALTH CHECK / KEEP ALIVE
# ==========================

@app.route("/", methods=["GET"])
def home():
    return "IMIP Bot Bendahara is active and running!"


# ==========================
# API BOT
# ==========================

@app.route("/bot", methods=["POST"])
def bot():
    data = request.json or {}
    pesan = data.get("message", "")
    text = pesan.lower()

    if not pesan or not pesan.strip():
        return jsonify({"reply": ""})

    # ATURAN EMAS GRUP BESAR: Bot HANYA BANGUN jika pengguna memanggil kata "ilmi"!
    # Jika tidak memanggil "ilmi", bot DIAM TOTAL (100% anti-spam di grup)
    if "ilmi" not in text:
        return jsonify({"reply": ""})

    # Catat semua log pertanyaan masuk karena sudah dipastikan memanggil ilmi
    simpan_log_pertanyaan(pesan)

    import re
    has_rekap = "rekap" in text
    has_kas_word = bool(re.search(r'\bkas\b', text))

    # Cari NIM (angka 8 digit ke atas)
    kata = pesan.split()
    nim = None
    for k in kata:
        k_bersih = ''.join(c for c in k if c.isdigit())
        if len(k_bersih) >= 8:
            nim = k_bersih
            break

    reply = ""

    # 1. Perintah Laporan / Log (Khusus pengembang / Riski Raditiya)
    if "log" in text or "laporan" in text:
        reply = "📋 LAPORAN PERTANYAAN MASUK KE ILMI AI (20 TERAKHIR):\n\n" + ambil_log_pertanyaan(20)

    # 2. Perintah Help / Bantuan (misal "ilmi help", "ilmi bantuan")
    elif "help" in text or "bantuan" in text:
        reply = bantuan()

    # 3. Perintah Rekap Kas Rapih (misal "ilmi rekap kas rapih", "ilmi rekap rapih")
    elif has_rekap and ("rapih" in text or "rapi" in text):
        anggota, transaksi = get_database()
        bulan = ambil_bulan(text)
        reply = proses_rekap_rapih(bulan, anggota, transaksi)

    # 4. Perintah Rekap Kas Biasa (misal "ilmi rekap kas", "ilmi rekap")
    elif has_rekap:
        anggota, transaksi = get_database()
        bulan = ambil_bulan(text)
        reply = proses_rekap(bulan, anggota, transaksi)

    # 5. Perintah Cek Kas NIM Spesifik (misal "ilmi kas 2490343138" atau "ilmi cek kas 2490343138")
    elif nim:
        anggota, transaksi = get_database()
        bulan = ambil_bulan(text)
        reply = proses_cek_kas(nim, bulan, anggota, transaksi)

    # 6. Pertanyaan Umum / AI Gemini (misal "ilmi siapa ketua IMIP?")
    else:
        reply = tanya_ilmi(pesan)

    reply_bersih = bersihkan_format_markdown(reply.strip())
    return jsonify({
        "reply": reply_bersih
    })


# ==========================
# WEB ROUTE LOGS PERTANYAAN (FOR RISKI RADITIYA)
# ==========================

@app.route("/logs", methods=["GET"])
def lihat_logs():
    logs = ambil_log_pertanyaan(100)
    return f"""
    <html>
        <head>
            <title>Laporan Pertanyaan Masuk - Ilmi AI</title>
            <style>
                body {{ font-family: monospace; background: #0f172a; color: #38bdf8; padding: 20px; }}
                h1 {{ color: #f43f5e; }}
                pre {{ background: #1e293b; padding: 15px; border-radius: 8px; color: #f8fafc; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>📋 Laporan Pertanyaan Masuk ke Ilmi AI</h1>
            <p>Pengembang: <b>Riski Raditiya</b> (Biro Bendahara LDK IMIP 2026)</p>
            <hr/>
            <pre>{logs}</pre>
        </body>
    </html>
    """





if __name__ == "__main__":


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

    