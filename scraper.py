import pandas as pd
import requests
from io import StringIO


# ==========================
# CONFIG
# ==========================

SPREADSHEET_ID = "1rfXkBE1hd_hu69AvC5YKRHaRsu8uTlaSAKELqpIRzpI"

URL_ANGGOTA = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Anggota"
)

URL_TRANSAKSI = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=Transaksi"
)


bulan_list = [
    "",
    "Januari",
    "Februari",
    "Maret",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Agustus",
    "September",
    "Oktober",
    "November",
    "Desember"
]


bulan_mapping = {
    "januari":1,
    "februari":2,
    "maret":3,
    "april":4,
    "mei":5,
    "juni":6,
    "juli":7,
    "agustus":8,
    "september":9,
    "oktober":10,
    "november":11,
    "desember":12
}



# ==========================
# AMBIL DATA
# ==========================

def ambil_data():

    print("Mengambil data...\n")

    anggota = pd.read_csv(URL_ANGGOTA)

    transaksi = pd.read_csv(URL_TRANSAKSI)


    return anggota, transaksi




# ==========================
# FILTER PEMBAYARAN KAS
# ==========================

def cek_pembayaran(id_anggota, transaksi):

    data = transaksi[
        (transaksi["id_anggota"] == id_anggota)
    ]


    # hanya kas pengurus
    if "kategori" in data.columns:
        data = data[
            data["kategori"] == "Kas Pengurus"
        ]


    hasil = []


    for _, row in data.iterrows():

        catatan = str(row["catatan"]).lower()


        for bulan in bulan_mapping:

            if bulan in catatan:

                hasil.append(
                    bulan.capitalize()
                )


    # hilangkan duplikat
    return list(set(hasil))





# ==========================
# HITUNG TUNGGAKAN
# ==========================

def hitung_tunggakan(
        id_anggota,
        bulan_limit,
        transaksi
):

    sudah_bayar = cek_pembayaran(
        id_anggota,
        transaksi
    )


    tunggakan = []


    for i in range(1, bulan_limit+1):

        bulan = bulan_list[i]


        if bulan not in sudah_bayar:

            tunggakan.append(
                bulan
            )


    return tunggakan





# ==========================
# PARSE BULAN COMMAND
# ==========================

def ambil_bulan(text):

    text = text.lower()


    for nama, angka in bulan_mapping.items():

        if nama in text:

            return angka


    # default
    return 12






# ==========================
# REKAP SEMUA (BIASA)
# ==========================

def rekap_kas(
        bulan_limit,
        anggota,
        transaksi
):

    print("========================")
    print(
        f"REKAP KAS {bulan_list[bulan_limit].upper()}"
    )
    print("========================\n")

    # hanya aktif
    anggota_aktif = anggota[
        anggota["is_active"] == True
    ]

    belum_lunas = []
    sudah_lunas = []

    for _, orang in anggota_aktif.iterrows():

        tunggakan = hitung_tunggakan(
            orang["id_anggota"],
            bulan_limit,
            transaksi
        )

        if len(tunggakan) > 0:
            jumlah = len(tunggakan) * 10000
            jumlah_str = f"{jumlah:,}".replace(",", ".")
            belum_lunas.append(f"{orang['nama']} : {jumlah_str}")
        else:
            sudah_lunas.append(f"{orang['nama']} : LUNAS")

    for item in belum_lunas:
        print(item)

    for item in sudah_lunas:
        print(item)


# ==========================
# REKAP SEMUA (RAPIH)
# ==========================

def rekap_kas_rapih(
        bulan_limit,
        anggota,
        transaksi
):

    # hanya aktif
    anggota_aktif = anggota[
        anggota["is_active"] == True
    ]

    belum_lunas = []
    sudah_lunas = []

    for _, orang in anggota_aktif.iterrows():

        tunggakan = hitung_tunggakan(
            orang["id_anggota"],
            bulan_limit,
            transaksi
        )

        if len(tunggakan) > 0:
            jumlah = len(tunggakan) * 10000
            jumlah_str = f"{jumlah:,}".replace(",", ".")
            belum_lunas.append((orang["nama"], jumlah_str))
        else:
            sudah_lunas.append(orang["nama"])

    nama_bulan = bulan_list[bulan_limit].upper()

    lines = []
    lines.append("====================")
    lines.append(f"REKAP KAS {nama_bulan}")
    lines.append("====================")
    lines.append("")
    lines.append("BELUM LUNAS")
    lines.append("")

    for idx, (nama, tunggakan_str) in enumerate(belum_lunas, 1):
        lines.append(f"{idx}. {nama}")
        lines.append(f"   Tunggakan: {tunggakan_str}")
        lines.append("")

    lines.append("")
    lines.append("====================")
    lines.append("SUDAH LUNAS")
    lines.append("")

    for nama in sudah_lunas:
        lines.append(f"- {nama}")

    lines.append("")
    lines.append("Total:")
    lines.append(f"Belum lunas: {len(belum_lunas)} orang")
    lines.append(f"Lunas: {len(sudah_lunas)} orang")
    lines.append("====================")

    print("\n".join(lines))





# ==========================
# CEK SATU ORANG
# ==========================


def cek_kas(
        nim,
        bulan_limit,
        anggota,
        transaksi
):


    user = anggota[
        anggota["nim"].astype(str)
        ==
        str(nim)
    ]


    if user.empty:

        print(
            "NIM tidak ditemukan"
        )

        return



    orang = user.iloc[0]


    tunggakan = hitung_tunggakan(
        orang["id_anggota"],
        bulan_limit,
        transaksi
    )



    print("========================")
    print(
        orang["nama"]
    )

    print(
        f"NIM : {nim}"
    )

    print(
        f"Sampai {bulan_list[bulan_limit]}"
    )

    print("========================")



    for i in range(1,bulan_limit+1):

        bulan = bulan_list[i]


        if bulan in tunggakan:

            print(
                f"❌ {bulan}"
            )

        else:

            print(
                f"✅ {bulan}"
            )



    print()

    if tunggakan:

        print(
            "Tunggakan:",
            len(tunggakan)*10000
        )

    else:

        print(
            "LUNAS"
        )





# ==========================
# TEST COMMAND
# ==========================


if __name__ == "__main__":


    anggota, transaksi = ambil_data()


    print(
        "JUMLAH ANGGOTA:",
        len(anggota)
    )

    print(
        "JUMLAH TRANSAKSI:",
        len(transaksi)
    )


    print("\n")


    # TEST REKAP
    rekap_kas(
        ambil_bulan(""),
        anggota,
        transaksi
    )


    print("\n")


    # TEST CEK
    cek_kas(
        "2490343138",
        ambil_bulan(""),
        anggota,
        transaksi
    )