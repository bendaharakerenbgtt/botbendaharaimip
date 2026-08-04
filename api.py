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
Bendahara IMIP Bot

Format:

1. Cek kas anggota
kas [NIM] [bulan]
Contoh: kas 2490343138 agustus

2. Rekap kas biasa
rekap kas [bulan]
Contoh: rekap kas agustus

3. Rekap kas rapih
rekap kas rapih [bulan]
Contoh: rekap kas rapih agustus

Jika bulan tidak ditulis:
otomatis sampai Desember.
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
# API BOT
# ==========================

@app.route("/bot", methods=["POST"])
def bot():


    data = request.json


    pesan = data.get(
        "message",
        ""
    )


    text = pesan.lower()



    # ambil database terbaru
    anggota, transaksi = get_database()



    # =====================
    # HELP
    # =====================

    if (
        "help" in text
        or "bantuan" in text
        or text.strip() == ""
    ):

        reply = bantuan()



    # =====================
    # REKAP RAPIH
    # =====================

    elif "rekap kas rapih" in text:

        bulan = ambil_bulan(text)

        reply = proses_rekap_rapih(
            bulan,
            anggota,
            transaksi
        )



    # =====================
    # REKAP BIASA
    # =====================

    elif "rekap kas" in text:

        bulan = ambil_bulan(text)

        reply = proses_rekap(
            bulan,
            anggota,
            transaksi
        )



    # =====================
    # CEK NIM
    # =====================

    elif "kas" in text:


        kata = pesan.split()


        nim = None


        for k in kata:

            if (
                k.isdigit()
                and len(k) >= 8
            ):

                nim = k



        if nim:


            bulan = ambil_bulan(text)


            reply = proses_cek_kas(
                nim,
                bulan,
                anggota,
                transaksi
            )


        else:

            reply = """
NIM tidak ditemukan.

Contoh:
kas 2490343138 agustus
"""



    else:


        reply = """
Perintah tidak dikenali.

Ketik:
bantuan
untuk melihat format.
"""



    return jsonify({

        "reply": reply.strip()

    })





if __name__ == "__main__":


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

    