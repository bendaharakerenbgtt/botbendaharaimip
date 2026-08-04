from scraper import (
    ambil_data,
    cek_kas,
    rekap_kas,
    rekap_kas_rapih,
    ambil_bulan
)


# ambil database
anggota, transaksi = ambil_data()



def proses_command(text):

    text_lower = text.lower()


    # ======================
    # REKAP KAS RAPIH
    # ======================

    if "rekap kas rapih" in text_lower:

        bulan = ambil_bulan(text_lower)

        rekap_kas_rapih(
            bulan,
            anggota,
            transaksi
        )

    # ======================
    # REKAP KAS (BIASA)
    # ======================

    elif "rekap kas" in text_lower:

        bulan = ambil_bulan(text_lower)

        rekap_kas(
            bulan,
            anggota,
            transaksi
        )


    # ======================
    # CEK KAS NIM
    # ======================

    elif "kas" in text_lower:


        # cari angka NIM
        kata = text.split()


        nim = None


        for k in kata:

            if k.isdigit():

                if len(k) >= 8:
                    nim = k



        if nim:

            bulan = ambil_bulan(
                text_lower
            )


            cek_kas(
                nim,
                bulan,
                anggota,
                transaksi
            )


        else:

            print(
                "NIM tidak ditemukan"
            )


    else:

        print(
            "Command tidak dikenali"
        )





while True:


    pesan = input("\nUser: ")


    if pesan == "exit":
        break


    proses_command(pesan)