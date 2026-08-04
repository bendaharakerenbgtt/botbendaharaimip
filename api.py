from flask import Flask, request, jsonify
import io
import contextlib

from scraper import (
    ambil_data,
    cek_kas,
    rekap_kas,
    rekap_kas_rapih,
    ambil_bulan
)
from ai_gemini import tanya_ilmi


app = Flask(__name__)


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
    anggota, transaksi = get_database()

    data = request.json or {}
    pesan = data.get("message", "")
    text = pesan.lower()


    # =====================
    # HELP
    # =====================

    if (
        "help" in text
        or "bantuan" in text
    ):

        reply = bantuan()



    # =====================
    # REKAP KAS RAPIH
    # =====================
    if "rekap" in text and ("rapih" in text or "rapi" in text):
        bulan = ambil_bulan(text)
        reply = proses_rekap_rapih(
            bulan,
            anggota,
            transaksi
        )

    # =====================
    # REKAP KAS BIASA
    # =====================
    elif "rekap" in text and "kas" in text:
        bulan = ambil_bulan(text)
        reply = proses_rekap(
            bulan,
            anggota,
            transaksi
        )

    # =====================
    # CEK KAS NIM / REKAP CONVERSATIONAL
    # =====================
    elif "kas" in text:
        kata = pesan.split()
        nim = None

        for k in kata:
            # bersihkan tanda baca jika ada
            k_bersih = ''.join(c for c in k if c.isdigit())
            if len(k_bersih) >= 8:
                nim = k_bersih
                break

        if nim:
            bulan = ambil_bulan(text)
            reply = proses_cek_kas(
                nim,
                bulan,
                anggota,
                transaksi
            )
        elif "rekap" in text:
            bulan = ambil_bulan(text)
            reply = proses_rekap(
                bulan,
                anggota,
                transaksi
            )
        elif "ilmi" in text:
            reply = tanya_ilmi(pesan)
        else:
            reply = """
NIM tidak ditemukan.

Contoh:
kas 2490343138 agustus
atau: ilmi rekap kas
"""

    # =====================
    # TANYA ILMI (GEMINI AI)
    # =====================
    elif "ilmi" in text:
        reply = tanya_ilmi(pesan)

    else:
        # Jika bukan perintah kas & tidak memanggil "ilmi", diam (tidak kirim balasan)
        reply = ""



    return jsonify({

        "reply": reply.strip()

    })





if __name__ == "__main__":


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

    