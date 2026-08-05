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
    import time
    ts = int(time.time())
    url_anggota = f"{URL_ANGGOTA}&_cb={ts}"
    url_transaksi = f"{URL_TRANSAKSI}&_cb={ts}"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    res_ang = requests.get(url_anggota, headers=headers, timeout=10)
    res_tra = requests.get(url_transaksi, headers=headers, timeout=10)
    
    anggota = pd.read_csv(StringIO(res_ang.text))
    transaksi = pd.read_csv(StringIO(res_tra.text))

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
# REKAP SEMUA (BIASA BERDASARKAN JABATAN & DIVISI)
# ==========================

def rekap_kas(
        bulan_limit,
        anggota,
        transaksi
):

    print("========================")
    print(f"REKAP KAS {bulan_list[bulan_limit].upper()}")
    print("========================\n")

    anggota_aktif = anggota[anggota["is_active"] == True]

    grup_order = [
        "Pimpinan Utama",
        "Kepala Departemen",
        "Biro Kesekretariatan",
        "Biro Bendahara",
        "Departemen Kaderisasi",
        "Departemen Syi'ar Islam",
        "Departemen Sosial Masyarakat",
        "Departemen HuMed",
        "Departemen UUS"
    ]
    grup_dict = {g: [] for g in grup_order}

    for _, orang in anggota_aktif.iterrows():
        nama = orang["nama"]
        jabatan = str(orang["jabatan"]).strip()
        divisi = str(orang["divisi"]).strip()
        
        tunggakan = hitung_tunggakan(orang["id_anggota"], bulan_limit, transaksi)
        if len(tunggakan) > 0:
            jumlah = len(tunggakan) * 10000
            jumlah_str = f"{jumlah:,}".replace(",", ".")
            status = f"Tunggakan Rp {jumlah_str}"
        else:
            status = "LUNAS"

        if divisi == "Pimpinan Utama" or jabatan in ["Ketua Umum", "Sekretaris Jenderal", "Sekretaris Jenderal (Mas'ul)", "Koor Keakhwatan"]:
            kategori = "Pimpinan Utama"
        elif jabatan in ["Kepala Departemen", "Kepala Biro"]:
            kategori = "Kepala Departemen"
        elif divisi in grup_dict:
            kategori = divisi
        else:
            kategori = "Lainnya"

        if kategori in grup_dict:
            grup_dict[kategori].append((nama, jabatan, status))

    for g in grup_order:
        list_orang = grup_dict[g]
        if list_orang:
            print(f"[ {g.upper()} ]")
            for nama, jab, status in list_orang:
                print(f"{nama} ({jab}) : {status}")
            print("")


# ==========================
# REKAP SEMUA (RAPIH BERDASARKAN JABATAN & DIVISI)
# ==========================

def rekap_kas_rapih(
        bulan_limit,
        anggota,
        transaksi
):

    anggota_aktif = anggota[anggota["is_active"] == True]

    grup_order = [
        "Pimpinan Utama",
        "Kepala Departemen",
        "Biro Kesekretariatan",
        "Biro Bendahara",
        "Departemen Kaderisasi",
        "Departemen Syi'ar Islam",
        "Departemen Sosial Masyarakat",
        "Departemen HuMed",
        "Departemen UUS"
    ]
    grup_dict = {g: [] for g in grup_order}

    tot_belum_lunas = 0
    tot_lunas = 0

    for _, orang in anggota_aktif.iterrows():
        nama = orang["nama"]
        jabatan = str(orang["jabatan"]).strip()
        divisi = str(orang["divisi"]).strip()

        tunggakan = hitung_tunggakan(orang["id_anggota"], bulan_limit, transaksi)
        if len(tunggakan) > 0:
            jumlah = len(tunggakan) * 10000
            jumlah_str = f"{jumlah:,}".replace(",", ".")
            status = f"Tunggakan Rp {jumlah_str}"
            tot_belum_lunas += 1
        else:
            status = "LUNAS"
            tot_lunas += 1

        if divisi == "Pimpinan Utama" or jabatan in ["Ketua Umum", "Sekretaris Jenderal", "Sekretaris Jenderal (Mas'ul)", "Koor Keakhwatan"]:
            kategori = "Pimpinan Utama"
        elif jabatan in ["Kepala Departemen", "Kepala Biro"]:
            kategori = "Kepala Departemen"
        elif divisi in grup_dict:
            kategori = divisi
        else:
            kategori = "Lainnya"

        if kategori in grup_dict:
            grup_dict[kategori].append((nama, jabatan, status))

    nama_bulan = bulan_list[bulan_limit].upper()
    lines = []
    lines.append("====================")
    lines.append(f"REKAP KAS {nama_bulan}")
    lines.append("====================\n")

    for g in grup_order:
        list_orang = grup_dict[g]
        if list_orang:
            lines.append(f"[ {g.upper()} ]")
            for nama, jab, status in list_orang:
                lines.append(f"{nama} ({jab}) : {status}")
            lines.append("")

    lines.append("====================")
    lines.append("RINGKASAN TOTAL:")
    lines.append(f"Belum Lunas: {tot_belum_lunas} orang")
    lines.append(f"Lunas: {tot_lunas} orang")
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